# Learn Now add-on for Anki 2.1
# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import functools
import random
import time
from gettext import ngettext
from typing import Sequence, Iterator
from typing import Sized, Callable

from anki.cards import Card
from anki.collection import Collection, OpChanges
from anki.decks import DeckConfigDict
from aqt import qconnect
from aqt.browser import Browser
from aqt.operations import CollectionOp
from aqt.operations import ResultWithChanges
from aqt.qt import QKeySequence
from aqt.utils import tooltip



def notify_user(msg: str) -> None:
    tooltip(msg, period=7000)  # 7 seconds
    print(msg)


def with_undo_entry(undo_msg: str):
    def decorator(function: Callable):
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
                num_accepted
            )
        )

    if (num_rejected := len(selected) - len(accepted)) > 0:
        msg.append(
            ngettext(
                f"{num_rejected} card was ignored because it isn't a new card.",
                f"{num_rejected} cards were ignored because they are not new cards.",
                num_rejected
            )
        )

    return ' '.join(msg)


def is_new(card: Card) -> bool:
    return card.type == 0 and card.queue == 0


def reps_to_graduate(col: Collection, card: Card) -> int:
    # magick number that tells anki how many times the card
    # has to be answered good to graduate
    # a * 1000 + b,
    # b - the number of reps left till graduation
    # a - the number of reps left today
    group_conf: DeckConfigDict = col.decks.config_dict_for_deck_id(card.did)

    reps_left = len(group_conf['new']['delays'])

    print('delays:', group_conf['new']['delays'], 'reps left:', reps_left)
    return reps_left * 1000 + reps_left


def put_in_learning(col: Collection, card: Card) -> None:
    # https://github.com/ankidroid/Anki-Android/wiki/Database-Structure

    # learn card
    card.type = 1
    card.queue = 1
    card.ivl = 0

    # due date, like this: 1608939774
    card.due = int(time.time() - random.randint(0, 100))

    # number of reps left till graduation
    card.left = reps_to_graduate(col, card)

    # obviously, because it's a new card.
    card.reps = 0
    card.lapses = 0

    # set initial factor
    card.factor = col.decks.config_dict_for_deck_id(card.did)['new']['initialFactor']


@with_undo_entry(undo_msg="Put cards in learning")
def put_cards_in_learning(col: Collection, cards: Sequence[Card]) -> OpChanges:
    for card in cards:
        put_in_learning(col, card)

    # save the cards and add an undo entry.
    return col.update_cards(cards)


def get_selected_cards(browser: Browser) -> Iterator[Card]:
    return map(browser.col.get_card, set(browser.selected_cards()))


def on_put_in_learning(browser: Browser) -> None:
    selected_cards = list(get_selected_cards(browser))
    new_cards = list(filter(is_new, selected_cards))

    if len(new_cards) < 1:
        notify_user("No new cards selected. Nothing to do.")
    else:
        CollectionOp(
            parent=browser, op=lambda col: put_cards_in_learning(col, new_cards)
        ).success(
            lambda out: notify_user(format_message(new_cards, selected_cards))
        ).run_in_background()


def add_learn_now_button(self: Browser, *, shortcut: Optional[str]):
    action = self.form.menu_Cards.addAction("Learn now")
    qconnect(action.triggered, functools.partial(on_put_in_learning, browser=self))

    if shortcut:
        action.setShortcut(QKeySequence(shortcut))
        action.setText(f"{action.text()} ({shortcut})")
