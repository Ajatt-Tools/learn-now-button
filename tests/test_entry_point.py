# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from unittest.mock import create_autospec

import pytest
from aqt import AnkiQt

from card_management import entry_point
from card_management.entry_point import EntryPoint
from card_management.reset_card_scheduling import (
    on_browser_setup_menus,
    on_deck_browser_show_options,
)
from playground.no_anki_config import NoAnkiConfigView


class TestEntryPoint:
    """Exercise controller initialization without testing add-on import behavior."""

    @pytest.mark.parametrize("inject_config", [False, True])
    def test_config_resolution(
        self,
        monkeypatch: pytest.MonkeyPatch,
        no_anki_config: NoAnkiConfigView,
        inject_config: bool,
    ) -> None:
        """Use injected settings directly and resolve the global accessor only when omitted."""
        accessor = create_autospec(entry_point.get_global_config, return_value=no_anki_config)
        monkeypatch.setattr(entry_point, "get_global_config", accessor)
        kwargs = {}
        if inject_config:
            kwargs["cfg"] = no_anki_config
        controller = EntryPoint(**kwargs)
        assert controller._cfg is no_anki_config
        assert accessor.call_count == int(not inject_config)

    def test_initialization(self, entry_point_window: AnkiQt, no_anki_config: NoAnkiConfigView) -> None:
        """Retain the entry point and wire every controller to the same configuration."""
        controller = EntryPoint(cfg=no_anki_config)
        controller.init()
        assert entry_point_window._ajt__card_management_entry_point is controller
        settings = entry_point.set_config_action.call_args.args[0]
        assert settings.__self__._cfg is no_anki_config
        handlers = entry_point.gui_hooks.browser_menus_did_init
        assert len(handlers) == 2
        assert handlers[0].__self__._cfg is no_anki_config
        assert handlers[1] is on_browser_setup_menus
        assert entry_point.gui_hooks.deck_browser_will_show_options_menu == [on_deck_browser_show_options]
