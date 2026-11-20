"""Generates the .ico of the executable and its splash screen from the tray icon drawing."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from wctc.icon import make_icon_image  # noqa: E402

output = Path(__file__).resolve().parent / "icon.ico"
make_icon_image(256).save(output, sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
print(output)

# Splash screen shown while the .exe starts.
from PIL import Image, ImageDraw  # noqa: E402

splash = Image.new("RGB", (360, 120), (16, 22, 30))
draw = ImageDraw.Draw(splash)
draw.rectangle((0, 0, 359, 119), outline=(51, 204, 255), width=2)
icon = make_icon_image(88)
splash.paste(icon, (16, 16), icon)
draw.text((118, 42), "WoWChatTranslator", fill=(255, 255, 255), font_size=22)
draw.text((118, 72), "Compagnion", fill=(255, 210, 80), font_size=16)
splash_path = output.with_name("splash.png")
splash.save(splash_path)
print(splash_path)
