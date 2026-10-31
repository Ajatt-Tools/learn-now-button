# Learn Now add-on for Anki 2.1
# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from aqt import mw
from aqt.qt import *

from .ajt_common.about_menu import menu_root_entry
from .config import LearnNowConfig
from .settings_dialog import ADDON_NAME, SettingsDialog


class MainMenu:
    """Manage settings actions using the shared configuration instance."""

    def __init__(self, cfg: LearnNowConfig) -> None:
        """Retain the configuration used by the settings dialog."""
        self._cfg = cfg

    def on_open_settings(self) -> None:
        """Apply and persist edits only when the settings dialog is accepted."""
        dialog = SettingsDialog(parent=mw, config=self._cfg)
        if dialog.exec():
            # if accepted
            self._cfg.update(dialog.cfg_as_dict())
            self._cfg.write_config()

    def setup_mainwindow_menu(self) -> None:
        """Add the settings action to the shared Ajatt-Tools menu."""
        root_menu = menu_root_entry()
        action = QAction(f"{ADDON_NAME} Options...", root_menu)
        # Discard triggered's checked flag before calling the runtime-checked Python method.
        # https://doc.qt.io/qt-6/qaction.html#triggered
        qconnect(action.triggered, lambda checked=False: self.on_open_settings())
        root_menu.addAction(action)
