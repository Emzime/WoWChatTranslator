"""Window shown when no translation model is installed yet (first launch): the player picks the
model to download (nothing is downloaded until he clicks), then follows the download. Same
look as the Options window."""

import tkinter as tk

from . import models
from .options import ACCENT, BG, BORDER, FIELD, GOLD, MUTED, PANEL, TEXT, Button, _font, init_scale, px, title_bar

WIDTH = 460


class ModelDialog:
    def __init__(self, root, texts, on_choose):
        self._texts = texts
        self._on_choose = on_choose          # callable(model key)
        init_scale(root)
        self.window = tk.Toplevel(root, bg=BORDER)
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        body = tk.Frame(self.window, bg=BG)
        body.pack(fill="both", expand=True, padx=1, pady=1)
        title_bar(body, self.window, texts("first_run_title"), self.close)
        self._frame = tk.Frame(body, bg=PANEL, padx=px(18), pady=px(16))
        self._frame.pack(fill="both", expand=True)
        self._bar = None
        self._progress_label = None
        self._show_choice()
        self._center()

    def _label(self, text, color=TEXT, size=10, weight="normal"):
        return tk.Label(self._frame, text=text, bg=PANEL, fg=color, font=_font(size, weight), justify="left",
                        anchor="w", wraplength=px(WIDTH))

    def _show_choice(self):
        t = self._texts
        recommended = models.recommended_model()
        self._label(t("first_run_text")).pack(fill="x")
        self._label(t("first_run_recommended", name=t(f"name_{recommended}")), GOLD, 10, "bold").pack(fill="x", pady=(px(12), px(10)))
        buttons = tk.Frame(self._frame, bg=PANEL)
        buttons.pack(fill="x")
        for key in ("standard", "quality"):
            label = t(f"first_run_{key}", size=models.MODELS[key]["size_mb"])
            if key == recommended:
                label = "★ " + label
            Button(buttons, label, lambda k=key: self._choose(k), primary=key == recommended).pack(
                side="left", expand=True, fill="x", padx=(px(0), px(6)) if key == "standard" else (px(6), 0))
        Button(self._frame, t("first_run_later"), self.close).pack(anchor="e", pady=(px(14), px(0)))

    def _choose(self, key):
        for child in self._frame.winfo_children():
            child.destroy()
        t = self._texts
        self._label(t("dl_started", name=t(f"name_{key}"), size=models.MODELS[key]["size_mb"])).pack(fill="x")
        self._bar = tk.Canvas(self._frame, width=px(WIDTH), height=px(10), bg=FIELD, highlightthickness=0)
        self._bar.pack(fill="x", pady=(px(12), px(4)))
        self._progress_label = self._label("", MUTED, 9)
        self._progress_label.pack(fill="x")
        Button(self._frame, t("dl_hide"), self.close).pack(anchor="e", pady=(px(14), px(0)))
        self._center()
        self._on_choose(key)

    def set_progress(self, done, expected):
        if not self._bar or not self.alive():
            return
        self._bar.delete("all")
        if expected:
            self._bar.create_rectangle(0, 0, int(self._bar.winfo_width() * done / expected), px(10), fill=ACCENT, width=0)
        self._progress_label.configure(text=self._texts("dl_progress", done=done // 2 ** 20,
                                                        total=expected // 2 ** 20 if expected else "?"))

    def _center(self):
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() - self.window.winfo_reqwidth()) // 2
        y = (self.window.winfo_screenheight() - self.window.winfo_reqheight()) // 3
        self.window.geometry(f"+{x}+{y}")

    def close(self):
        try:
            self.window.destroy()
        except tk.TclError:
            pass

    def alive(self):
        try:
            return bool(self.window.winfo_exists())
        except tk.TclError:
            return False
