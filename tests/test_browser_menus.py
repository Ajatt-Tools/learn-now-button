# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from unittest.mock import create_autospec

import pytest
from aqt.browser import Browser

from card_management import browser_menus
from card_management.browser_menus import BrowserMenus
from card_management.grade_now import Ease
from playground.no_anki_config import NoAnkiConfigView


class TestBrowserMenus:
    """Exercise the real QAction signals connected by the refactored controller."""

    @pytest.mark.parametrize("checked", [False, True])
    @pytest.mark.parametrize("shortcut", ["", "Ctrl+L"])
    def test_learning_action(
        self,
        monkeypatch: pytest.MonkeyPatch,
        browser: Browser,
        no_anki_config: NoAnkiConfigView,
        checked: bool,
        shortcut: str,
    ) -> None:
        """Forward the Browser but not QAction's checked flag to the learning callback."""
        no_anki_config["learn_shortcut"] = shortcut
        menus = BrowserMenus(no_anki_config)
        callback = create_autospec(menus._on_put_in_learning)
        monkeypatch.setattr(menus, "_on_put_in_learning", callback)
        menus._add_learn_now_button(browser)
        action = browser.form.menu_Cards.actions()[0]
        assert action.shortcut().toString() == shortcut
        action.triggered.emit(checked)
        callback.assert_called_once_with(browser=browser)

    @pytest.mark.parametrize("checked", [False, True])
    @pytest.mark.parametrize("ease", [1, 2, 3, 4])
    def test_grading_action(
        self,
        monkeypatch: pytest.MonkeyPatch,
        browser: Browser,
        no_anki_config: NoAnkiConfigView,
        checked: bool,
        ease: Ease,
    ) -> None:
        """Each loop-created action retains its own grade without forwarding checked."""
        callback = create_autospec(browser_menus.on_grade_cards)
        monkeypatch.setattr(browser_menus, "on_grade_cards", callback)
        menus = BrowserMenus(no_anki_config)
        menus._add_grade_now_buttons(browser)
        grade_menu = browser.form.menu_Cards.actions()[0].menu()
        grade_menu.actions()[ease - 1].triggered.emit(checked)
        callback.assert_called_once_with(self=browser, ease=ease)
