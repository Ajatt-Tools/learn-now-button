# Learn Now add-on for Anki 2.1
# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from collections.abc import Iterable, Iterator, Sized
from gettext import ngettext

from anki.cards import Card
from anki.collection import Collection
from anki.decks import DeckConfigDict
from anki.notes import NoteId
from aqt.browser import Browser
from aqt.utils import tooltip


def notify_user(msg: str) -> None:
    tooltip(msg, period=7_000)  # 7 seconds
    print(msg)


def format_message(accepted: Sized, selected: Sized) -> str:
    msg = []

    if (num_accepted := len(accepted)) > 0:
        msg.append(
            ngettext(
                f"{num_accepted} card was put in the learning queue.",
                f"{num_accepted} cards were put in the learning queue.",
                num_accepted,
            )
        )

    if (num_rejected := len(selected) - len(accepted)) > 0:
        msg.append(
            ngettext(
                f"{num_rejected} card was ignored because it isn't a new card or its sibling was chosen instead.",
                f"{num_rejected} cards were ignored because they are not new cards or their siblings were chosen"
                " instead.",
                num_rejected,
            )
        )

    return " ".join(msg)


def is_new(card: Card) -> bool:
    return card.type == 0 and card.queue == 0


def current_deck_id(card: Card) -> int:
    return card.odid if card.odid > 0 else card.did


def reps_to_graduate(col: Collection, card: Card) -> int:
    # magick number that tells anki how many times the card
    # has to be answered good to graduate
    # a * 1000 + b,
    # b - the number of reps left till graduation
    # a - the number of reps left today
    group_conf: DeckConfigDict = col.decks.config_dict_for_deck_id(current_deck_id(card))

    reps_left = len(group_conf["new"]["delays"])

    print("delays:", group_conf["new"]["delays"], "reps left:", reps_left)
    return reps_left * 1000 + reps_left


def get_selected_cards(browser: Browser) -> Iterator[Card]:
    return map(browser.col.get_card, set(browser.selected_cards()))


def filter_cards(cards: Iterable[Card], *, skip_siblings: bool) -> list[Card]:
    """
    Keep only new cards, and, if `skip_siblings` is enabled,
    keep only the sibling with the lowest `ord` per note (nid).

    Accept the Browser callback's list as well as one-shot iterators under runtime type checking.
    https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable
    """

    cards = (card for card in cards if is_new(card))
    if not skip_siblings:
        return [*cards]

    # For each note select one card with the lowest ord.
    note_id_to_min_card: dict[NoteId, Card] = {}

    for card in cards:
        current_best = note_id_to_min_card.get(card.nid)
        if current_best is None or card.ord < current_best.ord:
            note_id_to_min_card[card.nid] = card

    return [*note_id_to_min_card.values()]
