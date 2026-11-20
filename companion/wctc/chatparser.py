"""Chat line model and WoW escape-sequence cleanup."""

import re
from dataclasses import dataclass, field

# WoW UI escape sequences (colors, hyperlinks, textures, Battle.net names...).
_ESCAPE_RES = [
    # Player links keep the bare name: |Hplayer:Bob-Hyjal:12|h[Bob-Hyjal]|h -> Bob-Hyjal
    (re.compile(r"\|H(?:player|BNplayer|playerGM)[^|]*\|h\[([^\]]*)\]\|h"), r"\1"),
    (re.compile(r"\|c[0-9a-fA-F]{8}"), ""),
    (re.compile(r"\|cn[A-Za-z0-9_]+:"), ""),
    (re.compile(r"\|r"), ""),
    (re.compile(r"\|H[^|]*\|h"), ""),
    (re.compile(r"\|h"), ""),
    (re.compile(r"\|T[^|]*\|t"), ""),
    (re.compile(r"\|A[^|]*\|a"), ""),
    (re.compile(r"\|K[^|]*\|k"), "?"),
    (re.compile(r"\|\|"), "|"),
]
_RAID_ICON_RE = re.compile(r"\{(?:rt[1-8]|star|circle|diamond|triangle|moon|square|cross|x|skull)\}", re.IGNORECASE)


@dataclass
class ChatLine:
    raw: str
    timestamp: str
    prefix: str        # e.g. "[2. Commerce] Ela Borer" or "Ela Borer dit"
    speaker: str
    text: str          # the part to translate
    kind: str          # say/channel/guild/officer/party/raid/instance/whisper/whisper_out
    links: list = field(default_factory=list)   # [ChatLink] found in the message
    player_class: str = ""                        # "MAGE"... (class colour of the name), "" if unknown

    @property
    def translatable(self):
        return bool(self.text.strip())

    @property
    def separator(self):
        return ": "


@dataclass
class ChatLink:
    kind: str          # Wowhead type: item, spell, quest, achievement, currency
    id: int
    name: str          # text shown between brackets (quests: "[23+] Name", brackets included)
    color: str         # "#rrggbb" (item quality colour) or ""


_LINK_RE = re.compile(
    r"(?:\|c(?:n[A-Za-z0-9_]+:|[0-9a-fA-F]{2}([0-9a-fA-F]{6})))?"
    r"\|H(item|spell|enchant|quest|achievement|currency):(\d+)[^|]*\|h\[(.+?)\]\|h(?:\|r)?"
)
_LINK_TYPES = {"enchant": "spell"}


def parse_links(raw):
    """Links of a raw chat message ("|cff0070dd|Hitem:6948::|h[Pierre de foyer]|h|r")."""
    links = []
    for color, kind, ident, name in _LINK_RE.findall(raw):
        links.append(ChatLink(_LINK_TYPES.get(kind, kind), int(ident), name, f"#{color.lower()}" if color else ""))
    return links


def strip_escapes(text):
    for regex, repl in _ESCAPE_RES:
        text = regex.sub(repl, text)
    return _RAID_ICON_RE.sub("", text)
