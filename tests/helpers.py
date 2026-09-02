# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from collections.abc import Sequence
from types import ModuleType
from typing import NamedTuple
from unittest.mock import MagicMock, create_autospec

import pytest
from anki.cards import Card
from anki.collection import Collection, OpChanges
from aqt.browser import Browser
from aqt.operations import CollectionOp
from beartype import beartype


class CardSnapshot(NamedTuple):
    """Capture scheduling fields independently of a mutable Card instance."""

    card_type: int
    queue: int
    due: int
    interval: int
    repetitions: int
    lapses: int
    factor: int
    steps_left: int
    original_position: int | None


class FilterCardSpec(NamedTuple):
    """Describe a card's note, template, and scheduling state for filtering tests."""

    card_id: int
    note_id: int
    ordinal: int
    card_type: int = 0
    queue: int = 0


@beartype
def mock_filter_cards(specs: Sequence[FilterCardSpec]) -> Sequence[Card]:
    """Build autospecced cards from independent, immutable scheduling scenarios."""
    cards = []
    for spec in specs:
        card = create_autospec(Card, instance=True)
        card.id, card.nid, card.ord = spec.card_id, spec.note_id, spec.ordinal
        card.type, card.queue = spec.card_type, spec.queue
        cards.append(card)
    return cards


@beartype
def capture_collection_op(monkeypatch: pytest.MonkeyPatch, module: ModuleType) -> MagicMock:
    """Capture worker and success callbacks without starting an Anki background thread."""
    factory = create_autospec(CollectionOp)
    factory.return_value.success.return_value = factory.return_value
    monkeypatch.setattr(module, "CollectionOp", factory)
    return factory


@beartype
def complete_collection_op(factory: MagicMock, col: Collection) -> OpChanges:
    """Execute the captured worker and then its UI success callback."""
    changes = factory.call_args.kwargs["op"](col)
    factory.return_value.success.call_args.args[0](changes)
    return changes


@beartype
def make_new_cards(col: Collection, count: int) -> Sequence[Card]:
    """Add independent Basic notes and retrieve their new cards."""
    cards = []
    for index in range(count):
        note = col.new_note(col.models.by_name("Basic"))
        note["Front"] = f"Question {index}"
        note["Back"] = f"Answer {index}"
        col.add_note(note, col.decks.id("Default"))
        cards.extend(note.cards())
    return cards


@beartype
def select_new_cards(browser: Browser, col: Collection, count: int) -> Sequence[Card]:
    """Populate the Browser's mocked selection with cards from the supplied real collection."""
    cards = make_new_cards(col, count)
    browser.col = col
    browser.selected_cards.return_value = [card.id for card in cards]
    return cards


@beartype
def select_sibling_cards(browser: Browser, col: Collection) -> Sequence[Card]:
    """Create a two-template note and select both of its cards in reverse template order."""
    model = col.models.by_name("Basic")
    template = col.models.new_template("Reverse")
    template.update(qfmt="{{Back}}", afmt="{{Front}}")
    col.models.add_template(model, template)
    col.models.update_dict(model)
    cards = sorted(select_new_cards(browser, col, 1), key=lambda card: card.ord, reverse=True)
    browser.selected_cards.return_value = [card.id for card in cards]
    return cards


@beartype
def make_review_cards(col: Collection, count: int) -> Sequence[Card]:
    """Prepare review cards that are being graded before their scheduled due date."""
    cards = make_new_cards(col, count)
    for card in cards:
        card.type = 2
        card.queue = 2
        card.ivl = 30
        card.due = col.sched.today + 20
        card.factor = 2500
        card.reps = 3
    col.update_cards(cards)
    return cards


@beartype
def snapshot_cards(col: Collection, cards: Sequence[Card]) -> Sequence[CardSnapshot]:
    """Reload scheduling fields so assertions inspect stored collection state."""
    return tuple(
        CardSnapshot(
            card.type,
            card.queue,
            card.due,
            card.ivl,
            card.reps,
            card.lapses,
            card.factor,
            card.left,
            card.original_position,
        )
        for card in (col.get_card(original.id) for original in cards)
    )
