import logging
import time
from typing import Any
from typing import Callable
from typing import Literal
from typing import Type

from ahk import AHK
from ahk import Window
from ahk.directives import Directive
from ahk.directives import NoTrayIcon
from ahk.exceptions import AhkExecutableNotFoundError

from hd2_macros.config import find_config_file
from hd2_macros.config import MacroConfig
from hd2_macros.config import read_config
from hd2_macros.constants import INPUT_MAPPING
from hd2_macros.constants import STRATAGEMS
from hd2_macros.constants import T_Stratagems

logger = logging.getLogger('hd2-macros')
logger.propagate = False

ahk: AHK[Any] | None = None


def _set_ahk_global(config: MacroConfig) -> None:
    global ahk

    executable_path = config.general.autohotkey_executable_path or ''
    version: Literal['v1', 'v2'] | None

    if config.general.autohotkey_version == 'v1':
        version = 'v1'
    elif config.general.autohotkey_version == 'v2':
        version = 'v2'
    elif config.general.autohotkey_version is None:
        version = None
    else:
        raise Exception('Unexpected configuration value for autohotkey_version')
    directives: list[Directive | Type[Directive]] | None
    if config.general.no_tray_icon is True:
        directives = [NoTrayIcon(apply_to_hotkeys_process=True)]
    else:
        directives = None
    try:
        ahk = AHK(executable_path=executable_path, version=version, directives=directives)
    except AhkExecutableNotFoundError:
        if not executable_path and version is None:
            ahk = AHK(version='v2', directives=directives)
        else:
            raise
    return None


def find_helldivers_window() -> Window | None:
    assert ahk is not None
    for window in ahk.list_windows(blocking=False).result():
        try:
            process_path = window.process_path.lower()
        except Exception as e:
            logging.debug(f'error in getting window process path {e}')
            continue
        if 'helldivers2' in process_path:
            return window
    return None


def do_strat_input(
    strat: T_Stratagems,
    target: Window,
    startup_delay: float | int = 1,
    key_delay: float = 0.1,
    input_type: Literal['WASD', 'Arrows'] = 'WASD',
) -> None:
    time.sleep(startup_delay)
    input_code = STRATAGEMS[strat]
    is_wasd = input_type == 'WASD'
    for direction in input_code:
        if is_wasd:
            key = INPUT_MAPPING[direction]
        else:
            key = direction
        target.send(f'{{Blind}}{{{key} DOWN}}', blocking=False)
        time.sleep(key_delay)
        target.send(f'{{Blind}}{{{key} UP}}', blocking=False)
        time.sleep(key_delay)
    return None


def create_macro_function(
    stratagem: T_Stratagems,
    target: Window,
    startup_delay: float | int = 1,
    key_delay: float = 0.1,
    input_type: Literal['WASD', 'Arrows'] = 'WASD',
) -> Callable[[], Any]:
    def macro() -> None:
        logger.info(f'Performing input for {stratagem}')
        do_strat_input(stratagem, target, startup_delay, key_delay, input_type)

    return macro


def error_handler(key: str, error: Exception) -> None:
    logger.error(f'{key}: {error}')


_should_exit = 0


def _exit() -> None:
    global _should_exit
    _should_exit = 1
    return None


def main() -> int:
    print('Looking for config file.')
    config_file = find_config_file()
    print('Found', config_file)
    config = read_config(config_file)
    _set_ahk_global(config)
    assert ahk is not None
    _start = time.time()
    logger.setLevel(level=getattr(logging, config.general.log_level))
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s'))
    logger.addHandler(handler)
    logger.info('Looking for Helldivers2 window')
    logger.debug(repr(config))

    while time.time() - _start < config.general.win_wait:
        hd = find_helldivers_window()
        if hd is not None:
            logger.info('Found helldivers2 window')
            break
        logger.debug('Helldivers 2 window not found')
        time.sleep(1)
    else:
        logger.fatal(f'Helldivers2 window not found within configured timeout ({config.general.win_wait} seconds)')
        return 1
    assert hd is not None

    def create_loadout_switcher(this_name: str, hotkeys: dict[T_Stratagems, str]) -> Callable[[], None]:
        def switch_loadout() -> None:
            logger.info('Switching to loadout %s', this_name)
            ahk.stop_hotkeys()
            ahk.clear_hotkeys()
            for strat, hotkey in hotkeys.items():
                callback = create_macro_function(
                    strat, hd, config.general.hotkey_start_delay, config.general.key_delay, config.general.input_type
                )
                ahk.add_hotkey(hotkey, callback, ex_handler=error_handler)
            for name, loadout_config in config.loadouts.items():
                switch_callback = create_loadout_switcher(name, loadout_config.hotkeys)
                ahk.add_hotkey(loadout_config.switch_hotkey, switch_callback, ex_handler=error_handler)
            ahk.add_hotkey(config.general.exit_hotkey, _exit, ex_handler=error_handler)
            ahk.start_hotkeys()
            return None

        return switch_loadout

    for loadout_name, loadout in config.loadouts.items():
        logger.debug(f'Initializing loader {loadout_name}')
        callback = create_loadout_switcher(loadout_name, loadout.hotkeys)
        ahk.add_hotkey(loadout.switch_hotkey, callback, ex_handler=error_handler)

    for strat, hotkey in config.default_loadout.hotkeys.items():
        logger.debug('Initializing default loadout')
        callback = create_macro_function(
            strat, hd, config.general.hotkey_start_delay, config.general.key_delay, config.general.input_type
        )
        ahk.add_hotkey(hotkey, callback, ex_handler=error_handler)

    ahk.add_hotkey(config.general.exit_hotkey, _exit, ex_handler=error_handler)

    ahk.start_hotkeys()
    logger.info('hotkey listener started')
    try:
        while True:
            if _should_exit:
                logger.info('Stopping.')
                try:
                    ahk.stop_hotkeys()
                except Exception as e:
                    logger.debug('Failed to stop hotkey: %s', e)
                    pass
                break
            if not hd.exists():
                logger.info('Helldivers window not found. Exiting.')
                break
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info('Keyboard interrupt received. Exiting.')
        pass
    return 0
