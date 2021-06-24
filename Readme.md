OPNsense firewall manager used to manage rules created with the firewall automation plugin and intended to run on android phones. This app is given to clients who aren't very technical and need something more simplistic than the web interface provided by OPNsense, so it is intentionally light in its capabilities. It provides the clients the ability to conduct immediate actions then raise a ticket to me to go in and make configuration changes as needed.

## Current capabilities
- Stores API info in SQLite database.
    - Allows the user to manually paste keys, secret, URL/IP, and port number. (all Required to function)
- Firewall rule enable/disable
    - Checks the current status of each rule on load.
    - stores rule list locally in SQLite table.
    - Delete rule from SQLite table.
- Generates a device list based on the ARP table.
    - IP
    - Hostname
- Wireguard management.
    - Displays connection information.
    - Enable/Disable toggle switch
- Reboot firewall
- Alias Management.
    - Displays list of aliases
    - Allows the addition of IP addresses. 

### Usage
Download one of the releases or build with buildozer 
- Build with buildozer 
    - In accordance with https://github.com/kivy/buildozer 
    - For testing, enter the below command in the terminal. 
        - Connect the phone to the computer with a USB 
        - $ buildozer android debug deploy run logcat 
    - Or build an APK without pushing to a phone. 
        - $ buildozer android debug



### Screenshots
<img src="screenshots/menu.jpg" width="30%"></img<img src="screenshots/rules.jpg" width="30%"></img><img src="screenshots/vpn.jpg" width="30%"></img><img src="screenshots/power.jpg" width="30%"></img><img src="screenshots/api_info.jpg" width="30%"></img><img src="screenshots/add_rule.jpg" width="30%"></img><img src="screenshots/delete.jpg" width="30%"></img><img src="screenshots/splash_screen.jpg" width="30%"></img><img src="screenshots/alias_list.jpeg" width="30%"></img><img src="screenshots/alias_details.jpeg" width="30%"></img>
