# Learn Now add-on for Anki 2.1
# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from .ajt_common.addon_config import AddonConfigManager


class LearnNowConfig(AddonConfigManager):
    @property
    def randomize_card_due(self) -> bool:
        return bool(self["randomize_card_due"])

    @property
    def skip_sibling_cards(self) -> bool:
        return bool(self["skip_sibling_cards"])

    @property
    def learn_shortcut(self) -> str:
        return self["learn_shortcut"]


config = LearnNowConfig()
