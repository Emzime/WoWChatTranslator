"""Small question window with the companion's own look (not a grey Windows box): a message, a
highlighted line, and two buttons."""

import tkinter as tk

from .options import BG, BORDER, GOLD, PANEL, TEXT, Button, _font, init_scale, px, title_bar

WIDTH = 440


class ConfirmDialog:
    def __init__(self, root, title, message, highlight, yes_text, no_text, on_yes):
        init_scale(root)
        self._on_yes = on_yes
        self.window = tk.Toplevel(root, bg=BORDER)
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        body = tk.Frame(self.window, bg=BG)
        body.pack(fill="both", expand=True, padx=1, pady=1)
        title_bar(body, self.window, title, self.close)
        frame = tk.Frame(body, bg=PANEL, padx=px(18), pady=px(16))
        frame.pack(fill="both", expand=True)
        paragraphs = message.split("\n\n")
        for index, paragraph in enumerate(paragraphs):
            if highlight and index == max(1, len(paragraphs) - 1):
                # Just before the question ("Quit anyway?"): what to press in game.
                tk.Label(frame, text=highlight, bg=PANEL, fg=GOLD, font=_font(11, "bold"), anchor="w").pack(
                    fill="x", pady=(0, px(10)))
            tk.Label(frame, text=paragraph, bg=PANEL, fg=TEXT, font=_font(10), justify="left", anchor="w",
                     wraplength=px(WIDTH)).pack(fill="x", pady=(0, px(8)))
        if highlight and len(paragraphs) == 1:
            tk.Label(frame, text=highlight, bg=PANEL, fg=GOLD, font=_font(11, "bold"), anchor="w").pack(
                fill="x", pady=(0, px(10)))
        buttons = tk.Frame(frame, bg=PANEL)
        buttons.pack(fill="x")
        Button(buttons, no_text, self.close).pack(side="right")
        Button(buttons, yes_text, self._yes, primary=True).pack(side="right", padx=(0, px(8)))
        self.window.bind("<Escape>", lambda _: self.close())
        self._center()
        self.window.focus_force()

    def _yes(self):
        self.close()
        self._on_yes()

    def _center(self):
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() - self.window.winfo_reqwidth()) // 2
        y = (self.window.winfo_screenheight() - self.window.winfo_reqheight()) // 3
        self.window.geometry(f"+{x}+{y}")

    def close(self):
        try:
            self.window.destroy()
        except tk.TclError:
            pass  # window already closed

    def alive(self):
        try:
            return bool(self.window.winfo_exists())
        except tk.TclError:
            return False


def key_label(binding):
    """"ALT-F6" (the game's notation) -> "Alt+F6"; "" -> ""."""
    names = {"ALT": "Alt", "CTRL": "Ctrl", "SHIFT": "Shift", "META": "Cmd"}
    parts = [p for p in binding.split("-") if p] if binding else []
    return "+".join(names.get(p.upper(), p) for p in parts)
