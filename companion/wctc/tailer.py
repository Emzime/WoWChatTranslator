"""Follows WoWChatLog.txt in real time (handles truncation, new sessions and several flavors)."""

import logging
import threading
import time

log = logging.getLogger(__name__)


class ChatLogTailer(threading.Thread):
    def __init__(self, files_provider, on_line, interval=0.15):
        super().__init__(name="ChatLogTailer", daemon=True)
        self._files_provider = files_provider  # callable -> list[Path]
        self._on_line = on_line                # callable(str)
        self._interval = interval
        self._positions = {}
        self._buffers = {}
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def run(self):
        while not self._stop.is_set():
            try:
                for path in self._files_provider():
                    self._poll(path)
            except Exception:
                log.exception("Tailer error")
            self._stop.wait(self._interval)

    def _poll(self, path):
        key = str(path)
        try:
            size = path.stat().st_size
        except OSError:
            if key not in self._positions:
                # Not created yet: when the game creates it, read it from the beginning.
                self._positions[key] = 0
                self._buffers[key] = b""
                log.info("Waiting for %s", path)
            return
        if key not in self._positions:
            # Never replay old history: start at the end of an existing log.
            self._positions[key] = size
            self._buffers[key] = b""
            log.info("Following %s", path)
            return
        pos = self._positions[key]
        if size < pos:
            # Log was truncated or recreated by a new game session.
            pos, self._buffers[key] = 0, b""
        if size == pos:
            return
        try:
            with open(path, "rb") as fh:
                fh.seek(pos)
                data = fh.read(size - pos)
        except OSError:
            return
        self._positions[key] = pos + len(data)
        chunk = self._buffers[key] + data
        lines = chunk.split(b"\n")
        self._buffers[key] = lines.pop()  # incomplete last line, if any
        for raw in lines:
            line = raw.rstrip(b"\r").decode("utf-8", errors="replace")
            if line.strip():
                self._on_line(line)


def wait_for(predicate, timeout, step=0.05):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        if predicate():
            return True
        time.sleep(step)
    return predicate()
