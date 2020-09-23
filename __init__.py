from aqt import mw
from anki.lang import ngettext
from aqt import gui_hooks
from aqt.utils import tooltip
from aqt.browser import Browser
from random import randrange


def notify_user(msg):
    tooltip(msg, period = 5000) # 5 seconds
    print(msg)


def format_message(skipped_cids, accepted_cids):
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


def is_new(card):
    return card.type == 0 and card.queue == 0


def putToLearn(cids):
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

        # random int according to the anki database docs
        card.due = randrange(50, 500)

        # magick number that tells anki that the card
        # has to be answered good two times to graduate
        card.left = 2002

        # obviously, because it's a new card.
        card.reps = 0
        card.lapses = 0

        card.flush()
        accepted.append(cid)

    return (skipped, accepted)


def onBrowserPutToLearn(self):
    cids = self.selectedCards()

    self.model.beginReset()
    self.mw.checkpoint("Put cards in learning")

    skipped, accepted = putToLearn(cids)

    self.model.endReset()
    self.mw.reset()

    msg = format_message(skipped, accepted)
    notify_user(msg)


def onBrowserSetupMenus(self):
    menu = self.form.menu_Cards
    a = menu.addAction("Learn now")
    a.triggered.connect(self.onBrowserPutToLearn)


Browser.onBrowserPutToLearn = onBrowserPutToLearn
gui_hooks.browser_menus_did_init.append(onBrowserSetupMenus)
