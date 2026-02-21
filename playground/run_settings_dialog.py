# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from aqt.qt import *

from card_management.settings_dialog import SettingsDialog



def main() -> None:
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
