from kivymd.app import MDApp
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.button import (
    MDFlatButton,
    MDFloatingActionButton,
    MDFillRoundFlatButton,
)
from kivymd.uix.dialog import MDDialog
from kivymd.uix.behaviors import RoundedRectangularElevationBehavior
from kivymd.uix.card import MDCard
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.uix.list import (
    TwoLineIconListItem,
    IconLeftWidget,
    TwoLineListItem,
    OneLineAvatarIconListItem,
    OneLineListItem,
)
from kivy.clock import Clock
from db import *
import bcrypt
import re
import ssl
import requests
import json
import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class MD3Card(MDCard, RoundedRectangularElevationBehavior):
    """Implements a material design v3 card."""


class MainApp(MDApp):
    create_tables()
    db.execute("""SELECT * from api_info""")
    api_info = db.fetchall()
    if len(api_info) > 0:
        url = api_info[0][3]
        port = api_info[0][4]
        key = api_info[0][1]
        secret = api_info[0][2]
    else:
        url = ""
        port = ""
        key = ""
        secret = ""

    reboot_opn = f"{url}:{port}/api/core/system/reboot/"
    apply = f"{url}:{port}/api/firewall/filter/apply"
    check_wg = f"{url}:{port}/api/wireguard/general/get"
    start_wg = f"{url}:{port}/api/wireguard/general/set"
    save_wg = f"{url}:{port}/api/wireguard/service/reconfigure"
    wg_status = f"{url}:{port}/api/wireguard/service/showconf"
    url_check = f"{url}:{port}/api/core/menu/search"
    list_aliases = f"{url}:{port}/api/firewall/alias/searchItem"
    alias_reconfigure = f"{url}:{port}/api/firewall/alias/reconfigure"
    get_arp_table = f"{url}:{port}/api/diagnostics/interface/getArp"
    flush_arp_table = f"{url}:{port}/api/diagnostics/interface/flushArp"
    arp_refersh = {
        "Reload list": "reload",
        "Flush ARP": "delete",
    }

    def on_start(self):
        """Runs all on start functions, database creation and queries, rule status checks whatever else needs to
        happen on start"""

        api_info = self.get_api_info()
        if len(api_info) > 0:
            if api_info[0][5] != '':
                self.root.ids.screen_manager.current = "login"
            else:
                self.after_login_checks(api_info)
        else:
            self.root.ids.screen_manager.current = "settings"
            self.message_output("Info", "Enter API info")

    def login_check(self):
        api_info = self.get_api_info()
        hashed = api_info[0][5].encode()
        password = self.root.ids.login_txt.text.strip()
        password = password.encode()
        if bcrypt.checkpw(password, hashed):
            self.after_login_checks(api_info)
            self.root.ids.login_menu_btn.disabled = False
            self.root.ids.login_menu_btn.opacity = 1
        else:
            self.message_output("Error", "Check password")

    def after_login_checks(self, api_info):
        self.set_api_info_text(api_info)
        try:
            check = requests.post(
                url=self.url_check, auth=(
                    self.key, self.secret), verify=False
            )
            if check.status_code == 200:
                self.rule_list()
                self.delete_rule_list()
                self.check_wg1()
                self.function_interval = Clock.schedule_interval(
                    self.wg_connection_status, 2
                )
                self.alias_selection()
                self.arp_table_list()
                self.root.ids.login_txt.text = ''
                self.root.ids.screen_manager.current = "rules"
        except requests.exceptions.ConnectionError:
            self.connection_error()
            pass
        except requests.exceptions.Timeout:
            self.connection_timeout()
            pass
        except requests.exceptions.InvalidSchema:
            self.invalid_url()
            pass

    def logout(self):
        self.root.ids.ruleList.clear_widgets()
        self.root.ids.ruleList_delete.clear_widgets()
        self.root.ids.devicelist.clear_widgets()
        self.root.ids.aliasList.clear_widgets()
        self.root.ids.api_key.text = ''
        self.root.ids.api_secret.text = ''
        self.root.ids.api_url.text = ''
        self.root.ids.url_port.text = ''
        self.root.ids.password_txt.text = ''

    def build(self):
        """Sets app theme color and loads the builder kv file"""
        self.theme_cls.primary_palette = "Amber"


    def rule_query(self):
        """Queries the SQLite table to get stored list of rules to be managed from the app."""
        db.execute("""SELECT * from rules""")
        self.rows = db.fetchall()
        return self.rows

    def url_request_get(self, url):
        """Handles all get request for checking status with firewall API"""
        check = requests.get(
            url=url, timeout=5, auth=(self.key, self.secret), verify=False
        )
        return check

    def url_request_post(self, url):
        """Handles all post request for checking status with firewall API."""
        check = requests.post(
            url=url, timeout=10, auth=(self.key, self.secret), verify=False
        )
        return check

    def call_main_screen(self):
        """Switches to the main screen of the app."""
        self.root.ids.screen_manager.current = "rules"

    def previous_screen(self):
        """Handles actions for toolbar right arrow actions, currently returns to Rules screen"""
        screen = self.root.ids.screen_manager.current
        self.root.ids.screen_manager.direction = "left"
        if screen == "rules":
            self.root.ids.rule_description.text = ""
            self.root.ids.rule_uuid.text = ""
            self.root.ids.screen_manager.current = "settings"
        elif screen == "alias_details":
            self.root.ids.screen_manager.current = "alias"
            self.root.ids.details.remove_widget(
                self.root.ids.details.children[0])
        else:
            self.root.ids.screen_manager.current = "rules"

    def set_api_info_text(self, api_info):
        """Set API info in text fields on the API info page"""
        api_info = self.get_api_info()
        if len(api_info) > 0:
            self.root.ids.api_key.text = f"{api_info[0][1]}"
            self.root.ids.api_secret.text = f"{api_info[0][2]}"
            self.root.ids.api_url.text = f"{api_info[0][3]}"
            self.root.ids.url_port.text = f"{api_info[0][4]}"
            if api_info[0][5] != "":
                self.root.ids.password_txt.text = "Password set"

    def arp_callbacks(self, instance):
        """Callback handler for action button on device list"""
        if instance.icon == 'reload':
            instance.parent.close_stack()
            self.reload_device()
        else:
            instance.parent.close_stack()
            self.url_request_post(self.flush_arp_table)
            self.reload_device()

    def reload_device(self):
        """Reloads ARP device list"""
        self.root.ids.devicelist.clear_widgets()
        self.arp_table_list()

    def add_rule_clicked(self, rule_description, rule_uuid):
        """When the add button is clicked on the add rule screen, it will insert a text field string into the SQLite table.
        Then clear the rule list widgets, clear the text fields, rebuild the rule list and finally switch back to the
        main screen.
        """
        des = rule_description.rstrip()
        rule = rule_uuid.strip()
        if len(rule_description) > 0 and len(rule_uuid) > 0:
            try:
                db.execute(
                    f"""INSERT OR REPLACE INTO rules(
                                rname, uuid) VALUES
                                ('{des}', '{rule}')"""
                )

            finally:
                mydb.commit()
                self.message_output("Rules", "Rules have been added.")
                self.dialog.open()
                self.root.ids.ruleList.clear_widgets()
                self.root.ids.rule_description.text = ""
                self.root.ids.rule_uuid.text = ""
                self.rule_list()
                self.root.ids.ruleList_delete.clear_widgets()
                self.delete_rule_list()
                self.call_main_screen()
        else:
            self.message_output("Error", "Missing input.")

    def add_api_info(self, api_key, api_secret, api_url, url_port):
        """Inserts API Key, API Secret, API URL, URL Port to table"""
        key = api_key.strip()
        secret = api_secret.strip()
        url = api_url.strip()
        port = url_port.strip()
        api_info = self.get_api_info()
        password = self.root.ids.password_txt.text.strip()
        password = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password, salt)
        if password != '':
            stored_hash = hashed.decode()
        else:
            stored_hash = NULL
        if len(api_info) == 0:
            if len(key) > 0 and len(secret) > 0 and len(url) > 0 and len(port) > 0:
                try:
                    db.execute(
                        f"""INSERT INTO api_info(
                                    api_key, api_secret, url, port, password) VALUES
                                    ('{key}', '{secret}', '{url}', '{port}', '{stored_hash}')"""
                    )
                finally:
                    mydb.commit()
                    self.message_output("Info", "API info has been saved.")
            else:
                self.message_output("Error", "Missing Input.")

        elif len(api_info) == 1:

            if len(key) > 0 and len(secret) > 0 and len(url) > 0 and len(port) > 0:
                if self.root.ids.password_txt.text == "Password set":
                    db.execute(
                        f"""UPDATE api_info SET api_key = '{key}',
                    api_secret = '{secret}', url = '{url}', port = '{port}' WHERE id = 1; """
                    )
                elif self.root.ids.password_txt.text == '':
                    db.execute(
                        f"""UPDATE api_info SET api_key = '{key}',
                    api_secret = '{secret}', url = '{url}', port = '{port}', password = '' WHERE id = 1; """
                    )
                    self.root.ids.login_menu_btn.disabled = True
                    self.root.ids.login_menu_btn.opacity = 0
                else:
                    db.execute(
                        f"""UPDATE api_info SET api_key = '{key}',
                    api_secret = '{secret}', url = '{url}', port = '{port}', password = '{stored_hash}'WHERE id = 1; """
                    )
                    self.root.ids.login_menu_btn.disabled = False
                    self.root.ids.login_menu_btn.opacity = 1
                mydb.commit()
                self.message_output("Info", "API info has been saved.")
            else:
                self.message_output("Error", "Missing Input.")

        else:
            self.message_output("Error", "Missing input.")

    def alias_selection(self):
        """Request alias list from firewall and generates a list of aliases loads details screen when clicked."""
        a = f"{self.url}:{self.port}/api/firewall/alias/listNetworkAliases"
        check = self.url_request_post(a)
        check = json.loads(check.text)
        for k, v in check.items():
            name = v['name'].split("__")
            description = v['description']
            if description == "":
                description = "No description assigned."
            if len(name) == 1:
                alias_item = TwoLineListItem(
                    text=f"Alias Name:      {v['name']}",
                    secondary_text=f"Description:      {description}",
                    on_release=lambda x: self.alias_details(x.text)
                )
                self.root.ids.aliasList.add_widget(alias_item)

    def alias_details(self, a):
        """Displays alias details screen, Name, and IP information. It also includes a text field for adding IP addresses."""
        self.root.ids.alias_ip_list.clear_widgets()
        a = a.split(":")
        a = a[1].strip()
        check = self.url_request_get(self.list_aliases)
        if check.status_code == 200:
            alias_list = check.json()
            for alias in alias_list["rows"]:
                if alias["name"] == a:
                    a_name = str(alias["name"])
                    a_ip = str(alias["content"])
                    a_ip = a_ip.split(",")
                    l_ip = str(alias["content"])
                    a_uuid = str(alias["uuid"])
                    self.root.ids.alias_details_name.text = f"Alias:  {a_name}"
                    self.root.ids.alias_uuid.text = a_uuid
                    self.alias_ip_list(a_ip)
                    add_button = MDFillRoundFlatButton(
                        text="Add IP",
                        pos_hint={"center_x": 0.8, "center_y": 0.3},
                        on_release=lambda x: self.add_ip_to_alias(
                            a_uuid, l_ip),
                    )
                    self.root.ids.details.add_widget(add_button)
                self.root.ids.screen_manager.current = "alias_details"

    def alias_ip_list(self, a_ip):
        for i in a_ip:
            ip_list = OneLineListItem(
                text=i,
                on_release=lambda x: self.delete_alias_clicked(x)
            )
            self.root.ids.alias_ip_list.add_widget(ip_list)

    def add_ip_to_alias(self, uuid, a_ip):
        """Builds the JSON payload required to post to add IP to the alias. Also sends post request, and returns
        then send a post request to reconfigure alias. Only one IP input is supported at the moment.
        """
        new_ip = self.root.ids.ip_address.text.strip()
        new_ip = new_ip.split(",")
        alias_ip = re.sub("[,]", "\n", a_ip)
        for n in new_ip:
            alias_ip = f"{alias_ip}\n{n}"
        set_url = f"{self.url}:{self.port}/api/firewall/alias/setItem/{uuid}"
        check = self.url_request_get(
            f"{self.url}:{self.port}/api/firewall/alias/getItem/{uuid}"
        )
        slected_alias = check.json()
        alias_name = f'{str(slected_alias["alias"]["name"])}'
        payload = {
            "alias": {
                "name": f"{alias_name}",
                "content": f"{alias_ip}",
            }
        }
        try:
            a = requests.post(
                url=set_url,
                timeout=10,
                auth=(self.key, self.secret),
                verify=False,
                json=payload,
            )
            if a.status_code == 200:
                self.root.ids.ip_address.text = ""
                self.message_output(
                    "Added", f"IP has been added to {alias_name}")
                self.root.ids.screen_manager.current = "alias"
        except Exception as e:
            self.connection_error()

    def delete_alias_clicked(self, ip):
        """Ask user if they want to delete an IP address from alias."""
        self.dialog = MDDialog(
            text=f"Delete {ip.text} from alias?",
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    text_color=self.theme_cls.primary_color,
                    on_release=self.close_dialog,
                ),
                MDFlatButton(
                    text="DELETE",
                    text_color=self.theme_cls.primary_color,
                    on_release=lambda x: self.delete_alias_ip(
                        self.dialog,
                        ip,
                    ),
                ),
            ],
        )
        self.dialog.open()

    def delete_alias_ip(self, dialog, x):
        """
        Delete an IP from an alias.
        """
        dialog.dismiss()
        ip_list = x.parent.children
        new_list = []
        uuid = self.root.ids.alias_uuid.text
        a_name = self.root.ids.alias_details_name.text
        set_url = f"{self.url}:{self.port}/api/firewall/alias/setItem/{uuid}"
        for ip in ip_list:
            if ip.text != x.text:
                new_list.append(ip.text)
            a_ip = new_list[0:]
            a_ip = "\n".join(a_ip)
        payload = {
            "alias": {
                "name": f"{a_name}",
                "content": f"{a_ip}",
            }
        }
        a = requests.post(
            url=set_url,
            timeout=10,
            auth=(self.key, self.secret),
            verify=False,
            json=payload,
        )
        if a.status_code == 200:
            self.root.ids.ip_address.text = ""
            self.message_output(
                "Added", f"{x.text} has been removed from alias: {a_name}")
        self.root.ids.alias_ip_list.clear_widgets()
        self.alias_ip_list(new_list)

    def arp_table_list(self):
        """API get request for the ARP table on the firewall. Then generates a scrollview list of device IPs, Hostname, and"""
        arp_table = self.url_request_get(self.get_arp_table)
        arp_list = json.loads(arp_table.text)
        for d in arp_list:
            arp = TwoLineListItem(
                text="IP address: " + d["ip"],
                secondary_text="HostName: " + d["hostname"],
            )
            self.root.ids.devicelist.add_widget(arp)

    def rule_list(self):
        """Query of all rules and generates a list view under the rule tab....not really working all the way yet"""
        self.rule_query()
        for r in self.rows:
            self.rule = f"{self.url}:{self.port}/api/firewall/filter/getRule/{r[2]}"
            rules = TwoLineIconListItem(
                text=r[1],
                secondary_text=r[2],
                on_release=lambda x: self.rule_on_click(
                    x.secondary_text, x),
            )
            try:
                check = self.url_request_get(self.rule)
                if check.status_code == 200:
                    check_rule = json.loads(check.text)
                    if check_rule["rule"]["enabled"] == "0":
                        rules.add_widget(
                            IconLeftWidget(
                                icon="checkbox-blank-circle-outline")
                        )
                    elif check_rule["rule"]["enabled"] == "1":
                        rules.add_widget(
                            IconLeftWidget(
                                icon="checkbox-marked-circle-outline")
                        )
                else:
                    rules.add_widget(
                        IconLeftWidget(icon="checkbox-blank-circle-outline")
                    )
                self.root.ids.ruleList.add_widget(rules)

            except requests.exceptions.ConnectionError:
                self.connection_error()
                rules.add_widget(IconLeftWidget(
                    icon="checkbox-blank-circle-outline"))
                self.root.ids.ruleList.add_widget(rules)
                self.dialog.dismiss()
                pass
            except requests.exceptions.Timeout:
                self.connection_timeout()
                rules.add_widget(IconLeftWidget(
                    icon="checkbox-blank-circle-outline"))
                self.root.ids.ruleList.add_widget(rules)
                self.dialog.dismiss()
                pass
            except requests.exceptions.InvalidSchema:
                self.invalid_url()
                rules.add_widget(IconLeftWidget(
                    icon="checkbox-blank-circle-outline"))
                self.root.ids.ruleList.add_widget(rules)
                self.dialog.dismiss()
                pass

    def delete_rule_list(self):
        """Queries local SQLite table for rules and generates a list in a scroll view on the delete screen in screen
        manager. Allows for user to remove rules from local SQLite database
        """
        self.rule_query()
        for r in self.rows:
            rules = TwoLineListItem(
                text=r[1],
                secondary_text=r[2],
                on_release=lambda x: self.delete_rule_clicked(
                    x.text,),
            )
            self.root.ids.ruleList_delete.add_widget(rules)

    def delete_rule_clicked(self, description):
        """Confirms user intends to delete a rule from a local SQLite database."""
        self.dialog = MDDialog(
            text="Delete Rule?",
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    text_color=self.theme_cls.primary_color,
                    on_release=self.close_dialog,
                ),
                MDFlatButton(
                    text="DELETE",
                    text_color=self.theme_cls.primary_color,
                    on_release=lambda x: self.delete_rule(
                        self.dialog,
                        description,
                    ),
                ),
            ],
        )
        self.dialog.open()

    def delete_rule(self, dialog, description):
        """Closes dialog from delete_rule_clicked() and Deletes selected rule from SQLite database.
        Then regenerates rule list on main screen.
        """
        dialog.dismiss()
        sql = """DELETE FROM rules WHERE rname = ?"""
        db.execute(sql, (description,))
        mydb.commit()
        close_button = MDFlatButton(text="Close", on_release=self.close_dialog)
        self.dialog = MDDialog(
            title="Delete",
            text="Rule has been deleted.",
            size_hint=(0.7, 1),
            buttons=[close_button],
        )
        self.dialog.open()
        self.root.ids.ruleList.clear_widgets()
        self.root.ids.ruleList_delete.clear_widgets()
        self.delete_rule_list()
        self.rule_list()
        self.call_main_screen()

    def rule_on_click(self, uuid, x):
        """When a rule is clicked, these functions will check rule status, enable or disable the rule,
        and update the rule icon"""
        self.rule_check(uuid, x)

    def rule_check(self, uuid, x):
        """Checks to see if the rule is enabled or not. It grabs the UUID from the list view click
        and stuffs it into the rule string"""
        toggle = f"{self.url}:{self.port}/api/firewall/filter/toggleRule/{uuid}"
        self.rule = f"{self.url}:{self.port}/api/firewall/filter/getRule/{uuid}"
        try:
            check = self.url_request_get(self.rule)
            if check.status_code == 200:
                check_rule = json.loads(check.text)
                try:
                    if check_rule["rule"]["enabled"] == "1":
                        new_icon = "checkbox-blank-circle-outline"
                        message = "Rule has been disabled."
                        self.rule_state_change(
                            f"{toggle}/0", new_icon, x, message)
                    else:
                        new_icon = "checkbox-marked-circle-outline"
                        message = "Rule has been enabled."
                        self.rule_state_change(
                            f"{toggle}/1", new_icon, x, message)
                except TypeError:
                    self.message_output("Error", "Rule not found on Firewall")
            if check.status_code == 401:
                self.message_output("Error", "Check API info.")
        except requests.exceptions.ConnectionError:
            self.connection_error()
        except requests.exceptions.Timeout:
            self.connection_timeout()
            pass
        except requests.exceptions.InvalidSchema:
            self.invalid_url()
            pass

    def rule_state_change(self, r_url, new_icon, x, message):
        """Either enables or disables the selected rules based on the current status of the rule in the firewall.
        Then calls status message function to inform the user what happens."""
        self.r_url = r_url
        try:
            r = self.url_request_post(r_url)
            if r.status_code == 200:
                r = self.url_request_post(self.apply)
                x.children[0].children[0].icon = new_icon
                self.message_output("Complete", message)
            else:
                self.message_output("Error", "An error has occured.")
        except requests.exceptions.ConnectionError:
            self.connection_error()
            pass
        except requests.exceptions.Timeout:
            self.connection_timeout()
            pass
        except requests.exceptions.InvalidSchema:
            self.invalid_url()
            pass

    def get_api_info(self):
        db.execute("""SELECT * from api_info""")
        api_info = db.fetchall()
        return api_info

    def connection_error(self):
        """Connection error message"""
        self.message_output("Error", "Connection Error Check API info.")

    def connection_timeout(self):
        self.message_output("Error", "Connection Timeout.")

    def invalid_url(self):
        self.message_output("Error", "Invalid url Please check API Info")

    def message_output(self, title, message):
        """Creates a popup message to the user when required"""
        close_button = MDFlatButton(text="Close", on_release=self.close_dialog)
        self.dialog = MDDialog(
            title=f"{title}",
            text=f"{message}",
            size_hint=(0.7, 1),
            buttons=[close_button],
        )
        self.dialog.open()
        return self.dialog

    def check_wg1(self):
        """Checks current status of WG"""
        try:
            check = self.url_request_get(self.check_wg)
            if check.status_code == 200:
                check_rule = json.loads(check.text)
                if check_rule["general"]["enabled"] == "1":
                    self.root.ids.wg_switch.active = True
        except requests.exceptions.ConnectionError:
            self.message_output("Error", "Connection Error.")
            pass

        except requests.exceptions.Timeout:
            self.connection_timeout()
            pass
        except requests.exceptions.InvalidSchema:
            self.invalid_url()
            pass

    def on_wg_active(self, *args):
        """Sets api URL to Enable or disable wireguard client based on the current state."""
        try:
            check = self.url_request_get(self.check_wg)
            if check.status_code == 200:
                check_rule = json.loads(check.text)
                if check_rule["general"]["enabled"] == "1":
                    data = {"general": {"enabled": "0"}}
                    message = "VPN Off!"
                    self.wg_change_state(data, message)
                else:
                    data = {"general": {"enabled": "1"}}
                    message = "VPN On!"
                    self.wg_change_state(data, message)
        except requests.exceptions.ConnectionError:
            self.connection_error()
        except requests.exceptions.Timeout:
            self.connection_timeout()
            pass
        except requests.exceptions.InvalidSchema:
            self.invalid_url()
            pass

    def wg_connection_status(self, *args):
        """Every 5 seconds when the current screen is set to VPN updates connection information to a text label."""
        data = {}
        if self.root.ids.screen_manager.current == "vpn":
            try:
                s = requests.post(
                    url=self.wg_status,
                    timeout=5,
                    auth=(self.key, self.secret),
                    verify=False,
                    json=data,
                )
                if s.status_code == 200:
                    status = s.json()
                    self.root.ids.wg_connection_status.text = status["response"]
            except requests.exceptions.ConnectionError:
                pass
            except requests.exceptions.Timeout:
                pass
            except requests.exceptions.InvalidSchema:
                pass

    def ip_validator(self, ip):
        """Validates IP addresses are valid."""
        if iptools.ipv4.validate_ip(ip) is True or iptools.ipv6.validate_ip(ip) is True:
            return True
        else:
            return False

    def wg_change_state(self, data, message):
        """Will either enable or disable wireguard VPN depending on current status provided by on_wg_active"""
        try:
            r = requests.post(
                url=self.start_wg,
                timeout=5,
                auth=(self.key, self.secret),
                verify=False,
                json=data,
            )
            if r.status_code == 200:
                s = self.url_request_post(self.save_wg)
                if s.status_code == 200:
                    self.message_output("VPN", message)
            else:
                self.message_output("Error", "An error has occured.")
        except requests.exceptions.ConnectionError:
            self.connection_error()
        except requests.exceptions.Timeout:
            self.connection_timeout()
            pass
        except requests.exceptions.InvalidSchema:
            self.invalid_url()
            pass

    def reboot(self):
        """Sends Reboot API call to firewall"""
        try:
            r = self.url_request_post(self.reboot_opn)
            if r.status_code == 200:
                self.message_output("Reboot", "Rebooting please wait.")
            else:
                self.message_output("Error", "An error has occured.")
        except requests.exceptions.ConnectionError:
            self.connection_error()
        except requests.exceptions.Timeout:
            self.connection_timeout()
            pass
        except requests.exceptions.InvalidSchema:
            self.invalid_url()
            pass

    def close_dialog(self, obj):
        """Closes dialog boxes"""
        self.dialog.dismiss()


if __name__ == "__main__":
    ma = MainApp()
    ma.run()
