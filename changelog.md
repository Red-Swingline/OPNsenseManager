# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
