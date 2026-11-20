"""Text smileys (":D", "<3", "^^"...) shown as colour emoji pictures in the overlay.

Tk cannot draw colour emoji itself: each one is drawn once with the system's emoji font into a
small picture, then inserted in the text. Without an emoji font the smiley stays as typed.
"""

import logging
import os
import re
import sys
from pathlib import Path

log = logging.getLogger(__name__)

SMILEYS = {
    ":)": "🙂", ":-)": "🙂", "=)": "🙂", "(:": "🙂",
    ":D": "😄", ":-D": "😄", "=D": "😄", "xD": "😆", "XD": "😆", "xDD": "😆", "XDD": "😆",
    ":(": "🙁", ":-(": "🙁", ":c": "🙁", ":C": "🙁", "=(": "🙁",
    ";)": "😉", ";-)": "😉",
    ":p": "😛", ":P": "😛", ":-p": "😛", ":-P": "😛", ";p": "😜", ";P": "😜",
    ":o": "😮", ":O": "😮", ":-o": "😮", ":-O": "😮",
    ":/": "😕", ":-/": "😕", ":|": "😐",
    ":3": "😺", "<3": "❤️", "^^": "😊", "^_^": "😊",
    "-_-": "😑", "o_O": "😳", "O_o": "😳", "o_o": "😳", "O_O": "😳",
    ":*": "😘", ";*": "😘",
}
# Longest first, and never inside a word or a link/URL ("http://", "x:3").
SMILEY_RE = re.compile(r"(?<![\w:/])(?:" + "|".join(re.escape(s) for s in sorted(SMILEYS, key=len, reverse=True))
                       + r")(?![\w/])")

_CANDIDATE_FONTS = [
    Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts" / "seguiemj.ttf",      # Segoe UI Emoji
    Path("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"),
    Path("/System/Library/Fonts/Apple Color Emoji.ttc"),
]
_BITMAP_FONT_SIZE = 109   # Noto Color Emoji only exists at this size (then scaled down)


class EmojiRenderer:
    """Draws emoji pictures (PIL images) at a given pixel height, cached."""

    def __init__(self):
        self._font_path = next((p for p in _CANDIDATE_FONTS if p.is_file()), None)
        self._fonts = {}
        self._cache = {}
        if self._font_path is None:
            log.info("No colour emoji font found: smileys stay as text")

    @property
    def available(self):
        return self._font_path is not None

    def _font(self, size):
        from PIL import ImageFont
        if size not in self._fonts:
            try:
                self._fonts[size] = ImageFont.truetype(str(self._font_path), size)
            except OSError:
                # Bitmap colour fonts (Noto) only load at their own size.
                self._fonts[size] = ImageFont.truetype(str(self._font_path), _BITMAP_FONT_SIZE)
        return self._fonts[size]

    def image(self, emoji, height):
        """PIL RGBA image of the emoji, `height` pixels high, or None."""
        key = (emoji, height)
        if key in self._cache:
            return self._cache[key]
        result = None
        if self.available:
            try:
                from PIL import Image, ImageDraw
                font = self._font(max(8, height))
                left, top, right, bottom = font.getbbox(emoji, embedded_color=True) \
                    if "embedded_color" in font.getbbox.__code__.co_varnames else font.getbbox(emoji)
                canvas = Image.new("RGBA", (max(1, right - left) + 4, max(1, bottom - top) + 4), (0, 0, 0, 0))
                ImageDraw.Draw(canvas).text((2 - left, 2 - top), emoji, font=font, embedded_color=True)
                box = canvas.getbbox()
                if box:
                    canvas = canvas.crop(box)
                    width = max(1, round(canvas.width * height / canvas.height))
                    result = canvas.resize((width, height), Image.LANCZOS)
            except Exception:
                log.exception("Cannot draw emoji %r", emoji)
        self._cache[key] = result
        return result


def emoji_for(smiley):
    return SMILEYS.get(smiley)


if __name__ == "__main__":   # quick visual check: python -m wctc.emoji out.png
    renderer = EmojiRenderer()
    from PIL import Image
    pictures = [renderer.image(e, 32) for e in dict.fromkeys(SMILEYS.values())]
    pictures = [p for p in pictures if p]
    sheet = Image.new("RGBA", (sum(p.width + 4 for p in pictures) or 1, 36), (20, 24, 30, 255))
    x = 2
    for p in pictures:
        sheet.paste(p, (x, 2), p)
        x += p.width + 4
    sheet.save(sys.argv[1] if len(sys.argv) > 1 else "emoji.png")
