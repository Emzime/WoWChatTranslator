"""Screenshots of the companion's windows for the README and the wiki, in the language of
the page that shows them (docs/images/<language>/*.png).

Usage: python build/readme_screenshots.py [language ...] (default: fr en). The in-game shot
of the overlay (overlay.png) is taken in the game with the companion's screenshot command.
"""
import sys, time, os, tempfile
from pathlib import Path
os.environ["APPDATA"] = tempfile.mkdtemp()
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import tkinter as tk
from PIL import ImageGrab
from wctc.i18n import Texts
from wctc.config import Config
from wctc import options, models, model_dialog
langs = sys.argv[1:] or ['fr', 'en']
if len(langs) > 1:          # one language per run (a fresh Tk and a fresh scale each time)
    import subprocess
    for one in langs:
        subprocess.run([sys.executable, __file__, one], check=True)
    sys.exit(0)
lang = langs[0]; out = Path(__file__).resolve().parents[2] / 'docs' / 'images' / lang
out.mkdir(parents=True, exist_ok=True)
# Pretend the Standard model is installed and the game runs, as for a player.
models.model_path = lambda key: "x" if key == "standard" else None
models.installed_models = lambda: ["standard"]
root = tk.Tk(); root.withdraw()
t = Texts(lambda: lang)
def pump(n=20):
    for _ in range(n): root.update(); time.sleep(0.02)
def grab(win, name, pad=0):
    pump(); win.update_idletasks()
    x, y, w, h = win.winfo_rootx(), win.winfo_rooty(), win.winfo_width(), win.winfo_height()
    ImageGrab.grab(bbox=(x - pad, y - pad, x + w + pad, y + h + pad)).save(f"{out}/{name}.png")
cfg = Config()
w = options.OptionsWindow(root, cfg, t, lambda *a: None, game_running=lambda: True)
w.window.geometry("+20+20")
w.notice("translation", t("glossary_reloaded", n=12), "ok")
grab(w.window, "options-translation")
# The "?" bubble of "show original message".
for row in w.pages["translation"].winfo_children():
    labels = [c for c in row.winfo_children() if isinstance(c, tk.Label)]
    if labels and labels[0].cget("text") == t("menu_original"):
        q = [c for c in labels if c.cget("text") == "?"][0]
        q.event_generate("<Enter>"); pump(30)
        x, y = w.window.winfo_rootx(), w.window.winfo_rooty()
        ImageGrab.grab(bbox=(x, y, x + w.window.winfo_width() + 120, y + w.window.winfo_height())).save(f"{out}/options-help.png")
        q.event_generate("<Leave>")
w.select(1); grab(w.window, "options-display")
w.select(2); w.notice("general", t("upd_latest", version="1.0.0"), "ok"); grab(w.window, "options-general")
w.close()
d = model_dialog.ModelDialog(root, t, lambda k: None)
d.window.geometry("+20+20"); grab(d.window, "first-launch")
d._choose("standard"); pump(); d.set_progress(240 * 2**20, 600 * 2**20); d.window.geometry("+20+20"); grab(d.window, "model-download")
