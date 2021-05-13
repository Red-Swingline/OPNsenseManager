OPNsense firewall manager used to manage rules created with the firewall automation plugin. Intended to be built for android phones. 

### Usage
- Edit config.yaml file.
- Build with buildozers
    - In accordance with https://github.com/kivy/buildozer
    - For testing enter the below command in terminal.
        - $ buildozer android debug deploy run logcat

### Screenshots
<img src="screenshots/menu.jpg" width="30%"></img<img src="screenshots/rules.jpg" width="30%"></img><img src="screenshots/vpn.jpg" width="30%"></img><img src="screenshots/power.jpg" width="30%"></img><img src="screenshots/api_info.jpg" width="30%"></img><img src="screenshots/add_rule.jpg" width="30%"></img><img src="screenshots/delete.jpg" width="30%"></img><img src="screenshots/splash_screen.jpg" width="30%"></img>

### Todo
- [X] Add ability to delete rules from the main list.
- [x] Add a new Screen to add rules to DB manually.
- [x] Switch from png file for status indication to icons.
- [ ] <strike>Fix Email Admin Button.</strike>
- [ ] Speed up rule list generation on load.
- [X] Update only selected rule icon when enabling/disabling vs. querying rebuilding the whole list
- [ ] Fix dialog box not dismissing after delete rule. (You have to touch behind the rule to dismiss)
- [X] Add a table for an API key, Secret, and Firewall URL/IP