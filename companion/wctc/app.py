"""Application wiring: WoW detection, addon install, log tailing, translation, overlay and tray."""

import logging
import os
import queue
import subprocess
import sys
import time
import threading
import tkinter as tk
from logging.handlers import RotatingFileHandler
from tkinter import filedialog

from . import ADDON_NAME, APP_NAME, LANGUAGES, __version__, bridge, installer, savedvars, updater, winutil, wow
from .bridge import PixelBridge
from .chatlog import ChatLogRecovery
from .confirm import ConfirmDialog, key_label
from .update_dialog import UpdateDialog
from .config import Config
from .detector import LanguageDetector
from . import models
from .engine import TranslationEngine
from .glossary import Glossary
from .i18n import Texts
from .model_dialog import ModelDialog
from .options import TABS, OptionsWindow
from .overlay import Overlay
from .paths import config_dir, models_dir
from .pipeline import TranslationPipeline
from .screenshot import capture_with_overlay, screenshots_dir
from .tray import Tray

log = logging.getLogger(APP_NAME)

UI_POLL_MS = 15   # game windows opening must cut the overlay right away
ADDON_STATE_REFRESH_S = 1.0
HEARTBEAT_INTERVAL_S = 5.0     # the addon only starts if this signature is < 30 s old
RELOAD_HINT_AFTER_S = 45.0    # shown at most once per run, only if the grid was never seen


def setup_logging():
    handler = RotatingFileHandler(log_path(), maxBytes=1_000_000, backupCount=2, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    logging.basicConfig(level=logging.INFO, handlers=[handler])


def log_path():
    return config_dir() / "companion.log"


def open_path(path):
    if hasattr(os, "startfile"):
        os.startfile(str(path))
    else:
        subprocess.Popen(["xdg-open", str(path)])


def close_splash():
    """Closes the splash screen the .exe shows while it starts (nothing in a source run)."""
    try:
        import pyi_splash
        pyi_splash.close()
    except Exception:
        pass  # no splash screen (run from source)


TRAY_CHECK_MS = 5000
EXIT_CHECK_TIMEOUT_S = 5         # update check when closing: no longer than this
UPDATE_RESTART_DELAY_MS = 1500   # "update ready: restarting" stays readable this long
RECOVER_DELAYS_S = (1.0, 10.0)   # the chat log is read back at once, then once more (written late)
ADDON_CHECK_MS = 60_000     # the addon is checked (and put back if missing) this often
GAME_STATE_CHECK_MS = 500   # the tray menu items that need the game follow it within this time


class Dispatcher:
    """Thread-safe bridge from the tray thread to the Tk thread."""

    def __init__(self, app):
        self._app = app
        self.queue = queue.Queue()

    def __call__(self, action, *args):
        self.queue.put((action, args))

    def current_lang(self):
        return self._app.target_lang()

    def edit_mode(self):
        return self._app.overlay.edit_mode if self._app.overlay else False

    def game_running(self):
        return self._app.game_running()


class CompanionApp:
    def __init__(self):
        self.config = Config()
        self.texts = Texts(self.target_lang)
        self.flavors = []
        self.chat_log_in_game = None      # the game writes its chat log (reported by the addon)
        self.update_at_exit = None        # version to download and install when the companion closes
        self._update_dialog = None
        self._quitting = False
        self._exit_checked = False
        self._shut_down = False
        self.toggle_key = "ALT-F6"        # key showing / hiding the overlay in game (reported by the addon)
        self._quit_dialog = None
        self._chat_log_pending = None     # value set in the options, applied at the next /reload
        self.overlay = None
        self.display_queue = queue.Queue()
        self.dispatch = Dispatcher(self)
        self.glossary = Glossary()
        self._addon_rect = None
        self._addon_state_checked = 0.0
        self._addon_state_stamp = None
        self.pending_update = None
        self.loaded_model = None          # "standard" / "quality" once the engine is loaded
        self._model_override = None       # "standard" after Quality proved too slow (this session)
        self._model_download = None
        self._model_dialog = None
        self.options = None
        self._manual_check = False
        self._progress_shown = -1
        self.pipeline = None
        self.updater = None
        self.bridge = None
        self._last_heartbeat = 0.0
        self._game_seen_since = None
        self._reload_hint_sent = False

    # ----- setup ---------------------------------------------------------------------------

    def target_lang(self):
        lang = self.config["target_lang"]
        if lang in LANGUAGES:
            return lang
        for flavor in self.flavors:
            lang = wow.game_language(flavor)
            if lang in LANGUAGES:
                return lang
        lang = wow.windows_language()
        return lang if lang in LANGUAGES else "en"

    def _detect_wow(self, root_window):
        roots = wow.find_roots(self.config["wow_root"])
        if not roots:
            winutil.message_box(APP_NAME, self.texts("wow_not_found"))
            chosen = filedialog.askdirectory(parent=root_window, title="World of Warcraft")
            if chosen:
                roots = wow.find_roots(chosen)
                if roots:
                    self.config["wow_root"] = str(roots[0])
        self.flavors = [f for r in roots for f in wow.find_flavors(r)]
        for flavor in self.flavors:
            log.info("Flavor found: %s (product %s)", flavor.path, flavor.product or "?")
        return bool(self.flavors)

    def _check_addon(self, why):
        """The addon may have been deleted or replaced while the companion runs (reinstalled
        game, cleaned AddOns folder): put back and kept at the companion's version."""
        if self._install_addon(enable_always=False):
            log.info("Addon reinstalled (%s)", why)
            self._status("addon_updated")
            self.tray.notify(self.texts("addon_updated"))

    def _watch_addon(self):
        try:
            self._check_addon("periodic check")
        except Exception:
            log.exception("Addon check failed")
        self.root.after(ADDON_CHECK_MS, self._watch_addon)

    def _install_addon(self, enable_always=True):
        """enable_always: also tick the addon for every character even if nothing was copied
        (at start-up); the periodic check only does it when it had to put the addon back, so
        that a player who turned it off for a character is not overruled every minute."""
        updated = False
        for flavor in self.flavors:
            try:
                copied = installer.install(flavor)
                updated |= copied
                if copied or enable_always:
                    installer.enable_for_all_characters(flavor)
            except OSError:
                log.exception("Addon install failed for %s", flavor.path)
        return updated

    # ----- data providers (called from worker / Tk threads) --------------------------------

    def _active_flavor(self):
        """The flavor whose addon data was written most recently (the one being played)."""
        def mtime(flavor):
            files = wow.saved_variables_files(flavor, ADDON_NAME)
            try:
                return files[0].stat().st_mtime if files else 0
            except OSError:
                return 0
        return max(self.flavors, key=mtime) if self.flavors else None

    def addon_rect(self):
        """Chat frame rectangle reported by the addon."""
        self._refresh_addon_state()
        return self._addon_rect

    def game_running(self):
        """The game window is open (the overlay can be placed on it)."""
        return bool(self.bridge and self.bridge.game_window)

    def is_in_game(self):
        """The addon only draws the bridge grid while a character is in the world."""
        return bool(self.bridge and self.bridge.active)

    def _refresh_addon_state(self):
        """Re-reads the addon SavedVariables when WoW rewrites them (logout or /reload)."""
        now = time.monotonic()
        if now - self._addon_state_checked < ADDON_STATE_REFRESH_S:
            return
        self._addon_state_checked = now
        flavor = self._active_flavor()
        files = wow.saved_variables_files(flavor, ADDON_NAME) if flavor else []
        if not files:
            return
        path = files[0]
        try:
            stamp = (str(path), path.stat().st_mtime)
        except OSError:
            return
        if stamp == self._addon_state_stamp:
            return
        self._addon_state_stamp = stamp
        try:
            db = savedvars.load(path).get("WoWChatTranslatorDB") or {}
        except (OSError, ValueError):
            log.exception("Cannot read %s", path)
            return

        rect = db.get("chat")
        if isinstance(rect, dict) and all(isinstance(rect.get(k), (int, float)) for k in "xywh"):
            new_rect = {k: float(rect[k]) for k in "xywh"}
            if new_rect != self._addon_rect:
                log.info("Chat rect from addon (%s): %s", path, new_rect)
            self._addon_rect = new_rect


    # ----- Tk thread -----------------------------------------------------------------------

    def _poll(self):
        try:
            while True:
                kind, payload = self.display_queue.get_nowait()
                if kind == "line":
                    self.overlay.add_line(payload)
                elif kind == "covers":
                    self.overlay.set_covers(payload)
                elif kind == "state":
                    self._on_addon_state(payload)
                elif kind == "status":
                    key, extra = payload
                    self.overlay.add_status(self.texts(key, **extra))
                    if key in ("ready", "engine_error", "no_model"):
                        self.tray.notify(self.texts(key, **extra))
                elif kind == "model":
                    self._on_model_event(*payload)
                elif kind == "muted":
                    if self.options and self.options.alive():
                        self._notice(TABS[self.options.current_tab()], payload)
                elif kind == "update_check":
                    key, version = payload
                    kinds = {"upd_latest": "ok", "upd_error": "error", "upd_downloading": "busy"}
                    self._notice("general", self.texts(key, version=version), kinds.get(key, "info"))
                elif kind == "update":
                    self._on_update_event(*payload)
        except queue.Empty:
            pass  # nothing more waiting
        try:
            while True:
                action, args = self.dispatch.queue.get_nowait()
                self._handle(action, *args)
        except queue.Empty:
            pass  # nothing more waiting
        self._maybe_apply_update()
        self._heartbeat()
        self._check_reload_needed()
        self.root.after(UI_POLL_MS, self._poll)

    def _expected_grid_origins(self):
        """Where the addon draws its grid: a corner of the overlay rectangle it was given at
        login (Companion.lua) or of the chat frame, top-right first (another corner when a
        game window covers that one)."""
        client = self.overlay._client if self.overlay else None
        if not client:
            return []
        cx, cy, cw, ch = client
        w, h, inset = bridge.WIDTH, bridge.HEIGHT, bridge.INSET
        origins = []
        for rect in (self.config["overlay_rect"], self._addon_rect):   # no file reads: bridge thread
            if rect:
                left, top = cx + rect["x"] * cw, cy + rect["y"] * ch
                right, bottom = left + rect["w"] * cw, top + rect["h"] * ch
                for x, y in ((right - w - inset, top + inset), (left + inset, top + inset),
                             (right - w - inset, bottom - h - inset), (left + inset, bottom - h - inset)):
                    origins.append((int(round(x)), int(round(y))))
        return origins

    def _take_screenshot(self):
        """The game as the player sees it: with the overlay, without the bridge grid.
        Ordinary screenshots cannot show the overlay, which is hidden from screen capture so
        that the grid can be read through it."""
        hwnd = winutil.find_wow_window()
        client = winutil.client_rect(hwnd) if hwnd else None
        if not client or winutil.is_minimized(hwnd) or client[2] <= 0 or client[3] <= 0:
            self.tray.notify(self.texts("screenshot_failed"))
            return
        self.root.update_idletasks()
        img = capture_with_overlay(client, self.overlay.capture_excluded_windows())
        folder = screenshots_dir()
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / time.strftime("WoW_%Y-%m-%d_%H-%M-%S.png")
        from PIL import Image
        Image.fromarray(img).save(path)
        log.info("Screenshot saved to %s", path)
        self.tray.notify(self.texts("screenshot_saved", path=str(path)))

    # ----- translation model --------------------------------------------------------------

    def _make_engine(self):
        choice = self._model_override or self.config["model"]
        key, path = models.usable_model(choice)
        log.info("Translation model: %s (choice: %s, PC suited to Quality: %s)",
                 key, self.config["model"], models.machine_suits_quality())
        self.loaded_model = key
        return TranslationEngine(models_dir(), path, light=models.MODELS[key].get("light", False))

    def _start_pipeline(self):
        """Translation starts once a model is installed (downloaded at the player's request)."""
        if self.pipeline:
            return
        self.pipeline = TranslationPipeline(
            engine_factory=self._make_engine,
            detector_factory=LanguageDetector,
            glossary=self.glossary,
            get_target_lang=self.target_lang,
            on_display=lambda d: self.display_queue.put(("line", d)),
            on_status=self._on_pipeline_status,
        )
        self.pipeline.on_slow = lambda average: self.display_queue.put(("model", ("slow", average)))
        self.pipeline.trace_enabled = lambda: bool(self.config.get("translation_log", False))
        self.pipeline.start()

    def _offer_model(self):
        """No model yet: the player chooses the one to download (nothing happens without his click)."""
        if self._model_dialog and self._model_dialog.alive():
            return
        self._model_dialog = ModelDialog(self.root, self.texts, self._choose_model)

    def _choose_model(self, key):
        self.config["model"] = key
        self.tray.refresh()
        self._download_model(key)

    def _download_model(self, key):
        """Downloads a model in the background. Only ever started by the player's click (first
        launch window or menu): never on its own."""
        key = models.files_key(key)
        if models.model_path(key) or self._model_download:
            return
        target = models_dir()
        if not models.folder_writable(target):
            # The companion's folder is protected (Program Files...): ask before changing that.
            allowed = winutil.ask_yes_no(APP_NAME, self.texts("models_folder_locked", path=str(target)))
            if allowed:
                # Lets the Windows "Users" group modify this folder (Windows asks to confirm).
                winutil.run_elevated("icacls", f'"{target}" /grant *S-1-5-32-545:(OI)(CI)M /T /Q')
            if not (allowed and models.folder_writable(target)):
                target = models.fallback_models_dir()
                log.info("Models folder not writable: downloading to %s", target)
        self._progress_shown = -1
        self._model_download = models.ModelDownloader(
            key, target, lambda k, ok: self.display_queue.put(("model", ("downloaded", (k, ok)))),
            on_progress=self._download_progress)
        self._model_download.start()
        self.tray.notify(self.texts("dl_started", name=self.texts(f"name_{key}"), size=models.MODELS[key]["size_mb"]))
        if self.options:
            self.options.set_download(key, 0)

    def _open_options(self, tab=0):
        if self.options and self.options.alive():
            self.options.lift()
            return
        self.options = OptionsWindow(self.root, self.config, self.texts, self.dispatch, tab,
                                     game_running=self.game_running,
                                     edit_mode=lambda: bool(self.overlay and self.overlay.edit_mode))

    def _notice(self, tab, text, kind="info"):
        """Feedback in the Options window (if open) for an action started there."""
        if self.options and self.options.alive():
            self.options.notice(tab, text, kind)

    def _check_updates_now(self):
        """Asked by the player: always answers, even when automatic updates are off."""
        if self._manual_check:
            return
        self._manual_check = True

        def report(kind, version=""):
            self.display_queue.put(("update_check", (kind, version)))

        def work():
            try:
                release = updater.latest_release()
                tag = (release or {}).get("tag_name", "")
                if not release:
                    report("upd_none")
                elif updater.parse_version(tag) <= updater.parse_version(__version__):
                    report("upd_latest", __version__)
                else:
                    report("upd_available", tag)
                    if updater.is_frozen():   # the player chooses: nothing downloaded yet
                        self.display_queue.put(("update", ("offer", tag)))
            except Exception:
                log.exception("Update check failed")
                report("upd_error")
            finally:
                self._manual_check = False

        threading.Thread(target=work, name="UpdateCheck", daemon=True).start()

    def _download_progress(self, done, expected):
        # Download thread: the window is only told about whole percents.
        percent = done * 100 // expected if expected else done >> 24
        if percent != self._progress_shown:
            self._progress_shown = percent
            self.display_queue.put(("model", ("progress", (done, expected))))

    def _on_model_event(self, event, value):
        if event == "progress":
            if self._model_dialog:
                self._model_dialog.set_progress(*value)
            if self.options and self._model_download:
                done, expected = value
                self.options.set_download(self._model_download.key, done * 100 // expected if expected else 0)
        elif event == "downloaded":
            key, ok = value
            self._model_download = None
            if self.options:
                self.options.set_download(None, 0)
            if self._model_dialog:
                self._model_dialog.close()
                self._model_dialog = None
            name = self.texts(f"name_{key}")
            if not ok:
                self.tray.notify(self.texts("dl_failed", name=name))
                if not models.installed_models():
                    self._offer_model()
            elif not self.pipeline:
                self._start_pipeline()         # its "ready" notice tells the player
            elif models.usable_model(self._model_override or self.config["model"])[0] != self.loaded_model:
                self.pipeline.reload_engine()
                self.tray.notify(self.texts("dl_ready", name=name))
            self.tray.refresh()
        elif event == "slow" and self.config["model"] == "auto" and self.loaded_model in models.SLOWER_TO_FASTER[:-1]:
            # Chosen automatically but too slow on this PC while playing: one step lighter for
            # this session (Quality -> Standard -> Light), if that model is installed.
            order = models.SLOWER_TO_FASTER
            lighter = order[order.index(self.loaded_model) + 1]
            if models.model_path(lighter):
                self._model_override = lighter
                self.pipeline.reload_engine()
                self.tray.notify(self.texts("model_too_slow" if lighter == "standard" else "model_too_slow_light"))

    def _write_companion_state(self, alive=True):
        """Tells the addon that the companion runs (without a recent signature it stays idle)
        and where the overlay is, so its grid sits under it after the next /reload."""
        for flavor in self.flavors:
            try:
                installer.write_companion_state(flavor, time.time() if alive else 0, self.config["overlay_rect"],
                                                 self.target_lang(), self.config.get("chat_log"))
            except OSError:
                log.exception("Cannot write companion state for %s", flavor.path)

    def _on_addon_state(self, state):
        """The addon reports whether the game writes its chat log: the option follows a
        /chatlog typed in game, unless a change made in the options awaits the next /reload."""
        if "key" in state:
            self.toggle_key = state["key"]
        if "chatlog" not in state:
            return
        logging_on = state["chatlog"] == "1"
        self.chat_log_in_game = logging_on
        if self._chat_log_pending is not None and self._chat_log_pending != logging_on:
            return
        self._chat_log_pending = None
        if self.config.get("chat_log") != logging_on:
            log.info("Chat log %s in game", "on" if logging_on else "off")
            self.config["chat_log"] = logging_on
            self._write_companion_state()
            if self.options and self.options.alive():
                self.options.refresh()

    def _toggle_chat_log(self):
        current = self.config.get("chat_log")
        if current is None:
            current = bool(self.chat_log_in_game)
        self.config["chat_log"] = not current
        self._write_companion_state()
        if self.is_in_game() and self.chat_log_in_game is not None and self.chat_log_in_game == current:
            self._chat_log_pending = not current         # applied by the addon at the next /reload
            # The addon only reads the setting at login / reload, and nothing can be sent to it
            # in game: the player is told in the overlay (seen in game), the options and Windows.
            text = self.texts("chat_log_reload")
            self._notice("general", text)
            reminder = f"{self.texts('menu_chat_log')} — {text}"   # alone in the overlay: says what
            self.overlay.add_status(reminder)
            self.tray.notify(reminder)

    def _overlay_moved(self):
        self._write_companion_state()
        if self.is_in_game():
            self.tray.notify(self.texts("overlay_moved"))

    def _heartbeat(self):
        now = time.monotonic()
        if now - self._last_heartbeat < HEARTBEAT_INTERVAL_S:
            return
        self._last_heartbeat = now
        self._write_companion_state()

    def _check_reload_needed(self):
        """Game in the world without a grid: the addon started before the companion."""
        if self._reload_hint_sent or self.is_in_game() or not (self.bridge and self.bridge.game_window):
            self._game_seen_since = None
            return
        now = time.monotonic()
        if self._game_seen_since is None:
            self._game_seen_since = now
        elif now - self._game_seen_since > RELOAD_HINT_AFTER_S and not self.bridge.last_seen \
                and winutil.foreground_window() == self.bridge.game_window:
            self._reload_hint_sent = True
            self.tray.notify(self.texts("reload_needed"))

    def _on_update_event(self, kind, value):
        """Update window: offered when a new version is found (by the periodic check or the
        player's), then the download the player chose, with its progress."""
        if kind == "exit_check":
            self._exit_check_done(value)
        elif kind in ("available", "offer"):
            if self._quitting:
                return
            if not updater.is_frozen():
                self.tray.notify(self.texts("update_available", version=value))
                return
            if self._update_dialog and self._update_dialog.alive():
                self._update_dialog.window.lift()
                return
            if value in (self.update_at_exit, self.pending_update):
                return
            self.tray.notify(self.texts("update_available", version=value))
            self._update_dialog = UpdateDialog(self.root, self.texts, value, __version__,
                                               on_now=lambda: self._download_update(value),
                                               on_exit=lambda: self._update_at_exit(value))
        elif kind == "progress":
            if self._update_dialog:
                self._update_dialog.set_progress(*value)
        elif kind == "ready":
            if self._quitting:
                updater.apply_update_and_restart(restart=False)
                self._shutdown()
                return
            in_game = self.is_in_game()
            if self._update_dialog:
                self._update_dialog.set_status(self.texts("upd_ready_in_game" if in_game else "upd_ready_restart"))
            self._notice("general", self.texts("update_ready", version=value), "ok")
            self.pending_update = value          # installed (and restarted) once out of the game world
            self.root.after(UPDATE_RESTART_DELAY_MS, self._maybe_apply_update)
        elif kind == "failed":
            if self._quitting:
                self._shutdown()
                return
            if self._update_dialog:
                self._update_dialog.set_status(self.texts("upd_error"), error=True)
            self._notice("general", self.texts("upd_error"), "error")

    def _download_update(self, version):
        """Download chosen by the player: in a thread, its progress shown in the update window."""
        last = [-1]

        def progress(done, expected):
            percent = done * 100 // expected if expected else done >> 22
            if percent != last[0]:
                last[0] = percent
                self.display_queue.put(("update", ("progress", (done, expected))))

        def work():
            try:
                updater.download_update(version, progress)
                self.display_queue.put(("update", ("ready", version)))
            except Exception:
                log.exception("Update download failed")
                self.display_queue.put(("update", ("failed", version)))
        threading.Thread(target=work, name="UpdateDownload", daemon=True).start()

    def _update_at_exit(self, version):
        self.update_at_exit = version
        text = self.texts("upd_at_exit_set", version=version)
        self._notice("general", text, "ok")
        self.tray.notify(text)

    def _maybe_apply_update(self):
        """Installs a downloaded update only when no character is in the world."""
        if not self.pending_update or self.is_in_game() or self.overlay.edit_mode:
            return
        version, self.pending_update = self.pending_update, None
        self.tray.notify(self.texts("update_applying", version=version))
        if updater.apply_update_and_restart():
            self._quitting = True
            self._shutdown()

    def _handle(self, action, *args):
        if action == "toggle_chat_log":
            self._toggle_chat_log()
        elif action == "toggle":
            self.config[args[0]] = not self.config[args[0]]
        elif action == "set":
            self.config[args[0]] = args[1]
            self.overlay.apply_style()
        elif action == "set_model":
            self.config["model"] = args[0]
            self._model_override = None
            if self.pipeline and models.usable_model(args[0])[0] != self.loaded_model:
                self.pipeline.reload_engine()
            if args[0] != "auto":
                self._download_model(args[0])     # the player clicked it: download if missing
            elif not models.installed_models():
                self._offer_model()
        elif action == "set_lang":
            self.config["target_lang"] = args[0]          # None: the game's language
            self._status("ready", lang=LANGUAGES[self.target_lang()])
            self._write_companion_state()   # the addon's own texts follow at the next /reload
            if self.options and self.options.alive():
                # The window speaks the reading language: built again in the new one.
                tab = self.options.current_tab()
                self.options.close()
                self._open_options(tab)
        elif action == "toggle_edit":
            if not (self.game_running() or self.overlay.edit_mode):
                self._notice("display", self.texts("need_game"), "error")
                return
            self.overlay.set_edit_mode(not self.overlay.edit_mode)
            if not self.overlay.edit_mode:
                self._overlay_moved()
        elif action == "reset_position":
            if not self.game_running():
                self._notice("display", self.texts("need_game"), "error")
                return
            self.overlay.reset_position()
            self._overlay_moved()
        elif action == "toggle_autostart":
            self.config["autostart"] = not self.config["autostart"]
            winutil.set_autostart(APP_NAME, self.config["autostart"])
        elif action == "open_glossary":
            open_path(Glossary.user_file())
            self._notice("translation", self.texts("glossary_opened"))
        elif action == "reload_glossary":
            entries, error = self.glossary.reload()
            if error:
                self._notice("translation", self.texts("glossary_error", error=error), "error")
            else:
                self._notice("translation", self.texts("glossary_reloaded", n=entries), "ok")
        elif action == "scroll":
            self.overlay.scroll(args[0])
            return
        elif action == "launch_game":
            self._launch_game(self.flavors[args[0]])
        elif action == "check_updates":
            self._check_updates_now()
        elif action == "toggle_auto_update":
            self.config["auto_update"] = not self.config["auto_update"]
            self._start_updater()
        elif action == "open_logs":
            open_path(log_path())
        elif action == "screenshot":
            delay = args[0] if args else 0
            if delay:
                # From the menu: leave time to go back to the game.
                self.tray.notify(self.texts("screenshot_soon"))
                self.root.after(int(delay * 1000), lambda: self.dispatch("screenshot"))
            else:
                self._take_screenshot()
        elif action == "open_options":
            self._open_options()
        elif action == "quit":
            if self.is_in_game():
                self._confirm_quit()
                return
            self.quit()
            return
        self.tray.refresh()
        if self.options:
            self.options.refresh()

    def _launch_game(self, flavor):
        command = wow.game_command(flavor, self.config["launch_code"])
        if not command:
            self.tray.notify(self.texts("launch_failed"))
            return
        if len(command) == 2 and command[1].startswith("--exec="):
            # Battle.net reads its raw command line: keep the exact --exec="launch CODE" form.
            command = f'"{command[0]}" --exec="{command[1][len("--exec="):]}"'
        log.info("Launching %s (flavor %s, product %s)", command, flavor.name, flavor.product or "?")
        subprocess.Popen(command, close_fds=True)

    def _start_updater(self):
        if self.config["auto_update"] and not self.updater:
            self.updater = updater.Updater(__version__, lambda kind, version: self.display_queue.put(("update", (kind, version))))
            self.updater.start()
        elif not self.config["auto_update"] and self.updater:
            self.updater.stop()
            self.updater = None

    def _status(self, key, **extra):
        extra.setdefault("log", str(log_path()))
        self.display_queue.put(("status", (key, extra)))

    def _on_pipeline_status(self, key):
        extra = {"lang": LANGUAGES[self.target_lang()]} if key == "ready" else {}
        self._status(key, **extra)

    def _watch_game_state(self):
        """The tray menu only re-reads which items are enabled when told to: refresh it as soon
        as the game opens or closes ("Move / resize" is greyed while the game is not running)."""
        try:
            state = (self.game_running(), self.overlay.edit_mode)
            if state != getattr(self, "_menu_game_state", None):
                if state[0] and not (getattr(self, "_menu_game_state", None) or (False,))[0]:
                    self._check_addon("game started")      # the game reads its addons now
                self._menu_game_state = state
                self.tray.refresh()
        except Exception:
            log.exception("Game state check failed")
        self.root.after(GAME_STATE_CHECK_MS, self._watch_game_state)

    def _check_tray(self):
        """The icon must never vanish while the companion runs: recreated if its thread ended."""
        try:
            if not self.tray.alive():
                log.warning("Tray icon thread ended: recreating the icon")
                self.tray.stop()
                self.tray = Tray(self.config, self.texts, self.dispatch, [wow.flavor_label(f) for f in self.flavors])
                self.tray.on_muted = lambda message: self.display_queue.put(("muted", message))
                self.tray.start()
                self._menu_game_state = None      # the new icon's menu gets the current state
        except Exception:
            log.exception("Tray icon check failed")
        self.root.after(TRAY_CHECK_MS, self._check_tray)

    def _confirm_quit(self):
        """A character is in the world: the grid will show again once the companion is gone
        (the game cannot be told). The player is shown his own key to hide it."""
        if self._quit_dialog and self._quit_dialog.alive():
            return
        keys = " · ".join(k for k in (key_label(self.toggle_key), "/wct toggle", "/reload") if k)
        self._quit_dialog = ConfirmDialog(self.root, self.texts("menu_quit"), self.texts("quit_in_game"), keys,
                                          self.texts("menu_quit"), self.texts("cancel"), self.quit)

    def quit(self):
        """Closes the companion; first downloads the update the player chose to install when
        closing (its window shows the download), or installs one already downloaded."""
        if self._quitting:
            return
        self._quitting = True
        if self.pending_update and updater.update_ready():
            updater.apply_update_and_restart(restart=False)
        elif self.update_at_exit and updater.is_frozen():
            if self._update_dialog and self._update_dialog.alive():
                self._update_dialog.close()
            self._update_dialog = UpdateDialog(self.root, self.texts, self.update_at_exit, __version__)
            self._download_update(self.update_at_exit)
            return                                   # _shutdown() once downloaded (or failed)
        elif updater.is_frozen() and self.config["auto_update"]:
            self._check_update_on_exit()
            return                                   # _shutdown() once answered
        self._shutdown()

    def _check_update_on_exit(self):
        """Last look at GitHub when closing: a newer version is offered (update and quit, or
        just quit); nothing is downloaded without the player's click. No answer within a few
        seconds (no network): the companion simply closes."""
        def work():
            tag = None
            try:
                release = updater.latest_release(timeout=EXIT_CHECK_TIMEOUT_S)
                tag = (release or {}).get("tag_name") or None
            except Exception:
                log.info("Update check at exit failed", exc_info=True)
            self.display_queue.put(("update", ("exit_check", tag)))
        threading.Thread(target=work, name="UpdateCheckAtExit", daemon=True).start()
        self.root.after(int(EXIT_CHECK_TIMEOUT_S * 1000) + 1000, lambda: self._exit_check_done(None))

    def _exit_check_done(self, tag):
        if self._exit_checked:
            return
        self._exit_checked = True
        if not tag or updater.parse_version(tag) <= updater.parse_version(__version__):
            self._shutdown()
            return
        log.info("Update available at exit: %s -> %s", __version__, tag)
        if self._update_dialog and self._update_dialog.alive():
            self._update_dialog.close()
        self._update_dialog = UpdateDialog(self.root, self.texts, tag, __version__,
                                           on_now=lambda: self._download_update(tag), on_quit=self._shutdown)

    def _shutdown(self):
        if self._shut_down:
            return
        self._shut_down = True
        log.info("Quitting")
        self._write_companion_state(alive=False)
        for worker in (self.bridge, getattr(self, "pipeline", None), self.updater):
            if worker:
                worker.stop()
        self.tray.stop()
        self.root.destroy()

    def run(self):
        updater.cleanup_previous_update()
        for leftover in config_dir().glob("capture_*.png"):   # diagnostics of older versions
            try:
                leftover.unlink()
            except OSError:
                pass  # still in use or already gone: removed next time
        wait = 20.0 if "--after-update" in sys.argv else 0.0
        if not winutil.acquire_single_instance(APP_NAME, wait_s=wait):
            close_splash()
            winutil.message_box(APP_NAME, self.texts("already_running"))
            return 0
        winutil.set_dpi_aware()
        log.info("%s %s starting", APP_NAME, __version__)

        self.root = tk.Tk()
        if not self._detect_wow(self.root):
            close_splash()
            winutil.message_box(APP_NAME, self.texts("wow_not_found_exit"), error=True)
            return 1

        self.overlay = Overlay(self.root, self.config, self.texts, self.addon_rect, self.is_in_game,
                               lambda: self.bridge.grid_screen_rect if self.bridge else None,
                               lambda: bool(self.bridge and self.bridge.masking_supported),
                               get_lang=self.target_lang)
        winutil.start_wheel_hook(self.overlay.wants_wheel, lambda delta: self.dispatch("scroll", delta))
        self.tray = Tray(self.config, self.texts, self.dispatch, [wow.flavor_label(f) for f in self.flavors])
        self.tray.on_muted = lambda message: self.display_queue.put(("muted", message))
        self.tray.start()
        self.root.after(TRAY_CHECK_MS, self._check_tray)
        self.root.after(GAME_STATE_CHECK_MS, self._watch_game_state)
        close_splash()
        self._start_updater()
        if self.config["autostart"]:
            winutil.set_autostart(APP_NAME, True)  # keep the path valid if the exe was moved

        if self._install_addon():
            self._status("addon_updated")
            self.tray.notify(self.texts("addon_updated"))
        self.root.after(ADDON_CHECK_MS, self._watch_addon)

        if models.installed_models():
            self._start_pipeline()
        else:
            self._status("no_model")
            self._offer_model()
        self.chatlog = ChatLogRecovery(f.path for f in self.flavors)
        self.bridge = PixelBridge(self._on_bridge_lines, lambda covers: self.display_queue.put(("covers", covers)),
                                  lambda kind: self.dispatch("screenshot") if kind == "shot" else None,
                                  self._on_bridge_gap, lambda state: self.display_queue.put(("state", state)))
        self.bridge.expected_origins = self._expected_grid_origins
        self.bridge.start()

        self.root.after(UI_POLL_MS, self._poll)
        self.root.mainloop()
        # Nothing may keep the process alive without its icon (the icon's thread is not a
        # daemon thread): end it for good once everything is saved.
        logging.shutdown()
        os._exit(0)
        return 0   # not reached: os._exit() has ended the process

    def _on_bridge_lines(self, lines):
        self.chatlog.delivered(lines)
        self._submit(lines)

    def _on_bridge_gap(self, start, end, away):
        """Lines the bridge missed: read back from the game's chat log when it writes one (the
        game may write it a little late: read again after a while), else only noted."""
        def recover():
            for delay in RECOVER_DELAYS_S:
                time.sleep(delay)
                try:
                    if not self.chatlog.logging_since(start):
                        continue
                    lines = self.chatlog.missed_lines(start, end)
                except OSError:
                    log.exception("Chat log could not be read")
                    return
                if lines:
                    log.info("%d missed chat line(s) read back from the chat log", len(lines))
                    self._submit(lines)
            if not self.chatlog.log_file():
                log.info("No chat log (/chatlog in game): the missed lines cannot be read back")
        threading.Thread(target=recover, name="ChatLogRecovery", daemon=True).start()

    def _submit(self, lines):
        if not self.config["enabled"] and lines and not getattr(self, "_off_logged", False):
            self._off_logged = True
            log.info("Chat lines received but translation is turned off (option)")
        elif self.config["enabled"]:
            self._off_logged = False
        if self.config["enabled"] and self.pipeline:
            for line in lines:
                self.pipeline.submit(line)


def selftest():
    """Headless check used by the build: engine, detection, glossary and overlay rendering."""
    close_splash()
    from . import bridge
    from .pipeline import DisplayLine

    # Bridge: a packet drawn as the addon does is found and decoded.
    payload = "guild\x1f[Guild] Bob Stone\x1fBob Stone\x1fLF tank for the dungeon tonight, who is in?".encode()
    import numpy as np
    img = np.full((300, 600, 3), 40, dtype=np.int16)
    for index, value in enumerate(bridge.encode(1, 1, payload)):
        row, col = divmod(index, bridge.COLS)
        y, x = 40 + row * bridge.CELL, 300 + col * bridge.CELL
        img[y:y + bridge.CELL, x:x + bridge.CELL] = [
            base + bridge.DELTA * bool(value & mask) for base, mask in zip(bridge.BASE, (4, 2, 1))]
    line = bridge.parse_payload(bridge.find_grid(img)[2][3])[0]

    glossary = Glossary()
    pipeline = TranslationPipeline(None, None, glossary, lambda: "fr", print, print)
    pipeline.detector = LanguageDetector()
    pipeline.engine = TranslationEngine(models_dir(), models.usable_model("standard")[1])
    result = pipeline.process(line)
    print("selftest translation:", result.text)
    assert result.translated and "tank" in result.text and "donjon" in result.text

    config = Config()
    root = tk.Tk()
    overlay = Overlay(root, config, Texts(lambda: "fr"), lambda: None)
    overlay.add_line(result)
    overlay.add_line(DisplayLine(line, line.text, False))
    root.after(1000, root.destroy)
    root.mainloop()
    print("selftest OK")
    return 0


def main():
    setup_logging()
    if "--selftest" in sys.argv:
        return selftest()
    try:
        return CompanionApp().run()
    except Exception:
        log.exception("Fatal error")
        winutil.message_box(APP_NAME, f"Fatal error, see {config_dir() / 'companion.log'}", error=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
