# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import sys

from aqt.qt import QApplication

from card_management.settings_dialog import SettingsDialog
from playground.no_anki_config import NoAnkiConfigView


def main() -> None:
    """Preview the settings dialog using the actual default configuration."""
    app = QApplication(sys.argv)
    config = NoAnkiConfigView()
    w = SettingsDialog(config=config)
    w.show()
    code = app.exec()
    print(f"{'Accepted' if w.result() else 'Rejected'}.")
    for k, v in w.cfg_as_dict().items():
        print(f'{k} = "{v}"')
    sys.exit(code)


if __name__ == "__main__":
    main()
