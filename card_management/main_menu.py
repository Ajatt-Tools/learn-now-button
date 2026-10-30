# Learn Now add-on for Anki 2.1
# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from aqt import mw
from aqt.qt import *

from .ajt_common.about_menu import menu_root_entry
from .ajt_common.addon_config import set_config_action
from .config import LearnNowConfig, get_global_config
from .settings_dialog import ADDON_NAME, SettingsDialog


class MainMenu:
    def __init__(self, cfg: LearnNowConfig) -> None:
        self._cfg = cfg

    def on_open_settings(self) -> None:
        dialog = SettingsDialog(parent=mw, config=self._cfg)
        if dialog.exec():
            # if accepted
            self._cfg.update(dialog.cfg_as_dict())
            self._cfg.write_config()

    def setup_mainwindow_menu(self) -> None:
        root_menu = menu_root_entry()
        action = QAction(f"{ADDON_NAME} Options...", root_menu)
        qconnect(action.triggered, self.on_open_settings)
        root_menu.addAction(action)


def init() -> None:
    menus = MainMenu(cfg=get_global_config())
    set_config_action(menus.on_open_settings)
    menus.setup_mainwindow_menu()
