import time
from anki.cards import Card
from anki.lang import ngettext
from aqt import gui_hooks
from aqt import mw
from aqt.browser import Browser
from aqt.utils import tooltip


def notify_user(msg: str) -> None:
    tooltip(msg, period=7000)  # 7 seconds
    print(msg)


def format_message(skipped_cids: list, accepted_cids: list) -> str:
    msg = ''
    if len(accepted_cids) > 0:
        msg += ngettext("%d card was put in the learning queue.",
                        "%d cards were put in the learning queue.",
                        len(accepted_cids)
                        ) % len(accepted_cids)

    if len(skipped_cids) > 0:
        if len(msg) > 0:
            msg += ' '
        msg += ngettext("%d card was ignored because it wasn't a new card.",
                        "%d cards were ignored because they were not new cards.",
                        len(skipped_cids)
                        ) % len(skipped_cids)
    return msg


def is_new(card: Card) -> bool:
    return card.type == 0 and card.queue == 0


def reps_to_graduate(card: Card) -> int:
    # magick number that tells anki how many times the card
    # has to be answered good to graduate
    # a * 1000 + b,
    # b - the number of reps left till graduation
    # a - the number of reps left today
    group_conf: dict = mw.col.decks.confForDid(card.did)

    try:
        reps_left = len(group_conf['new']['delays'])
    except KeyError:
        reps_left = 2  # default in anki

    print('delays:', group_conf['new']['delays'], 'reps left:', reps_left)
    return reps_left * 1000 + reps_left


def putToLearn(cids: list) -> tuple:
    # https://github.com/ankidroid/Anki-Android/wiki/Database-Structure
    skipped, accepted = [], []

    for cid in cids:
        card = mw.col.getCard(cid)

        if not is_new(card):
            skipped.append(cid)
            continue

        # learn card
        card.type = 1
        card.queue = 1
        card.ivl = 0

        # due date, like this: 1608939774
        card.due = int(time.time())

        # number of reps left till graduation
        card.left = reps_to_graduate(card)

        # obviously, because it's a new card.
        card.reps = 0
        card.lapses = 0

        card.flush()
        accepted.append(cid)

    return skipped, accepted


def onBrowserPutToLearn(self: Browser) -> None:
    cids = self.selectedCards()

    self.model.beginReset()
    self.mw.checkpoint("Put cards in learning")

    skipped, accepted = putToLearn(cids)

    self.model.endReset()
    self.mw.reset()

    msg = format_message(skipped, accepted)
    notify_user(msg)


def onBrowserSetupMenus(self: Browser) -> None:
    menu = self.form.menu_Cards
    a = menu.addAction("Learn now")
    a.triggered.connect(self.onBrowserPutToLearn)


Browser.onBrowserPutToLearn = onBrowserPutToLearn
gui_hooks.browser_menus_did_init.append(onBrowserSetupMenus)
