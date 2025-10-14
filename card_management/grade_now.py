# Learn Now add-on for Anki 2.1
# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import functools
from collections.abc import Sequence, Sized
from gettext import ngettext
from typing import Literal

from anki.cards import Card
from anki.collection import Collection, OpChanges
from aqt.browser import Browser
from aqt.operations import CollectionOp
from aqt.qt import *
from aqt.utils import showInfo

from .learn_now import notify_user, with_undo_entry, get_selected_cards

Ease = Literal[1, 2, 3, 4]
UNDO_QUEUE_LIMIT = 30  # https://forums.ankiweb.net/t/add-on-porting-notes-for-anki-2-1-45/11212


def format_message(answered: Sized, selected: Sized, button: str) -> str:
    msg = []

    if (num_answered := len(answered)) > 0:
        msg.append(
            ngettext(
                f"{num_answered} card was answered {button}.",
                f"{num_answered} cards were answered {button}.",
                num_answered,
            )
        )

    if (num_rejected := len(selected) - len(answered)) > 0:
        msg.append(
            ngettext(
                f"{num_rejected} card was ignored because it is suspended or buried.",
                f"{num_rejected} cards were ignored because they are suspended or buried.",
                num_rejected,
            )
        )

    return " ".join(msg)


def last_rep_day(card: Card) -> int:
    return card.due - card.ivl


def days_since_last_rep(col: Collection, card: Card) -> int:
    return col.sched.today - last_rep_day(card)


def adjust_intervals(col: Collection, cards: Sequence[Card]) -> OpChanges:
    """
    When answering a card prematurely, i.e. when it's not due yet,
    its actual interval is smaller than the recorded one.
    Intervals of such cards have to be reduced, making them match the reality.
    """
    for card in cards:
        if card.ivl > (passed := days_since_last_rep(col, card)) >= 0:
            card.ivl = passed
    return col.update_cards(cards)


@with_undo_entry(undo_msg="Grade cards from Browser")
def grade_cards(col: Collection, cards: Sequence[Card], ease: Ease):
    adjust_intervals(col, cards)

    for card in cards:
        card.start_timer()
        col.sched.answerCard(card, ease)


def is_not_suspended_or_buried(card: Card) -> bool:
    # https://github.com/ankidroid/Anki-Android/wiki/Database-Structure
    return card.queue >= 0


def on_grade_cards(self: Browser, ease: Ease):
    selected_cards = list(get_selected_cards(self))
    to_answer = list(filter(is_not_suspended_or_buried, selected_cards))
    if self.col.sched.version < 3:
        return showInfo("Aborted. Enable v3 scheduler in Preferences.")
    if not to_answer:
        return notify_user("Nothing to do.")
    if len(to_answer) > UNDO_QUEUE_LIMIT:
        return notify_user(f"Can't perform this operation on more than {UNDO_QUEUE_LIMIT} cards at once.")
    CollectionOp(
        parent=self,
        op=lambda col: grade_cards(col, to_answer, ease),
    ).success(
        lambda out: notify_user(format_message(to_answer, selected_cards, answer_buttons()[ease])),
    ).run_in_background()


def answer_buttons() -> dict[Ease, str]:
    return {
        1: "Again",
        2: "Hard",
        3: "Good",
        4: "Easy",
    }


def add_grade_now_buttons(self: Browser, *, config: dict[str, str]):
    grade_menu = self.form.menu_Cards.addMenu("Grade now")
    for ease, text in answer_buttons().items():
        action = grade_menu.addAction(text)
        qconnect(action.triggered, functools.partial(on_grade_cards, self=self, ease=ease))
        if shortcut := config.get(f"{text.lower()}_shortcut"):
            action.setShortcut(QKeySequence(shortcut))
            action.setText(f"{action.text()} ({shortcut})")
