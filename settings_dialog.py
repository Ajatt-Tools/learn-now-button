# Learn Now add-on for Anki 2.1
# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from collections.abc import Sequence

from aqt.qt import *

try:
    from .ajt_common.grab_key import ShortCutGrabButton
except ImportError:
    from ajt_common.grab_key import ShortCutGrabButton

OK = QDialogButtonBox.StandardButton.Ok
CANCEL = QDialogButtonBox.StandardButton.Cancel


def as_label(config_key: str) -> str:
    return config_key.replace('_', ' ').capitalize()


class SettingsDialog(QDialog):
    def __init__(self, *args, config: dict = None, grab_keys: Sequence[str], **kwargs):
        super().__init__(*args, **kwargs)
        self.setMinimumSize(320, 64)
        self.setWindowTitle("Learn Now Settings")
        self._config = config or {}
        self._grab_buttons = {
            key: ShortCutGrabButton(self._config.get(key))
            for key in grab_keys
            if key.endswith('_shortcut')
        }
        self._button_box = QDialogButtonBox(OK | CANCEL)
        self.setLayout(self.make_layout())
        self.setup_logic()

    def as_dict(self) -> dict[str, str]:
        return {
            key: grab_button.value()
            for key, grab_button in self._grab_buttons.items()
        }

    def make_layout(self) -> QLayout:
        layout = QVBoxLayout()
        layout.addLayout(self.make_form())
        layout.addWidget(self._button_box)
        return layout

    def make_form(self) -> QLayout:
        layout = QFormLayout()
        for key, widget in self._grab_buttons.items():
            layout.addRow(as_label(key), widget)
        return layout

    def setup_logic(self):
        qconnect(self._button_box.accepted, self.accept)
        qconnect(self._button_box.rejected, self.reject)
        self._button_box.button(OK).setFocus()


def test_dialog():
    app = QApplication(sys.argv)
    w = SettingsDialog(grab_keys=('learn_shortcut', 'again_shortcut'))
    w.show()
    code = app.exec()
    print(f"{'Accepted' if w.result() else 'Rejected'}.")
    for k, v in w.as_dict().items():
        print(f'{k} = "{v}"')
    sys.exit(code)


if __name__ == '__main__':
    test_dialog()
