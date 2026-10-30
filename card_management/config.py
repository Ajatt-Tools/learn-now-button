# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
# Learn Now add-on for Anki 2.1

import functools

from aqt import mw

from .ajt_common.addon_config import AddonConfigManager


class LearnNowConfig(AddonConfigManager):
    @property
    def randomize_card_due(self) -> bool:
        return bool(self["randomize_card_due"])

    @property
    def learn_shortcut(self) -> str:
        return self["learn_shortcut"]


@functools.cache
def get_global_config() -> LearnNowConfig:
    """Load the shared configuration on first use."""
    assert mw, "anki must be running"
    # The settings dialog updates this instance directly, so no Anki config-update callback is needed.
    return LearnNowConfig()
