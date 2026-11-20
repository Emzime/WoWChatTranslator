"""Application icon, drawn in code (used for the tray and the .exe)."""

from PIL import Image, ImageDraw


def make_icon_image(size=64):
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    s = size / 64
    draw.rounded_rectangle((4 * s, 6 * s, 60 * s, 46 * s), radius=10 * s, fill=(16, 22, 30, 255), outline=(51, 204, 255, 255), width=int(3 * s))
    draw.polygon([(16 * s, 44 * s), (14 * s, 58 * s), (30 * s, 45 * s)], fill=(51, 204, 255, 255))
    # "WCT": WoW Chat Translator.
    font_size = int(17 * s)
    letters = (("W", (255, 255, 255, 255)), ("C", (51, 204, 255, 255)), ("T", (255, 210, 80, 255)))
    bold = max(1, round(0.8 * s))   # thickened strokes: readable down to 16 px
    widths = [draw.textlength(letter, font_size=font_size) + bold for letter, _ in letters]
    x = 32 * s - sum(widths) / 2
    for (letter, color), width in zip(letters, widths):
        draw.text((x, 26 * s), letter, fill=color, font_size=font_size, anchor="lm",
                  stroke_width=bold, stroke_fill=color)
        x += width
    return image
