# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from collections.abc import Sequence
from unittest.mock import create_autospec

import pytest
from anki.collection import Collection
from aqt.browser import Browser

from card_management import browser_menus
from card_management.browser_menus import BrowserMenus
from card_management.grade_now import Ease
from playground.no_anki_config import NoAnkiConfigView
from tests.helpers import (
    capture_collection_op,
    complete_collection_op,
    select_new_cards,
    select_sibling_cards,
    snapshot_cards,
)


class TestBrowserMenus:
    """Exercise the real QAction signals connected by the refactored controller."""

    @pytest.mark.parametrize("skip_siblings,expected", [(False, (1, 1)), (True, (0, 1))])
    def test_sibling_worker(
        self,
        monkeypatch: pytest.MonkeyPatch,
        browser: Browser,
        anki_collection: Collection,
        no_anki_config: NoAnkiConfigView,
        skip_siblings: bool,
        expected: Sequence[int],
    ) -> None:
        """Apply sibling settings before persistence and report the accepted and rejected counts."""
        cards = select_sibling_cards(browser, anki_collection)
        no_anki_config["skip_sibling_cards"] = skip_siblings
        factory = capture_collection_op(monkeypatch, browser_menus)
        notify = create_autospec(browser_menus.notify_user)
        monkeypatch.setattr(browser_menus, "notify_user", notify)
        BrowserMenus(no_anki_config)._on_put_in_learning(browser)
        assert complete_collection_op(factory, anki_collection).card is True
        assert [card.queue for card in snapshot_cards(anki_collection, cards)] == list(expected)
        notify.assert_called_once_with(browser_menus.format_message(cards[: sum(expected)], cards))

    @pytest.mark.parametrize("count", [1, 2])
    def test_learning_worker_and_success(
        self,
        monkeypatch: pytest.MonkeyPatch,
        browser: Browser,
        anki_collection: Collection,
        no_anki_config: NoAnkiConfigView,
        count: int,
    ) -> None:
        """The worker uses the captured selection and reports completion only after persistence."""
        cards = select_new_cards(browser, anki_collection, count)
        factory = capture_collection_op(monkeypatch, browser_menus)
        notify = create_autospec(browser_menus.notify_user)
        monkeypatch.setattr(browser_menus, "notify_user", notify)
        BrowserMenus(no_anki_config)._on_put_in_learning(browser)
        assert factory.call_args.kwargs["parent"] is browser
        factory.return_value.run_in_background.assert_called_once_with()
        notify.assert_not_called()
        browser.selected_cards.return_value = []
        assert complete_collection_op(factory, anki_collection).card is True
        assert [card.queue for card in snapshot_cards(anki_collection, cards)] == [1] * count
        notify.assert_called_once_with(browser_menus.format_message(cards, cards))

    @pytest.mark.parametrize("has_selection", [False, True])
    def test_no_eligible_cards(
        self,
        monkeypatch: pytest.MonkeyPatch,
        browser: Browser,
        anki_collection: Collection,
        no_anki_config: NoAnkiConfigView,
        has_selection: bool,
    ) -> None:
        """Empty selections and non-new cards must not start a collection operation."""
        cards = select_new_cards(browser, anki_collection, int(has_selection))
        for card in cards:
            card.queue = -1
        anki_collection.update_cards(cards)
        factory = capture_collection_op(monkeypatch, browser_menus)
        notify = create_autospec(browser_menus.notify_user)
        monkeypatch.setattr(browser_menus, "notify_user", notify)
        BrowserMenus(no_anki_config)._on_put_in_learning(browser)
        factory.assert_not_called()
        notify.assert_called_once_with("No new cards selected. Nothing to do.")

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
