# Learn Now add-on for Anki 2.1
# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from aqt.qt import *

try:
    from .ajt_common.grab_key import ShortCutGrabButton
except ImportError:
    from ajt_common.grab_key import ShortCutGrabButton

OK = QDialogButtonBox.StandardButton.Ok
CANCEL = QDialogButtonBox.StandardButton.Cancel


class SettingsDialog(QDialog):
    def __init__(self, *args, config: dict = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMinimumSize(320, 64)
        self.setWindowTitle("Learn Now Settings")
        self._config = config or {}
        self._change_shortcut_button = ShortCutGrabButton(self._config.get('learn_shortcut'))
        self._button_box = QDialogButtonBox(OK | CANCEL)
        self.setLayout(self.make_layout())
        self.setup_logic()

    def learn_shortcut(self) -> str:
        return self._change_shortcut_button.value()

    def make_layout(self) -> QLayout:
        layout = QVBoxLayout()
        layout.addLayout(self.make_form())
        layout.addWidget(self._button_box)
        return layout

    def make_form(self) -> QLayout:
        layout = QFormLayout()
        layout.addRow("Keyboard shortcut:", self._change_shortcut_button)
        return layout

    def setup_logic(self):
        qconnect(self._button_box.accepted, self.accept)
        qconnect(self._button_box.rejected, self.reject)
        self._button_box.button(OK).setFocus()


def test_dialog():
    app = QApplication(sys.argv)
    w = SettingsDialog()
    w.show()
    code = app.exec()
    print(f"{'Accepted' if w.result() else 'Rejected'}. Shortcut: \"{w.learn_shortcut()}\"")
    sys.exit(code)


if __name__ == '__main__':
    test_dialog()
