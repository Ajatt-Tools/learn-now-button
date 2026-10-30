# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import random
from unittest.mock import create_autospec

import pytest
from aqt import AnkiQt

from card_management import config as config_module
from card_management.ajt_common import addon_config
from card_management.browser_menus import BrowserMenus
from playground.no_anki_config import NoAnkiConfigView


class TestGlobalConfig:
    """Check lazy construction and shared configuration identity."""

    @pytest.mark.parametrize("anki_running", [False, True])
    def test_cached_accessor(
        self,
        monkeypatch: pytest.MonkeyPatch,
        clear_config_cache: None,
        no_anki_config: NoAnkiConfigView,
        anki_running: bool,
    ) -> None:
        """Only construct settings with Anki running and reuse that instance afterward."""
        defaults = create_autospec(addon_config.get_default_config, return_value=no_anki_config.default_config)
        stored = create_autospec(addon_config.get_config, return_value=no_anki_config.dict_copy())
        monkeypatch.setattr(addon_config, "get_default_config", defaults)
        monkeypatch.setattr(addon_config, "get_config", stored)
        monkeypatch.setattr(config_module, "mw", None)
        if not anki_running:
            with pytest.raises(AssertionError, match="anki must be running"):
                config_module.get_global_config()
            defaults.assert_not_called()
            stored.assert_not_called()
            return
        monkeypatch.setattr(config_module, "mw", create_autospec(AnkiQt, instance=True))
        config = config_module.get_global_config()
        assert config_module.get_global_config() is config
        defaults.assert_called_once_with()
        stored.assert_called_once_with()

    @pytest.mark.parametrize("randomize", [False, True])
    def test_existing_controller_sees_changes(
        self, monkeypatch: pytest.MonkeyPatch, no_anki_config: NoAnkiConfigView, randomize: bool
    ) -> None:
        """Settings updates affect existing controllers without replacing their configuration."""
        menus = BrowserMenus(no_anki_config)
        randint = create_autospec(random.randint, return_value=42)
        monkeypatch.setattr("card_management.browser_menus.random.randint", randint)
        no_anki_config.update({"randomize_card_due": randomize})
        if randomize:
            assert menus._get_due_offset() == 42
            randint.assert_called_once_with(0, 1000)
        else:
            assert menus._get_due_offset() == 0
            randint.assert_not_called()


class TestNoAnkiConfig:
    """Keep standalone settings compatible with the concrete production configuration."""

    @pytest.mark.parametrize("key,value", [("randomize_card_due", False), ("learn_shortcut", "Ctrl+L")])
    def test_edits_preserve_defaults(self, no_anki_config: NoAnkiConfigView, key: str, value: str | bool) -> None:
        """Editable settings and dict copies must remain detached from defaults."""
        original = no_anki_config[key]
        no_anki_config[key] = value
        assert no_anki_config[key] == value
        assert no_anki_config.default_config[key] == original
        detached = no_anki_config.dict_copy()
        detached[key] = original
        assert no_anki_config[key] == value
        assert no_anki_config.is_default is False
