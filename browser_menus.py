from aqt import gui_hooks
from aqt.browser import Browser

from .grade_now import add_grade_now_buttons
from .learn_now import add_learn_now_button


def on_browser_menus_did_init(self: Browser) -> None:
    from .config import config

    add_learn_now_button(self, shortcut=config.get("learn_shortcut"))
    add_grade_now_buttons(self, config=config)


def init():
    gui_hooks.browser_menus_did_init.append(on_browser_menus_did_init)
