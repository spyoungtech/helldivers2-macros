import os
import pathlib
import sys
import tomllib
from typing import Any
from typing import Literal
from typing import TypeGuard

import pydantic

from hd2_macros.constants import STRATAGEMS
from hd2_macros.constants import T_Stratagems

_valid_log_levels = ('DEBUG', 'INFO', 'WARNING', 'ERROR')

if getattr(sys, 'frozen', False):
    _DEFAULT_CONFIG_FILE = pathlib.Path(sys.executable).parent / '_internal' / 'config.toml'
else:
    _DEFAULT_CONFIG_FILE = pathlib.Path(__file__).parent / 'config.toml'



class Loadout(pydantic.BaseModel):
    switch_hotkey: str = pydantic.Field(..., description='The hotkey to use to switch to this loadout')
    hotkeys: dict[T_Stratagems, str] = pydantic.Field(..., description='Mapping of stratagems to hotkeys')


class GeneralSection(pydantic.BaseModel):
    log_level: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR'] = 'INFO'
    no_tray_icon: bool = False
    win_wait: int = 120
    hotkey_start_delay: int | float = 1.0
    exit_hotkey: str = '#q'


class MacroConfig(pydantic.BaseModel):
    general: GeneralSection = pydantic.Field(..., description='General settings')
    loadouts_: dict[str, Loadout] = pydantic.Field(default_factory=dict, alias='loadouts')
    default_loadout: Loadout = pydantic.Field(..., description='The loadout that is used by default at startup')

    @property
    def loadouts(self) -> dict[str, Loadout]:
        return {'default': self.default_loadout} | self.loadouts_


def _check_valid_log_level(log_level: Any) -> TypeGuard[Literal['DEBUG', 'INFO', 'WARNING', 'ERROR']]:
    return log_level in _valid_log_levels


def _check_valid_hotkeys(hotkeys: Any) -> TypeGuard[dict[str, T_Stratagems | Literal['EXIT']]]:
    if not isinstance(hotkeys, dict):
        return False
    for key, value in hotkeys.items():
        if key not in STRATAGEMS and key != 'EXIT':
            return False
        if not isinstance(value, str):
            return False
    return True


def read_config(config_file: str) -> MacroConfig:
    with open(config_file, 'rb') as f:
        config_data = tomllib.load(f)

    return MacroConfig.parse_obj(config_data)


def find_config_file() -> str:
    # TODO: implement better ways to find config file
    if os.path.exists('config.toml'):
        return os.path.abspath('config.toml')
    else:
        return str(_DEFAULT_CONFIG_FILE.absolute())
