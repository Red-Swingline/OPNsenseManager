from kivymd.app import MDApp
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.button import MDFlatButton, MDFloatingActionButton
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.dialog import MDDialog
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.uix.list import TwoLineIconListItem, IconLeftWidget, TwoLineListItem
from db import *
import ssl
import threading
import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Tab(MDFloatLayout, MDTabsBase):
    '''Class implementing content for a tab.'''


class MainApp(MDApp):
    db.execute("""CREATE TABLE  IF NOT EXISTS rules(
    id integer PRIMARY KEY,
    rname TEXT,
    uuid TEXT NOT NULL UNIQUE
    );""")

    db.execute("""CREATE TABLE  IF NOT EXISTS api_info(
    id integer PRIMARY KEY,
    api_key TEXT NOT NULL UNIQUE,
    api_secret TEXT NOT NULL UNIQUE,
    url TEXT NOT NULL UNIQUE,
    port INTEGER
    );""")

    db.execute('''SELECT * from api_info''')
    api_info = db.fetchall()

    if len(api_info) > 0:
        url = api_info[0][3]
        port = api_info[0][4]
        key = api_info[0][1]
        secret = api_info[0][2]
    else:
        url = ''
        port = ''
        key = ''
        secret = ''

    reboot_opn = f'{url}:{port}/api/core/system/reboot/'
    apply = f'{url}:{port}/api/firewall/filter/apply'
    check_wg = f'{url}:{port}/api/wireguard/general/get'
    Start_wg = f'{url}:{port}/api/wireguard/general/set'
    save_wg = f'{url}:{port}/api/wireguard/service/reconfigure'
    url_check = f'{url}:{port}/api/core/menu/search'

    def on_start(self):
        '''Runs all on start fuctions, database creation and queries, rule status checks whatever else needs to
        happen on start'''

        if len(self.api_info) > 0:

            try:
                self.check = requests.post(url=self.url_check, auth=(
                    self.key, self.secret), verify=False)
                if self.check.status_code == 200:

                    # generates enable disable rule list on main screen.
                    self.rule_list()
                    # Generates list for selecting rules to delete from sqlite.
                    self.delete_rule_list()
                    # Checks current status of wireguard
                    self.check_wg1()
            except requests.exceptions.RequestException as e:
                self.message_output(
                    'Error', 'Error while connecting to Firewall, check URL in API Info.')
                pass
            self.set_api_info_text(self.api_info)

    def build(self):
        '''Sets app theme color and loads the builder kv file'''
        self.theme_cls.primary_palette = 'Amber'
        self.screen = Builder.load_file("main.kv")

        return self.screen

    def on_tab_switch(
        self, instance_tabs, instance_tab, instance_tab_label, tab_text
    ):
        pass

    def rule_query(self):
        '''Queries the SQLite table to get stored list of rules to be managed from the app.'''
        db.execute('''SELECT * from rules''')
        self.rows = db.fetchall()
        return self.rows

    def url_request_get(self, url):
        '''Handles all get request for checking status with firewall API'''
        self.check = requests.get(url=url, auth=(
            self.key, self.secret), verify=False)
        return self.check

    def url_request_post(self, url):
        '''Handles all post request for checking status with firewall API.'''
        self.check = requests.post(url=url, auth=(
            self.key, self.secret), verify=False)
        return self.check

    def call_main_screen(self):
        '''Switches to the main screen of the app.'''
        self.root.ids.screen_manager.current = 'rules'

    def add_back_arrow_clicked(self):
        '''Clear text fields and change to main screen'''
        self.root.ids.rule_description.text = ''
        self.root.ids.rule_uuid.text = ''
        self.call_main_screen()

    def set_api_info_text(self, api_info):
        '''Set API info in text feilds on the API info page'''
        if len(self.api_info) > 0:
            self.root.ids.api_key.text = f'{api_info[0][1]}'
            self.root.ids.api_secret.text = f'{api_info[0][2]}'
            self.root.ids.api_url.text = f'{api_info[0][3]}'
            self.root.ids.url_port.text = f'{api_info[0][4]}'

    def add_rule_clicked(self, rule_description, rule_uuid):
        ''' When the add button is clicked on the add rule screen, it will insert text field string into SQLite table.
            Then clear the rule list widgets, clear the text fields, rebuild the rule list and finally switch back to the
            main screen.
            '''
        des = rule_description.rstrip()
        rule = rule_uuid.strip()
        if len(rule_description) > 0 and len(rule_uuid) > 0:
            try:
                db.execute(f'''INSERT OR REPLACE INTO rules(
                                rname, uuid) VALUES
                                ('{des}', '{rule}')''')

            finally:
                mydb.commit()
                close_button = MDFlatButton(
                    text='Close', on_release=self.close_dialog)
                self.dialog = MDDialog(title='Rules', text='Rules have been added.',
                                       size_hint=(0.7, 1),
                                       buttons=[close_button])
                self.dialog.open()
                self.root.ids.ruleList.clear_widgets()
                self.root.ids.rule_description.text = ''
                self.root.ids.rule_uuid.text = ''
                self.rule_list()
                self.root.ids.ruleList_delete.clear_widgets()
                self.delete_rule_list()
                self.call_main_screen()
        else:
            self.message_output('Error', 'Missing input.')

    def add_api_info(self, api_key, api_secret, api_url, url_port):
        '''Inserts API Key, API Secret, API URL, URL Port to table '''
        key = api_key.strip()
        secret = api_secret.strip()
        url = api_url.strip()
        port = url_port.strip()
        if len(self.api_info) == 0:
            if len(key) > 0 and len(secret) > 0 and len(url) > 0 and len(port) > 0:
                try:
                    db.execute(f'''INSERT INTO api_info(
                                    api_key, api_secret, url, port) VALUES
                                    ('{key}', '{secret}', '{url}', '{port}')''')
                finally:
                    mydb.commit()
                    self.message_output('Info', 'API info has been saved.')
        elif len(self.api_info) == 1:

            if len(key) > 0 and len(secret) > 0 and len(url) > 0 and len(port) > 0:
                try:
                    db.execute(f'''UPDATE api_info SET api_key = '{key}',
                    api_secret = '{secret}', url = '{url}', port = '{port}' WHERE id = 1; ''')

                finally:
                    mydb.commit()
                    self.message_output('Info', 'API info has been saved.')

        else:
            self.message_output('Error', 'Missing input.')

    def rule_list(self):
        '''Query of all rules and generates a list view under the rule tab....not really working all the way yet'''
        self.rule_query()
        for r in self.rows:
            self.rule = f'{self.url}:{self.port}/api/firewall/filter/getRule/{r[2]}'
            rules = TwoLineIconListItem(
                text=r[1],
                secondary_text=r[2],
                on_release=lambda x: threading.Thread(
                    target=self.rule_on_click, args=(x.secondary_text, x), daemon=True).start()
            )
            self.url_request_get(self.rule)
            if self.check.status_code == 200:
                check_rule = json.loads(self.check.text)
                if not 'rule' in check_rule or len(check_rule['rule']['enabled']) == 0:
                    rules.add_widget(IconLeftWidget(
                        icon='checkbox-blank-circle-outline'
                    ))
                elif check_rule['rule']['enabled'] == '1':
                    rules.add_widget(IconLeftWidget(
                        icon='checkbox-marked-circle-outline'
                    ))
                else:
                    rules.add_widget(IconLeftWidget(
                        icon='checkbox-blank-circle-outline'
                    ))
            self.root.ids.ruleList.add_widget(rules)

    def delete_rule_list(self):
        '''Query of all rules and generates a list view under the rule tab....not really working all the way yet'''
        self.rule_query()
        for r in self.rows:
            rules = TwoLineListItem(
                text=r[1],
                secondary_text=r[2],
                on_release=lambda x: threading.Thread(
                    target=self.delete_rule_clicked, args=(x.text,), daemon=True).start()
            )
            self.root.ids.ruleList_delete.add_widget(rules)

    def delete_rule_clicked(self, description):
        '''Confirms user intends to delete rule from local database.'''
        self.dialog = MDDialog(
            text="Delete Rule?",
            buttons=[
                MDFlatButton(
                    text="CANCEL", text_color=self.theme_cls.primary_color,
                    on_release=self.close_dialog
                ),
                MDFlatButton(
                    text="DELETE", text_color=self.theme_cls.primary_color,
                    on_release=lambda x: self.delete_rule(description,)
                ),
            ],
        )
        self.dialog.open()

    def delete_rule(self, description):

        sql = """DELETE FROM rules WHERE rname = ?"""
        db.execute(sql, (description,))
        mydb.commit()
        close_button = MDFlatButton(
            text='Close', on_release=self.close_dialog)
        self.dialog = MDDialog(title='Delete', text='Rule has been deleted.',
                               size_hint=(0.7, 1),
                               buttons=[close_button])
        self.dialog.open()
        self.root.ids.ruleList.clear_widgets()
        self.rule_list()
        self.call_main_screen()

    def rule_on_click(self, uuid, x):
        ''' When a rule is clicked these functions will check rule status, enable or disable the rule,
            and update the rule icon'''
        self.rule_check(uuid, x)

    def rule_check(self, uuid, x):
        '''Should check to see if a rule from the list is enabled or not. It grabs the uuid from the list view click
            and stuffs it into the rule string'''
        toggle = f'{self.url}:{self.port}/api/firewall/filter/toggleRule/{uuid}'
        self.rule = f'{self.url}:{self.port}/api/firewall/filter/getRule/{uuid}'
        self.url_request_get(self.rule)
        if self.check.status_code == 200:
            check_rule = json.loads(self.check.text)
            if check_rule['rule']['enabled'] == '1':
                new_icon = 'checkbox-blank-circle-outline'
                message = 'Rule has been disabled.'
                self.rule_state_change(f'{toggle}/0', new_icon, x, message)
            else:
                new_icon = 'checkbox-marked-circle-outline'
                message = 'Rule has been enabled.'
                self.rule_state_change(f'{toggle}/1', new_icon, x, message)

    def rule_state_change(self, r_url, new_icon, x, message):
        '''Either enables or disables the selected rules based on current status of the rule in the firewall.
            Then calls status message function to inform the user what happens'''
        self.r_url = r_url
        r = self.url_request_post(r_url)
        if r.status_code == 200:
            r = self.url_request_post(self.apply)
            x.children[0].children[0].icon = new_icon
            self.message_output('Complete', message)
        else:
            self.message_output('Error', 'An error has occured.')

    def message_output(self, title, message):
        '''Creates a popup message to the user when required'''
        close_button = MDFlatButton(
            text='Close', on_release=self.close_dialog)
        self.dialog = MDDialog(title=f'{title}', text=f'{message}',
                               size_hint=(0.7, 1),
                               buttons=[close_button])
        self.dialog.open()

    def check_wg1(self):
        '''Checks current status of WG '''
        check = self.url_request_get(self.check_wg)
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
        '''Will either enable or disable wireguard VPN depending on current status provided by on_wg_active'''
        r = self.url_request_post(self.Start_wg)
        if r.status_code == 200:
            r = self.url_request_post(self.save_wg)
            self.message_output('Complete', 'VPN On!')
        else:
            self.message_output('Error', 'An error has occured.')

    def reboot(self):
        '''Sends Reboot API call to firewall'''
        r = self.url_request_post(self.reboot_OPN)
        if r.status_code == 200:
            self.message_output('Reboot', "Rebooting please wait.")
        else:
            self.message_output('Error', 'An error has occured.')

    def close_dialog(self, obj):
        '''Closes dialog boxes'''
        self.dialog.dismiss()


if __name__ == '__main__':
    ma = MainApp()
    ma.run()
