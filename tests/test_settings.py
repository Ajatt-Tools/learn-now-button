# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from unittest.mock import create_autospec

import pytest
from aqt.qt import QApplication, QMenu

from card_management import main_menu
from card_management.main_menu import MainMenu
from card_management.settings_dialog import SettingsDialog
from playground.no_anki_config import NoAnkiConfigView


class TestSettingsDialog:
    """Verify the dialog accepts concrete standalone settings and preserves unsaved state."""

    @pytest.mark.parametrize("randomize", [False, True])
    def test_round_trip(self, qapp: QApplication, no_anki_config: NoAnkiConfigView, randomize: bool) -> None:
        """Read all default keys and serialize edited controls without updating config yet."""
        no_anki_config["randomize_card_due"] = randomize
        dialog = SettingsDialog(config=no_anki_config)
        assert dialog.cfg_as_dict() == no_anki_config.dict_copy()
        dialog._checkboxes["randomize_card_due"].setChecked(not randomize)
        expected = no_anki_config.dict_copy()
        expected["randomize_card_due"] = not randomize
        assert dialog.cfg_as_dict() == expected
        assert no_anki_config.randomize_card_due is randomize
        dialog.close()


class TestMainMenu:
    """Keep edits on the shared configuration instance and persist only accepted changes."""

    @pytest.mark.parametrize("checked", [False, True])
    def test_options_action(
        self,
        monkeypatch: pytest.MonkeyPatch,
        qapp: QApplication,
        no_anki_config: NoAnkiConfigView,
        checked: bool,
    ) -> None:
        """The real signal must open settings without forwarding its checked argument."""
        menu = QMenu()
        monkeypatch.setattr(main_menu, "menu_root_entry", lambda: menu)
        factory = create_autospec(SettingsDialog)
        factory.return_value.exec.return_value = 0
        monkeypatch.setattr(main_menu, "SettingsDialog", factory)
        controller = MainMenu(no_anki_config)
        controller.setup_mainwindow_menu()
        menu.actions()[0].triggered.emit(checked)
        factory.return_value.exec.assert_called_once_with()

    @pytest.mark.parametrize("accepted", [False, True])
    def test_settings_acceptance(
        self, monkeypatch: pytest.MonkeyPatch, no_anki_config: NoAnkiConfigView, accepted: bool
    ) -> None:
        """Cancel leaves configuration untouched, while acceptance updates and saves it."""
        factory = create_autospec(SettingsDialog)
        factory.return_value.exec.return_value = int(accepted)
        factory.return_value.cfg_as_dict.return_value = {"randomize_card_due": False}
        monkeypatch.setattr(main_menu, "SettingsDialog", factory)
        write = create_autospec(no_anki_config.write_config)
        monkeypatch.setattr(no_anki_config, "write_config", write)
        MainMenu(no_anki_config).on_open_settings()
        factory.assert_called_once_with(parent=main_menu.mw, config=no_anki_config)
        assert no_anki_config.randomize_card_due is not accepted
        if accepted:
            write.assert_called_once_with()
        else:
            write.assert_not_called()
