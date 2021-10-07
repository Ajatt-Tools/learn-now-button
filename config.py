from aqt import mw


def get_config() -> dict:
    return mw.addonManager.getConfig(__name__)


def write_config() -> None:
    return mw.addonManager.writeConfig(__name__, config)


config = get_config()
