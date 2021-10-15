# Learn Now add-on for Anki 2.1
# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from aqt.qt import *


class KeyPressDialog(QDialog):
    MOD_MASK = Qt.CTRL | Qt.ALT | Qt.SHIFT | Qt.META

    def __init__(self, parent: QWidget = None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.shortcut = None
        self.setMinimumSize(380, 64)
        self.setWindowTitle("Grab key combination")
        self.label = QLabel(
            "Please press the key combination you would like to assign.\n"
            "Supported modifiers: CTRL, ALT, SHIFT or META.\n"
            "Press ESC to delete the shortcut."
        )
        self.setLayout(self.make_layout())

    def make_layout(self) -> QLayout:
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.label.setAlignment(Qt.AlignCenter)
        return layout

    def keyPressEvent(self, event):
        # https://stackoverflow.com/questions/35033116
        key, modifiers = int(event.key()), int(event.modifiers())

        if key == Qt.Key_Escape:
            self.shortcut = None
            self.accept()
        elif (
                modifiers
                and modifiers & self.MOD_MASK == modifiers
                and key > 0
                and key != Qt.Key_Shift
                and key != Qt.Key_Alt
                and key != Qt.Key_Control
                and key != Qt.Key_Meta
        ):
            self.shortcut = QKeySequence(modifiers + key).toString()
            self.accept()


def detect_keypress():
    app = QApplication(sys.argv)
    w = KeyPressDialog()
    w.show()
    code = app.exec()
    print(f"{'Accepted' if w.result() else 'Rejected'}. Shortcut: \"{w.shortcut}\"")
    sys.exit(code)


if __name__ == '__main__':
    detect_keypress()
