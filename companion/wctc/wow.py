"""Locating the WoW installation, its flavors (_retail_, Forever...) and game metadata."""

import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path

log = logging.getLogger(__name__)

FLAVOR_RE = re.compile(r"^_[a-z0-9_]+_$", re.IGNORECASE)

COMMON_ROOTS = [
    r"C:\Program Files (x86)\World of Warcraft",
    r"C:\Program Files\World of Warcraft",
    r"C:\World of Warcraft",
    r"D:\World of Warcraft",
    r"D:\Games\World of Warcraft",
    r"D:\Jeux\World of Warcraft",
    r"E:\World of Warcraft",
    r"E:\Games\World of Warcraft",
]

# WoW client locale -> engine language code
LOCALE_TO_LANG = {
    "frFR": "fr", "enUS": "en", "enGB": "en", "deDE": "de", "esES": "es", "esMX": "es",
    "itIT": "it", "ptBR": "pt", "ptPT": "pt", "ruRU": "ru",
}


@dataclass
class Flavor:
    root: Path        # World of Warcraft folder
    path: Path        # e.g. <root>/_retail_
    product: str      # e.g. "wow"

    @property
    def name(self):
        return self.path.name

    @property
    def addons_dir(self):
        return self.path / "Interface" / "AddOns"



def _registry_roots():
    roots = []
    try:
        import winreg
    except ImportError:
        return roots
    keys = [
        r"SOFTWARE\WOW6432Node\Blizzard Entertainment\World of Warcraft",
        r"SOFTWARE\Blizzard Entertainment\World of Warcraft",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\World of Warcraft",
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\World of Warcraft",
    ]
    for key in keys:
        for value in ("InstallPath", "InstallLocation", "GamePath"):
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key) as handle:
                    roots.append(winreg.QueryValueEx(handle, value)[0])
            except OSError:
                continue
    return roots


def normalize_root(path) -> Path:
    """Accepts the WoW folder, a flavor folder or an executable path."""
    p = Path(path)
    if p.is_file():
        p = p.parent
    if FLAVOR_RE.match(p.name):
        p = p.parent
    return p


def find_roots(configured=None):
    candidates = ([configured] if configured else []) + _registry_roots() + COMMON_ROOTS
    seen, roots = set(), []
    for candidate in candidates:
        if not candidate:
            continue
        root = normalize_root(candidate)
        key = str(root).lower()
        if key in seen or not root.is_dir():
            continue
        seen.add(key)
        if find_flavors(root):
            roots.append(root)
    return roots


def read_product(flavor_path: Path) -> str:
    """Reads the Battle.net product code from .flavor.info (last non-empty line)."""
    info = flavor_path / ".flavor.info"
    try:
        lines = [l.strip() for l in info.read_text(encoding="utf-8", errors="ignore").splitlines() if l.strip()]
        if len(lines) >= 2:
            return lines[-1]
    except OSError:
        pass
    return ""


def find_flavors(root: Path):
    flavors = []
    try:
        entries = list(root.iterdir())
    except OSError:
        return flavors
    for entry in entries:
        if not entry.is_dir() or not FLAVOR_RE.match(entry.name):
            continue
        has_exe = any(entry.glob("Wow*.exe")) or any(entry.glob("World of Warcraft*.app"))
        if has_exe or (entry / "Interface").is_dir() or (entry / "WTF").is_dir():
            flavors.append(Flavor(root=root, path=entry, product=read_product(entry)))
    return flavors


def interface_number(root: Path, product: str):
    """Computes the .toc Interface number from .build.info (e.g. 12.0.1.x -> 120001)."""
    info = root / ".build.info"
    try:
        lines = info.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return None
    if not lines:
        return None
    header = [h.split("!")[0] for h in lines[0].split("|")]
    try:
        version_idx = header.index("Version")
        product_idx = header.index("Product")
    except ValueError:
        return None
    for line in lines[1:]:
        cols = line.split("|")
        if len(cols) <= max(version_idx, product_idx):
            continue
        if product and cols[product_idx] != product:
            continue
        parts = cols[version_idx].split(".")
        try:
            major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
        except (IndexError, ValueError):
            continue
        return major * 10000 + minor * 100 + patch
    return None


def game_language(flavor: Flavor):
    """Returns the engine language matching the client's text locale, if any."""
    config = flavor.path / "WTF" / "Config.wtf"
    try:
        content = config.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None
    match = re.search(r'SET\s+textLocale\s+"(\w+)"', content)
    return LOCALE_TO_LANG.get(match.group(1)) if match else None


def windows_language():
    try:
        import ctypes
        import locale
        lang_id = ctypes.windll.kernel32.GetUserDefaultUILanguage()
        name = locale.windows_locale.get(lang_id, "")
    except (AttributeError, OSError):
        name = os.environ.get("LANG", "")
    if not name:
        return None
    code = name[:2].lower()
    return {"nb": "no", "nn": "no"}.get(code, code)   # Norwegian Bokmål / Nynorsk


def saved_variables_files(flavor: Flavor, addon_name: str):
    account_dir = flavor.path / "WTF" / "Account"
    if not account_dir.is_dir():
        return []
    files = list(account_dir.glob(f"*/SavedVariables/{addon_name}.lua"))
    return sorted(files, key=lambda f: f.stat().st_mtime, reverse=True)


FLAVOR_LABELS = {
    "_retail_": "World of Warcraft",
    "_classic_": "WoW Classic",
    "_classic_era_": "WoW Classic Era",
    "_ptr_": "WoW PTR",
    "_xptr_": "WoW PTR 2",
    "_beta_": "WoW Beta",
}
_EXE_PREFERENCE = ("Wow.exe", "WowClassic.exe", "WowT.exe", "WowB.exe")
# Battle.net product uid per flavor folder, used when .flavor.info is missing.
_FOLDER_PRODUCTS = {
    "_retail_": "wow",
    "_classic_": "wow_classic",
    "_classic_era_": "wow_classic_era",
    "_ptr_": "wowt",
    "_xptr_": "wowxptr",
    "_beta_": "wow_beta",
}
BATTLENET_DEFAULT_PATHS = (
    r"C:\Program Files (x86)\Battle.net\Battle.net.exe",
    r"C:\Program Files\Battle.net\Battle.net.exe",
)


def flavor_label(flavor: Flavor):
    if flavor.name in FLAVOR_LABELS:
        return FLAVOR_LABELS[flavor.name]
    return "WoW " + flavor.name.strip("_").replace("_", " ").title()


def game_executable(flavor: Flavor):
    for name in _EXE_PREFERENCE:
        if (flavor.path / name).is_file():
            return flavor.path / name
    candidates = sorted(flavor.path.glob("Wow*.exe"))
    return candidates[0] if candidates else None


def battlenet_executable():
    """Locates Battle.net.exe (registry first, then the default install folders)."""
    candidates = []
    try:
        import winreg
        keys = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Battle.net", "InstallLocation"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Battle.net", "InstallLocation"),
            (winreg.HKEY_CLASSES_ROOT, r"battlenet\shell\open\command", ""),
        ]
        for hive, key, value in keys:
            try:
                with winreg.OpenKey(hive, key) as handle:
                    data = winreg.QueryValueEx(handle, value)[0]
            except OSError:
                continue
            match = re.search(r'"?([^"]+?Battle\.net(?: Launcher)?\.exe)"?', data, re.IGNORECASE)
            candidates.append(Path(match.group(1)) if match else Path(data) / "Battle.net.exe")
    except ImportError:
        pass
    candidates += [Path(p) for p in BATTLENET_DEFAULT_PATHS]
    for candidate in candidates:
        # The protocol handler may point to the launcher; the client sits next to it.
        for exe in (candidate, candidate.with_name("Battle.net.exe")):
            if exe.is_file():
                return exe
    return None


# Battle.net launch codes ("Battle.net Launcher.exe --exec=\"launch <code>\"").
_LAUNCH_CODES = (
    ("forever", "WoWF"),
    ("classic_era", "WoWCE"),
    ("classic", "WoWC"),
    ("ptr", "WoWT"),
    ("beta", "WoWB"),
)


def launch_code(flavor: Flavor, override=None):
    if override:
        return override
    names = f"{flavor.product} {flavor.name}".lower()
    for marker, code in _LAUNCH_CODES:
        if marker in names:
            return code
    return "WoW"


def battlenet_launcher():
    bnet = battlenet_executable()
    if not bnet:
        return None
    launcher = bnet.with_name("Battle.net Launcher.exe")
    return launcher if launcher.is_file() else bnet


def game_command(flavor: Flavor, override_code=None):
    """Asks Battle.net to start the game, so the saved session is used (no login screen)."""
    launcher = battlenet_launcher()
    if launcher:
        return [str(launcher), f"--exec=launch {launch_code(flavor, override_code)}"]
    exe = game_executable(flavor)
    return [str(exe)] if exe else None
