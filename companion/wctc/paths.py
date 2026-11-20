import os
import sys
from pathlib import Path

from . import APP_NAME


def resource_dir() -> Path:
    """Folder holding bundled resources (PyInstaller temp dir or the source tree)."""
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


def addon_source_dir() -> Path:
    bundled = resource_dir() / "addon" / "WoWChatTranslator"
    if bundled.is_dir():
        return bundled
    # Source tree layout: <repo>/addon/WoWChatTranslator
    return resource_dir().parent / "addon" / "WoWChatTranslator"


def models_dir() -> Path:
    """Translation models: the "models" folder next to the .exe (kept out of the .exe, which
    would otherwise unpack ~500 MB at every launch), or the source tree's."""
    override = os.environ.get("WCT_MODELS")
    if override:
        return Path(override)
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / "models"
    return resource_dir() / "models"


def config_dir() -> Path:
    base = os.environ.get("APPDATA") or os.path.join(os.path.expanduser("~"), ".config")
    path = Path(base) / APP_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path
