# Learn Now add-on for Anki 2.1
# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from aqt.qt import *

try:
    from .grab_key import KeyPressDialog
except ImportError:
    from grab_key import KeyPressDialog


class SettingsDialog(QDialog):
    def __init__(self, config: dict = None):
        super(SettingsDialog, self).__init__()
        config = config or {}
        self.setMinimumSize(320, 64)
        self.setWindowTitle("Learn Now Settings")
        self.shortcut = config.get('shortcut') or ''
        self.change_shortcut_button = QPushButton(config.get('shortcut') or '[Not assigned]')
        self.setLayout(self.make_layout())
        qconnect(self.change_shortcut_button.clicked, self.on_set_shortcut)

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

    def on_set_shortcut(self):
        if (d := KeyPressDialog(self)).exec():
            self.shortcut = d.shortcut or ''
            self.change_shortcut_button.setText(d.shortcut or '[Not assigned]')


def test_dialog():
    app = QApplication(sys.argv)
    w = SettingsDialog()
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    test_dialog()
