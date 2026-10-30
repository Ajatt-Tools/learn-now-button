import functools
import random
import time
from collections.abc import MutableSequence

import anki.collection
from anki.cards import Card
from aqt import gui_hooks
from aqt.browser import Browser
from aqt.operations import CollectionOp
from aqt.qt import *

from .config import LearnNowConfig, get_global_config
from .grade_now import answer_buttons, on_grade_cards
from .learn_now import (
    current_deck_id,
    format_message,
    get_selected_cards,
    is_new,
    notify_user,
    reps_to_graduate,
)


class BrowserMenus:
    def __init__(self, cfg: LearnNowConfig):
        self._cfg = cfg

    def on_browser_menus_did_init(self, browser: Browser) -> None:
        self._add_learn_now_button(browser)
        self._add_grade_now_buttons(browser)

    def _add_learn_now_button(self, browser: Browser):
        action = browser.form.menu_Cards.addAction("Learn now")
        qconnect(action.triggered, functools.partial(self._on_put_in_learning, browser=browser))

        if self._cfg.learn_shortcut:
            action.setShortcut(QKeySequence(self._cfg.learn_shortcut))
            action.setText(f"{action.text()} ({self._cfg.learn_shortcut})")

    def _add_grade_now_buttons(self, browser: Browser):
        grade_menu = browser.form.menu_Cards.addMenu("Grade now")
        for ease, text in answer_buttons().items():
            action = grade_menu.addAction(text)
            qconnect(action.triggered, functools.partial(on_grade_cards, self=browser, ease=ease))
            if shortcut := self._cfg.get(f"{text.lower()}_shortcut"):
                action.setShortcut(QKeySequence(shortcut))
                action.setText(f"{action.text()} ({shortcut})")

    def _get_due_offset(self) -> int:
        """
        By default, the add-on adds some randomness to due dates
        to make sure that the order of cards doesn't affect retention.
        """
        if self._cfg.randomize_card_due:
            return random.randint(0, 1000)
        return 0

    def _put_in_learning(self, col: anki.collection.Collection, card: Card) -> None:
        # https://github.com/ankidroid/Anki-Android/wiki/Database-Structure

        # learn card
        card.type = 1  # type: ignore
        card.queue = 1  # type: ignore
        card.ivl = 0

        # save card's original position
        card.original_position = card.odue if card.odid else card.due

        # due date, like this: 1608939774
        card.due = int(time.time() - self._get_due_offset())

        # number of reps left till graduation
        card.left = reps_to_graduate(col, card)

        # obviously, because it's a new card.
        card.reps = 0
        card.lapses = 0

        # set initial factor
        card.factor = col.decks.config_dict_for_deck_id(current_deck_id(card))["new"]["initialFactor"]

    def _put_cards_in_learning(
        self, col: anki.collection.Collection, cards: MutableSequence[Card]
    ) -> anki.collection.OpChanges:
        """Save learning changes in a single undo entry."""
        if not cards:
            return anki.collection.OpChanges()
        if self._cfg.randomize_card_due:
            random.shuffle(cards)
        for card in cards:
            self._put_in_learning(col, card)

        # Preparation can fail. Start undo history only when the batch is ready to write.
        # https://addon-docs.ankiweb.net/background-ops.html#collection-operations
        pos = col.add_custom_undo_entry("Put cards in learning")
        col.update_cards(cards)
        return col.merge_undo_entries(pos)

    def _on_put_in_learning(self, browser: Browser) -> None:
        selected_cards = list(get_selected_cards(browser))
        new_cards = list(filter(is_new, selected_cards))

        if len(new_cards) < 1:
            notify_user("No new cards selected. Nothing to do.")
        else:
            CollectionOp(
                parent=browser,
                op=lambda col: self._put_cards_in_learning(col, new_cards),
            ).success(lambda out: notify_user(format_message(new_cards, selected_cards))).run_in_background()


def init() -> None:
    menus = BrowserMenus(cfg=get_global_config())
    gui_hooks.browser_menus_did_init.append(menus.on_browser_menus_did_init)
