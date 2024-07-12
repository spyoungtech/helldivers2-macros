# Helldivers2 Stratagem Macro

This is software for macroing stratagem inputs in Helldivers2.

Windows only.

Please note: This project makes no efforts to hide itself, evade detection, or circumvent any anti-cheat measures.
If you use this software in Helldivers 2, there is no guarantee of any kind that you will not be banned. **Use at your own risk.**

# Installation

Prerequisite: this requires that you have [autohotkey](https://www.autohotkey.com/) installed in a default location. Python users may use `pip install ahk[binary]` to satisfy this requirement.

## Binary downloads

Check the [releases page](https://github.com/spyoungtech/helldivers2-macros/releases) for traditional
windows setup install or zip download. This is the preferred method for end-users who are not Python developers.


## With pip

For Python developers, you can also install using `pip`

```
pip install hd2_macros
```

In this method, you will need to launch using `python -m hd2_macros` and the `config.toml` is expected to be in the
present working directory.

# Usage

The short version is:

1. Configure your hotkeys using the `config.toml` file
2. Run the program with helldivers2
3. When you trigger one of your configured hotkeys, a short delay (`hotkey_start_delay`) will occur -- enough time for you to make sure you have your stratagem menu up -- and the program will enter the WASD inputs for the associated stratagem.


## Configuration
In the installation directory (or the current working directory for `pip` install users) use the `config.toml` file
to configure your hotkey loadouts.

```toml
# General settings apply for all loadouts
[general]
# How long to wait for the helldivers window before exiting
win_wait = 120

# Delay in seconds between when the hotkey pressed and beginning of WASD inputs
# Intended to allow you enough time to ensure the strategem menu is up and ready for input
hotkey_start_delay = 1.0
# Change logging verbosity (valid values are "DEBUG", "INFO", "WARNING", "ERROR")
log_level = "DEBUG"

# Hide the system tray icon for the application
no_tray_icon = false

# Define a hotkey that can be used to stop the program
# By default, bound to Windows key + Q
exit_hotkey = "#q"

# The time in between key UP/DOWN events when inputting macros.
# Lowering this value will make inputs faster, but may cause inputs to be dropped.
key_delay = 0.1

# If you have AutoHotkey in a non-default location, you may specify it by uncommenting this line:
# autohotkey_executable_path = "C:\Path\To\AutoHotkey64.exe"

# You can explicitly specify the version of AutoHotkey. Usually, this is not necessary.
# autohotkey_version = ""



# A Loadout provides a mapping of Strategems to hotkeys. Each loadout specifies a hotkey used to switch to that loadout.
# For hotkey/modifiers syntax, see https://www.autohotkey.com/docs/v2/Hotkeys.htm and https://www.autohotkey.com/docs/v2/KeyList.htm

# The default loadout is the loadout used at program starts
[ default_loadout ]
switch_hotkey = "#1"  # press Win+1 to load this loadout
[ default_loadout.hotkeys ]
# Maps the orbital precision strike strategem to "Windows key + n"
# All stratagem names are lowercase
"orbital precision strike" = "#n"

# Add separate sets of loadouts using `[ loadouts.<NAME> ]`
[ loadouts.secondary ]
switch_hotkey = "#2" # press Win+2 to load this loadout
[ loadouts.secondary.hotkeys ]
"orbital precision strike" = "#b"
"mortar sentry" = "#s"
"eagle cluster bomb" = "#c"

# You can add as many loadouts as you want.
# ...
```

# Stratagem list

- `heavy machine gun`
- `quasar cannon`
- `resupply`
- `orbital illumination flare`
- `hellbomb`
- `reinforce`
- `machine gun`
- `anti-material rifle`
- `stalwart`
- `expendable anti-tank`
- `recoilless rifle`
- `flamethrower`
- `autocannon`
- `railgun`
- `spear`
- `eagle strafing run`
- `eagle airstrike`
- `eagle cluster bomb`
- `eagle napalm airstrike`
- `jump pack`
- `eagle smoke strike`
- `eagle 110mm rocket pods`
- `eagle 500kg bomb`
- `orbital gatling barrage`
- `orbital airburst strike`
- `orbital 120mm he barrage`
- `orbital walking barrage`
- `orbital 380mm he barrage`
- `orbital lasers`
- `orbital railcannon strike`
- `orbital precision strike`
- `orbital gas strike`
- `orbital ems strike`
- `orbital smoke strike`
- `hmg emplacement`
- `shield generation relay`
- `tesla tower`
- `machine gun sentry`
- `gatling sentry`
- `mortar sentry`
- `guard dog`
- `autocannon sentry`
- `rocket sentry`
- `ems mortar sentry`
- `anti-personnel minefield`
- `supply pack`
- `grenade launcher`
- `laser cannon`
- `incendiary mines`
- `guard dog rover`
- `ballistic shield backpack`
- `arc thrower`
- `shield generator pack`
- `patriot exosuit`
- `emancipator exosuit`
- `commando`

See also: [constants.py](https://github.com/spyoungtech/helldivers2-macros/blob/main/hd2_macros/constants.py) for input mappings.
