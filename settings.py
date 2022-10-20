# Learn Now add-on for Anki 2.1
# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from aqt.qt import *

try:
    from .ajt_common.grab_key import ShortCutGrabButton
except ImportError:
    from ajt_common.grab_key import ShortCutGrabButton


class SettingsDialog(QDialog):
    def __init__(self, config: dict = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        config = config or {}
        self.setMinimumSize(320, 64)
        self.setWindowTitle("Learn Now Settings")
        self.change_shortcut_button = ShortCutGrabButton(config.get('learn_shortcut'))
        self.setLayout(self.make_layout())

    def shortcut(self) -> str:
        return self.change_shortcut_button.value()

    def make_layout(self) -> QLayout:
        layout = QVBoxLayout()
        layout.addLayout(self.make_upper())
        layout.addLayout(self.make_lower())
        return layout

    def make_upper(self) -> QLayout:
        layout = QFormLayout()
        layout.addRow("Keyboard shortcut:", self.change_shortcut_button)
        return layout

    def make_lower(self) -> QLayout:
        layout = QHBoxLayout()
        layout.addWidget(ok_b := QPushButton("Save"))
        layout.addWidget(cancel_b := QPushButton("Cancel"))
        layout.addStretch()
        qconnect(ok_b.clicked, self.accept)
        qconnect(cancel_b.clicked, self.reject)
        return layout


def test_dialog():
    app = QApplication(sys.argv)
    w = SettingsDialog()
    w.show()
    code = app.exec()
    print(f"{'Accepted' if w.result() else 'Rejected'}. Shortcut: \"{w.shortcut()}\"")
    sys.exit(code)


if __name__ == '__main__':
    test_dialog()
