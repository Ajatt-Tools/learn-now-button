# Learn Now add-on for Anki 2.1
# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from aqt.qt import *


class KeyPressDialog(QDialog):
    MOD_MASK = Qt.CTRL | Qt.ALT | Qt.SHIFT | Qt.META

    def __init__(self):
        super().__init__()
        self.setMinimumSize(380, 64)
        self.setWindowTitle("Grab key combination")
        self.label = QLabel("Please press the key combination you would like to assign.")
        self.setLayout(self.make_layout())
        self.key_name = None

    def make_layout(self) -> QLayout:
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.label.setAlignment(Qt.AlignCenter)
        return layout

    def keyPressEvent(self, event):
        # https://stackoverflow.com/questions/35033116
        key = event.key()
        modifiers = int(event.modifiers())
        if (
                modifiers
                and modifiers & self.MOD_MASK == modifiers
                and key > 0
                and key != Qt.Key_Shift
                and key != Qt.Key_Alt
                and key != Qt.Key_Control
                and key != Qt.Key_Meta
        ):
            self.key_name = QKeySequence(modifiers + key).toString()
            self.accept()
        else:
            self.label.setText(
                f"<font color=\"#540000\">Please try again and use a modifier: CTRL, ALT, SHIFT or META.</font>"
            )


def detect_keypress():
    app = QApplication(sys.argv)
    w = KeyPressDialog()
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    detect_keypress()
