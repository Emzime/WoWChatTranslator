"""Installs / updates the bundled addon into every WoW flavor, like the Raider.IO client does."""

import logging
import re
import shutil

from . import ADDON_NAME
from .paths import addon_source_dir
from .wow import Flavor, interface_number

log = logging.getLogger(__name__)

TOC_NAME = f"{ADDON_NAME}.toc"
COMPANION_FILE = "Companion.lua"   # rewritten by the companion while it runs: never overwritten here


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


def install(flavor: Flavor) -> bool:
    """Returns True when files were written (the game then needs a /reload)."""
    source = addon_source_dir()
    if not source.is_dir():
        log.error("Bundled addon not found at %s", source)
        return False

    template = (source / TOC_NAME).read_text(encoding="utf-8")
    toc = _render_toc(template, interface_number(flavor.root, flavor.product))
    target = flavor.addons_dir / ADDON_NAME

    installed_toc = target / TOC_NAME
    if installed_toc.is_file():
        current = installed_toc.read_text(encoding="utf-8", errors="ignore")
        same_files = all(
            (target / f.name).is_file() and (target / f.name).read_bytes() == f.read_bytes()
            for f in source.iterdir() if f.is_file() and f.name not in (TOC_NAME, COMPANION_FILE)
        )
        if current == toc and same_files:
            return False

    target.mkdir(parents=True, exist_ok=True)
    for item in source.iterdir():
        if not item.is_file() or item.name == TOC_NAME:
            continue
        if item.name == COMPANION_FILE and (target / item.name).exists():
            continue
        shutil.copy2(item, target / item.name)
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
    tmp = path.with_suffix(".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(path)
    return True
