"""Click-through overlay drawn over the game chat, following the WoW window.

The overlay and the mask are excluded from screen capture: the companion reads the addon's
grid through them, while the player only sees a plain overlay. Both windows are kept just
above the game in the Z order (not "always on top"), so they go behind other applications
together with the game.
"""

import logging
import time
import tkinter as tk
import tkinter.font as tkfont

from . import winutil
from .emoji import SMILEY_RE, EmojiRenderer, emoji_for
from .wowhead import TooltipCache

log = logging.getLogger(__name__)

BACKGROUND = "#0b0e12"   # keep in sync with BASE in Bridge.lua / bridge.py
HOLE_KEY = "#010203"     # colour made transparent by Windows (never used for drawing)
FONT_FAMILY = "Segoe UI"
FOLLOW_INTERVAL_MS = 30    # the overlay must vanish as fast as the game windows open
STATUS_LIFETIME_MS = 15000   # companion messages (blue) stay this long *while visible*
WHEEL_LINES = 3
LINK_COLOR = "#ffd100"           # links without a quality colour (quests, spells...)
TOOLTIP_BG = "#10151c"
TOOLTIP_BORDER = "#5a6573"
TOOLTIP_WIDTH_CHARS = 42
TOOLTIP_OFFSET = 18
MAX_LINK_TAGS = 400
FADE_DURATION_MS = 3000          # like the game's chat: the text fades out in a few seconds
# Rough position of the default chat frame, used until the addon reports the real one.
DEFAULT_RECT = {"x": 0.015, "y": 0.66, "w": 0.30, "h": 0.20}

KIND_COLORS = {
    "guild": "#40ff40", "officer": "#40c040", "raid": "#ff7f00", "party": "#aaaaff",
    "instance": "#ff7f00", "whisper": "#ff80ff", "whisper_out": "#ff80ff",
    "say": "#ffffff", "channel": "#ffc0c0",
}

# Class colours of the game (RAID_CLASS_COLORS), for the sender's name.
CLASS_COLORS = {
    "WARRIOR": "#c69b6d", "PALADIN": "#f48cba", "HUNTER": "#aad372", "ROGUE": "#fff468", "PRIEST": "#ffffff",
    "SHAMAN": "#0070dd", "MAGE": "#3fc7eb", "WARLOCK": "#8788ee", "DRUID": "#ff7c0a", "DEATHKNIGHT": "#c41e3a",
    "MONK": "#00ff98", "DEMONHUNTER": "#a330c9", "EVOKER": "#33937f",
}


class Overlay:
    def __init__(self, root: tk.Tk, config, texts, get_addon_rect, is_in_game=lambda: True, get_grid_rect=lambda: None,
                 masking_supported=lambda: False, get_lang=lambda: "en"):
        self._last_activity = time.monotonic()  # last message, scroll or hover (text fading)
        self._fade_level = 1.0            # 1: text fully shown, 0: faded out
        self._fade_colors = {}            # tag -> original text colour
        self._emoji = EmojiRenderer()
        self._emoji_images = {}           # (emoji, height) -> PhotoImage, reused by every line
        self.root = root
        self.config = config
        self.texts = texts
        self.get_addon_rect = get_addon_rect  # callable -> dict | None
        self.is_in_game = is_in_game          # callable -> bool (grid visible = character in the world)
        self.get_grid_rect = get_grid_rect    # callable -> (x, y, w, h) of the bridge grid on screen
        self.masking_supported = masking_supported  # callable -> bool (DXGI capture in use)
        self.edit_mode = False
        self._shown = False
        self._geometry = None
        self._wow_hwnd = None
        self._client = None
        self._drag = None
        self._at_bottom = True      # follow new messages unless the player scrolled up
        self._status_count = 0
        self._status_timers = {}    # tag -> remaining visible milliseconds
        self.get_lang = get_lang          # callable -> language of the Wowhead tooltips
        self._links = {}                  # text tag -> ChatLink
        self._link_count = 0
        self._tooltips = TooltipCache()
        self._tip_key = None              # what the tooltip window currently shows
        self._covers = ()                 # game windows open on screen (screen rects)
        self._cover_frames = []           # transparent cut-outs showing them
        self._cover_places = []

        root.title("WoWChatTranslatorCompagnion")
        root.overrideredirect(True)
        root.configure(bg=BACKGROUND, highlightthickness=0)
        root.attributes("-alpha", config["opacity"])
        root.withdraw()

        self.font = tkfont.Font(family=FONT_FAMILY, size=config["font_size"])
        self.small_font = tkfont.Font(family=FONT_FAMILY, size=max(7, config["font_size"] - 2), slant="italic")
        self.text = tk.Text(
            root, bg=BACKGROUND, fg="#ffffff", bd=0, highlightthickness=0, wrap="word",
            font=self.font, padx=6, pady=4, cursor="arrow", state="disabled", spacing1=1,
        )
        self.text.pack(fill="both", expand=True)
        for kind, color in KIND_COLORS.items():
            self.text.tag_configure(kind, foreground=color)
        self.text.tag_configure("lang", foreground="#7f8c99", font=self.small_font)
        self.text.tag_configure("original", foreground="#8a8f96", font=self.small_font, lmargin1=18, lmargin2=18)
        self.text.tag_configure("status", foreground="#33ccff", font=self.small_font)
        for player_class, color in CLASS_COLORS.items():     # created last: above the channel colour
            self.text.tag_configure(f"class_{player_class}", foreground=color)

        self.grip = tk.Label(root, text="◢", bg=BACKGROUND, fg="#33ccff", cursor="size_nw_se", font=(FONT_FAMILY, 12))
        for widget in (self.text, root):
            widget.bind("<ButtonPress-1>", self._start_move)
            widget.bind("<B1-Motion>", self._move)
        for sequence in ("<Double-Button-1>", "<Triple-Button-1>", "<ButtonPress-2>", "<ButtonPress-3>"):
            self.text.bind(sequence, lambda event: "break")
        self.grip.bind("<ButtonPress-1>", self._start_resize)
        self.grip.bind("<B1-Motion>", self._resize)

        # The overlay itself is invisible to screen capture: the grid is read through it.
        root.update_idletasks()
        self._overlay_excluded = winutil.exclude_from_capture(self._hwnd)
        if not self._overlay_excluded and winutil.IS_WINDOWS:
            log.warning("Overlay capture exclusion unavailable: using a transparent hole over the grid")
        # Fallback when the grid cannot be read through the overlay (older Windows, or GDI
        # capture which ignores the exclusion): a colour-keyed hole over the grid.
        root.attributes("-transparentcolor", HOLE_KEY)
        self.hole = tk.Frame(root, bg=HOLE_KEY, highlightthickness=0, bd=0)
        self._hole = None
        self._create_mask()
        self._create_tooltip()
        self.root.after(FOLLOW_INTERVAL_MS, self._follow)

    @property
    def _hwnd(self):
        return winutil.toplevel_hwnd(self.root)

    # ----- content -------------------------------------------------------------------------

    def add_line(self, display):
        line = display.line
        self.wake()
        self.text.configure(state="normal")
        if line.prefix:
            self._insert_prefix(line)
        if display.translated and display.source_lang:
            self.text.insert("end", f"[{display.source_lang.upper()}] ", "lang")
        start = self.text.index("end-1c")
        self.text.insert("end", display.text, line.kind)
        if display.translated and self.config["show_original"]:
            self.text.insert("end", f"\n{line.text}", "original")
        self._tag_links(start, getattr(line, "links", None))
        self._insert_emoji(start)
        self.text.insert("end", "\n")
        self._trim()
        self.text.configure(state="disabled")
        self._follow_tail()

    def _insert_prefix(self, line):
        """"[2. Trade] Name: " in the channel colour, the name in its class colour (like the game)."""
        prefix = line.prefix
        player_class = getattr(line, "player_class", "")
        at = prefix.rfind(line.speaker) if line.speaker else -1
        if at < 0 or player_class not in CLASS_COLORS or not self.config.get("class_colors", True):
            self.text.insert("end", f"{prefix}{line.separator}", line.kind)
            return
        end = at + len(line.speaker)
        self.text.insert("end", prefix[:at], line.kind)
        self.text.insert("end", prefix[at:end], (line.kind, f"class_{player_class}"))
        self.text.insert("end", f"{prefix[end:]}{line.separator}", line.kind)

    def _insert_emoji(self, start):
        """Text smileys (":D", "<3", "^^") of the new line shown as colour emoji pictures."""
        if not self._emoji.available:
            return
        text = self.text.get(start, "end-1c") or ""
        height = max(10, (self.font.metrics("linespace") or 18) - 2)
        for match in reversed(list(SMILEY_RE.finditer(text))):
            picture = self._emoji_picture(emoji_for(match.group(0)), height)
            if picture is None:
                continue
            first = f"{start}+{match.start()}c"
            self.text.delete(first, f"{start}+{match.end()}c")
            self.text.image_create(first, image=picture, padx=1, align="center")
            self.text.tag_add("emoji", first)

    def _emoji_picture(self, emoji, height):
        key = (emoji, height)
        if key not in self._emoji_images:
            image = self._emoji.image(emoji, height)
            if image is None:
                self._emoji_images[key] = None
            else:
                from PIL import ImageTk
                self._emoji_images[key] = ImageTk.PhotoImage(image, master=self.root)
        return self._emoji_images[key]

    def _tag_links(self, start, links):
        """Colours "[Name]" like in game and remembers which Wowhead entry it points to."""
        for link in links or ():
            needle = f"[{link.name}]"
            index = start
            while True:
                index = self.text.search(needle, index, stopindex="end", exact=True)
                if not index:
                    break
                end = f"{index}+{len(needle)}c"
                self._link_count += 1
                tag = f"link{self._link_count}"
                self._links[tag] = link
                self.text.tag_configure(tag, foreground=link.color or LINK_COLOR)
                self.text.tag_add(tag, index, end)
                index = end
        while len(self._links) > MAX_LINK_TAGS:
            tag = next(iter(self._links))
            del self._links[tag]
            self.text.tag_delete(tag)

    def add_status(self, message):
        self.wake()
        self._status_count += 1
        tag = f"status{self._status_count}"
        self.text.configure(state="normal")
        self.text.insert("end", f"{message}\n", ("status", tag))
        self._trim()
        self.text.configure(state="disabled")
        self._follow_tail()
        self._status_timers[tag] = STATUS_LIFETIME_MS

    def _age_statuses(self, elapsed_ms):
        """Companion messages expire only while the player can actually see them."""
        for tag in list(self._status_timers):
            self._status_timers[tag] -= elapsed_ms
            if self._status_timers[tag] <= 0:
                del self._status_timers[tag]
                self._remove_tag(tag)

    def _remove_tag(self, tag):
        ranges = self.text.tag_ranges(tag)
        if ranges:
            self.text.configure(state="normal")
            self.text.delete(ranges[0], ranges[-1])
            self.text.configure(state="disabled")
            self._follow_tail()

    def _follow_tail(self):
        if self._at_bottom:
            self.text.see("end")

    def _trim(self):
        excess = int(self.text.index("end-1c").split(".")[0]) - self.config["max_lines"]
        if excess > 0:
            self.text.delete("1.0", f"{excess + 1}.0")

    # ----- mouse wheel (no scrollbar) --------------------------------------------------------

    # ----- game windows (bags, character sheet, professions, tooltips...) ---------------------

    def set_covers(self, covers):
        """The addon reports the game windows open on screen: wherever the overlay is placed,
        it is cut out where they overlap it, so they stay visible as if the overlay was part
        of the game's interface, below its windows."""
        covers = tuple(covers)
        if len(covers) != len(self._covers):
            log.debug("Game windows on screen: %d", len(covers))
        self._covers = covers
        self._update_covers()

    def _covered(self, x, y):
        return any(cx <= x < cx + cw and cy <= y < cy + ch for cx, cy, cw, ch in self._covers)

    def _update_covers(self):
        places = []
        if self._geometry and self._shown and not self.edit_mode:
            w, h, ox, oy = self._geometry
            for cx, cy, cw, ch in self._covers:
                left, top = max(0, cx - ox), max(0, cy - oy)
                right, bottom = min(w, cx + cw - ox), min(h, cy + ch - oy)
                if right > left and bottom > top:
                    places.append((left, top, right - left, bottom - top))
        if places == self._cover_places:
            return
        self._cover_places = places
        while len(self._cover_frames) < len(places):
            self._cover_frames.append(tk.Frame(self.root, bg=HOLE_KEY, highlightthickness=0, bd=0))
        for index, frame in enumerate(self._cover_frames):
            if index < len(places):
                x, y, cw, ch = places[index]
                frame.place(x=x, y=y, width=cw, height=ch)
                frame.lift()
            else:
                frame.place_forget()

    def wants_wheel(self, x, y):
        """Called from the wheel hook thread: cursor over the visible overlay, on the game?"""
        if not self._shown or self.edit_mode or not self._geometry:
            return False
        w, h, ox, oy = self._geometry
        if not (ox <= x < ox + w and oy <= y < oy + h):
            return False
        if self._covered(x, y):
            return False   # a game window (bag...) is there: the wheel is for the game
        # Another application covering this spot gets its wheel events as usual.
        return winutil.root_window_at(x, y) in (self._wow_hwnd, self._hwnd)

    def scroll(self, delta):
        self.wake()
        steps = -int(delta / 120 * WHEEL_LINES) or (-1 if delta > 0 else 1)
        self.text.yview_scroll(steps, "units")
        self._at_bottom = self.text.yview()[1] >= 0.999

    # ----- fading out when nothing happens (like the game's chat) ---------------------------

    def wake(self):
        """Activity: the text shows again at once, and the fading delay starts over."""
        self._last_activity = time.monotonic()
        if self._fade_level < 1.0:
            self._set_fade(1.0)

    def _update_fade(self):
        delay = self.config["fade_after"] or 0
        if not delay or self.edit_mode or not self._shown:
            if self._fade_level < 1.0:
                self._set_fade(1.0)
            return
        if self._geometry:
            x, y = self.root.winfo_pointerxy()
            w, h, ox, oy = self._geometry
            if ox <= x < ox + w and oy <= y < oy + h and not self._covered(x, y):
                self.wake()     # the player is looking at the chat (mouse over it)
                return
        idle_ms = (time.monotonic() - self._last_activity - delay) * 1000
        if idle_ms > 0:
            level = max(0.0, 1.0 - idle_ms / FADE_DURATION_MS)
            if abs(level - self._fade_level) >= 0.04 or (level == 0.0 and self._fade_level > 0.0):
                self._set_fade(level)

    def _set_fade(self, level):
        """Blends every text colour towards the background (the panel itself stays, as the game's
        chat background does, and keeps hiding the bridge grid)."""
        self._fade_level = level
        background = self.text.cget("background")
        targets = [("", self.text)] + [(tag, None) for tag in self.text.tag_names()]
        for tag, widget in targets:
            key = tag or "<text>"
            if key not in self._fade_colors:
                colour = self.text.cget("foreground") if not tag else self.text.tag_cget(tag, "foreground")
                if not colour:
                    continue
                self._fade_colors[key] = colour
            blended = self._blend(self._fade_colors[key], background, level)
            if tag:
                self.text.tag_configure(tag, foreground=blended)
            else:
                self.text.configure(foreground=blended)
        # Emoji pictures cannot change colour: hidden when the text is mostly faded.
        self.text.tag_configure("emoji", elide=level < 0.5)
        if level >= 1.0:
            self._fade_colors.clear()    # colours may change (style, new links): read them afresh

    def _blend(self, colour, background, level):
        try:
            r1, g1, b1 = (v // 257 for v in self.root.winfo_rgb(colour))
            r2, g2, b2 = (v // 257 for v in self.root.winfo_rgb(background))
        except tk.TclError:
            return colour
        mix = lambda a, b: int(round(b + (a - b) * level))
        return f"#{mix(r1, r2):02x}{mix(g1, g2):02x}{mix(b1, b2):02x}"

    # ----- appearance ----------------------------------------------------------------------

    def apply_style(self):
        if getattr(self, "_fade_level", 1.0) < 1.0:   # also called while the overlay is built
            self._set_fade(1.0)
        self.root.attributes("-alpha", self.config["opacity"])
        self.font.configure(size=self.config["font_size"])
        self.small_font.configure(size=max(7, self.config["font_size"] - 2))
        self.title_font.configure(size=self.config["font_size"] + 1)
        self._tip_key = None if not self._tip_key else self._tip_key[:3] + ("restyle",)   # refill on next hover
        self._apply_mouse_mode()

    def _apply_mouse_mode(self):
        """The overlay catches the mouse like the chat it replaces: the game's chat lines and
        links below it get no hover (their tooltips would cut the overlay), and clicks there do
        nothing in the game. It never takes the keyboard focus from the game, except in edit
        mode. Cut-outs over game windows (bags...) stay fully usable: transparent pixels let
        the mouse through."""
        winutil.set_click_through(self._hwnd, False, no_activate=not self.edit_mode)

    def set_edit_mode(self, enabled):
        self.edit_mode = enabled
        if enabled:
            self.root.configure(highlightthickness=2, highlightbackground="#33ccff")
            self.grip.place(relx=1.0, rely=1.0, anchor="se")
            self.add_status(self.texts("edit_hint"))
            self._show()
        else:
            self.root.configure(highlightthickness=0)
            self.grip.place_forget()
            self._save_user_rect()
        self._apply_mouse_mode()

    def reset_position(self):
        self.config["overlay_rect"] = None
        self._geometry = None

    # ----- following the game window -------------------------------------------------------

    def _current_rect(self):
        return self.config["overlay_rect"] or self.get_addon_rect() or DEFAULT_RECT

    def _game_visible(self):
        if not winutil.is_window(self._wow_hwnd):
            self._wow_hwnd = winutil.find_wow_window()
        return bool(self._wow_hwnd) and not winutil.is_minimized(self._wow_hwnd)

    def _follow(self):
        try:
            self._update_fade()
        except Exception:
            log.exception("Fade error")
        try:
            self._update_position()
        except Exception:
            log.exception("Overlay follow error")
            self._hide()
        try:
            self._update_mask()
        except Exception:
            log.exception("Mask error")
            self._hide_mask()
        try:
            self._update_covers()
        except Exception:
            log.exception("Cover error")
        try:
            self._update_tooltip()
        except Exception:
            log.exception("Tooltip error")
            self._hide_tooltip()
        try:
            self._keep_z_order()
            if self._shown:
                self._age_statuses(FOLLOW_INTERVAL_MS)
        except Exception:
            log.exception("Overlay z-order error")
        self.root.after(FOLLOW_INTERVAL_MS, self._follow)

    def _keep_z_order(self):
        """WoW < mask < overlay, right above the game."""
        if not self._wow_hwnd:
            return
        below = self._wow_hwnd
        if self._mask_shown:
            winutil.place_above(below, self._mask_hwnd)
            below = self._mask_hwnd
        if self._shown:
            winutil.place_above(below, self._hwnd)
            below = self._hwnd
        if self._tip_key:
            winutil.place_above(below, self._tip_hwnd)

    def _update_position(self):
        if self.edit_mode:
            return
        if not self.config["enabled"] or not self._game_visible() or not self.is_in_game():
            self._hide()
            return
        client = winutil.client_rect(self._wow_hwnd)
        if not client or client[2] <= 0 or client[3] <= 0:
            self._hide()
            return
        self._client = client
        rect = self._current_rect()
        cx, cy, cw, ch = client
        geometry = (
            max(80, int(rect["w"] * cw)), max(40, int(rect["h"] * ch)),
            cx + int(rect["x"] * cw), cy + int(rect["y"] * ch),
        )
        if geometry != self._geometry:
            source = "user" if self.config["overlay_rect"] else ("addon" if self.get_addon_rect() else "default")
            log.info("Overlay placed from %s rect %s on client %s -> %s", source, rect, client, geometry)
            self._geometry = geometry
            self.root.geometry("{}x{}+{}+{}".format(*geometry))
            self._show()
            self._apply_native_geometry()
        else:
            self._show()
        if self._read_through_overlay():
            self._clear_hole()
        else:
            self._update_hole()

    def _apply_native_geometry(self):
        """Tk sometimes keeps the old position of borderless windows on high-DPI screens:
        enforce it through Win32 and check the result."""
        if not self._geometry:
            return
        w, h, x, y = self._geometry
        if winutil.move_window(self._hwnd, x, y, w, h):
            actual = winutil.window_rect(self._hwnd)
            if actual and actual != (x, y, w, h):
                log.warning("Overlay position mismatch: wanted %s, got %s", (x, y, w, h), actual)

    def _read_through_overlay(self):
        """DXGI capture ignores capture-excluded windows: the grid is read through the overlay."""
        return self._overlay_excluded and self.masking_supported()

    def capture_excluded_windows(self):
        """Our windows hidden from screen capture (for a screenshot that must show them)."""
        hwnds = []
        if self._overlay_excluded:
            hwnds.append(self._hwnd)
        if self._mask_enabled and self._mask_shown:
            hwnds.append(self._mask_hwnd)
        if self._tip_key:
            hwnds.append(self._tip_hwnd)
        return [h for h in hwnds if h]

    def _grid_under_game_window(self, rect):
        """The grid is drawn at the chat's level: a game window over it hides it already
        (and the mask must not be drawn over that window)."""
        gx, gy, gw, gh = rect
        return any(cx < gx + gw and gx < cx + cw and cy < gy + gh and gy < cy + ch
                   for cx, cy, cw, ch in self._covers)

    def _grid_covered_by_overlay(self, rect):
        if not (self._shown and self._read_through_overlay() and self._geometry):
            return False
        gx, gy, gw, gh = rect
        w, h, x, y = self._geometry
        return x <= gx and y <= gy and gx + gw <= x + w and gy + gh <= y + h

    # ----- mask over the bridge grid (only when the overlay does not cover it) -----------------

    def _create_mask(self):
        """Patch in the overlay colour over the addon's grid, excluded from screen capture.
        Needed only when the overlay does not cover the grid (moved before a /reload...)."""
        self.mask = tk.Toplevel(self.root)
        self.mask.overrideredirect(True)
        self.mask.configure(bg=BACKGROUND)
        self.mask.withdraw()
        self.mask.update_idletasks()
        self._mask_hwnd = winutil.toplevel_hwnd(self.mask)
        self._mask_shown = False
        self._mask_enabled = winutil.exclude_from_capture(self._mask_hwnd)
        if not self._mask_enabled and winutil.IS_WINDOWS:
            log.warning("Capture exclusion unavailable (Windows 10 2004+ needed): grid cannot be masked")

    def _hide_mask(self):
        if self._mask_shown:
            self.mask.withdraw()
            self._mask_shown = False

    def _update_mask(self):
        rect = self.get_grid_rect() if self._mask_enabled and self.masking_supported() else None
        if not rect or not self._game_visible() or self._grid_covered_by_overlay(rect) \
                or self._grid_under_game_window(rect):
            self._hide_mask()
            return
        x, y, w, h = rect
        self.mask.geometry(f"{w}x{h}+{x}+{y}")
        if not self._mask_shown:
            self.mask.deiconify()
            self._mask_shown = True
            self.root.after(50, lambda: winutil.set_click_through(self._mask_hwnd, True))

    def _update_hole(self):
        """Fallback when the overlay cannot be excluded from capture: transparent hole over
        the grid (the mask, below the overlay, hides it from the player)."""
        rect = self.get_grid_rect()
        if rect and self._geometry:
            gx, gy, gw, gh = rect
            w, h, x, y = self._geometry
            rx, ry = gx - x, gy - y
            if rx + gw > 0 and ry + gh > 0 and rx < w and ry < h:
                if (rx, ry, gw, gh) != self._hole:
                    self._hole = (rx, ry, gw, gh)
                    self.hole.place(x=rx, y=ry, width=gw, height=gh)
                    self.hole.lift()
                return
        self._clear_hole()

    def _clear_hole(self):
        if self._hole:
            self._hole = None
            self.hole.place_forget()

    def _show(self):
        if not self._shown:
            self.root.deiconify()
            self._shown = True
            # Tk resets extended styles when the window is mapped: re-apply afterwards.
            self.root.after(50, self._apply_mouse_mode)
            # Re-mapping can restore a stale position: enforce the expected one again.
            self.root.after(60, lambda: None if self.edit_mode else self._apply_native_geometry())

    def _hide(self):
        self._hide_tooltip()
        if self._shown:
            self.root.withdraw()
            self._shown = False

    # ----- Wowhead tooltip when the cursor rests on a link -------------------------------------

    def _create_tooltip(self):
        self.tip = tk.Toplevel(self.root)
        self.tip.overrideredirect(True)
        self.tip.configure(bg=TOOLTIP_BORDER)
        self.tip.withdraw()
        self.tip_text = tk.Text(
            self.tip, bg=TOOLTIP_BG, fg="#ffffff", bd=0, highlightthickness=0, wrap="word",
            font=self.font, padx=8, pady=6, width=TOOLTIP_WIDTH_CHARS, height=1, cursor="arrow",
            spacing1=1, spacing3=1,
        )
        self.tip_text.pack(padx=1, pady=1)
        # Keep a reference: Tk forgets fonts whose Python object is garbage-collected.
        self.title_font = tkfont.Font(family=FONT_FAMILY, size=self.config["font_size"] + 1, weight="bold")
        self.tip_text.tag_configure("title", font=self.title_font)
        self.tip_text.tag_configure("muted", foreground="#7f8c99", font=self.small_font)
        self.tip.update_idletasks()
        self._tip_hwnd = winutil.toplevel_hwnd(self.tip)
        # Never read by the bridge capture, never catches the mouse.
        winutil.exclude_from_capture(self._tip_hwnd)
        self._tip_colors = set()

    def _link_under_cursor(self):
        if not self._shown or self.edit_mode or not self._geometry:
            return None
        x, y = self.root.winfo_pointerxy()
        w, h, ox, oy = self._geometry
        if not (ox <= x < ox + w and oy <= y < oy + h):
            return None
        if winutil.IS_WINDOWS and winutil.root_window_at(x, y) not in (self._wow_hwnd, self._hwnd):
            return None   # another window is in front of the chat
        if self._covered(x, y):
            return None   # a game window is over the overlay there
        lx, ly = x - self.text.winfo_rootx(), y - self.text.winfo_rooty()
        index = self.text.index(f"@{lx},{ly}")
        bbox = self.text.bbox(index)
        if not bbox or not (bbox[0] <= lx < bbox[0] + bbox[2] and bbox[1] <= ly < bbox[1] + bbox[3]):
            return None
        for tag in self.text.tag_names(index):
            if tag in self._links:
                return self._links[tag], (x, y)
        return None

    def _update_tooltip(self):
        found = self._link_under_cursor()
        if not found:
            self._hide_tooltip()
            return
        link, (x, y) = found
        lang = self.get_lang()
        lines = self._tooltips.get(link.kind, link.id, lang)
        key = (link.kind, link.id, lang, lines is None)
        if key != self._tip_key:
            self._fill_tooltip(link, lines)
            self._tip_key = key
        self._place_tooltip(x, y)

    def _fill_tooltip(self, link, lines):
        text = self.tip_text
        text.configure(state="normal")
        text.delete("1.0", "end")
        if not lines:
            text.insert("end", link.name, ("title", self._color_tag(link.color or LINK_COLOR)))
            text.insert("end", "\n…" if lines is None else "\nwowhead.com", "muted")
        for number, segments in enumerate(lines or ()):
            if number:
                text.insert("end", "\n")
            for chunk, color in segments:
                tags = (self._color_tag(color), "title") if number == 0 else (self._color_tag(color),)
                text.insert("end", chunk, tags)
        text.configure(state="disabled")
        # Width: the longest line, capped; height: the wrapped lines.
        longest = max((len("".join(t for t, _ in seg)) for seg in (lines or [[(link.name, "")]])), default=10)
        text.configure(width=max(16, min(TOOLTIP_WIDTH_CHARS, longest + 1)))
        text.configure(height=1)
        self.tip.update_idletasks()
        rows = text.count("1.0", "end", "displaylines")
        text.configure(height=max(1, rows[0] if isinstance(rows, tuple) else rows or 1))

    def _color_tag(self, color):
        tag = f"c{color}"
        if tag not in self._tip_colors:
            self.tip_text.tag_configure(tag, foreground=color)
            self._tip_colors.add(tag)
        return tag

    def _place_tooltip(self, x, y):
        self.tip.update_idletasks()
        tw, th = self.tip.winfo_reqwidth(), self.tip.winfo_reqheight()
        left, top, right, bottom = 0, 0, self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        if self._client:
            cx, cy, cw, ch = self._client
            left, top, right, bottom = cx, cy, cx + cw, cy + ch
        tx, ty = x + TOOLTIP_OFFSET, y + TOOLTIP_OFFSET
        if ty + th > bottom:
            ty = y - TOOLTIP_OFFSET - th   # no room below the cursor: above it
        tx = max(left, min(tx, right - tw))
        ty = max(top, min(ty, bottom - th))
        self.tip.geometry(f"+{tx}+{ty}")
        if not self.tip.winfo_viewable():
            self.tip.deiconify()
            self.root.after(30, lambda: winutil.set_click_through(self._tip_hwnd, True))

    def _hide_tooltip(self):
        if self._tip_key:
            self._tip_key = None
            self.tip.withdraw()

    # ----- move / resize (edit mode only) -----------------------------------------------------

    def _start_move(self, event):
        if self.edit_mode:
            self._drag = (event.x_root, event.y_root, self.root.winfo_x(), self.root.winfo_y())
        return "break"   # no text selection, no keyboard focus

    def _move(self, event):
        if self.edit_mode and self._drag:
            sx, sy, wx, wy = self._drag
            self.root.geometry(f"+{wx + event.x_root - sx}+{wy + event.y_root - sy}")
        return "break"

    def _start_resize(self, event):
        if self.edit_mode:
            self._drag = (event.x_root, event.y_root, self.root.winfo_width(), self.root.winfo_height())
        # Stop propagation to the toplevel binding, which would start a move instead.
        return "break"

    def _resize(self, event):
        if self.edit_mode and self._drag:
            sx, sy, w, h = self._drag
            self.root.geometry(f"{max(120, w + event.x_root - sx)}x{max(60, h + event.y_root - sy)}")
            return "break"
        return None

    def _save_user_rect(self):
        if not self._client:
            return
        cx, cy, cw, ch = self._client
        self.root.update_idletasks()
        self.config["overlay_rect"] = {
            "x": (self.root.winfo_x() - cx) / cw,
            "y": (self.root.winfo_y() - cy) / ch,
            "w": self.root.winfo_width() / cw,
            "h": self.root.winfo_height() / ch,
        }
        self._geometry = None
