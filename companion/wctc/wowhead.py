"""Wowhead tooltips for chat links, in the player's language.

Uses Wowhead's public tooltip service (the one behind its embeddable tooltips):
https://nether.wowhead.com/tooltip/{type}/{id}?dataEnv=16&locale=2
dataEnv 16 is the WoW Forever database. Results are cached for the session.
"""

import html.parser
import json
import logging
import queue
import threading
import urllib.request

from .updater import _ssl_context

log = logging.getLogger(__name__)

URL = "https://nether.wowhead.com/tooltip/{kind}/{id}?dataEnv={env}&locale={locale}"
DATA_ENV_FOREVER = 16
LOCALES = {"en": 0, "fr": 2, "de": 3, "es": 6, "ru": 8, "pt": 9, "it": 10}
TIMEOUT_S = 8

QUALITY_COLORS = {
    "q": "#ffd100", "q0": "#9d9d9d", "q1": "#ffffff", "q2": "#1eff00", "q3": "#0070dd",
    "q4": "#a335ee", "q5": "#ff8000", "q6": "#e5cc80", "q7": "#00ccff", "q8": "#00ccff",
    "q9": "#71d5ff", "q10": "#ff4040",
    # Money ("Sell price: 25 53 55"): coloured like the coins in game.
    "moneygold": "#ffd100", "moneysilver": "#c7c7cf", "moneycopper": "#eda55f",
}
DEFAULT_COLOR = "#ffffff"


class _TooltipHtml(html.parser.HTMLParser):
    """Turns Wowhead tooltip HTML into lines of (text, colour) segments."""

    BREAKS = {"br", "div", "table", "tr", "p"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lines = [[]]
        self._colors = []      # stack of (tag, colour or None)
        self._cells = 0

    def _color(self):
        for _, color in reversed(self._colors):
            if color:
                return color
        return DEFAULT_COLOR

    def _newline(self):
        if self.lines[-1]:
            self.lines.append([])

    def handle_starttag(self, tag, attrs):
        if tag in self.BREAKS:
            self._newline()
        if tag == "tr":
            self._cells = 0
        if tag in ("td", "th"):
            self._cells += 1
            if self._cells > 1 and self.lines[-1]:
                # Right-hand cell ("Head ... Plate"): keep it on the same line.
                self.lines[-1].append(("    ", DEFAULT_COLOR))
        if tag in ("br",):
            return
        classes = (dict(attrs).get("class") or "").split()
        color = next((QUALITY_COLORS[c] for c in classes if c in QUALITY_COLORS), None)
        self._colors.append((tag, color))

    def handle_startendtag(self, tag, attrs):
        if tag in self.BREAKS:
            self._newline()

    def handle_endtag(self, tag):
        for index in range(len(self._colors) - 1, -1, -1):
            if self._colors[index][0] == tag:
                del self._colors[index:]
                break
        if tag in ("div", "table", "p"):
            self._newline()

    def handle_data(self, data):
        if not data.strip():
            text = " " if self.lines[-1] else ""
        else:
            text = " ".join(data.split())
            if data[:1].isspace() and self.lines[-1]:
                text = " " + text
            if data[-1:].isspace():
                text += " "
        if text:
            self.lines[-1].append((text, self._color()))


def html_to_lines(markup):
    parser = _TooltipHtml()
    parser.feed(markup or "")
    parser.close()
    lines = []
    for segments in parser.lines:
        merged = []
        for text, color in segments:
            if merged and merged[-1][1] == color:
                merged[-1] = (merged[-1][0] + text, color)
            else:
                merged.append((text, color))
        if merged and "".join(t for t, _ in merged).strip():
            merged[0] = (merged[0][0].lstrip(), merged[0][1])
            merged[-1] = (merged[-1][0].rstrip(), merged[-1][1])
            lines.append(merged)
    return lines


def fetch(kind, ident, lang):
    url = URL.format(kind=kind, id=ident, env=DATA_ENV_FOREVER, locale=LOCALES.get(lang, 0))
    request = urllib.request.Request(url, headers={"User-Agent": "WoWChatTranslatorCompagnion"})
    with urllib.request.urlopen(request, timeout=TIMEOUT_S, context=_ssl_context()) as response:
        data = json.loads(response.read().decode("utf-8"))
    lines = html_to_lines(data.get("tooltip", ""))
    if not lines and data.get("name"):
        lines = [[(data["name"], DEFAULT_COLOR)]]
    return lines


class TooltipCache:
    """Fetches tooltips in a background thread; results are polled from the Tk thread."""

    def __init__(self):
        self._cache = {}
        self._pending = set()
        self._requests = queue.Queue()
        self._thread = None

    def get(self, kind, ident, lang):
        """Tooltip lines, [] if unavailable, or None while it is being fetched."""
        key = (kind, ident, lang)
        if key in self._cache:
            return self._cache[key]
        if key not in self._pending:
            self._pending.add(key)
            self._requests.put(key)
            if not self._thread or not self._thread.is_alive():
                self._thread = threading.Thread(target=self._worker, name="wowhead", daemon=True)
                self._thread.start()
        return None

    def _worker(self):
        while True:
            try:
                key = self._requests.get(timeout=30)
            except queue.Empty:
                return
            try:
                self._cache[key] = fetch(*key)
            except Exception as exc:
                log.info("Wowhead tooltip %s unavailable: %s", key, exc)
                self._cache[key] = []
            self._pending.discard(key)
