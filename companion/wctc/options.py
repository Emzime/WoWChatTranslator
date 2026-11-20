"""Options window: every setting of the companion in one place (the tray menu keeps only what is
used while playing). Drawn in the companion's own colours rather than as a Windows dialog;
every setting has a "?" bubble explaining it, and every button shows what it did."""

import sys
import tkinter as tk

from . import APP_NAME, EXTRA_LANGUAGES, LANGUAGES, WOW_LANGUAGES, __version__, models

FADE_DELAYS = (0, 15, 30, 60, 120, 300)
FONT_SIZES = (9, 10, 11, 12, 13, 14, 16, 18)
MODEL_CHOICES = ("auto", "light", "standard", "quality")
TABS = ("translation", "display", "general")
NOTICE_MS = 8000
STATE_POLL_MS = 1000

# Colours of the overlay and of the WCT icon.
BG = "#0f151c"
PANEL = "#16202b"
FIELD = "#1f2c3a"
FIELD_HOVER = "#2a3b4d"
BORDER = "#2b3c4e"
TEXT = "#e6edf3"
MUTED = "#8b98a5"
DISABLED = "#4f5b68"
DISABLED_BG = "#1b2631"
ACCENT = "#33ccff"
GOLD = "#ffd250"
OK = "#5fd38d"
ERROR = "#ff6b6b"
FONT = "Segoe UI" if sys.platform == "win32" else "DejaVu Sans"


# Size of the windows: larger than Windows' own dialogs, and following the screen's DPI.
TEXT_SCALE = 1.3
UI = TEXT_SCALE


def init_scale(root):
    """Sets the pixel scale from the screen's DPI (fonts in points already follow it)."""
    global UI
    try:
        dpi = root.winfo_fpixels("1i")
    except tk.TclError:
        dpi = 96
    UI = TEXT_SCALE * max(1.0, dpi / 96)


def px(n):
    return int(round(n * UI))


def _font(size=10, weight="normal"):
    return (FONT, int(round(size * TEXT_SCALE)), weight)


class Tooltip:
    """Bubble shown when the mouse rests on a widget. `text` may be a callable (text or None)."""

    def __init__(self, widget, text, delay=250):
        self.widget, self.text, self.delay = widget, text, delay
        self._after = None
        self._tip = None
        widget.bind("<Enter>", self._schedule, add="+")
        widget.bind("<Leave>", self._hide, add="+")
        widget.bind("<ButtonPress>", self._hide, add="+")

    def _schedule(self, _event=None):
        self._cancel()
        self._after = self.widget.after(self.delay, self._show)

    def _cancel(self):
        if self._after:
            self.widget.after_cancel(self._after)
            self._after = None

    def _show(self):
        text = self.text() if callable(self.text) else self.text
        if not text:
            return
        self._tip = tk.Toplevel(self.widget)
        self._tip.overrideredirect(True)
        self._tip.attributes("-topmost", True)
        frame = tk.Frame(self._tip, bg=BG, highlightthickness=1, highlightbackground=ACCENT)
        frame.pack()
        tk.Label(frame, text=text, bg=BG, fg=TEXT, font=_font(9), justify="left", wraplength=px(320),
                 padx=px(10), pady=px(7)).pack()
        self._tip.update_idletasks()
        x = self.widget.winfo_rootx() + self.widget.winfo_width() + 6
        y = self.widget.winfo_rooty() - 4
        if x + self._tip.winfo_reqwidth() > self.widget.winfo_screenwidth():
            x = self.widget.winfo_rootx() - self._tip.winfo_reqwidth() - 6
        self._tip.geometry(f"+{x}+{y}")

    def _hide(self, _event=None):
        self._cancel()
        if self._tip:
            self._tip.destroy()
            self._tip = None


class Button(tk.Label):
    """Flat button; disabled ones explain why in their bubble."""

    def __init__(self, parent, text, command, primary=False, why_disabled=None):
        self._colors = (ACCENT, "#7fdfff", BG) if primary else (FIELD, FIELD_HOVER, TEXT)
        super().__init__(parent, text=text, bg=self._colors[0], fg=self._colors[2], font=_font(9, "bold" if primary else "normal"),
                         padx=px(12), pady=px(5), cursor="hand2")
        self.command = command
        self.enabled = True
        self.bind("<Enter>", lambda _: self.enabled and self.configure(bg=self._colors[1]))
        self.bind("<Leave>", lambda _: self.enabled and self.configure(bg=self._colors[0]))
        self.bind("<ButtonRelease-1>", lambda _: self.enabled and self.command())
        if why_disabled:
            Tooltip(self, lambda: None if self.enabled else why_disabled)

    def set_enabled(self, enabled):
        if enabled == self.enabled:
            return
        self.enabled = enabled
        self.configure(bg=self._colors[0] if enabled else DISABLED_BG, fg=self._colors[2] if enabled else DISABLED,
                       cursor="hand2" if enabled else "arrow")


class Switch(tk.Canvas):
    """On/off switch."""

    def __init__(self, parent, command):
        self.W, self.H = px(40), px(22)
        super().__init__(parent, width=self.W, height=self.H, bg=PANEL, highlightthickness=0, cursor="hand2")
        self.command = command
        self.value = False
        self.bind("<ButtonRelease-1>", lambda _: self.command())
        self._draw()

    def set(self, value):
        if bool(value) != self.value:
            self.value = bool(value)
            self._draw()

    def _draw(self):
        self.delete("all")
        w, h, r = self.W, self.H, self.H / 2
        color = ACCENT if self.value else FIELD
        self.create_oval(1, 1, h - 1, h - 1, fill=color, outline=color)
        self.create_oval(w - h + 1, 1, w - 1, h - 1, fill=color, outline=color)
        self.create_rectangle(r, 1, w - r, h - 1, fill=color, outline=color)
        x = w - h + px(3) if self.value else px(3)
        m = px(3)
        self.create_oval(x, m, x + h - 2 * m, h - m, fill="#ffffff" if self.value else MUTED, outline="")


class Slider(tk.Canvas):
    """Horizontal slider by steps; `command(value)` once the mouse is released."""

    def __init__(self, parent, low, high, step, on_move, command):
        self.W, self.H, self.KNOB = px(170), px(22), px(7)
        super().__init__(parent, width=self.W, height=self.H, bg=PANEL, highlightthickness=0, cursor="hand2")
        self.low, self.high, self.step = low, high, step
        self.on_move, self.command = on_move, command
        self.value = low
        self.bind("<ButtonPress-1>", self._drag)
        self.bind("<B1-Motion>", self._drag)
        self.bind("<ButtonRelease-1>", lambda e: (self._drag(e), self.command(self.value)))
        self._draw()

    def set(self, value):
        self.value = max(self.low, min(self.high, value))
        self._draw()

    def _drag(self, event):
        span = self.W - 2 * self.KNOB
        ratio = min(1.0, max(0.0, (event.x - self.KNOB) / span))
        value = self.low + round(ratio * (self.high - self.low) / self.step) * self.step
        if value != self.value:
            self.value = value
            self._draw()
            self.on_move(value)

    def _draw(self):
        self.delete("all")
        k, mid = self.KNOB, self.H / 2
        x = k + (self.value - self.low) / (self.high - self.low) * (self.W - 2 * k)
        self.create_line(k, mid, self.W - k, mid, fill=FIELD, width=px(4), capstyle="round")
        self.create_line(k, mid, x, mid, fill=ACCENT, width=px(4), capstyle="round")
        self.create_oval(x - k, mid - k, x + k, mid + k, fill="#ffffff", outline=ACCENT, width=2)


class Dropdown(tk.Label):
    """Field that opens a list of choices."""

    def __init__(self, parent, labels, command, width=26):
        super().__init__(parent, bg=FIELD, fg=TEXT, font=_font(10), anchor="w", padx=px(10), pady=px(4), width=width,
                         cursor="hand2")
        self.labels, self.command, self.index = list(labels), command, 0
        self.bind("<Enter>", lambda _: self.configure(bg=FIELD_HOVER))
        self.bind("<Leave>", lambda _: self.configure(bg=FIELD))
        self.bind("<ButtonRelease-1>", self._open)

    def set(self, index):
        self.index = index
        self.configure(text=f"{self.labels[index]}   ▾")

    def _open(self, _event):
        menu = tk.Menu(self, tearoff=0, bg=FIELD, fg=TEXT, activebackground=ACCENT, activeforeground=BG,
                       font=_font(10), bd=0, relief="flat")
        for i, label in enumerate(self.labels):
            menu.add_command(label=("● " if i == self.index else "    ") + label,
                             command=lambda i=i: (self.set(i), self.command(i)))
        menu.tk_popup(self.winfo_rootx(), self.winfo_rooty() + self.winfo_height())


class Choice(tk.Frame):
    """One option of a list (radio): round mark, title, and a green note ("installed")."""

    def __init__(self, parent, command):
        super().__init__(parent, bg=PANEL, cursor="hand2")
        self.mark = tk.Canvas(self, width=px(16), height=px(16), bg=PANEL, highlightthickness=0)
        self.mark.pack(side="left", padx=(px(0), px(8)))
        self.title = tk.Label(self, bg=PANEL, fg=TEXT, font=_font(10))
        self.title.pack(side="left")
        self.note = tk.Label(self, bg=PANEL, fg=OK, font=_font(9))
        self.note.pack(side="left", padx=(px(8), px(0)))
        for widget in (self, self.mark, self.title, self.note):
            widget.bind("<ButtonRelease-1>", lambda _: command())

    def show(self, title, selected, note=""):
        self.title.configure(text=title, fg=TEXT if selected else MUTED)
        self.note.configure(text=note)
        self.mark.delete("all")
        self.mark.create_oval(px(2), px(2), px(14), px(14), outline=ACCENT if selected else MUTED, width=px(2))
        if selected:
            self.mark.create_oval(px(5), px(5), px(11), px(11), fill=ACCENT, outline="")


def title_bar(body, window, subtitle, on_close):
    """The companion's own title bar (icon, name, close cross); the window is moved by it."""
    bar = tk.Frame(body, bg=BG, padx=px(12), pady=px(8))
    bar.pack(fill="x")
    try:
        from PIL import ImageTk
        from .icon import make_icon_image
        bar.icon = ImageTk.PhotoImage(make_icon_image(px(24)))
        tk.Label(bar, image=bar.icon, bg=BG).pack(side="left", padx=(px(0), px(8)))
    except Exception:
        pass
    title = tk.Label(bar, text="WoW Chat Translator", bg=BG, fg=GOLD, font=_font(11, "bold"))
    title.pack(side="left")
    sub = tk.Label(bar, text=f"  {subtitle}", bg=BG, fg=MUTED, font=_font(10))
    sub.pack(side="left")
    close = tk.Label(bar, text="✕", bg=BG, fg=MUTED, font=_font(12), padx=px(6), cursor="hand2")
    close.pack(side="right")
    close.bind("<Enter>", lambda _: close.configure(fg=ERROR))
    close.bind("<Leave>", lambda _: close.configure(fg=MUTED))
    close.bind("<ButtonRelease-1>", lambda _: on_close())
    drag = {}

    def start(event):
        drag["d"] = (event.x_root - window.winfo_x(), event.y_root - window.winfo_y())

    def move(event):
        dx, dy = drag.get("d", (0, 0))
        window.geometry(f"+{event.x_root - dx}+{event.y_root - dy}")

    for widget in (bar, title, sub):
        widget.bind("<ButtonPress-1>", start)
        widget.bind("<B1-Motion>", move)
    return bar


class OptionsWindow:
    def __init__(self, root, config, texts, dispatch, tab=0, game_running=lambda: True, edit_mode=lambda: False):
        """`dispatch(action, *args)` queues the change for the app, like the tray menu."""
        self.config, self.texts, self.dispatch = config, texts, dispatch
        self.game_running, self.edit_mode = game_running, edit_mode
        self._download = None              # (model key, percent) while a model downloads
        self._notice_after = {}
        t = texts

        init_scale(root)
        self.window = tk.Toplevel(root, bg=BORDER)
        self.window.overrideredirect(True)          # our own title bar, in the companion's colours
        self.window.title(f"{APP_NAME} - {t('opt_title')}")
        self.body = tk.Frame(self.window, bg=BG)
        self.body.pack(fill="both", expand=True, padx=1, pady=1)
        self._title_bar()
        self._tab_bar()
        self.pages = {}
        self.notices = {}
        for name, build in zip(TABS, (self._translation_tab, self._display_tab, self._general_tab)):
            page = tk.Frame(self.body, bg=PANEL, padx=px(18), pady=px(14))
            build(page)
            notice = tk.Label(page, text="", bg=PANEL, fg=MUTED, font=_font(9), anchor="w", justify="left",
                              wraplength=px(430))
            notice.pack(side="bottom", fill="x", pady=(px(10), px(0)))
            self.notices[name] = notice
            self.pages[name] = page
        footer = tk.Frame(self.body, bg=BG, padx=px(14), pady=px(10))
        footer.pack(side="bottom", fill="x")
        tk.Label(footer, text=t("opt_version", version=__version__), bg=BG, fg=MUTED, font=_font(9)).pack(side="left")
        Button(footer, t("opt_close"), self.close, primary=True).pack(side="right")
        self.refresh()
        self._fix_size()
        self.select(tab)
        self._poll_state()
        self._place(root)

    # ----- frame ---------------------------------------------------------------------------

    def _title_bar(self):
        title_bar(self.body, self.window, self.texts("opt_title"), self.close)

    def _fix_size(self):
        """Same size for every tab (the window does not jump when changing tab)."""
        width = height = 0
        for page in self.pages.values():
            page.pack(fill="both", expand=True)
            self.window.update_idletasks()
            width = max(width, self.window.winfo_reqwidth())
            height = max(height, self.window.winfo_reqheight())
            page.pack_forget()
        self.window.geometry(f"{max(width, px(480))}x{height}")

    def _tab_bar(self):
        bar = tk.Frame(self.body, bg=BG, padx=px(12))
        bar.pack(fill="x")
        self.tab_labels = []
        for index, name in enumerate(TABS):
            cell = tk.Frame(bar, bg=BG)
            cell.pack(side="left", padx=(px(0), px(4)))
            label = tk.Label(cell, text=self.texts(f"tab_{name}"), bg=BG, fg=MUTED, font=_font(10, "bold"),
                             padx=px(12), pady=px(6), cursor="hand2")
            label.pack()
            line = tk.Frame(cell, bg=BG, height=px(3))
            line.pack(fill="x")
            label.bind("<ButtonRelease-1>", lambda _, i=index: self.select(i))
            self.tab_labels.append((label, line))

    def select(self, index):
        self._tab = index
        for i, (label, line) in enumerate(self.tab_labels):
            label.configure(fg=TEXT if i == index else MUTED)
            line.configure(bg=ACCENT if i == index else BG)
        for i, name in enumerate(TABS):
            page = self.pages.get(name)
            if page is None:
                continue
            if i == index:
                page.pack(fill="both", expand=True)     # between the tabs and the footer
            else:
                page.pack_forget()

    def _row(self, page, label_key, help_key, pady=(0, 12)):
        """A setting line: name, "?" bubble, and a slot on the right for its control."""
        row = tk.Frame(page, bg=PANEL)
        row.pack(fill="x", pady=(px(pady[0]), px(pady[1])))
        tk.Label(row, text=self.texts(label_key), bg=PANEL, fg=TEXT, font=_font(10)).pack(side="left")
        self._help(row, help_key).pack(side="left", padx=(px(6), px(0)))
        return row

    def _help(self, parent, help_key):
        mark = tk.Label(parent, text="?", bg=FIELD, fg=ACCENT, font=_font(8, "bold"), width=2, cursor="question_arrow")
        Tooltip(mark, self.texts(help_key))
        return mark

    # ----- tabs ----------------------------------------------------------------------------

    def _translation_tab(self, page):
        t = self.texts
        row = self._row(page, "menu_enabled", "help_enabled")
        self.enabled = Switch(row, lambda: self.dispatch("toggle", "enabled"))
        self.enabled.pack(side="right")

        row = self._row(page, "menu_lang", "help_lang")
        self._lang_codes = [None, *WOW_LANGUAGES, *EXTRA_LANGUAGES]
        self.lang = Dropdown(row, [t("lang_auto")] + [LANGUAGES[c] for c in self._lang_codes[1:]],
                             lambda i: self.dispatch("set_lang", self._lang_codes[i]))
        self.lang.pack(side="right")

        row = self._row(page, "menu_model", "help_model", pady=(0, 4))
        box = tk.Frame(page, bg=PANEL, padx=px(14))
        box.pack(fill="x", pady=(px(0), px(4)))
        self.model_choices = {key: Choice(box, lambda k=key: self.dispatch("set_model", k)) for key in MODEL_CHOICES}
        for choice in self.model_choices.values():
            choice.pack(anchor="w", pady=px(2))
        self.model_status = tk.Label(page, text="", bg=PANEL, fg=ACCENT, font=_font(9), anchor="w", padx=px(14))
        self.model_status.pack(fill="x", pady=(px(0), px(10)))

        row = self._row(page, "menu_original", "help_original")
        self.show_original = Switch(row, lambda: self.dispatch("toggle", "show_original"))
        self.show_original.pack(side="right")

        row = self._row(page, "menu_glossary_title", "help_glossary", pady=(0, 0))
        Button(row, t("menu_reload_glossary"), lambda: self.dispatch("reload_glossary")).pack(side="right")
        Button(row, t("menu_glossary"), lambda: self.dispatch("open_glossary")).pack(side="right", padx=(px(0), px(6)))

    def _display_tab(self, page):
        row = self._row(page, "menu_opacity", "help_opacity")
        self.opacity_label = tk.Label(row, bg=PANEL, fg=TEXT, font=_font(10), width=5, anchor="e")
        self.opacity_label.pack(side="right")
        self.opacity = Slider(row, 40, 100, 5, lambda v: self.opacity_label.configure(text=f"{v} %"),
                              lambda v: self.dispatch("set", "opacity", v / 100))
        self.opacity.pack(side="right", padx=(px(0), px(6)))

        row = self._row(page, "menu_class_colors", "help_class_colors")
        self.class_colors = Switch(row, lambda: self.dispatch("toggle", "class_colors"))
        self.class_colors.pack(side="right")

        row = self._row(page, "menu_fade", "help_fade")
        self.fade = Dropdown(row, [self._fade_label(v) for v in FADE_DELAYS],
                             lambda i: self.dispatch("set", "fade_after", FADE_DELAYS[i]), width=14)
        self.fade.pack(side="right")

        row = self._row(page, "menu_font", "help_font")
        self.font = Dropdown(row, [str(v) for v in FONT_SIZES],
                             lambda i: self.dispatch("set", "font_size", FONT_SIZES[i]), width=14)
        self.font.pack(side="right")

        need_game = self.texts("need_game")
        row = self._row(page, "menu_edit", "help_edit")
        self.edit_button = Button(row, self.texts("menu_edit_short"), lambda: self.dispatch("toggle_edit"),
                                  why_disabled=need_game)
        self.edit_button.pack(side="right")
        row = self._row(page, "menu_reset", "help_reset")
        self.reset_button = Button(row, self.texts("menu_reset_short"), lambda: self.dispatch("reset_position"),
                                   why_disabled=need_game)
        self.reset_button.pack(side="right")

    def _general_tab(self, page):
        t = self.texts
        row = self._row(page, "menu_autostart", "help_autostart")
        self.autostart = Switch(row, lambda: self.dispatch("toggle_autostart"))
        self.autostart.pack(side="right")
        row = self._row(page, "menu_auto_update", "help_auto_update")
        self.auto_update = Switch(row, lambda: self.dispatch("toggle_auto_update"))
        self.auto_update.pack(side="right")
        row = self._row(page, "menu_notifications", "help_notifications")
        self.notifications = Switch(row, lambda: self.dispatch("toggle", "notifications"))
        self.notifications.pack(side="right")
        row = self._row(page, "menu_updates", "help_updates")
        self.update_button = Button(row, t("menu_updates_short"), self._check_updates)
        self.update_button.pack(side="right")
        row = self._row(page, "menu_translation_log", "help_translation_log")
        self.translation_log = Switch(row, lambda: self.dispatch("toggle", "translation_log"))
        self.translation_log.pack(side="right")
        row = self._row(page, "menu_chat_log", "help_chat_log")
        self.chat_log = Switch(row, lambda: self.dispatch("toggle_chat_log"))
        self.chat_log.pack(side="right")
        row = self._row(page, "menu_logs", "help_logs")
        Button(row, t("menu_logs_short"), lambda: self.dispatch("open_logs")).pack(side="right")

    def _check_updates(self):
        self.update_button.set_enabled(False)          # until the answer arrives
        self.notice("general", self.texts("upd_checking"), "busy")
        self.dispatch("check_updates")

    # ----- state ---------------------------------------------------------------------------

    def refresh(self):
        """Shows the current settings (also called after a change made from the tray menu)."""
        if not self.alive():
            return
        cfg, t = self.config, self.texts
        self.enabled.set(cfg["enabled"])
        self.show_original.set(cfg["show_original"])
        self.class_colors.set(cfg["class_colors"])
        self.autostart.set(cfg["autostart"])
        self.auto_update.set(cfg["auto_update"])
        self.notifications.set(cfg["notifications"])
        self.translation_log.set(cfg["translation_log"])
        self.chat_log.set(bool(cfg.get("chat_log")))
        lang = cfg["target_lang"] if cfg["target_lang"] in LANGUAGES else None
        self.lang.set(self._lang_codes.index(lang))
        chosen = cfg["model"] if cfg["model"] in MODEL_CHOICES else "auto"
        for key, choice in self.model_choices.items():
            installed = key != "auto" and models.model_path(models.files_key(key))
            choice.show(t(f"model_{key}"), key == chosen, f"✓ {t('opt_installed')}" if installed else "")
        if self._download:
            key, percent = self._download
            self.model_status.configure(text=t("opt_downloading", name=t(f"name_{key}"), percent=percent), fg=ACCENT)
        elif not models.installed_models():
            self.model_status.configure(text=t("no_model"), fg=GOLD)
        else:
            self.model_status.configure(text="")
        self.opacity.set(round(float(cfg["opacity"]) * 20) * 5)
        self.opacity_label.configure(text=f"{self.opacity.value} %")
        self.fade.set(FADE_DELAYS.index(cfg["fade_after"]) if cfg["fade_after"] in FADE_DELAYS else 0)
        self.font.set(FONT_SIZES.index(min(FONT_SIZES, key=lambda v: abs(v - int(cfg["font_size"])))))
        self._update_game_buttons()

    def _update_game_buttons(self):
        """Moving the overlay needs the game: its buttons wait for it."""
        running = bool(self.game_running())
        editing = bool(self.edit_mode())
        self.edit_button.set_enabled(running or editing)
        self.reset_button.set_enabled(running and not editing)
        self.edit_button.configure(text=self.texts("edit_done") if editing else self.texts("menu_edit_short"))

    def _poll_state(self):
        if not self.alive():
            return
        self._update_game_buttons()
        self.window.after(STATE_POLL_MS, self._poll_state)

    def notice(self, tab, text, kind="info"):
        """Feedback under the buttons of a tab: info, ok, error, or busy (stays until replaced)."""
        if not self.alive():
            return
        label = self.notices[tab]
        label.configure(text=text, fg={"ok": OK, "error": ERROR, "busy": ACCENT}.get(kind, MUTED))
        if tab in self._notice_after:
            self.window.after_cancel(self._notice_after.pop(tab))
        if kind != "busy":
            self._notice_after[tab] = self.window.after(NOTICE_MS, lambda: label.configure(text=""))
        if tab == "general" and kind != "busy":
            self.update_button.set_enabled(True)

    def set_download(self, key, percent):
        """Model download progress (key None when it is over)."""
        self._download = (models.files_key(key), percent) if key else None
        self.refresh()

    def current_tab(self):
        return self._tab

    def _fade_label(self, seconds):
        t = self.texts
        if not seconds:
            return t("fade_off")
        return t("fade_seconds", n=seconds) if seconds < 60 else t("fade_minutes", n=seconds // 60)

    def _place(self, root):
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() - self.window.winfo_reqwidth()) // 2
        y = (self.window.winfo_screenheight() - self.window.winfo_reqheight()) // 3
        self.window.geometry(f"+{x}+{y}")
        self.lift()

    def lift(self):
        self.window.deiconify()
        self.window.lift()
        self.window.attributes("-topmost", True)    # in front once, without staying above everything
        self.window.after(200, lambda: self.alive() and self.window.attributes("-topmost", False))
        self.window.focus_force()

    def alive(self):
        try:
            return bool(self.window.winfo_exists())
        except tk.TclError:
            return False

    def close(self):
        try:
            self.window.destroy()
        except tk.TclError:
            pass
