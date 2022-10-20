# Learn Now add-on for Anki 2.1
# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from typing import Callable

from aqt import mw


def get_config() -> dict:
    return mw.addonManager.getConfig(__name__)


def get_default_config():
    manager = mw.addonManager
    addon = manager.addonFromModule(__name__)
    return manager.addonConfigDefaults(addon)


def write_config() -> None:
    return mw.addonManager.writeConfig(__name__, config)


def set_config_action(fn: Callable) -> None:
    return mw.addonManager.setConfigAction(__name__, fn)


config = get_config()
