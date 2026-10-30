# Learn Now add-on for Anki 2.1
# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import functools
from collections.abc import Iterator, Sized
from gettext import ngettext
from typing import Callable

from anki.cards import Card
from anki.collection import Collection
from anki.decks import DeckConfigDict
from aqt.browser import Browser
from aqt.operations import ResultWithChanges
from aqt.utils import tooltip


def notify_user(msg: str) -> None:
    tooltip(msg, period=7_000)  # 7 seconds
    print(msg)


def with_undo_entry(undo_msg: str):
    def decorator(function: Callable):
        @functools.wraps(function)
        def wrapper(col: Collection, *args, **kwargs) -> ResultWithChanges:
            pos = col.add_custom_undo_entry(undo_msg)
            function(col, *args, **kwargs)
            return col.merge_undo_entries(pos)

        return wrapper

    return decorator


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
                f"{num_rejected} card was ignored because it isn't a new card.",
                f"{num_rejected} cards were ignored because they are not new cards.",
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
