# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from unittest.mock import create_autospec

import pytest
from anki.collection import Collection
from anki.decks import DeckManager
from aqt import AnkiQt
from aqt.browser import Browser
from aqt.qt import QApplication, QMenu

from card_management import reset_card_scheduling as reset


class TestResetMenus:
    """Verify reset actions consume QAction's checked flag before invoking callbacks."""

    @pytest.mark.parametrize("checked", [False, True])
    def test_browser_action(self, monkeypatch: pytest.MonkeyPatch, browser: Browser, checked: bool) -> None:
        """The original Browser callback handles an empty selection without a signal argument error."""
        browser.selected_cards.return_value = []
        tooltip = create_autospec(reset.tooltip)
        monkeypatch.setattr(reset, "tooltip", tooltip)
        reset.on_browser_setup_menus(browser)
        browser.form.menu_Cards.actions()[0].triggered.emit(checked)
        tooltip.assert_called_once_with("No cards selected.")

    @pytest.mark.parametrize("checked", [False, True])
    def test_deck_action(self, monkeypatch: pytest.MonkeyPatch, qapp: QApplication, checked: bool) -> None:
        """The original deck callback receives the captured deck ID, not checked."""
        window = create_autospec(AnkiQt, instance=True)
        window.col = create_autospec(Collection, instance=True)
        window.col.decks = create_autospec(DeckManager, instance=True)
        window.col.decks.is_filtered.return_value = True
        monkeypatch.setattr(reset, "mw", window)
        tooltip = create_autospec(reset.tooltip)
        monkeypatch.setattr(reset, "tooltip", tooltip)
        menu = QMenu()
        reset.on_deck_browser_show_options(menu, 42)
        menu.actions()[0].triggered.emit(checked)
        window.col.decks.is_filtered.assert_called_once_with(42)
        tooltip.assert_called_once_with("Can't reset scheduling for filtered/custom decks.")
