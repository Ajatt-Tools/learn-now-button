# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from collections.abc import Sequence
from typing import NamedTuple

from anki.cards import Card
from anki.collection import Collection
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
