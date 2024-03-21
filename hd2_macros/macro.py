import logging
import time
from typing import Any
from typing import Callable

from ahk import AHK
from ahk import Window

from .config import find_config_file
from .config import read_config
from .constants import INPUT_MAPPING
from .constants import STRATAGEMS
from .constants import T_Stratagems

logger = logging.getLogger('hd2-macros')
logger.propagate = False

ahk = AHK()


def find_helldivers_window() -> Window | None:
    for window in ahk.list_windows(blocking=False).result():
        if 'helldivers2' in window.process_path.lower():
            return window
    return None


def do_strat_input(strat: T_Stratagems, target: Window, startup_delay: float | int = 1, key_delay: float = 0.1) -> None:
    time.sleep(startup_delay)
    input_code = STRATAGEMS[strat]
    for direction in input_code:
        key = INPUT_MAPPING[direction]
        target.send(f'{{Blind}}{{{key} DOWN}}', blocking=False)
        time.sleep(key_delay)
        target.send(f'{{Blind}}{{{key} UP}}', blocking=False)
        time.sleep(key_delay)
    return None


def create_macro_function(stratagem: T_Stratagems, target: Window) -> Callable[[], Any]:
    def macro() -> None:
        logger.info(f"Performing input for {stratagem}")
        do_strat_input(stratagem, target)

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
                callback = create_macro_function(strat, hd)
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
        callback = create_macro_function(strat, hd)
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
                logger.info("Helldivers window not found. Exiting.")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info('Keyboard interrupt received. Exiting.')
        pass
    return 0
