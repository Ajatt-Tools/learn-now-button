# Learn Now add-on for Anki 2.1
# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from aqt import mw
from aqt.qt import *

from .settings_dialog import SettingsDialog


def get_config() -> dict:
    return mw.addonManager.getConfig(__name__)


def write_config() -> None:
    return mw.addonManager.writeConfig(__name__, config)


def set_config_action(fn: Callable) -> None:
    return mw.addonManager.setConfigAction(__name__, fn)


config = get_config()
