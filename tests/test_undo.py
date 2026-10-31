# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from unittest.mock import create_autospec

import pytest
from anki.cards import Card
from anki.collection import Collection, OpChanges

from card_management.browser_menus import BrowserMenus
from card_management.grade_now import Ease, grade_cards
from playground.no_anki_config import NoAnkiConfigView
from tests.helpers import make_new_cards, make_review_cards, snapshot_cards


class TestLearningUndo:
    """Verify that learning batches have one usable undo step and no empty steps."""

    @pytest.mark.parametrize("count", [1, 3])
    @pytest.mark.parametrize("randomize", [False, True])
    def test_batch_undo_redo(
        self, anki_collection: Collection, no_anki_config: NoAnkiConfigView, count: int, randomize: bool
    ) -> None:
        """One Undo restores every card and one Redo reapplies the complete batch."""
        no_anki_config["randomize_card_due"] = randomize
        cards = list(make_new_cards(anki_collection, count))
        original_order = cards.copy()
        before = snapshot_cards(anki_collection, original_order)
        changes = BrowserMenus(no_anki_config)._put_cards_in_learning(anki_collection, cards)
        after = snapshot_cards(anki_collection, original_order)
        assert changes.card is True
        assert [card.queue for card in after] == [1] * count
        assert anki_collection.undo_status().undo == "Put cards in learning"
        anki_collection.undo()
        assert snapshot_cards(anki_collection, original_order) == before
        anki_collection.redo()
        assert snapshot_cards(anki_collection, original_order) == after

    @pytest.mark.parametrize("randomize", [False, True])
    def test_preparation_failure_does_not_create_undo(
        self, monkeypatch: pytest.MonkeyPatch, no_anki_config: NoAnkiConfigView, randomize: bool
    ) -> None:
        """A failure before card persistence must not create an empty undo entry."""
        no_anki_config["randomize_card_due"] = randomize
        col = create_autospec(Collection, instance=True)
        menus = BrowserMenus(no_anki_config)
        prepare = create_autospec(menus._put_in_learning, side_effect=ValueError("preparation failed"))
        monkeypatch.setattr(menus, "_put_in_learning", prepare)
        with pytest.raises(ValueError, match="preparation failed"):
            menus._put_cards_in_learning(col, [create_autospec(Card, instance=True)])
        col.add_custom_undo_entry.assert_not_called()
        col.update_cards.assert_not_called()


class TestGradingUndo:
    """Verify that answers and scheduling changes are grouped together."""

    @pytest.mark.parametrize("ease", [1, 2, 3, 4])
    @pytest.mark.parametrize("review", [False, True], ids=["new", "early-review"])
    def test_batch_undo_redo(self, anki_collection: Collection, ease: Ease, review: bool) -> None:
        """Undo and Redo restore both cards and their review log entries."""
        make_cards = make_new_cards
        if review:
            make_cards = make_review_cards
        cards = make_cards(anki_collection, 2)
        before = snapshot_cards(anki_collection, cards)
        log_count = anki_collection.db.scalar("select count(*) from revlog")
        changes = grade_cards(anki_collection, cards, ease)
        after = snapshot_cards(anki_collection, cards)
        assert changes.card is True
        assert anki_collection.undo_status().undo == "Grade cards from Browser"
        assert anki_collection.db.scalar("select count(*) from revlog") == log_count + 2
        anki_collection.undo()
        assert snapshot_cards(anki_collection, cards) == before
        assert anki_collection.db.scalar("select count(*) from revlog") == log_count
        anki_collection.redo()
        assert snapshot_cards(anki_collection, cards) == after
        assert anki_collection.db.scalar("select count(*) from revlog") == log_count + 2


class TestEmptyBatchUndo:
    """Apply the same history-preservation contract to learning and grading."""

    @pytest.mark.parametrize("learning", [False, True], ids=["grade", "learn"])
    @pytest.mark.parametrize("has_redo", [False, True])
    def test_empty_batch_preserves_history(
        self, anki_collection: Collection, no_anki_config: NoAnkiConfigView, learning: bool, has_redo: bool
    ) -> None:
        """Empty requests leave both Undo and Redo history intact."""
        make_new_cards(anki_collection, 1)
        if has_redo:
            anki_collection.undo()
        before = anki_collection.undo_status()
        if learning:
            changes = BrowserMenus(no_anki_config)._put_cards_in_learning(anki_collection, [])
        else:
            changes = grade_cards(anki_collection, [], 3)
        assert changes == OpChanges()
        assert anki_collection.undo_status() == before
