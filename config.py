# Learn Now add-on for Anki 2.1
# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from .ajt_common.addon_config import AddonConfigManager


class LearnNowConfig(AddonConfigManager):
    @property
    def randomize_card_due(self) -> bool:
        return bool(self["randomize_card_due"])


config = LearnNowConfig()
