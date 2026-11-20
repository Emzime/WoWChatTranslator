"""Pixel bridge: receives chat messages drawn by the addon as a grid of dark cells.

An addon cannot write files or use the network while the game runs, so it draws each packet
as a small grid in the top-right corner of the chat (see addon/WoWChatTranslator/Bridge.lua,
whose constants must match these). The companion hides the grid under a mask window that is
excluded from screen capture, and reads it with DXGI Desktop Duplication, which honours that
exclusion (classic GDI capture does not). The overlay also leaves a transparent hole over the
grid. The companion finds the grid by scanning the game window, then captures only that
area, calibrates on the sync cells and decodes it.
"""

import logging
import threading
import time

import numpy as np

from . import winutil
from .chatparser import ChatLine, parse_links, strip_escapes

log = logging.getLogger(__name__)

COLS, ROWS, CELL = 64, 16, 3
WIDTH, HEIGHT = COLS * CELL, ROWS * CELL   # physical pixels
INSET = 4                 # keep in sync with Bridge.lua: grid offset from the chat's top-right corner
PROBE_MARGIN = 32         # search margin around an expected grid position (fast path)
SYNC = (7, 0, 5, 2, 7, 0, 3, 4)
BASE = (11, 14, 18)                        # grid "off" colour (overlay background)
DELTA = 48                                 # "on" = BASE + DELTA on each channel
MIN_CONTRAST = 10                          # on/off difference needed after calibration
SCAN_TOLERANCE = 8                         # "off" cells may differ by this much from each other
SCAN_ON_RANGE = (15, 250)                  # "on" minus "off", after any gamma/brightness change
HEADER_BYTES = 4                           # session, seq, length (2)
CRC_BYTES = 2
MAX_BYTES = ((COLS * ROWS - len(SYNC)) * 3) // 8
MAX_PAYLOAD = MAX_BYTES - HEADER_BYTES - CRC_BYTES
FIELD_SEP, RECORD_SEP = "\x1f", "\x1e"

CAPTURE_INTERVAL_S = 0.012   # keep in sync with HOLD_TIME / MIN_HOLD_TIME in Bridge.lua
SCAN_INTERVAL_S = 1.0
LOST_AFTER_S = 1.5          # locked grid unreadable for this long -> scan again
STALL_AFTER_S = 30          # grid on screen without a new packet for this long: addon stalled
ACTIVE_TIMEOUT_S = 2.0      # grid not seen for this long -> no character in the world
GONE_AFTER_MISSES = 3       # sync cells absent this many captures in a row (~36 ms): grid hidden
                            # (game window over it, UI hidden, character left the world...)
WINDOW_REFRESH_S = 1.0
KINDS = {"say", "guild", "officer", "party", "raid", "instance", "whisper", "whisper_out", "channel"}


def crc16(data):
    """CRC16-CCITT (0x1021, init 0xFFFF), same as the addon."""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return crc


def encode(session, seq, payload: bytes):
    """Python twin of the addon encoder (used by tests and the self-test)."""
    data = bytes([session, seq, len(payload) >> 8, len(payload) & 0xFF]) + payload
    crc = crc16(data)
    data += bytes([crc >> 8, crc & 0xFF])
    cells = list(SYNC)
    acc = acc_bits = 0
    for byte in data:
        acc = (acc << 8) | byte
        acc_bits += 8
        while acc_bits >= 3:
            acc_bits -= 3
            cells.append((acc >> acc_bits) & 7)
        acc &= (1 << acc_bits) - 1
    if acc_bits:
        cells.append((acc << (3 - acc_bits)) & 7)
    return cells + [0] * (COLS * ROWS - len(cells))


def decode(cells):
    """Returns (session, seq, crc, payload bytes) or None if no valid packet is visible."""
    if tuple(cells[:len(SYNC)]) != SYNC:
        return None
    out = bytearray()
    acc = acc_bits = 0
    for value in cells[len(SYNC):]:
        acc = (acc << 3) | value
        acc_bits += 3
        if acc_bits >= 8:
            acc_bits -= 8
            out.append((acc >> acc_bits) & 0xFF)
            acc &= (1 << acc_bits) - 1
    if len(out) < HEADER_BYTES + CRC_BYTES:
        return None
    length = (out[2] << 8) | out[3]
    end = HEADER_BYTES + length
    if length > MAX_PAYLOAD or end + CRC_BYTES > len(out):
        return None
    crc = (out[end] << 8) | out[end + 1]
    if crc16(out[:end]) != crc:
        return None
    return out[0], out[1], crc, bytes(out[HEADER_BYTES:end])


def bgra_to_rgb(raw, width, height):
    """mss screenshots are BGRA bytes: returns an (height, width, 3) RGB int16 array."""
    return np.frombuffer(raw, dtype=np.uint8).reshape(height, width, 4)[:, :, 2::-1].astype(np.int16)


def sample_cells(img, ox, oy):
    """Reads the cells of a grid whose top-left corner is at (ox, oy) in `img`.

    Thresholds are calibrated per channel on the sync cells, so the very dark levels used by
    the addon still decode reliably whatever the game's gamma or brightness.
    """
    ys = oy + np.arange(ROWS) * CELL + CELL // 2
    xs = ox + np.arange(COLS) * CELL + CELL // 2
    if ys[-1] >= img.shape[0] or xs[-1] >= img.shape[1] or ox < 0 or oy < 0:
        return None
    centres = img[np.ix_(ys, xs)].reshape(-1, 3)
    sync = centres[: len(SYNC)]
    bits = np.array([[(v >> shift) & 1 for shift in (2, 1, 0)] for v in SYNC], dtype=bool)
    thresholds = []
    for channel in range(3):
        on = sync[bits[:, channel], channel].mean()
        off = sync[~bits[:, channel], channel].mean()
        if on - off < MIN_CONTRAST:
            return None
        thresholds.append((on + off) / 2)
    high = centres > np.array(thresholds)
    return (high[:, 0] * 4 + high[:, 1] * 2 + high[:, 2]).tolist()


FAINT_CONTRAST = 4        # sync pattern still visible in one channel (dimmed, tinted): grid there


def sync_visible(img):
    """True if the sync cells still show in at least one colour channel, with every cell on the
    right side: the grid is still there but tinted (the game's red low-health flash saturates
    the red channel), not covered by a window. Such a capture is no reason to hide the overlay."""
    if img is None:
        return False
    ys = np.full(len(SYNC), CELL // 2)
    xs = np.arange(len(SYNC)) * CELL + CELL // 2
    if xs[-1] >= img.shape[1] or ys[0] >= img.shape[0]:
        return False
    sync = img[ys, xs].reshape(-1, 3)
    bits = np.array([[(v >> shift) & 1 for shift in (2, 1, 0)] for v in SYNC], dtype=bool)
    for channel in range(3):
        on, off = sync[bits[:, channel], channel], sync[~bits[:, channel], channel]
        if on.min() - off.max() >= FAINT_CONTRAST:
            return True
    return False


def find_grid(img):
    """Scans an RGB image for the sync cells; returns (ox, oy, packet) of the first valid grid.

    Matching is relative (cells compared to the all-off sync cell), so it works whatever the
    absolute colours after the game's gamma/brightness settings.
    """
    height, width, _ = img.shape
    span = (len(SYNC) - 1) * CELL
    if width <= span:
        return None
    lo, hi = SCAN_ON_RANGE
    off_index = SYNC.index(0)
    ref = img[:, off_index * CELL: width - span + off_index * CELL]
    match = np.ones((height, width - span), dtype=bool)
    for k, value in enumerate(SYNC):
        if k == off_index:
            continue
        view = img[:, k * CELL: width - span + k * CELL]
        for channel, shift in enumerate((2, 1, 0)):
            diff = view[:, :, channel] - ref[:, :, channel]
            if (value >> shift) & 1:
                match &= (diff >= lo) & (diff <= hi)
            else:
                match &= np.abs(diff) <= SCAN_TOLERANCE
    tried = set()
    for y, x in np.argwhere(match)[:400]:
        for dy in range(CELL):
            for dx in range(CELL):
                ox, oy = int(x) - dx, int(y) - dy
                if (ox, oy) in tried:
                    continue
                tried.add((ox, oy))
                cells = sample_cells(img, ox, oy)
                packet = decode(cells) if cells else None
                if packet:
                    return ox, oy, packet
    return None


def parse_payload(payload: bytes):
    lines = []
    for record in payload.decode("utf-8", errors="replace").split(RECORD_SEP):
        fields = record.split(FIELD_SEP)
        if len(fields) == 4:
            fields.append("")                 # no class: Battle.net whisper, or an older addon
        if len(fields) != 5:
            continue
        kind, prefix, sender, text, player_class = fields
        if kind not in KINDS or not text.strip():
            continue
        lines.append(ChatLine(record, "", strip_escapes(prefix).strip(), sender, strip_escapes(text).strip(), kind,
                              parse_links(text), player_class.strip().upper()))
    return lines


REQUESTS = {"shot"}


def parse_state(payload: bytes):
    """State reported by the addon ("state" records, "chatlog=1"): {"chatlog": "1"}."""
    state = {}
    for record in payload.decode("utf-8", errors="replace").split(RECORD_SEP):
        fields = record.split(FIELD_SEP)
        if len(fields) == 4 and fields[0] == "state":
            for item in fields[1].split(","):
                key, _, value = item.partition("=")
                if key:
                    state[key.strip()] = value.strip()
    return state


def parse_requests(payload: bytes):
    """Requests from the game: "shot" (screenshot with the overlay, key bound in game)."""
    kinds = []
    for record in payload.decode("utf-8", errors="replace").split(RECORD_SEP):
        kind = record.split(FIELD_SEP, 1)[0]
        if kind in REQUESTS:
            kinds.append(kind)
    return kinds


COVER_DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz+/"


def parse_covers(payload: bytes):
    """Game windows open on screen, from the last "cover" record: [(x, y, w, h)] in pixels
    relative to the game's client area, or None when the packet has no cover record.
    Each window is 8 characters: x, y, w, h halved, 2 base-64 digits each (see Bridge.lua)."""
    covers = None
    for record in payload.decode("utf-8", errors="replace").split(RECORD_SEP):
        fields = record.split(FIELD_SEP)
        if len(fields) != 4 or fields[0] != "cover":
            continue
        covers = []
        data = fields[1]
        for start in range(0, len(data) - 7, 8):
            chunk = data[start:start + 8]
            if any(c not in COVER_DIGITS for c in chunk):
                continue
            x, y, w, h = (COVER_DIGITS.index(chunk[i]) * 64 + COVER_DIGITS.index(chunk[i + 1])
                          for i in range(0, 8, 2))
            if w > 0 and h > 0:
                covers.append((x * 2, y * 2, w * 2, h * 2))
    return covers


class MssCapture:
    """GDI capture (fallback): does not see through capture-excluded windows."""

    name = "gdi"

    def __init__(self):
        import mss
        self._sct = mss.mss()

    def grab(self, left, top, width, height):
        shot = self._sct.grab({"left": left, "top": top, "width": width, "height": height})
        return bgra_to_rgb(shot.raw, shot.width, shot.height)

    def close(self):
        self._sct.close()


class DxgiCapture:
    """DXGI Desktop Duplication: capture-excluded windows (the mask) are left out."""

    name = "dxgi"

    def __init__(self):
        import dxcam
        self._dxcam = dxcam
        self._factory = getattr(dxcam, "__factory")
        self._camera = None
        self._key = None

    def _camera_for(self, x, y):
        for device_idx, outputs in enumerate(self._factory.outputs):
            for output_idx, output in enumerate(outputs):
                output.update_desc()
                r = output.desc.DesktopCoordinates
                if r.left <= x < r.right and r.top <= y < r.bottom:
                    if (device_idx, output_idx) != self._key:
                        self.close()
                        self._camera = self._dxcam.create(device_idx=device_idx, output_idx=output_idx,
                                                          output_color="BGRA", processor_backend="cv2")
                        self._key = (device_idx, output_idx)
                        log.info("DXGI capture on output %s", self._key)
                    return self._camera, (r.left, r.top)
        return None, None

    def grab(self, left, top, width, height):
        camera, origin = self._camera_for(left, top)
        if not camera:
            return None
        x, y = left - origin[0], top - origin[1]
        region = (x, y, min(x + width, camera.width), min(y + height, camera.height))
        # new_frame_only=False: when the screen did not change, reuse the last frame.
        frame = camera.grab(region=region, new_frame_only=False)
        if frame is None:
            return None
        return np.asarray(frame)[:, :, 2::-1].astype(np.int16)

    def close(self):
        if self._camera is not None:
            try:
                self._camera.release()
            except Exception:
                pass  # capture already gone: nothing to free
        self._camera, self._key = None, None


def make_capture():
    try:
        return DxgiCapture()
    except Exception:
        log.exception("DXGI capture unavailable, falling back to GDI (mask disabled)")
        return MssCapture()


class PixelBridge(threading.Thread):
    def __init__(self, on_lines, on_covers=lambda covers: None, on_request=lambda kind: None,
                 on_gap=lambda start, end, away: None, on_state=lambda state: None):
        super().__init__(name="PixelBridge", daemon=True)
        self.on_lines = on_lines          # callable(list[ChatLine])
        self.on_covers = on_covers        # callable([(x, y, w, h)] in screen pixels)
        self.on_request = on_request      # callable(kind): requests from the game ("shot")
        self.on_gap = on_gap              # callable(start, end, away): packets lost between two
                                          # wall-clock times; away: the game was out of sight
        self.on_state = on_state          # callable(dict): state reported by the addon
        self._last_packet_wall = 0.0
        self._last_new_packet = 0.0       # monotonic time of the last new packet
        self._stall_logged = False
        self._away = False                # game not in front since the last packet
        self._client = None
        self.last_seen = 0.0
        self.grid_origin = None           # (x, y) on screen once the grid is located
        self._last_packet = None
        self._stop = threading.Event()
        self._hwnd = None
        self._hwnd_checked = 0.0
        self._last_scan = 0.0
        self._last_origin = None          # last place the grid was seen (kept when lost)
        self._misses = 0                  # consecutive captures without the sync cells
        self._gone = False                # grid vanished: hide the overlay right away
        self.expected_origins = lambda: []  # callable -> [(x, y)] where the addon should draw it
        self.capture_name = None

    @property
    def masking_supported(self):
        """The mask is only invisible to DXGI capture."""
        return self.capture_name == "dxgi"

    @property
    def active(self):
        return not self._gone and time.monotonic() - self.last_seen < ACTIVE_TIMEOUT_S

    @property
    def grid_screen_rect(self):
        """Screen rectangle of the grid (for the mask), or None when not locked."""
        if not self.grid_origin or not self.active:
            return None
        return self.grid_origin[0], self.grid_origin[1], WIDTH, HEIGHT

    @property
    def game_window(self):
        return self._hwnd

    def stop(self):
        self._stop.set()

    def _game_client(self):
        now = time.monotonic()
        if now - self._hwnd_checked > WINDOW_REFRESH_S or not winutil.is_window(self._hwnd):
            self._hwnd_checked = now
            self._hwnd = winutil.find_wow_window()
        if not self._hwnd or winutil.is_minimized(self._hwnd):
            return None
        rect = winutil.client_rect(self._hwnd)
        if not rect or rect[2] < WIDTH or rect[3] < HEIGHT:
            return None
        return rect

    def run(self):
        capture = make_capture()
        self.capture_name = capture.name
        errors = 0
        while not self._stop.is_set():
            try:
                self._tick(capture)
                errors = 0
            except Exception:
                errors += 1
                log.exception("Bridge capture error")
                capture.close()
                if errors >= 5 and capture.name == "dxgi":
                    log.warning("DXGI capture keeps failing, switching to GDI capture")
                    capture = MssCapture()
                    self.capture_name = capture.name
                elif capture.name == "dxgi":
                    capture = make_capture()
                self._stop.wait(1.0)
            self._stop.wait(CAPTURE_INTERVAL_S)
        capture.close()

    def _tick(self, capture):
        client = self._game_client()
        self._client = client
        if not client:
            self.grid_origin = None
            return
        now = time.monotonic()
        packet = None
        if not self._away and self._hwnd and (winutil.foreground_window() != self._hwnd
                                              or winutil.is_minimized(self._hwnd)):
            self._away = True
        if (self.active and self._last_new_packet and not self._stall_logged
                and now - self._last_new_packet > STALL_AFTER_S):
            # The addon resends its windows list every few seconds: a grid still on screen with
            # the same packet means sending is paused in game (all corners covered...).
            self._stall_logged = True
            log.warning("Bridge grid visible but no new packet for %d s: sending paused in game "
                        "(type /wct covers in game to see why)", STALL_AFTER_S)
        if self.grid_origin:
            gx, gy = self.grid_origin
            img = capture.grab(gx, gy, WIDTH, HEIGHT)
            cells = sample_cells(img, 0, 0) if img is not None else None
            packet = decode(cells) if cells else None
            if img is not None and (not cells or cells[:len(SYNC)] != SYNC) and sync_visible(img):
                # Tinted, not gone (low-health flash): keep the overlay, wait for clear colours.
                self.last_seen = now
                self._misses = 0
            elif img is not None and (not cells or cells[:len(SYNC)] != SYNC):
                # Not a decoding hiccup: the grid is no longer there. It may have moved to
                # another corner (a game window opened over it): look there first, and hide
                # the overlay at once if it is nowhere (no 2-second wait).
                self._misses += 1
                if self._misses >= GONE_AFTER_MISSES:
                    self._misses = 0
                    self.grid_origin = None
                    packet = self._probe(capture, client)
                    if not packet:
                        if not self._gone:
                            log.debug("Bridge grid hidden")
                        self._gone = True
                        self.on_covers([])
                        return
            else:
                self._misses = 0
            if not packet and self.grid_origin and now - self.last_seen > LOST_AFTER_S:
                log.info("Bridge grid lost, scanning again")
                self.grid_origin = None
                self.on_covers([])
        if not packet and not self.grid_origin:
            # Fast path, every tick: look where the grid is expected, so that the mask covers
            # it within a few hundredths of a second when it appears (login, /reload...).
            found = self._probe(capture, client)
            if found:
                packet = found
        if not packet and not self.grid_origin and now - self._last_scan >= SCAN_INTERVAL_S:
            self._last_scan = now
            img = capture.grab(*client)
            found = find_grid(img) if img is not None else None
            if found:
                ox, oy, packet = found
                self.grid_origin = self._last_origin = (client[0] + ox, client[1] + oy)
                log.info("Bridge grid found at %s (%s capture)", self.grid_origin, capture.name)
        if packet:
            self.last_seen = now
            self._gone = False
            self._misses = 0
            self._handle_packet(packet)

    def _probe(self, capture, client):
        cx, cy, cw, ch = client
        candidates = [self._last_origin] if self._last_origin else []
        try:
            candidates += list(self.expected_origins() or [])
        except Exception:
            log.exception("Expected grid position error")
        tried = set()
        for origin in candidates:
            if not origin or origin in tried:
                continue
            tried.add(origin)
            left = max(cx, int(origin[0]) - PROBE_MARGIN)
            top = max(cy, int(origin[1]) - PROBE_MARGIN)
            right = min(cx + cw, int(origin[0]) + WIDTH + PROBE_MARGIN)
            bottom = min(cy + ch, int(origin[1]) + HEIGHT + PROBE_MARGIN)
            if right - left < WIDTH or bottom - top < HEIGHT:
                continue
            img = capture.grab(left, top, right - left, bottom - top)
            found = find_grid(img) if img is not None else None
            if found:
                ox, oy, packet = found
                self.grid_origin = self._last_origin = (left + ox, top + oy)
                log.info("Bridge grid found at %s (expected position, %s capture)", self.grid_origin, capture.name)
                return packet
        return None

    def _handle_packet(self, packet):
        session, seq, crc, payload = packet
        key = (session, seq, crc)
        if key == self._last_packet:
            return
        wall = time.time()
        if self._last_packet and self._last_packet[0] == session and seq != (self._last_packet[1] + 1) % 256:
            if self._away:   # player on the desktop: expected, the chat log may give them back
                log.info("Bridge packets missed while the game was out of sight (%d -> %d)", self._last_packet[1], seq)
            else:
                log.warning("Bridge packets lost (%d -> %d)", self._last_packet[1], seq)
            self.on_gap(self._last_packet_wall, wall, self._away)
        self._last_packet = key
        self._last_packet_wall = wall
        self._last_new_packet = time.monotonic()
        if self._stall_logged:
            log.info("Bridge packets flowing again")
            self._stall_logged = False
        self._away = False
        if payload:
            covers = parse_covers(payload)
            if covers is not None and self._client:
                cx, cy = self._client[0], self._client[1]
                self.on_covers([(cx + x, cy + y, w, h) for x, y, w, h in covers])
            for kind in parse_requests(payload):
                self.on_request(kind)
            state = parse_state(payload)
            if state:
                self.on_state(state)
            lines = parse_payload(payload)
            if lines:
                self.on_lines(lines)
