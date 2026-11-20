"""Self-update from the latest GitHub release (the addon is embedded, so it is updated too).

The companion is a folder: WoWChatTranslatorCompagnion.exe, plus models\\ once the player has
downloaded a translation model. An update is the release's zip of that folder (the .exe only):
downloaded and unpacked in AppData, then copied over the installation by a small script once
the companion has exited, which then restarts it. The models are never touched."""

import hashlib
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import threading
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

from .paths import config_dir

log = logging.getLogger(__name__)

GITHUB_REPO = "Emzime/WoWChatTranslator"
LATEST_RELEASE_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
RELEASE_BY_TAG_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/tags/{{tag}}"
ASSET_NAME = "WoWChatTranslatorCompagnion.zip"
APP_FOLDER = "WoWChatTranslatorCompagnion"     # top folder inside the zip
CHECK_INTERVAL_S = 3600            # one request an hour (GitHub allows 60 without an account)
CHUNK = 1024 * 1024


def latest_release(timeout=20):
    """The latest published GitHub release (dict), or None if there is none."""
    try:
        with _open(LATEST_RELEASE_URL, timeout) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return None
        raise


class IntegrityError(RuntimeError):
    """A downloaded file is not the one GitHub published (corrupted or tampered with)."""


def expected_sha256(asset):
    """SHA-256 that GitHub computed when the file was uploaded (asset "digest": "sha256:<hex>")."""
    digest = (asset or {}).get("digest") or ""
    algorithm, _, value = digest.partition(":")
    if algorithm.lower() != "sha256" or not re.fullmatch(r"[0-9a-fA-F]{64}", value):
        raise IntegrityError(f"No SHA-256 published for {(asset or {}).get('name')}: download refused")
    return value.lower()


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(CHUNK), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_sha256(path, asset):
    """Raises IntegrityError (and deletes the file) unless it matches GitHub's digest."""
    expected = expected_sha256(asset)
    actual = sha256_of(path)
    if actual != expected:
        Path(path).unlink(missing_ok=True)
        raise IntegrityError(f"SHA-256 mismatch for {Path(path).name}: expected {expected}, got {actual}")
    log.info("SHA-256 verified for %s", Path(path).name)


def release_asset(tag, name):
    """The asset `name` of the release `tag` (dict with browser_download_url and digest), or None."""
    with _open(RELEASE_BY_TAG_URL.format(tag=tag), 20) as resp:
        release = json.load(resp)
    return next((a for a in release.get("assets", []) if a.get("name") == name), None)


def parse_version(text):
    numbers = [int(n) for n in re.findall(r"\d+", text or "")[:3]]
    return tuple(numbers + [0] * (3 - len(numbers)))


def is_frozen():
    return bool(getattr(sys, "frozen", False))


def app_dir():
    return Path(sys.executable).resolve().parent


def staging_dir():
    return config_dir() / "update"


def _new_build():
    return staging_dir() / "new" / APP_FOLDER


def cleanup_previous_update():
    """Leftovers of an applied update, and of the old single-file versions."""
    if not is_frozen():
        return
    shutil.rmtree(staging_dir() / "new", ignore_errors=True)
    exe = Path(sys.executable)
    for leftover in (exe.with_name(exe.name + ".old"), exe.with_name(exe.name + ".new"),
                     exe.with_name(exe.name + ".new.part")):
        try:
            leftover.unlink(missing_ok=True)
        except OSError:
            pass  # still in use: removed next time


def _ssl_context():
    """Windows' own certificate verification (fetches missing intermediates, follows the
    certificates installed by antivirus/proxies); certifi as a fallback."""
    import ssl
    try:
        import truststore
        return truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    except ImportError:
        pass  # truststore missing: certifi below
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def _open(url, timeout):
    return urllib.request.urlopen(_request(url), timeout=timeout, context=_ssl_context())


def _request(url):
    return urllib.request.Request(url, headers={
        "User-Agent": "WoWChatTranslatorCompagnion",
        "Accept": "application/vnd.github+json",
    })


class Updater(threading.Thread):
    """Looks for a newer release now and then. Only tells: nothing is downloaded until the
    player agrees (download_update)."""

    def __init__(self, current_version, on_event):
        """`on_event("available", tag)` once per new version."""
        super().__init__(name="Updater", daemon=True)
        self.current_version = current_version
        self.on_event = on_event
        self.notified_version = None
        self._wake = threading.Event()
        self._stop = threading.Event()

    def check_now(self):
        self._wake.set()

    def stop(self):
        self._stop.set()
        self._wake.set()

    def run(self):
        while not self._stop.is_set():
            try:
                self._check()
            except Exception:
                log.exception("Update check failed")
            self._wake.wait(CHECK_INTERVAL_S)
            self._wake.clear()

    def _check(self):
        release = latest_release()
        if not release:
            log.info("No public release found at %s", LATEST_RELEASE_URL)
            return
        tag = release.get("tag_name", "")
        if parse_version(tag) <= parse_version(self.current_version):
            log.info("Up to date (%s, latest release %s)", self.current_version, tag or "none")
            return
        if self.notified_version == tag:
            return
        log.info("Update available: %s -> %s", self.current_version, tag)
        self.notified_version = tag
        self.on_event("available", tag)


def download_update(tag, on_progress=lambda done, expected: None, cancelled=lambda: False):
    """Downloads the release's companion zip (asked by the player), checks its SHA-256 and
    unpacks it in AppData. Raises on any failure; nothing is installed until apply_update()."""
    with _open(RELEASE_BY_TAG_URL.format(tag=tag), 20) as resp:
        release = json.load(resp)
    asset = next((a for a in release.get("assets", []) if a.get("name") == ASSET_NAME), None)
    if not asset:
        raise RuntimeError(f"Release {tag} has no {ASSET_NAME} asset")
    url, expected_size = asset["browser_download_url"], int(asset.get("size", 0))
    expected_sha256(asset)        # no published digest: nothing is downloaded
    staging = staging_dir()
    staging.mkdir(parents=True, exist_ok=True)
    archive = staging / ASSET_NAME
    part = archive.with_name(archive.name + ".part")
    if archive.is_file() and sha256_of(archive) != expected_sha256(asset):
        archive.unlink()          # an older or damaged download
    if not archive.is_file():
        log.info("Downloading %s", url)
        done = 0
        with _open(url, 60) as resp, open(part, "wb") as out:
            while True:
                chunk = resp.read(CHUNK)
                if not chunk:
                    break
                out.write(chunk)
                done += len(chunk)
                on_progress(done, expected_size)
                if cancelled():
                    raise RuntimeError("Download cancelled")
        if expected_size and part.stat().st_size != expected_size:
            part.unlink(missing_ok=True)
            raise RuntimeError("Incomplete download")
        verify_sha256(part, asset)   # never unpacked, nor installed, if it differs
        os.replace(part, archive)
    on_progress(expected_size, expected_size)
    unpack(archive, staging / "new")
    log.info("Update ready in %s", _new_build())


def unpack(archive, destination):
    shutil.rmtree(destination, ignore_errors=True)
    with zipfile.ZipFile(archive) as zf:
        zf.extractall(destination)
    build = destination / APP_FOLDER
    if not (build / (APP_FOLDER + ".exe")).is_file():
        raise RuntimeError(f"{archive.name} does not contain {APP_FOLDER}/{APP_FOLDER}.exe")


def update_script(pid, new_build, target, exe_name, restart=True):
    """Windows batch run once the companion has exited: copies the new build over the
    installation (the downloaded models stay as they are, nothing is deleted) and, unless the
    player was closing it, starts it again."""
    lines = [
        "@echo off",
        ":wait",
        f'tasklist /FI "PID eq {pid}" /NH | find "{pid}" >nul && (ping -n 2 127.0.0.1 >nul & goto wait)',
        f'robocopy "{new_build}" "{target}" /E /IS /IT /R:10 /W:1 /XD models >nul',
        f'start "" "{target}\\{exe_name}" --after-update' if restart else None,
        f'rd /s /q "{new_build.parent}"',
        f'del /q "{new_build.parent.parent / ASSET_NAME}"',
        '(goto) 2>nul & del "%~f0"',
        "",
    ]
    return "\r\n".join(line for line in lines if line is not None)


def independent_environment():
    """Environment for starting a new, independent instance of a PyInstaller one-file exe.

    Without this, the child reuses the parent's temporary _MEI folder (old version's files),
    which the parent deletes when it exits.
    """
    env = {k: v for k, v in os.environ.items() if not k.startswith(("_PYI_", "_MEIPASS"))}
    env["PYINSTALLER_RESET_ENVIRONMENT"] = "1"
    return env


def update_ready():
    return (_new_build() / (APP_FOLDER + ".exe")).is_file()


def apply_update_and_restart(restart=True):
    """Starts the copy script; the caller must then exit. Returns True on success."""
    new_build = _new_build()
    if not (new_build / (APP_FOLDER + ".exe")).is_file():
        return False
    script = staging_dir() / "apply_update.cmd"
    try:
        script.write_text(update_script(os.getpid(), new_build, app_dir(), Path(sys.executable).name, restart),
                          encoding="mbcs" if sys.platform == "win32" else "utf-8")
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)   # hidden console: robocopy needs one
        # Clean environment: the restarted .exe must not reuse this one's temporary folder.
        subprocess.Popen(["cmd", "/c", str(script)], close_fds=True, creationflags=flags,
                         env=independent_environment())
    except OSError:
        log.exception("Cannot start the update")
        return False
    log.info("Applying the update after exit")
    return True
