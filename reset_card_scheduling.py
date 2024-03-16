"""
This file is part of the Reset Card Scheduling add-on for Anki.

Main Module, hooks add-on methods into Anki.

Copyright: (c) 2015-2016 Jeff Baitis <jeff@baitis.net>
           (c) 2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

import functools
from typing import Sequence, Optional

from anki.cards import CardId
from anki.collection import Collection, OpChanges
from anki.consts import QUEUE_TYPE_NEW
from anki.decks import DeckId
from aqt import mw, gui_hooks
from aqt.browser import Browser
from aqt.operations import CollectionOp
from aqt.qt import QMenu, qconnect
from aqt.utils import askUser, tooltip


# Col is a collection of cards, cids are the ids of the cards to reset.
def resetSelectedCardScheduling(col: Collection, cids: Sequence[CardId], undo_msg: Optional[str] = None) -> OpChanges:
    """
    Resets statistics for selected cards,
    and removes them from learning queues.
    """
    # Removes card from dynamic deck
    mw.col.sched.remFromDyn(cids)
    # Resets selected cards in current collection
    mw.col.sched.reset_cards(cids)

    pos = col.add_custom_undo_entry(undo_msg or "Reset scheduling and learning on selected cards")

    cards = [col.get_card(cid) for cid in cids]
    for card in cards:
        card.reps = 0
        card.lapses = 0
        card.odid = DeckId(0)
        card.odue = 0
        card.queue = QUEUE_TYPE_NEW

    col.update_cards(cards)
    return col.merge_undo_entries(pos)


def onBrowserResetCards(self: Browser):
    cids = self.selected_cards()
    if not cids:
        tooltip("No cards selected.")
        return
    r = askUser(
        "This will reset <b>ALL</b> the scheduling information and "
        "progress of <b>{}</b> selected cards."
        "<br><br>Are you sure you want to proceed?".format(len(cids)),
        defaultno=True,
        title="Reset Card Scheduling",
    )
    if not r:
        return

    CollectionOp(
        parent=self,
        op=lambda col: resetSelectedCardScheduling(col, cids),
    ).success(
        lambda changes: tooltip(f"{len(cids)} cards reset.", parent=self),
    ).run_in_background()


def onDeckBrowserResetCards(deck_id: DeckId):
    assert mw, "Main window should be available."

    if mw.col.decks.is_filtered(deck_id):
        tooltip("Can't reset scheduling for filtered/custom decks.")
        return

    deck_name = mw.col.decks.name(deck_id)
    cids = mw.col.decks.cids(deck_id, children=True)

    if not cids:
        tooltip("Deck contains no cards.")
        return

    r = askUser(
        "This will reset <b>ALL</b> scheduling information and "
        "progress in the deck '{}' and all of its subdecks ({} cards)."
        "<br><br>Are you sure you want to proceed?".format(deck_name, len(cids)),
        defaultno=True,
        title="Reset Card Scheduling",
    )
    if not r:
        return

    CollectionOp(
        parent=mw,
        op=lambda col: resetSelectedCardScheduling(col, cids, undo_msg="Reset selected deck"),
    ).success(
        lambda changes: tooltip(f"{len(cids)} card(s) reset.", parent=mw),
    ).run_in_background()


def onBrowserSetupMenus(self: Browser):
    menu = self.form.menu_Cards
    a = menu.addAction("Reset selected cards")
    a.triggered.connect(functools.partial(onBrowserResetCards, self))


def onDeckBrowserShowOptions(menu: QMenu, deck_id: int):
    action = menu.addAction("Reset deck")
    qconnect(action.triggered, functools.partial(onDeckBrowserResetCards, deck_id))


# Hooks

def setup():
    gui_hooks.browser_menus_did_init.append(onBrowserSetupMenus)
    gui_hooks.deck_browser_will_show_options_menu.append(onDeckBrowserShowOptions)
