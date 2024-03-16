# Learn Now add-on for Anki 2.1
# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from . import browser_menus, main_menu, reset_card_scheduling

main_menu.init()
browser_menus.init()
reset_card_scheduling.setup()
