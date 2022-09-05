OPNsense firewall manager used to manage rules created with the firewall automation plugin and intended to run on android phones. This app is given to clients who aren't very technical and need something more simplistic than the web interface provided by OPNsense, so it is intentionally light in its capabilities. It provides the clients the ability to conduct immediate actions then raise a ticket to me to go in and make configuration changes as needed.


<br>**NOTE:** All rules you would like to control with this app need to be recreated using the firewall automation plugin https://docs.opnsense.org/development/api/plugins/firewall.html
<br>

## Current capabilities
- Stores API info in SQLite database.
    - Allows the user to manually paste keys, secret, URL/IP, and port number. (all Required to function)
- Firewall rule enable/disable <br>
    - Checks the current status of each rule on load.
    - Form to add rule uuids generted by firewall automation plugin
    - stores rule list locally in SQLite table.
    - Delete rule from SQLite table.
- Generates a device list based on the ARP table.
    - IP
    - Hostname
    - Reload arp table
    - Flush arp table 
- Wireguard management.
    - Displays connection information.
    - Enable/Disable toggle switch
- Reboot firewall
- Alias Management.
    - Displays list of aliases
    - Allows the addition of IP addresses. 
    - Deletion of IP addresses for an alias

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
<img src="screenshots/f96ca555-35e2-4589-8e20-66746cbad041.png" width="30%">  <img src="screenshots/5082df12-52cb-42a6-87e0-c316b80d4509.png" width="30%"></img>  <img src="screenshots/1eb1f475-a0fd-449a-a251-fefe79b6507a.png" width="30%">  </img><img src="screenshots/3c1541e8-8be2-4a41-9ec9-11a5fef8603b.png" width="30%"></img>  <img src="screenshots/d75625a6-4625-43f6-9ba7-3436e1520a20.png" width="30%"></img>  <img src="screenshots/e3f6d1e8-f37b-4a73-84f7-ada7999a956b.png" width="30%"></img>  <img src="screenshots/97824f57-5472-491f-b8af-04058a1b4841.png" width="30%"></img>  <img src="screenshots/ba3cdc0a-23cb-461b-a1e9-1d168558fc10.png" width="30%"></img>  <img src="screenshots/ba2b7fb6-e2f3-401b-bf01-04a8fcd217a6.png" width="30%"></img> <img src="screenshots/e1754c53-a33c-4cc4-875a-646fdaae7da1.png" width="30%"></img> <img src="screenshots/95db32f0-0832-4bd2-8e7e-3fd878048ba4.png" width="30%"></img>  <img src="screenshots/9bd409d3-70cb-4e3f-8051-5ad389c7b013.png" width="30%"></img>
