import time
from gettext import ngettext
from typing import Iterable
from typing import Sized, Callable

from anki.cards import Card
from anki.collection import Collection
from anki.decks import DeckConfigDict
from aqt import gui_hooks, qconnect
from aqt.browser import Browser
from aqt.operations import CollectionOp
from aqt.operations import ResultWithChanges
from aqt.utils import tooltip

UNDO_QUEUE_LIMIT = 30  # https://forums.ankiweb.net/t/add-on-porting-notes-for-anki-2-1-45/11212


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


def format_message(accepted: Sized, skipped: Sized) -> str:
    msg = []

    if len(accepted) > 0:
        msg.append(
            ngettext(
                "%d card was put in the learning queue.",
                "%d cards were put in the learning queue.",
                len(accepted)
            ) % len(accepted)
        )

    if len(skipped) > 0:
        msg.append(
            ngettext(
                "%d card was ignored because it wasn't a new card.",
                "%d cards were ignored because they were not new cards.",
                len(skipped)
            ) % len(skipped)
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
    card.due = int(time.time())

    # number of reps left till graduation
    card.left = reps_to_graduate(col, card)

    # obviously, because it's a new card.
    card.reps = 0
    card.lapses = 0

    # set initial factor
    card.factor = col.decks.config_dict_for_deck_id(card.did)['new']['initialFactor']

    # save the card and add an undo entry.
    col.update_card(card)


@with_undo_entry(undo_msg="Put cards in learning")
def put_cards_in_learning(col: Collection, cards: Iterable[Card]):
    for card in cards:
        put_in_learning(col, card)


def on_put_to_learn(self: Browser) -> None:
    selected_cards = {self.col.get_card(cid) for cid in self.selected_cards()}
    new_cards = {card for card in selected_cards if is_new(card)}

    if len(new_cards) > UNDO_QUEUE_LIMIT:
        notify_user(f"Can't perform this operation on more than {UNDO_QUEUE_LIMIT} cards at once.")
    if len(new_cards) < 1:
        notify_user("No new cards selected. Nothing to do.")
    else:
        CollectionOp(
            parent=self, op=lambda col: put_cards_in_learning(col, new_cards)
        ).success(
            lambda out: notify_user(format_message(new_cards, selected_cards - new_cards))
        ).run_in_background()


def on_browser_menus_did_init(self: Browser) -> None:
    menu = self.form.menu_Cards
    a = menu.addAction("Learn now")
    qconnect(a.triggered, self.onBrowserPutToLearn)


######################################################################
# Entry point
######################################################################

def init():
    Browser.onBrowserPutToLearn = on_put_to_learn
    gui_hooks.browser_menus_did_init.append(on_browser_menus_did_init)
