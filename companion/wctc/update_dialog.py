"""Window offering a new version (nothing is downloaded until the player chooses), then showing
its download. Same look as the model window."""

import tkinter as tk

from .options import ACCENT, BG, BORDER, FIELD, GOLD, MUTED, PANEL, TEXT, Button, _font, init_scale, px, title_bar

WIDTH = 460


class UpdateDialog:
    def __init__(self, root, texts, version, current, on_now=None, on_exit=None, on_quit=None):
        """Offers the update (on_now / on_exit: the player's choice), or, with neither, opens
        straight on the download (update chosen for when the companion closes). on_quit: the
        companion is closing; its second choice quits without updating."""
        self._texts = texts
        self._on_quit = on_quit
        self._version = version.lstrip("vV")          # "v1.0.9" -> "1.0.9", as the current one
        self._on_now, self._on_exit = on_now, on_exit
        init_scale(root)
        self.window = tk.Toplevel(root, bg=BORDER)
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        body = tk.Frame(self.window, bg=BG)
        body.pack(fill="both", expand=True, padx=1, pady=1)
        title_bar(body, self.window, texts("upd_title"), self._quit if on_quit else self.close)
        self._frame = tk.Frame(body, bg=PANEL, padx=px(18), pady=px(16))
        self._frame.pack(fill="both", expand=True)
        self._bar = self._progress_label = self._status = None
        if on_now or on_exit:
            self._show_choice(current)
        else:
            self.show_download(texts("upd_exit_download", version=self._version), closable=False)
        self._center()

    def _label(self, text, color=TEXT, size=10, weight="normal"):
        return tk.Label(self._frame, text=text, bg=PANEL, fg=color, font=_font(size, weight), justify="left",
                        anchor="w", wraplength=px(WIDTH))

    def _show_choice(self, current):
        t = self._texts
        self._label(t("upd_text", version=self._version, current=current), GOLD, 10, "bold").pack(fill="x", pady=(0, px(14)))
        if self._on_quit:
            Button(self._frame, t("upd_now_quit"), self._now_closing, primary=True).pack(fill="x")
            Button(self._frame, t("upd_quit_only"), self._quit).pack(fill="x", pady=(px(8), 0))
            return
        Button(self._frame, t("upd_now"), self._now, primary=True).pack(fill="x")
        Button(self._frame, t("upd_at_exit"), self._at_exit).pack(fill="x", pady=(px(8), 0))
        Button(self._frame, t("upd_later"), self.close).pack(anchor="e", pady=(px(14), 0))

    def _clear(self):
        for child in self._frame.winfo_children():
            child.destroy()

    def _now(self):
        self.show_download(self._texts("upd_download", version=self._version))
        self._on_now()

    def _now_closing(self):
        self.show_download(self._texts("upd_exit_download", version=self._version), closable=False)
        self._on_now()

    def _quit(self):
        self.close()
        self._on_quit()

    def _at_exit(self):
        self.close()
        self._on_exit()

    def show_download(self, title, closable=True):
        self._clear()
        self._label(title).pack(fill="x")
        self._bar = tk.Canvas(self._frame, width=px(WIDTH), height=px(10), bg=FIELD, highlightthickness=0)
        self._bar.pack(fill="x", pady=(px(12), px(4)))
        self._progress_label = self._label("", MUTED, 9)
        self._progress_label.pack(fill="x")
        self._status = self._label("", TEXT, 10)
        self._status.pack(fill="x", pady=(px(8), 0))
        if closable:
            Button(self._frame, self._texts("dl_hide"), self.close).pack(anchor="e", pady=(px(14), 0))
        self._center()

    def set_progress(self, done, expected):
        if not self._bar or not self.alive():
            return
        self._bar.update_idletasks()
        self._bar.delete("all")
        if expected:
            width = int(self._bar.winfo_width() * min(done, expected) / expected)
            self._bar.create_rectangle(0, 0, width, px(10), fill=ACCENT, width=0)
        self._progress_label.configure(text=self._texts("dl_progress", done=done // 2 ** 20,
                                                        total=expected // 2 ** 20 if expected else "?"))

    def set_status(self, text, error=False):
        if self._status and self.alive():
            self._status.configure(text=text, fg="#ff7b72" if error else GOLD)

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
