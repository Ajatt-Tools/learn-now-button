# Learn Now add-on for Anki 2.1
# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import sys

from aqt import mw


def start_addon() -> None:
    from . import browser_menus, main_menu, reset_card_scheduling

    main_menu.init()
    browser_menus.init()
    reset_card_scheduling.setup()


if mw and "pytest" not in sys.modules:
    start_addon()
