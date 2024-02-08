# Changelog

All notable changes to this project will be documented in this file.<br>
(**Note:** The format is mostly based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/))

**Format:** `[x.y.z] - mm/dd/yyyy`
<hr>

## [0.5.1] - 02/08/2024
### Added
- Added voice commands, customized in settings
- Added more logs events
- Added app icons (on the title bar and task bar)
- Added option to clear the recorded events of the mouse recorder
### Changed
- Changed the format of the elapsed time label in the Credits & Info page
- Changed the logs formatting when started clicking
- Optimized the code
### Fixed
- Fixed some minor bugs
- Fixed minor formatting mistakes in the log files

## [0.3.1] - 01/21/2024
### Added
- Added 2 default extensions (MouseRecorder, CPS-Counter)
- Added 2 more statistics related to scrolling
- Added a terminal/console
- Added advanced settings category in settings
- Added an OS filter
- Added click-on image detection feature
- Added extensions and plugins
- Added more hotkeys
- Added random intervals feature
- Added random mouse position feature
- Added scrolling type
- Added the click area feature
### Changed
- A messagebox will be displayed when the user resets all data
- Changed the default trigger hotkey to `Ctrl`+`Q`
- Changed the indents of `data.json` from 2 to 4
- Improved the background tasks system
- Optimized & Revamped many features
- Saving all the settings takes approx. 1sec before closing
- The interval must be longer than 0s in all cases
- The user can now refresh the GUI
### Removed
- Removed some unnecessary information in `data.json`
### Fixed
- Fixed a bug when the app can't be closed properly
- Fixed a bug when the user can break the app by triggering the mouse while a widget is not focused
- Fixed a bug when the user can break the GUI by auto triple-clicking on the start button with 1s interval

## [0.0.2] - 11/26/2023
### Added
- Added 1 hotkey
- Added a folder for assets
### Changed
- Changed the author position at the **Credits & Information** window
- Changed the icon of some messageboxes
- Hold `shift` while closing the application will make it run in the background
- Pressing `Ctrl` while closing a window bypassed the extra message
- The fixed position of the mouse must be inside the main single-screen
### Fixed
- Fixed the formatting of `logs.txt` and its children's log files

## [0.0.1] - 11/26/2023
### Added
- Initial commit

<hr>

## ToDo List
- Specific window clicking
