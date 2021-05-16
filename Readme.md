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
- [ ] Add String validation for inputs.
- [ ] Speed up rule list generation on load.
- [ ] Add ability to add IP to firewall alias.