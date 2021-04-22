from kivy.app import App
from kivymd.app import MDApp
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.button import MDFlatButton, MDFloatingActionButton
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.dialog import MDDialog
from smtplib import SMTP_SSL as SMTP
from email.mime.text import MIMEText
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.uix.list import TwoLineIconListItem, IconLeftWidget
from db import *
import threading
import requests
import json
import yaml


class Tab(MDFloatLayout, MDTabsBase):
    '''Class implementing content for a tab.'''


class MainApp(MDApp):
    with open("config.yaml", "r") as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

    reboot_opn = f'{cfg["host"]}:{cfg["port"]}/api/core/system/reboot/'
    apply = f'{cfg["host"]}:{cfg["port"]}/api/firewall/filter/apply'
    check_wg = f'{cfg["host"]}:{cfg["port"]}/api/wireguard/general/get'
    Start_wg = f'{cfg["host"]}:{cfg["port"]}/api/wireguard/general/set'
    save_wg = f'{cfg["host"]}:{cfg["port"]}/api/wireguard/service/reconfigure'

    key = cfg["key"]
    secret = cfg["secret"]

    def on_start(self):
        '''Runs all on start fuctions, database creation and queries, rule status checks whatever else needs to happen on start'''
        self.create_table()
        self.rule_list()

    def build(self):
        self.theme_cls.primary_palette = 'BlueGray'
        self.screen = Builder.load_file("main.kv")
        return self.screen

    def on_tab_switch(
        self, instance_tabs, instance_tab, instance_tab_label, tab_text
    ):
        pass

    def create_table(self):
        db.execute("""CREATE TABLE  IF NOT EXISTS rules(
        id integer PRIMARY KEY,
        name TEXT,
        uuid TEXT NOT NULL UNIQUE
        );""")

    def add_rule_clicked(self, rule_description, rule_uuid):
        try:
            db.execute(f'''INSERT OR REPLACE INTO rules(
                            name, uuid) VALUES
                            ('{rule_description}', '{rule_uuid}')''')

        finally:
            mydb.commit()
            close_button = MDFlatButton(
                text='Close', on_release=self.close_dialog)
            self.dialog = MDDialog(title='Rules', text='Rules have been added.',
                                   size_hint=(0.7, 1),
                                   buttons=[close_button])
            self.dialog.open()
            self.root.ids.ruleList.clear_widgets()
            self.rule_list()
            self.root.ids.screen_manager.current = 'MainScreen'

    def rule_list(self):
        '''Query of all rules and generates a list view under the rule tab....not really working all the way yet'''
        db.execute('''SELECT * from rules''')
        self.rows = db.fetchall()
        for r in self.rows:
            self.rule = f'{self.cfg["host"]}:{self.cfg["port"]}/api/firewall/filter/getRule/{r[2]}'
            rules = TwoLineIconListItem(
                text=r[1],
                secondary_text=r[2],
                on_release=lambda x: threading.Thread(
                    target=self.rule_on_click, args=(x.secondary_text, x), daemon=True).start()
            )
            self.check = requests.get(url=self.rule, auth=(
                self.key, self.secret), verify=False)
            if self.check.status_code == 200:
                check_rule = json.loads(self.check.text)
                if check_rule['rule']['enabled'] == '1':
                    rules.add_widget(IconLeftWidget(
                        icon='checkbox-marked-circle-outline'
                    ))
                else:
                    rules.add_widget(IconLeftWidget(
                        icon='checkbox-blank-circle-outline'
                    ))

            self.root.ids.ruleList.add_widget(rules)

    def rule_on_click(self, uuid, x):
        ''' When a rule is clicked these fuctions will check rule status, enable or disable the rule,
        clear the list view and finally recreate it with the new rule status'''
        self.rule_check(uuid, x)
        self.root.ids.ruleList.clear_widgets()
        self.rule_list()

    def rule_check(self, uuid, x):
        '''Should check to see if a rule from the list is enabled or not. It grabs the uuid from the list view click 
            and stuffs it into the rule string'''
        toggle = f'{self.cfg["host"]}:{self.cfg["port"]}/api/firewall/filter/toggleRule/{uuid}'
        self.rule = f'{self.cfg["host"]}:{self.cfg["port"]}/api/firewall/filter/getRule/{uuid}'
        self.check = requests.get(url=self.rule, auth=(
            self.key, self.secret), verify=False)
        if self.check.status_code == 200:
            check_rule = json.loads(self.check.text)
            if check_rule['rule']['enabled'] == '1':
                new_icon = 'checkbox-blank-circle-outline'
                self.rule_state_change(f'{toggle}/0', new_icon, x)
            else:
                new_icon = 'checkbox-marked-circle-outline'
                self.rule_state_change(f'{toggle}/1', new_icon, x)

    def rule_state_change(self, r_url, new_icon, x):
        '''Either enables or disables the selected rules based on current status of the rule in the firewall.
        Then calls status message function to inform the user what happend
        '''
        self.r_url = r_url
        r = requests.post(url=r_url, auth=(
            self.key, self.secret), verify=False)
        if r.status_code == 200:
            r = requests.post(url=self.apply, auth=(
                self.key, self.secret), verify=False)
            x.icon = new_icon
            self.status_message(r, r_url)

    def status_message(self, r, r_url):
        '''Creates a dialog box to notify user rule is enabled'''
        if r.status_code == 200:
            if "/1" in r_url:
                status_text = 'Rule has been enabled'
            elif "/0" in r_url:
                status_text = 'Rule has been disabled'
            elif "1" in r_url:
                status_text = 'VPN On!'
            elif "0" in r_url:
                status_text = 'VPN Off!'
            elif "reboot" in r_url:
                status_text = 'Rebooting Please wait'
            close_button = MDFlatButton(
                text='Close', on_release=self.close_dialog)
            self.dialog = MDDialog(title='Complete', text=status_text,
                                   size_hint=(0.7, 1),
                                   buttons=[close_button])
            self.dialog.open()
        else:
            close_button = MDFlatButton(
                text='Close', on_release=self.close_dialog)
            self.dialog = MDDialog(title='Error', text='An error has occured.',
                                   size_hint=(0.7, 1),
                                   buttons=[close_button])
            self.dialog.open()

    def check_wg1(self):
        '''Checks current status of WG '''
        check = requests.get(url=self.check_wg, auth=(
            self.key, self.secret), verify=False)
        if check.status_code == 200:
            check_rule = json.loads(check.text)
            if check_rule['general']['enabled'] == '1':
                self.root.ids.wg_switch.active = True

    def on_wg_active(self, *args):
        '''Enable or disable firewall rule based on current state'''
        if self.root.ids.wg_switch.active == True:
            data = {'general': {'enabled': 0}}
            self.wg_change_state(data)
        else:
            data = {'general': {'enabled': 1}}
            self.wg_change_state(data)

    def wg_change_state(self, data):
        r = requests.post(url=self.Start_wg, auth=(
            self.key, self.secret), verify=False, json=data)
        if r.status_code == 200:
            r = requests.post(url=self.save_wg, auth=(
                self.key, self.secret), verify=False)
            self.status_message(r, str(data['general']['enabled']))

    def reboot(self):
        ''' Sends Reboot API call to firewall'''
        r = requests.post(url=self.reboot_OPN, auth=(
            self.key, self.secret), verify=False)
        self.status_message(r, "reboot")

    def close_dialog(self, obj):
        '''Closes dialog boxes'''
        self.dialog.dismiss()

    def support_email(self):
        SMTPserver = self.cfg["email_host"]
        sender = self.cfg["From_email"]
        destination = [f'{self.cfg["To_email"]}']
        USERNAME = sender
        PASSWORD = self.cfg["password"]

        text_subtype = 'plain'

        content = """\
        I am having firewall issues please check it out for me.
        """

        subject = "Firewall Issues"

        try:
            msg = MIMEText(content, text_subtype)
            msg['Subject'] = subject
            msg['From'] = sender

            conn = SMTP(SMTPserver)
            conn.set_debuglevel(False)
            conn.login(USERNAME, PASSWORD)
            try:
                conn.sendmail(sender, destination, msg.as_string())
            finally:
                conn.quit()
                close_button = MDFlatButton(
                    text='Close', on_release=self.close_dialog)
                self.dialog = MDDialog(title='Email', text='You Sent an Email to admin',
                                       size_hint=(0.7, 1),
                                       buttons=[close_button])
                self.dialog.open()

        except:
            close_button = MDFlatButton(
                text='Close', on_release=self.close_dialog)
            self.dialog = MDDialog(title='Error', text='There was an error when sending your email.',
                                   size_hint=(0.7, 1),
                                   buttons=[close_button])
            self.dialog.open()


if __name__ == '__main__':
    ma = MainApp()
    ma.run()
