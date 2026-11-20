"""Thin Win32 helpers (no-ops on other platforms so the core stays testable)."""

import ctypes
import logging
import sys
import threading

log = logging.getLogger(__name__)

IS_WINDOWS = sys.platform == "win32"

GWL_EXSTYLE = -20
WS_EX_TRANSPARENT = 0x00000020
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_LAYERED = 0x00080000
WS_EX_NOACTIVATE = 0x08000000
ERROR_ALREADY_EXISTS = 183
LWA_ALPHA = 0x00000002
WOW_WINDOW_CLASSES = ("GxWindowClass", "GxWindowClassD3d", "GxWindowClassOpenGl")

if IS_WINDOWS:
    import ctypes.wintypes as wintypes

    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    user32.GetWindowLongW.restype = ctypes.c_long
    user32.GetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int]
    user32.SetWindowLongW.restype = ctypes.c_long
    user32.SetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_long]
    user32.GetForegroundWindow.restype = wintypes.HWND
    user32.GetParent.restype = wintypes.HWND
    user32.GetParent.argtypes = [wintypes.HWND]
    user32.GetWindow.restype = wintypes.HWND
    user32.GetWindow.argtypes = [wintypes.HWND, ctypes.c_uint]
    user32.WindowFromPoint.restype = wintypes.HWND
    user32.WindowFromPoint.argtypes = [wintypes.POINT]
    user32.GetAncestor.restype = wintypes.HWND
    user32.GetAncestor.argtypes = [wintypes.HWND, ctypes.c_uint]
    _ENUM_PROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)


def set_dpi_aware():
    """Work in physical pixels so overlay and game coordinates match."""
    if not IS_WINDOWS:
        return
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except (AttributeError, OSError):
        try:
            user32.SetProcessDPIAware()
        except (AttributeError, OSError):
            pass  # older Windows: no DPI awareness


def _class_name(hwnd):
    buf = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, buf, 256)
    return buf.value


def _window_title(hwnd):
    buf = ctypes.create_unicode_buffer(256)
    user32.GetWindowTextW(hwnd, buf, 256)
    return buf.value


def find_wow_window():
    if not IS_WINDOWS:
        return None
    found = []

    def callback(hwnd, _):
        if user32.IsWindowVisible(hwnd):
            cls = _class_name(hwnd)
            if cls.startswith(WOW_WINDOW_CLASSES) or _window_title(hwnd) == "World of Warcraft":
                found.append(hwnd)
                return False
        return True

    user32.EnumWindows(_ENUM_PROC(callback), 0)
    return found[0] if found else None


def is_window(hwnd):
    return bool(IS_WINDOWS and hwnd and user32.IsWindow(hwnd))


def is_minimized(hwnd):
    return bool(IS_WINDOWS and user32.IsIconic(hwnd))


def foreground_window():
    return user32.GetForegroundWindow() if IS_WINDOWS else None


def client_rect(hwnd):
    """Client area of a window in screen coordinates: (x, y, width, height)."""
    if not IS_WINDOWS:
        return None
    rect = wintypes.RECT()
    if not user32.GetClientRect(hwnd, ctypes.byref(rect)):
        return None
    origin = wintypes.POINT(0, 0)
    user32.ClientToScreen(hwnd, ctypes.byref(origin))
    return origin.x, origin.y, rect.right - rect.left, rect.bottom - rect.top


def toplevel_hwnd(tk_widget):
    if not IS_WINDOWS:
        return None
    try:
        return int(tk_widget.wm_frame(), 16)
    except (ValueError, TypeError):
        return user32.GetParent(tk_widget.winfo_id())


def set_click_through(hwnd, enabled, no_activate=None):
    """Click-through window: mouse events go to the game below. `no_activate` (default: same
    as `enabled`) keeps clicks from taking the keyboard focus away from the game."""
    if not IS_WINDOWS or not hwnd:
        return
    if no_activate is None:
        no_activate = enabled
    style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    newly_layered = not style & WS_EX_LAYERED
    style |= WS_EX_LAYERED | WS_EX_TOOLWINDOW
    style = style | WS_EX_TRANSPARENT if enabled else style & ~WS_EX_TRANSPARENT
    style = style | WS_EX_NOACTIVATE if no_activate else style & ~WS_EX_NOACTIVATE
    user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
    if newly_layered:
        # A layered window stays invisible until its attributes are set: fully opaque.
        user32.SetLayeredWindowAttributes(wintypes.HWND(hwnd), 0, 255, LWA_ALPHA)


def move_window(hwnd, x, y, width, height):
    """Places a window in physical pixels, bypassing Tk's own geometry handling."""
    if not IS_WINDOWS or not hwnd:
        return False
    return bool(user32.SetWindowPos(wintypes.HWND(hwnd), None, int(x), int(y), int(width), int(height),
                                    SWP_NOZORDER | SWP_NOACTIVATE))


def window_rect(hwnd):
    """Outer rectangle of a window in screen coordinates: (x, y, width, height)."""
    if not IS_WINDOWS or not hwnd:
        return None
    rect = wintypes.RECT()
    if not user32.GetWindowRect(wintypes.HWND(hwnd), ctypes.byref(rect)):
        return None
    return rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top


# ----- z-order: our windows stay just above the game -----------------------------------------

GW_HWNDPREV = 3
GA_ROOT = 2
SWP_NOSIZE, SWP_NOMOVE, SWP_NOZORDER, SWP_NOACTIVATE = 0x0001, 0x0002, 0x0004, 0x0010
WS_EX_TOPMOST = 0x00000008
HWND_TOP = 0


def place_above(target, hwnd):
    """Puts `hwnd` directly above `target` in the Z order (not topmost): it then hides with
    the game when another application covers it, instead of floating over everything."""
    if not IS_WINDOWS or not target or not hwnd:
        return
    prev = user32.GetWindow(wintypes.HWND(target), GW_HWNDPREV)
    if prev == hwnd:
        return
    after = prev
    if not prev or user32.GetWindowLongW(wintypes.HWND(prev), GWL_EXSTYLE) & WS_EX_TOPMOST:
        after = HWND_TOP   # the game is the top normal window: go just above it
    user32.SetWindowPos(wintypes.HWND(hwnd), wintypes.HWND(after), 0, 0, 0, 0,
                        SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE)


def root_window_at(x, y):
    """Top-level window under a screen point (click-through windows are skipped by Windows)."""
    if not IS_WINDOWS:
        return None
    hwnd = user32.WindowFromPoint(wintypes.POINT(x, y))
    return user32.GetAncestor(hwnd, GA_ROOT) if hwnd else None


# ----- mouse wheel over the click-through overlay -----------------------------------------------

WH_MOUSE_LL = 14
WM_MOUSEWHEEL = 0x020A


def start_wheel_hook(should_capture, on_wheel):
    """Low-level mouse hook (read-only, nothing is injected into the game): wheel events over
    the overlay scroll it instead of reaching the game. `should_capture(x, y)` and
    `on_wheel(delta)` are called from the hook thread and must be fast and thread-safe."""
    if not IS_WINDOWS:
        return None


    class MSLLHOOKSTRUCT(ctypes.Structure):
        _fields_ = [("pt", wintypes.POINT), ("mouseData", wintypes.DWORD), ("flags", wintypes.DWORD),
                    ("time", wintypes.DWORD), ("dwExtraInfo", ctypes.c_void_p)]

    LRESULT = ctypes.c_ssize_t
    HOOKPROC = ctypes.WINFUNCTYPE(LRESULT, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)
    user32.CallNextHookEx.argtypes = [wintypes.HHOOK, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM]
    user32.CallNextHookEx.restype = LRESULT
    user32.SetWindowsHookExW.argtypes = [ctypes.c_int, HOOKPROC, wintypes.HINSTANCE, wintypes.DWORD]
    user32.SetWindowsHookExW.restype = wintypes.HHOOK
    kernel32.GetModuleHandleW.restype = wintypes.HMODULE

    def callback(n_code, w_param, l_param):
        try:
            if n_code == 0 and w_param == WM_MOUSEWHEEL:
                info = ctypes.cast(l_param, ctypes.POINTER(MSLLHOOKSTRUCT)).contents
                if should_capture(info.pt.x, info.pt.y):
                    on_wheel(ctypes.c_short(info.mouseData >> 16).value)
                    return 1   # swallowed: the game does not zoom the camera
        except Exception:
            log.exception("Wheel hook error")
        return user32.CallNextHookEx(None, n_code, w_param, l_param)

    proc = HOOKPROC(callback)

    def loop():
        hook = user32.SetWindowsHookExW(WH_MOUSE_LL, proc, kernel32.GetModuleHandleW(None), 0)
        if not hook:
            log.warning("Mouse wheel hook unavailable")
            return
        msg = wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

    thread = threading.Thread(target=loop, name="WheelHook", daemon=True)
    thread.proc = proc  # keep the callback alive
    thread.start()
    return thread


WDA_EXCLUDEFROMCAPTURE = 0x11


WDA_NONE = 0


def exclude_from_capture(hwnd, exclude=True):
    """Hides a window from screen capture (Windows 10 2004+), or shows it again with
    exclude=False. Returns True on success."""
    if not IS_WINDOWS or not hwnd:
        return False
    try:
        affinity = WDA_EXCLUDEFROMCAPTURE if exclude else WDA_NONE
        return bool(user32.SetWindowDisplayAffinity(wintypes.HWND(hwnd), affinity))
    except (AttributeError, OSError):
        return False


_mutex = None


def acquire_single_instance(name, wait_s=0.0):
    """Returns False if another instance owns the mutex (after waiting up to `wait_s`,
    used right after a self-update while the previous process exits)."""
    global _mutex
    if not IS_WINDOWS:
        return True
    import time
    deadline = time.monotonic() + wait_s
    while True:
        _mutex = kernel32.CreateMutexW(None, False, f"Local\\{name}")
        if kernel32.GetLastError() != ERROR_ALREADY_EXISTS:
            return True
        kernel32.CloseHandle(_mutex)
        _mutex = None
        if time.monotonic() >= deadline:
            return False
        time.sleep(0.5)


def set_autostart(name, enabled):
    if not IS_WINDOWS:
        return
    import winreg
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
        if enabled:
            command = f'"{sys.executable}"' if getattr(sys, "frozen", False) else f'"{sys.executable}" "{sys.argv[0]}"'
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, command)
        else:
            try:
                winreg.DeleteValue(key, name)
            except FileNotFoundError:
                pass  # autostart entry already absent


def ask_yes_no(title, text):
    """Warning box with Yes / No buttons; True for Yes."""
    if not IS_WINDOWS:
        return True
    MB_YESNO, MB_ICONWARNING, MB_TOPMOST, IDYES = 0x04, 0x30, 0x40000, 6
    return user32.MessageBoxW(None, text, title, MB_YESNO | MB_ICONWARNING | MB_TOPMOST) == IDYES


def run_elevated(program, parameters, timeout_s=120):
    """Runs a program as administrator (Windows asks the player to confirm). True if it ran
    and ended with exit code 0; False if refused or failed."""
    if not IS_WINDOWS:
        return False

    class ShellExecuteInfo(ctypes.Structure):
        _fields_ = [("cbSize", wintypes.DWORD), ("fMask", ctypes.c_ulong), ("hwnd", wintypes.HWND),
                    ("lpVerb", wintypes.LPCWSTR), ("lpFile", wintypes.LPCWSTR), ("lpParameters", wintypes.LPCWSTR),
                    ("lpDirectory", wintypes.LPCWSTR), ("nShow", ctypes.c_int), ("hInstApp", wintypes.HINSTANCE),
                    ("lpIDList", ctypes.c_void_p), ("lpClass", wintypes.LPCWSTR), ("hkeyClass", wintypes.HKEY),
                    ("dwHotKey", wintypes.DWORD), ("hIconOrMonitor", wintypes.HANDLE), ("hProcess", wintypes.HANDLE)]

    SEE_MASK_NOCLOSEPROCESS, SW_HIDE = 0x40, 0
    info = ShellExecuteInfo(cbSize=ctypes.sizeof(ShellExecuteInfo), fMask=SEE_MASK_NOCLOSEPROCESS,
                            lpVerb="runas", lpFile=program, lpParameters=parameters, nShow=SW_HIDE)
    if not ctypes.windll.shell32.ShellExecuteExW(ctypes.byref(info)) or not info.hProcess:
        return False   # refused by the player (UAC) or impossible
    kernel32.WaitForSingleObject(info.hProcess, int(timeout_s * 1000))
    code = wintypes.DWORD()
    kernel32.GetExitCodeProcess(info.hProcess, ctypes.byref(code))
    kernel32.CloseHandle(info.hProcess)
    return code.value == 0


def message_box(title, text, error=False):
    if IS_WINDOWS:
        user32.MessageBoxW(None, text, title, 0x10 if error else 0x40)
    else:
        print(f"{title}: {text}", file=sys.stderr)
