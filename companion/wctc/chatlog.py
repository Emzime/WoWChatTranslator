"""Chat lines missed while the game was out of sight, read back from the game's own chat log.

The bridge only sees the addon's grid while the game is on screen: lines sent while the player
is on the desktop never reach the companion. When the game writes its chat log (/chatlog, file
Logs/WoWChatLog.txt), those lines are read back from it and translated late. Without the log,
nothing can be recovered and the gap is only noted.
"""

import logging
import re
import time
from collections import deque
from datetime import datetime, timedelta
from pathlib import Path

from .chatparser import ChatLine, parse_links, strip_escapes

log = logging.getLogger(__name__)

LOG_NAME = "WoWChatLog.txt"
TAIL_BYTES = 512 * 1024      # the gap is recent: its lines are at the end of the file
EDGE_S = 2.0                 # lines this close to the gap's ends are kept (clocks, buffering)

# "11/19 10:59:06.037  [1. Général] Usøpp Mugiwara : quelqu'un ?"
_LINE_RE = re.compile(r"^(\d{1,2})/(\d{1,2}) (\d\d):(\d\d):(\d\d)\.(\d{3})  (.*)$")
_CHANNEL_RE = re.compile(r"^(\[[^\]]+\]) (.+?)\s?: (.*)$")      # French puts a (no-break) space
# "Bob chuchote : salut", "Bob whispers: hi". Not "dit" / "crie" (say, yell): the log mixes them
# with the NPCs' lines, which the addon never sends.
_WHISPER_RE = re.compile(r"^(.+?) (chuchote|whispers|flüstert|susurra|sussurra|шепчет)\s?: (.*)$")
_LABEL_KINDS = [
    (re.compile(r"^\[\d+\. "), "channel"),
    (re.compile(r"offic|offiz", re.I), "officer"),
    (re.compile(r"guil|gild|herman|гильд", re.I), "guild"),
    (re.compile(r"raid|рейд", re.I), "raid"),
    (re.compile(r"group|party|grupp|grupo|групп", re.I), "party"),
    (re.compile(r"instance|bataille|battleground|schlachtfeld|campo|поле", re.I), "instance"),
]


def parse_line(raw, year):
    """(datetime, ChatLine) for a player's message of the log (channels, guild, group, raid,
    whispers), None for anything else (crafting, loot, system and NPC messages)."""
    match = _LINE_RE.match(raw.rstrip("\r\n"))
    if not match:
        return None
    month, day, hour, minute, second, ms, body = match.groups()
    try:
        when = datetime(year, int(month), int(day), int(hour), int(minute), int(second), int(ms) * 1000)
    except ValueError:
        return None
    channel = _CHANNEL_RE.match(body)
    if channel:
        label, speaker, text = channel.groups()
        kind = next((k for pattern, k in _LABEL_KINDS if pattern.search(label)), "channel")
        prefix = f"{label} {speaker}"
    else:
        whisper = _WHISPER_RE.match(body)
        if not whisper:
            return None
        speaker, verb, text = whisper.groups()
        kind = "whisper"
        prefix = f"{speaker} {verb}"
    text = strip_escapes(text).strip()
    if not text:
        return None
    return when, ChatLine(raw, when.strftime("%H:%M"), strip_escapes(prefix).strip(), speaker.strip(),
                          text, kind, parse_links(text))


class ChatLogRecovery:
    """Remembers the lines the bridge delivered, and reads back from the chat log the ones of a
    gap that it did not."""

    def __init__(self, folders):
        self._folders = list(folders)            # game folders whose Logs/ may hold the log
        self._recent = deque(maxlen=400)         # (speaker, text) delivered by the bridge

    def delivered(self, lines):
        for line in lines:
            self._recent.append(_key(line))

    def log_file(self):
        """The chat log written most recently, or None (the game does not log the chat)."""
        files = [Path(f) / "Logs" / LOG_NAME for f in self._folders]
        files = [f for f in files if f.is_file()]
        return max(files, key=lambda f: f.stat().st_mtime) if files else None

    def logging_since(self, start):
        """True if the game wrote its chat log during the gap (logging is on)."""
        path = self.log_file()
        return bool(path) and path.stat().st_mtime >= start - EDGE_S

    def missed_lines(self, start, end):
        """Lines of the log between two wall-clock times that the bridge did not deliver."""
        path = self.log_file()
        if not path:
            return []
        with open(path, "rb") as handle:
            size = handle.seek(0, 2)
            handle.seek(max(0, size - TAIL_BYTES))
            data = handle.read().decode("utf-8", errors="replace")
        now = datetime.now()
        first, last = datetime.fromtimestamp(start - EDGE_S), datetime.fromtimestamp(end + EDGE_S)
        known = set(self._recent)
        found = []
        for raw in data.splitlines():
            parsed = parse_line(raw, now.year)
            if not parsed:
                continue
            when, line = parsed
            if when > now + timedelta(days=1):           # December line read in January
                when = when.replace(year=now.year - 1)
            if first <= when <= last and _key(line) not in known:
                known.add(_key(line))
                found.append(line)
        self.delivered(found)
        return found


def _key(line):
    return line.speaker.split("-")[0].strip().lower(), " ".join(line.text.split()).lower()


def wall_clock():
    return time.time()
