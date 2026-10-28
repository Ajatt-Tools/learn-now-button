# Learn Now add-on for Anki 2.1
# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

try:
    # https://github.com/beartype/beartype
    from beartype.claw import beartype_this_package

    # Anki normally has no beartype. If installed, it rejects numeric package names such as '1021636467'.
    # Skip the hook for those AnkiWeb directories, but keep it active for development imports.
    if all(part.isidentifier() for part in __name__.split(".")):
        beartype_this_package()
except ImportError:
    pass

import sys

from aqt import mw


def start_addon() -> None:
    from . import browser_menus, main_menu, reset_card_scheduling

    main_menu.init()
    browser_menus.init()
    reset_card_scheduling.setup()


if mw and "pytest" not in sys.modules:
    start_addon()
