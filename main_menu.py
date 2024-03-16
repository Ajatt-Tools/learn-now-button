# Learn Now add-on for Anki 2.1
# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from aqt import mw
from aqt.qt import *

from .ajt_common.about_menu import menu_root_entry
from .ajt_common.addon_config import set_config_action
from .settings_dialog import SettingsDialog, ADDON_NAME


def on_open_settings():
    from .config import config

    dialog = SettingsDialog(mw, config=config)
    if dialog.exec():
        # if accepted
        config.update(dialog.cfg_as_dict())
        config.write_config()


def setup_mainwindow_menu():
    root_menu = menu_root_entry()
    action = QAction(f"{ADDON_NAME} Options...", root_menu)
    qconnect(action.triggered, on_open_settings)
    root_menu.addAction(action)


def init():
    set_config_action(on_open_settings)
    setup_mainwindow_menu()
