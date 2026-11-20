"""Installs / updates the bundled addon into every WoW flavor, like the Raider.IO client does."""

import logging
import re
import shutil

from . import ADDON_NAME
from .paths import addon_source_dir
from .wow import Flavor, interface_number

log = logging.getLogger(__name__)

TOC_NAME = f"{ADDON_NAME}.toc"
COMPANION_FILE = "Data/Companion.lua"   # rewritten by the companion while it runs: never overwritten here
# Files of earlier versions, all at the addon's root before it had folders: removed on update.
OLD_FILES = ("Locales.lua", "Companion.lua", "Bridge.lua", "Chat.lua")


def _toc_field(text, field):
    match = re.search(rf"^##\s*{field}\s*:\s*(.+)$", text, re.MULTILINE)
    return match.group(1).strip() if match else None


def _render_toc(template: str, interface):
    if not interface:
        return template
    current = _toc_field(template, "Interface") or ""
    values = [v.strip() for v in current.split(",") if v.strip()]
    if str(interface) not in values:
        values.insert(0, str(interface))
    return re.sub(r"^##\s*Interface\s*:.*$", f"## Interface: {', '.join(values)}", template, count=1, flags=re.MULTILINE)


def enable_for_all_characters(flavor: Flavor) -> int:
    """Ticks the addon in every character's AddOns.txt (taken into account at next game start).

    WoW rewrites these files on logout/reload, so this only helps when the game is closed,
    which is the normal case once the companion starts with Windows.
    """
    account_dir = flavor.path / "WTF" / "Account"
    if not account_dir.is_dir():
        return 0
    changed = 0
    line_re = re.compile(rf"^{re.escape(ADDON_NAME)}[ \t]*:[ \t]*(\w+)[ \t]*\r?$", re.MULTILINE | re.IGNORECASE)
    for path in list(account_dir.glob("*/AddOns.txt")) + list(account_dir.glob("*/*/*/AddOns.txt")):
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        match = line_re.search(content)
        if match and match.group(1).lower() == "enabled":
            continue
        if match:
            content = line_re.sub(f"{ADDON_NAME}: enabled", content, count=1)
        else:
            content = content.rstrip("\r\n") + ("\n" if content.strip() else "") + f"{ADDON_NAME}: enabled\n"
        try:
            path.write_text(content, encoding="utf-8")
            changed += 1
        except OSError:
            log.exception("Cannot update %s", path)
    if changed:
        log.info("Addon enabled in %d AddOns.txt file(s) for %s", changed, flavor.name)
    return changed


def _addon_files(source):
    """Relative paths ("Core/Bridge.lua", "Locales/fr.lua"...) of the bundled addon's files."""
    return sorted(p.relative_to(source).as_posix() for p in source.rglob("*") if p.is_file())


def install(flavor: Flavor) -> bool:
    """Returns True when files were written (the game then needs a /reload)."""
    source = addon_source_dir()
    if not source.is_dir():
        log.error("Bundled addon not found at %s", source)
        return False

    template = (source / TOC_NAME).read_text(encoding="utf-8")
    toc = _render_toc(template, interface_number(flavor.root, flavor.product))
    target = flavor.addons_dir / ADDON_NAME
    # Never an old root file, even if one was left in the source next to the folders.
    files = [f for f in _addon_files(source) if f not in (TOC_NAME, COMPANION_FILE) and f not in OLD_FILES]
    old = [target / name for name in OLD_FILES if (target / name).is_file()]

    installed_toc = target / TOC_NAME
    if installed_toc.is_file() and not old:
        current = installed_toc.read_text(encoding="utf-8", errors="ignore")
        same_files = all((target / f).is_file() and (target / f).read_bytes() == (source / f).read_bytes()
                         for f in files)
        if current == toc and same_files and (target / COMPANION_FILE).is_file():
            return False

    for name in files:
        (target / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / name, target / name)
    companion = target / COMPANION_FILE
    if not companion.is_file():
        companion.parent.mkdir(parents=True, exist_ok=True)
        previous = target / "Companion.lua"           # an earlier version's, at the root
        shutil.copy2(previous if previous.is_file() else source / COMPANION_FILE, companion)
    for path in old:
        try:
            path.unlink()
        except OSError:
            log.warning("Could not remove the old addon file %s", path)
    (target / TOC_NAME).write_text(toc, encoding="utf-8")
    log.info("Addon installed/updated in %s (version %s)", target, _toc_field(toc, "Version"))
    return True


def write_companion_state(flavor: Flavor, seen, overlay_rect=None, lang=None, chat_log=None):
    """Writes Companion.lua (read by the addon at login and on /reload, never written by WoW)."""
    target = flavor.addons_dir / ADDON_NAME
    if not target.is_dir():
        return False
    fields = [f"seen = {int(seen)}"]
    if lang and lang.isalpha():
        fields.append(f'lang = "{lang}"')   # the addon speaks the player's reading language
    if chat_log is not None:
        fields.append(f"chatLog = {'true' if chat_log else 'false'}")   # applied at login / reload
    if overlay_rect:
        rect = ", ".join(f"{k} = {float(overlay_rect[k])!r}" for k in "xywh")
        fields.append(f"overlayRect = {{ {rect} }}")
    content = ("-- Written by WoWChatTranslatorCompagnion while it runs (WoW only reads this file, at login\n"
               "-- and on /reload).\n"
               f"WoWChatTranslatorCompanion = {{ {', '.join(fields)} }}\n")
    path = target / COMPANION_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(path)
    return True
