"""Translation model choice: Standard or Quality, both downloaded once from the GitHub "models"
release, only when the player chooses one (first launch window or menu): never on their own.
The companion's own download stays small that way.

"auto" uses Quality if it is installed and the PC can run it comfortably (memory and
processor), Standard otherwise; whichever is installed when only one is.
"""

import logging
import os
import sys
import threading
import zipfile
from pathlib import Path

from .paths import config_dir, models_dir

log = logging.getLogger(__name__)

MODELS = {
    # NLLB-200 (Meta, CC-BY-NC 4.0: free, non-commercial use only).
    "standard": {"dir": "nllb-200-distilled-600m", "asset": "WoWChatTranslator-model-standard.zip", "size_mb": 600},
    "quality": {"dir": "nllb-200-distilled-1.3b", "asset": "WoWChatTranslator-model-quality.zip", "size_mb": 1400},
    # Same files as Standard, lighter settings (see TranslationEngine light mode).
    "light": {"dir": "nllb-200-distilled-600m", "asset": "WoWChatTranslator-model-standard.zip", "size_mb": 600,
              "light": True, "files_of": "standard"},
}
CHOICES = ("auto", "light", "standard", "quality")
# "auto" falls back along this list when translations lag while playing.
SLOWER_TO_FASTER = ("quality", "standard", "light")
# Models are published once in the "models" release, not with every version.
MODELS_RELEASE_TAG = "models"
# Quality model: about twice the work per line. Below this, translations would lag.
QUALITY_MIN_RAM_GB = 16
QUALITY_MIN_CPUS = 8


def folder_writable(folder):
    try:
        folder.mkdir(parents=True, exist_ok=True)
        probe = folder / ".write_test"
        probe.write_bytes(b"")
        probe.unlink()
        return True
    except OSError:
        return False


def fallback_models_dir():
    return config_dir() / "models"


def model_path(key):
    """Folder of a model if it is present (next to the .exe or downloaded), else None."""
    name = MODELS[key]["dir"]
    for base in (models_dir(), fallback_models_dir()):
        if (base / name / "model.bin").is_file():
            return base / name
    return None


def total_ram_gb():
    if sys.platform == "win32":
        import ctypes

        class MemoryStatus(ctypes.Structure):
            _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong),
                        ("total_phys", ctypes.c_ulonglong), ("avail_phys", ctypes.c_ulonglong),
                        ("total_page", ctypes.c_ulonglong), ("avail_page", ctypes.c_ulonglong),
                        ("total_virtual", ctypes.c_ulonglong), ("avail_virtual", ctypes.c_ulonglong),
                        ("avail_extended", ctypes.c_ulonglong)]

        status = MemoryStatus()
        status.length = ctypes.sizeof(MemoryStatus)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            return status.total_phys / 2 ** 30
        return 0.0
    try:
        return os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / 2 ** 30
    except (ValueError, OSError, AttributeError):
        return 0.0


def machine_suits_quality():
    return total_ram_gb() >= QUALITY_MIN_RAM_GB and (os.cpu_count() or 1) >= QUALITY_MIN_CPUS


def machine_is_modest():
    """Few processor cores or little memory: the Light mode keeps translations quick."""
    return (os.cpu_count() or 1) <= 4 or 0 < total_ram_gb() < 8


def files_key(key):
    """The model whose files a choice uses ("light" runs the Standard files)."""
    return MODELS[key].get("files_of", key)


def installed_models():
    return [key for key in ("standard", "quality") if model_path(key)]


def recommended_model():
    """The model to suggest first on this PC."""
    return "quality" if machine_suits_quality() else "standard"


def wanted_model(choice):
    """The model the player's choice asks for. "auto" never asks for a model that is not
    installed (no download without the player's click)."""
    if choice in MODELS:
        return choice
    if model_path("quality") and (machine_suits_quality() or not model_path("standard")):
        return "quality"
    return "light" if machine_is_modest() else "standard"


def usable_model(choice):
    """(key, path) of the model to load now: the wanted one if present, else the other one
    installed, else (key, None) when no model is installed yet."""
    key = wanted_model(choice)
    path = model_path(key)
    if path is None:
        for other in ("standard", "quality"):
            if model_path(other):
                return other, model_path(other)
    return key, path


class ModelDownloader(threading.Thread):
    """Downloads a model zip from the GitHub "models" release and unpacks it in the models folder."""

    def __init__(self, key, target, on_done, on_progress=None):
        super().__init__(name=f"ModelDownload-{key}", daemon=True)
        self.key = files_key(key)
        self.target = Path(target)   # models folder next to the .exe (or AppData if refused)
        self.on_done = on_done    # callable(key, ok)
        self.on_progress = on_progress    # callable(bytes done, bytes expected or 0)

    def run(self):
        from . import updater   # same GitHub access and certificates as the updates
        ok = False
        asset_name = MODELS[self.key]["asset"]
        target = self.target
        archive = target / asset_name
        try:
            # The release tells the file's address and the SHA-256 GitHub computed at upload.
            asset = updater.release_asset(MODELS_RELEASE_TAG, asset_name)
            if not asset:
                raise RuntimeError(f"{asset_name} is not in the {MODELS_RELEASE_TAG} release")
            updater.expected_sha256(asset)     # no published digest: nothing is downloaded
            url = asset["browser_download_url"]
            target.mkdir(parents=True, exist_ok=True)
            part = archive.with_name(archive.name + ".part")
            log.info("Downloading the %s model from %s", self.key, url)
            with updater._open(url, 120) as resp, open(part, "wb") as out:
                expected = int(resp.headers.get("Content-Length") or 0)
                done = 0
                while True:
                    block = resp.read(1 << 20)
                    if not block:
                        break
                    out.write(block)
                    done += len(block)
                    if self.on_progress:
                        self.on_progress(done, expected)
            if expected and part.stat().st_size != expected:
                raise RuntimeError("Incomplete download")
            updater.verify_sha256(part, asset)   # never unpacked if it differs
            os.replace(part, archive)
            with zipfile.ZipFile(archive) as zf:
                zf.extractall(target)
            ok = model_path(self.key) is not None
            if not ok:
                raise RuntimeError(f"{asset_name} does not contain {MODELS[self.key]['dir']}/model.bin")
        except Exception:
            log.exception("Model download failed")
        finally:
            Path(archive).unlink(missing_ok=True)
            Path(str(archive) + ".part").unlink(missing_ok=True)
        self.on_done(self.key, ok)
