# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

<<<<<<< HEAD
## [1.0.0] - 2021-5-13
### Changed 
- New layout
- New logo, remove the opnsense logo in case someone gets mad.


=======
>>>>>>> main
## [0.0.5] - 2021-5-12
### Removed
- Removed config Yaml file, this is no longer needed.

### Changed
- Moved table creation from on start to main app, because API info is stored in SQLite table it the query to get the API info on load would cause the table to not get created on first run of app.
- silenced urllib3 warnings about insecure connection
- changes API info variables to use query results from api_info table.

### Added
- Added a table called api_info 
- Added a function to set api info to text fields on the add api info admin screen
- Added check to on start to for api_info table to see if info is already stored.
- Added check to on start to see if can connect to Firewall 
- Added error message to on start for connection issues.
 

## [0.0.4] - 2021-5-8
### Removed
- Removed Email prameters from config.yaml

### Changed
- Added check_wg1() to on_start()

## [0.0.3] - 2021-04-30
### Removed
- Email admin button from admin tab
- Email admin function from main.py

## [0.0.2] - 2021-04-28
### Changed
- Changed rule_on_click to only update the list item icon instead of removing the list and regenerating.
- Buildozer.spec updated to account for bug in KivyMD and python 3.9
- Added sdl2_ttf==2.0.15 to buidlozer.spec file for a kivyMD error for icons not rendering correctly on android.
- Floatlayout on delete rules screen, so the back button can float correctly above the list.
- Centered text fields on add rules screen.

### Removed
- Clear widgets from rule_on_click, this was used to clear the widget list, before I understood how to change the widgets children. No longer needed.
- rule_list from rule_on_click, this was used to generate a new list object with the new icon values by checking the firewall for each rule status. rule_list is only needed on first load and when adding or deleting rules.
 
## [0.0.1] - 2021-04-27
### Added
- CHANGELOG file to better track changes.
- Error checking on user input on add rule screen.
- Added function for back arrow button on add rule screen. Button will clear text fields and change to main screen.

### Changed
- Refactored URL requests in all functions.
- Refactored rule_list function to not crash when rules that don't exist on the firewall are passed to the firewall API from this app.

### Removed
- Removed rule_lookup function.
