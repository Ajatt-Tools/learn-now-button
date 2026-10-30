# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from aqt import gui_hooks, mw

from .ajt_common.addon_config import set_config_action
from .browser_menus import BrowserMenus
from .config import LearnNowConfig, get_global_config
from .main_menu import MainMenu
from .reset_card_scheduling import on_browser_setup_menus, on_deck_browser_show_options


class EntryPoint:
    def __init__(self, cfg: LearnNowConfig | None = None) -> None:
        self._cfg = cfg or get_global_config()

    def attach_self_to_mw(self) -> None:
        setattr(mw, "_ajt__card_management_entry_point", self)  # call setattr to avoid LSP errors

    def main_menu_init(self) -> None:
        menus = MainMenu(cfg=self._cfg)
        set_config_action(menus.on_open_settings)
        menus.setup_mainwindow_menu()

    def browser_menus_init(self) -> None:
        """Register the shared Browser menu controller."""
        menus = BrowserMenus(cfg=self._cfg)
        gui_hooks.browser_menus_did_init.append(menus.on_browser_menus_did_init)

    @staticmethod
    def reset_card_scheduling_init() -> None:
        gui_hooks.browser_menus_did_init.append(on_browser_setup_menus)
        gui_hooks.deck_browser_will_show_options_menu.append(on_deck_browser_show_options)

    def init(self) -> None:
        self.attach_self_to_mw()
        self.main_menu_init()
        self.browser_menus_init()
        self.reset_card_scheduling_init()
