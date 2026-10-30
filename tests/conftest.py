# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import os
import sys
import traceback
from collections.abc import Iterator
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import create_autospec

import anki.lang
import pytest
from anki.collection import Collection
from aqt.browser import Browser
from aqt.qt import QApplication, QMenu
from beartype import beartype

from card_management.config import get_global_config
from playground.no_anki_config import NoAnkiConfigView


@pytest.fixture
def browser(qapp: QApplication) -> Browser:
    """Provide a real Cards menu without constructing the full Browser window."""
    browser = create_autospec(Browser, instance=True)
    browser.form = SimpleNamespace(menu_Cards=QMenu())
    return browser


@pytest.fixture
def no_anki_config() -> NoAnkiConfigView:
    """Provide independent editable settings without a running Anki instance."""
    return NoAnkiConfigView()


@pytest.fixture
def clear_config_cache() -> Iterator[None]:
    """Isolate tests that exercise the actual cached configuration accessor."""
    get_global_config.cache_clear()
    yield
    get_global_config.cache_clear()


@pytest.fixture(scope="session", autouse=True)
def qt_offscreen_platform() -> None:
    """Default Qt to a display-free platform for headless tests.

    https://github.com/Ajatt-Tools/lancet/blob/a306fd1774f2b3a70a0f836bab1135d66f4741f2/tests/conftest.py#L22
    """
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture(scope="session", autouse=True)
def qapp(qt_offscreen_platform: None) -> QApplication:
    """Ensure widget tests have a QApplication with a nonempty argument list.

    https://github.com/Ajatt-Tools/lancet/blob/a306fd1774f2b3a70a0f836bab1135d66f4741f2/tests/conftest.py#L28
    """
    match instance := QApplication.instance():
        case None:
            return QApplication(["pytest"])
        case QApplication():
            return instance
        case _:
            raise RuntimeError("A QCoreApplication already exists. Widget tests require QApplication")


@pytest.fixture(autouse=True)
def no_qt_callback_errors() -> Iterator[None]:
    """Fail tests when Qt sends a Python callback exception to sys.excepthook."""
    errors: list[str] = []
    # An independent patch context keeps this guard active through test monkeypatch cleanup.
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(
            sys,
            "excepthook",
            lambda kind, error, tb: errors.append("".join(traceback.format_exception(kind, error, tb))),
        )
        yield
        if errors:
            pytest.fail("Unhandled Qt callback exceptions:\n" + "\n".join(errors), pytrace=False)


@pytest.fixture
def anki_collection(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Collection]:
    """Open an isolated real collection for persistence and Undo/Redo tests."""
    collection = Collection(str(tmp_path / "collection.anki2"))
    # Anki's standalone text helpers need the same backend as this collection.
    monkeypatch.setattr(anki.lang, "current_i18n", collection._backend)
    try:
        yield collection
    finally:
        collection.close()


@beartype
def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Runtime-check collected tests after Pytest has rewritten their imports.
    https://github.com/beartype/beartype
    https://github.com/Ajatt-Tools/lancet/blob/a306fd1774f2b3a70a0f836bab1135d66f4741f2/tests/conftest.py#L11
    """
    for item in items:
        if isinstance(item, pytest.Function):
            item.obj = beartype(item.obj)
