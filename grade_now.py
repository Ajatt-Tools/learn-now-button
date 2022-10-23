# Learn Now add-on for Anki 2.1
# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import functools
from gettext import ngettext
from typing import Sequence, Dict, Literal, Sized

from anki.cards import Card
from anki.collection import Collection, OpChanges
from aqt.browser import Browser
from aqt.operations import CollectionOp
from aqt.qt import *

from .learn_now import notify_user, with_undo_entry, get_selected_cards

Ease = Literal[1, 2, 3, 4]


def format_message(answered: Sized, selected: Sized, button: str) -> str:
    msg = []

    if (num_answered := len(answered)) > 0:
        msg.append(
            ngettext(
                f"{num_answered} card was answered {button}.",
                f"{num_answered} cards were answered {button}.",
                num_answered
            )
        )

    if (num_rejected := len(selected) - len(answered)) > 0:
        msg.append(
            ngettext(
                f"{num_rejected} card was ignored because it is suspended or buried.",
                f"{num_rejected} cards were ignored because they are suspended or buried.",
                num_rejected
            )
        )

    return ' '.join(msg)


@with_undo_entry(undo_msg="Grade cards from Browser")
def grade_cards(col: Collection, cards: Sequence[Card], ease: Ease) -> OpChanges:
    for card in cards:
        card.start_timer()
        col.sched.answerCard(card, ease)
    # save the cards and add an undo entry.
    return col.update_cards(cards)


def is_not_suspended_or_buried(card: Card) -> bool:
    # https://github.com/ankidroid/Anki-Android/wiki/Database-Structure
    return card.queue >= 0


def on_grade_cards(self: Browser, ease: Ease) -> None:
    selected_cards = list(get_selected_cards(self))
    to_answer = list(filter(is_not_suspended_or_buried, selected_cards))

    CollectionOp(
        parent=self, op=lambda col: grade_cards(col, to_answer, ease)
    ).success(
        lambda out: notify_user(format_message(to_answer, selected_cards, answer_buttons()[ease]))
    ).run_in_background()


def answer_buttons() -> Dict[Ease, str]:
    return {
        1: 'Again',
        2: 'Hard',
        3: 'Good',
        4: 'Easy',
    }


def add_grade_now_buttons(self: Browser, *, config: Dict[str, str]):
    grade_menu = self.form.menu_Cards.addMenu("Grade now")
    for ease, text in answer_buttons().items():
        action = grade_menu.addAction(text)
        qconnect(action.triggered, functools.partial(on_grade_cards, self=self, ease=ease))
        if shortcut := config.get(f'{text.lower()}_shortcut'):
            action.setShortcut(QKeySequence(shortcut))
            action.setText(f"{action.text()} ({shortcut})")
