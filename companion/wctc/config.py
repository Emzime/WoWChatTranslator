import json
import logging
import threading

from .paths import config_dir

log = logging.getLogger(__name__)

DEFAULTS = {
    "enabled": True,
    "target_lang": None,          # None = auto (game locale, then Windows locale)
    "wow_root": None,             # None = auto-detect
    "show_original": False,       # show the original message under its translation
    "opacity": 0.9,
    "fade_after": 0,              # seconds without activity before the text fades out (0: never)
    "font_size": 11,
    "class_colors": True,         # sender's name in his class colour, like the game chat
    "max_lines": 200,
    "overlay_rect": None,         # user-adjusted rect, fractions of the game client area
    "auto_update": True,
    "notifications": True,        # Windows notifications near the clock
    "translation_log": False,
    "chat_log": None,             # the game's chat log (/chatlog): None = left to the player     # each chat line and what became of it, in the log (to report errors)
    "launch_code": None,          # Battle.net launch code override (auto: WoWF for Forever...)
    "model": "auto",              # translation model: auto (from this PC), standard, quality
    "autostart": True,           # installs the addon before WoW starts, avoiding a /reload
}


class Config:
    def __init__(self):
        self._path = config_dir() / "config.json"
        self._lock = threading.Lock()
        self._data = dict(DEFAULTS)
        self.load()

    def load(self):
        try:
            with open(self._path, encoding="utf-8") as fh:
                stored = json.load(fh)
            self._data.update({k: v for k, v in stored.items() if k in DEFAULTS})
        except FileNotFoundError:
            pass
        except (OSError, ValueError):
            log.exception("Invalid config file, using defaults")

    def save(self):
        with self._lock:
            tmp = self._path.with_suffix(".tmp")
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(self._data, fh, indent=2, ensure_ascii=False)
            tmp.replace(self._path)

    def __getitem__(self, key):
        return self._data[key]

    def get(self, key, default=None):
        return self._data.get(key, default)

    def __setitem__(self, key, value):
        self._data[key] = value
        self.save()
