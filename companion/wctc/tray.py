"""System tray icon and menu (pystray runs in its own thread; actions are forwarded to Tk)."""

import pystray

from . import APP_NAME
from .icon import make_icon_image


class Tray:
    def __init__(self, config, texts, dispatch, games=()):
        """`dispatch(action, *args)` must be thread-safe (it queues work for the Tk thread).
        `games` lists the labels of the detected WoW flavors, in the app's flavor order."""
        self.config = config
        self.on_muted = None
        self.games = list(games)
        self.texts = texts
        self.dispatch = dispatch
        self.icon = pystray.Icon(APP_NAME, make_icon_image(), APP_NAME, menu=self._menu())

    def _menu(self):
        """Only what is used while playing; every setting is in the Options window."""
        t, cfg, dispatch = self.texts, self.config, self.dispatch

        def action(name, *args):
            return lambda icon, item: dispatch(name, *args)

        if len(self.games) == 1:
            launch = [pystray.MenuItem(lambda _: t("menu_launch", game=self.games[0]), action("launch_game", 0))]
        elif self.games:
            launch = [pystray.MenuItem(lambda _: t("menu_launch_group"), pystray.Menu(*(
                pystray.MenuItem(label, action("launch_game", i)) for i, label in enumerate(self.games))))]
        else:
            launch = []
        if launch:
            launch.append(pystray.Menu.SEPARATOR)

        return pystray.Menu(
            *launch,
            pystray.MenuItem(lambda _: t("menu_enabled"), action("toggle", "enabled"), checked=lambda _: cfg["enabled"]),
            pystray.MenuItem(lambda _: t("menu_screenshot"), action("screenshot", 3.0)),
            pystray.MenuItem(lambda _: t("menu_edit"), action("toggle_edit"), checked=lambda _: dispatch.edit_mode(),
                             enabled=lambda _: dispatch.game_running() or dispatch.edit_mode()),
            pystray.Menu.SEPARATOR,
            # Default item: a click on the icon opens the options.
            pystray.MenuItem(lambda _: t("menu_options"), action("open_options"), default=True),
            pystray.MenuItem(lambda _: t("menu_quit"), action("quit")),
        )

    def start(self):
        self.icon.run_detached()

    def alive(self):
        """False if the icon's thread ended (its window gone: Windows then removes the icon as
        soon as the mouse passes over it)."""
        thread = getattr(self.icon, "_thread", None)
        return thread is None or thread.is_alive()   # None: still starting

    def notify(self, message):
        if not self.config.get("notifications", True):
            if self.on_muted:
                self.on_muted(message)    # shown in the Options window instead, if it is open
            return
        try:
            self.icon.notify(message, APP_NAME)
        except Exception:
            pass

    def refresh(self):
        self.icon.update_menu()

    def stop(self):
        try:
            self.icon.stop()
        except Exception:
            pass
