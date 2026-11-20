"""Screenshots of the game as the player sees it: with the overlay, without the bridge grid."""

import sys
import time

from . import bridge, winutil


def screenshots_dir():
    """Pictures\\WoWChatTranslator (the user's Pictures folder, wherever Windows put it)."""
    from pathlib import Path
    if sys.platform == "win32":
        import ctypes.wintypes
        buffer = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        CSIDL_MYPICTURES = 0x27
        if ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_MYPICTURES, None, 0, buffer) == 0:
            return Path(buffer.value) / "WoWChatTranslator"
    return Path.home() / "Pictures" / "WoWChatTranslator"


def capture_with_overlay(client, excluded_hwnds):
    """GDI capture of the game area. If the overlay is missing from it (Windows applies the
    capture exclusion to GDI too), the exclusion is lifted for the time of the shot."""
    import mss
    import numpy as np

    def grab():
        x, y, w, h = client
        with mss.mss() as sct:
            shot = np.asarray(sct.grab({"left": x, "top": y, "width": w, "height": h}))
        return shot[:, :, 2::-1].copy()   # BGRA -> RGB

    img = grab()
    if bridge.find_grid(img.astype(np.int16)) is None:
        return img
    for hwnd in excluded_hwnds:
        winutil.exclude_from_capture(hwnd, False)
    try:
        time.sleep(0.05)   # let the compositor draw the windows into the capture again
        img = grab()
    finally:
        for hwnd in excluded_hwnds:
            winutil.exclude_from_capture(hwnd, True)
    return img
