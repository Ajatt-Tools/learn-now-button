# Learn Now add-on for Anki 2.1
# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from aqt.qt import *


try:
    from .protocols import LearnNowConfigProtocol
    from .ajt_common.grab_key import ShortCutGrabButton
except ImportError:
    from protocols import LearnNowConfigProtocol
    from ajt_common.grab_key import ShortCutGrabButton

OK = QDialogButtonBox.StandardButton.Ok
CANCEL = QDialogButtonBox.StandardButton.Cancel
ADDON_NAME = "Card Management"


def as_label(config_key: str) -> str:
    return config_key.replace("_", " ").capitalize()


def make_checkboxes(config: LearnNowConfigProtocol):
    return {key: QCheckBox(as_label(key)) for key in config.bool_keys()}


class SettingsDialog(QDialog):
    def __init__(self, *args, config: LearnNowConfigProtocol = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMinimumSize(320, 64)
        self.setWindowTitle(f"{ADDON_NAME} Options")
        self._config = config or {}
        self._grab_buttons: dict[str, ShortCutGrabButton] = {
            key: ShortCutGrabButton() for key in self._config.keys() if key.endswith("_shortcut")
        }
        self._checkboxes = make_checkboxes(config)
        self._button_box = QDialogButtonBox(OK | CANCEL)
        self._setup_layout()
        self._setup_logic()
        self._set_initial_values()

    def cfg_as_dict(self) -> dict[str, Union[str, bool]]:
        d1 = {key: grab_button.value() for key, grab_button in self._grab_buttons.items()}
        d2 = {key: checkbox.isChecked() for key, checkbox in self._checkboxes.items()}
        return d1 | d2

    def _setup_layout(self) -> None:
        layout = QVBoxLayout()
        layout.addLayout(self._make_form())
        layout.addWidget(self._button_box)
        self.setLayout(layout)

    def _make_form(self) -> QLayout:
        layout = QFormLayout()
        for key, widget in self._grab_buttons.items():
            layout.addRow(as_label(key), widget)
        for key, widget in self._checkboxes.items():
            layout.addRow(widget)
        return layout

    def _setup_logic(self):
        qconnect(self._button_box.accepted, self.accept)
        qconnect(self._button_box.rejected, self.reject)
        self._button_box.button(OK).setFocus()

    def _set_initial_values(self):
        for cfg_key, shortcut_but in self._grab_buttons.items():
            shortcut_but.setValue(self._config[cfg_key])
        for cfg_key, checkbox in self._checkboxes.items():
            checkbox.setChecked(bool(self._config[cfg_key]))


def main():
    class Cfg:
        def bool_keys(self):
            return "bool_one", "bool_two"

        def keys(self):
            return "key_one", "key_two", "one_shortcut", "two_shortcut"

        def get(self, _key):
            return "Ctrl+x"

        def __getitem__(self, _item):
            return "Ctrl+x"

    app = QApplication(sys.argv)
    w = SettingsDialog(config=Cfg())
    w.show()
    code = app.exec()
    print(f"{'Accepted' if w.result() else 'Rejected'}.")
    for k, v in w.cfg_as_dict().items():
        print(f'{k} = "{v}"')
    sys.exit(code)


if __name__ == "__main__":
    main()
