import os
import sys
import tempfile
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("APPDATA", tempfile.mkdtemp())

from wctc import savedvars  # noqa: E402
from wctc.glossary import Glossary  # noqa: E402
from wctc.wow import Flavor, interface_number  # noqa: E402
from wctc import installer  # noqa: E402


def test_glossary_roundtrip():
    g = Glossary()
    masked, chunks = g.protect("LF tank and heal for M+, WTS [Flask of Power] 25k")
    assert "tank" not in masked and "[Flask" not in masked
    # LF is written out for the model; WTS is a term with the reader's own word ("Je vends").
    assert g.restore(masked, chunks, "fr") == "looking for tank and heal for M+, Je vends [Flask of Power] 25k"
    assert g.residual_text(g.protect("lf people")[0]) == "looking for people"
    assert g.restore("ZX1 seulement", chunks, "fr") is None
    assert g.residual_text(g.protect("gg wp")[0]) == ""


def test_savedvars():
    content = '''
WoWChatTranslatorDB = {
\t["chat"] = {
\t\t["y"] = 0.71,
\t\t["x"] = 0.0125,
\t\t["w"] = 0.3,
\t\t["h"] = 0.17,
\t},
\t["player"] = "Al\\195\\169a",
\t["dataVersion"] = 1,
\t["list"] = { "a", "b", },
\t["flag"] = true,
}
'''
    data = savedvars.parse(content)["WoWChatTranslatorDB"]
    assert data["chat"]["x"] == 0.0125
    assert data["player"] == "Aléa"
    assert data["list"] == {1: "a", 2: "b"}
    assert data["flag"] is True


def test_installer(tmp_path):
    root = tmp_path / "World of Warcraft"
    flavor_dir = root / "_retail_"
    (flavor_dir / "Interface" / "AddOns").mkdir(parents=True)
    (root / ".build.info").write_text(
        "Branch!STRING:0|Active!DEC:1|Version!STRING:0|Product!STRING:0\n"
        "eu|1|12.0.5.64000|wow\n", encoding="utf-8")
    flavor = Flavor(root, flavor_dir, "wow")
    assert interface_number(root, "wow") == 120005
    assert installer.install(flavor) is True
    toc = (flavor_dir / "Interface/AddOns/WoWChatTranslator/WoWChatTranslator.toc").read_text(encoding="utf-8")
    assert "## Interface: 120005, 120001" in toc
    assert installer.install(flavor) is False


def test_enable_for_all_characters(tmp_path):
    flavor_dir = tmp_path / "_retail_"
    char_dir = flavor_dir / "WTF/Account/ACC/Hyjal/Toto"
    char_dir.mkdir(parents=True)
    (char_dir / "AddOns.txt").write_text("ElvUI: enabled\nWoWChatTranslator: disabled\n", encoding="utf-8")
    other = flavor_dir / "WTF/Account/ACC/Hyjal/Titi"
    other.mkdir(parents=True)
    (other / "AddOns.txt").write_text("ElvUI: enabled\n", encoding="utf-8")
    flavor = Flavor(tmp_path, flavor_dir, "wow")
    assert installer.enable_for_all_characters(flavor) == 2
    assert (char_dir / "AddOns.txt").read_text(encoding="utf-8") == "ElvUI: enabled\nWoWChatTranslator: enabled\n"
    assert (other / "AddOns.txt").read_text(encoding="utf-8") == "ElvUI: enabled\nWoWChatTranslator: enabled\n"
    assert installer.enable_for_all_characters(flavor) == 0


def _import_app(monkeypatch):
    """Imports wctc.app, stubbing GUI modules on machines without Tk or a display."""
    import types
    for name in ("tkinter", "tkinter.font", "tkinter.filedialog", "pystray"):
        try:
            __import__(name)
        except Exception:
            monkeypatch.setitem(sys.modules, name, types.ModuleType(name))
    if not hasattr(sys.modules["tkinter"], "Tk"):
        sys.modules["tkinter"].filedialog = sys.modules["tkinter.filedialog"]
        sys.modules["tkinter"].font = sys.modules["tkinter.font"]
        sys.modules["tkinter"].Tk = object
    from wctc import app
    return app


def test_updater(monkeypatch):
    import io
    import json
    from wctc import updater
    assert updater.parse_version("v1.2.10") > updater.parse_version("1.2.9")
    assert updater.parse_version("v1.1") == (1, 1, 0)

    def fake_urlopen(request, timeout=0, context=None):
        return io.BytesIO(json.dumps({"tag_name": "v9.0.0", "assets": []}).encode())

    monkeypatch.setattr(updater.urllib.request, "urlopen", fake_urlopen)
    events = []
    updater.Updater("1.0.0", lambda kind, version: events.append((kind, version)))._check()
    assert events == [("available", "v9.0.0")]
    events.clear()
    updater.Updater("9.0.0", lambda kind, version: events.append((kind, version)))._check()
    assert events == []


def test_launch_command(tmp_path, monkeypatch):
    from wctc import wow
    forever = tmp_path / "_forever_"
    forever.mkdir()
    (forever / "Wow.exe").write_bytes(b"")
    bnet_dir = tmp_path / "Battle.net"
    bnet_dir.mkdir()
    (bnet_dir / "Battle.net.exe").write_bytes(b"")
    (bnet_dir / "Battle.net Launcher.exe").write_bytes(b"")
    launcher = str(bnet_dir / "Battle.net Launcher.exe")
    monkeypatch.setattr(wow, "battlenet_executable", lambda: bnet_dir / "Battle.net.exe")
    assert wow.game_command(Flavor(tmp_path, forever, "")) == [launcher, "--exec=launch WoWF"]
    assert wow.game_command(Flavor(tmp_path, tmp_path / "_retail_", "wow")) == [launcher, "--exec=launch WoW"]
    assert wow.game_command(Flavor(tmp_path, tmp_path / "_classic_era_", "")) == [launcher, "--exec=launch WoWCE"]
    assert wow.game_command(Flavor(tmp_path, forever, ""), "XYZ") == [launcher, "--exec=launch XYZ"]
    monkeypatch.setattr(wow, "battlenet_executable", lambda: None)
    assert wow.game_command(Flavor(tmp_path, forever, "")) == [str(forever / "Wow.exe")]


def test_update_unpack_and_script(tmp_path):
    import zipfile
    from wctc import updater

    archive = tmp_path / updater.ASSET_NAME
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("WoWChatTranslatorCompagnion/WoWChatTranslatorCompagnion.exe", b"MZ")
    updater.unpack(archive, tmp_path / "new")           # the .exe alone: models are downloaded apart
    new_build = tmp_path / "new" / "WoWChatTranslatorCompagnion"
    assert (new_build / "WoWChatTranslatorCompagnion.exe").is_file()
    script = updater.update_script(4242, new_build, Path("C:/Games/WCT"), "WoWChatTranslatorCompagnion.exe")
    assert '"PID eq 4242"' in script and "/XD models" in script   # downloaded models never touched
    assert "/MIR" not in script
    assert script.index("robocopy") < script.index("--after-update")   # restart after the copy
    with zipfile.ZipFile(tmp_path / "bad.zip", "w") as zf:
        zf.writestr("something.txt", b"")
    with pytest.raises(RuntimeError):
        updater.unpack(tmp_path / "bad.zip", tmp_path / "bad")


def test_update_environment(monkeypatch):
    from wctc import updater
    monkeypatch.setenv("_PYI_APPLICATION_HOME_DIR", "C:/Temp/_MEI123")
    monkeypatch.setenv("_MEIPASS2", "C:/Temp/_MEI123")
    env = updater.independent_environment()
    assert env["PYINSTALLER_RESET_ENVIRONMENT"] == "1"
    assert "_PYI_APPLICATION_HOME_DIR" not in env and "_MEIPASS2" not in env


# ----- pixel bridge -----------------------------------------------------------------------

from wctc import bridge  # noqa: E402


def test_bridge_roundtrip_python():
    payload = "say\x1fElla dit\x1fElla\x1fBonjour à tous ! Привет".encode()
    session, seq, _, data = bridge.decode(bridge.encode(42, 7, payload))
    assert (session, seq, data) == (42, 7, payload)
    corrupted = bridge.encode(42, 7, payload)
    corrupted[50] ^= 1
    assert bridge.decode(corrupted) is None
    assert bridge.decode([0] * (bridge.COLS * bridge.ROWS)) is None


def test_bridge_lua_encoder_matches_python():
    pytest.importorskip("lupa")
    from tests.lua_harness import cells, load_addon
    lua = load_addon()
    g = lua.globals()
    lua.execute("WoWChatTranslatorCompanion = { seen = 1 }")   # Companion.lua written by the companion
    g.FireEvent("ADDON_LOADED", "WoWChatTranslator")
    g.FireEvent("PLAYER_LOGIN")
    idle = bridge.decode(cells(lua))
    assert idle is not None and idle[3] == b""          # grid visible as soon as in world

    lua.execute('function GetPlayerInfoByGUID(g) if g == "Player-1-0ABC" then return "Mage", "MAGE" end end')
    g.FireEvent("CHAT_MSG_SAY", "Hello everyone, LF tank", "Bob Stone-Realm", "", "", "", "", 0, 0, "", 0, 0, "Player-1-0ABC")
    g.FireEvent("CHAT_MSG_CHANNEL", "WTS |cff0070dd|Hitem:1::|h[Flask]|h|r 25k", "Ann Smith", "", "", "", "", 0, 2, "Commerce")
    g.FireEvent("CHAT_MSG_GUILD", "Привет всем", "Ivan Petrov")
    g.FireEvent("CHAT_MSG_EMOTE", "danse joyeusement.", "Ela Borer")
    g.FireEvent("CHAT_MSG_WHISPER", "salut", "Ann Smith")
    g.FireEvent("CHAT_MSG_YELL", "ignored", "Ela Borer")
    g.FireEvent("CHAT_MSG_MONSTER_YELL", "UUUUrgh", "Abomination inachevée")
    g.FireEvent("CHAT_MSG_TRADESKILLS", "Os Bone crée Goujon.", "Os Bone")
    g.FireEvent("CHAT_MSG_ACHIEVEMENT", "%s a obtenu le haut fait [Explorer] !", "Ela Borer")
    g.Tick(0.2)
    packet = bridge.decode(cells(lua))
    lines = bridge.parse_payload(packet[3])
    assert [(l.kind, l.prefix, l.speaker, l.text) for l in lines] == [
        ("say", "Bob Stone dit", "Bob Stone", "Hello everyone, LF tank"),
        ("channel", "[2. Commerce] Ann Smith", "Ann Smith", "WTS [Flask] 25k"),
        ("guild", "[Guilde] Ivan Petrov", "Ivan Petrov", "Привет всем"),
        ("whisper", "Ann Smith chuchote", "Ann Smith", "salut"),
    ]
    assert [l.player_class for l in lines] == ["MAGE", "", "", ""]     # class colour of the name
    first_seq = packet[1]

    # Burst larger than one packet: split across several packets, nothing lost.
    for i in range(12):
        g.FireEvent("CHAT_MSG_SAY", f"message {i} " + "x" * 200, "Bob Stone")
    received = []
    for _ in range(16):
        g.Tick(0.13)
        p = bridge.decode(cells(lua))
        if p[1] != first_seq:
            first_seq = p[1]
            received += [l.text.split()[1] for l in bridge.parse_payload(p[3])]
    assert received == [str(i) for i in range(12)]

    g.SlashCmdList.WOWCHATTRANSLATOR("test")
    g.Tick(0.2)
    assert bridge.parse_payload(bridge.decode(cells(lua))[3])[0].text == "Hello, this is a translation test."


def _screen_with_grid(cells, ox, oy, width=900, height=500, gamma=1.0, seed=1):
    """Synthetic game screenshot: textured background with the grid drawn at (ox, oy)."""
    rng = np.random.default_rng(seed)
    img = rng.integers(0, 256, size=(height, width, 3)).astype(np.int16)
    img[oy - 10:oy + bridge.HEIGHT + 10, ox - 10:ox + bridge.WIDTH + 10] = rng.integers(0, 30, size=(1, 1, 3))

    def shade(level):
        return round(255 * (level / 255) ** gamma)

    for index, value in enumerate(cells):
        row, col = divmod(index, bridge.COLS)
        y, x = oy + row * bridge.CELL, ox + col * bridge.CELL
        img[y:y + bridge.CELL, x:x + bridge.CELL] = [
            shade(base + (bridge.DELTA if value & mask else 0)) for base, mask in zip(bridge.BASE, (4, 2, 1))]
    return img


@pytest.mark.parametrize("gamma", [1.0, 0.8, 1.2])
def test_bridge_scan_and_calibration(gamma):
    payload = "say\x1fBob Stone dit\x1fBob Stone\x1fHello there".encode()
    img = _screen_with_grid(bridge.encode(3, 9, payload), 431, 217, gamma=gamma)
    ox, oy, packet = bridge.find_grid(img)
    assert (ox, oy) == (431, 217) and packet[3] == payload
    # Once locked, only the grid area is captured.
    crop = img[oy:oy + bridge.HEIGHT, ox:ox + bridge.WIDTH]
    assert bridge.decode(bridge.sample_cells(crop, 0, 0))[3] == payload


def test_bridge_scan_finds_nothing_on_plain_screen():
    rng = np.random.default_rng(5)
    img = rng.integers(0, 256, size=(400, 800, 3)).astype(np.int16)
    img[100:300, 100:500] = rng.integers(0, 30, size=(200, 400, 3))   # dark noisy area
    assert bridge.find_grid(img) is None


def test_bridge_bgra_conversion():
    raw = bytes([10, 20, 30, 255, 40, 50, 60, 255])
    assert bridge.bgra_to_rgb(raw, 2, 1).tolist() == [[[30, 20, 10], [60, 50, 40]]]


def test_addon_idle_without_companion():
    pytest.importorskip("lupa")
    from tests.lua_harness import load_addon
    lua = load_addon()
    g = lua.globals()
    lua.execute("WoWChatTranslatorCompanion = { seen = -500 }")   # stale signature
    g.FireEvent("ADDON_LOADED", "WoWChatTranslator")
    g.FireEvent("PLAYER_LOGIN")
    assert len(g.textures) == 0                                     # no grid at all
    g.FireEvent("CHAT_MSG_SAY", "Hello", "Bob Stone")
    assert g.SlashCmdList.WOWCHATTRANSLATOR is not None
    g.SlashCmdList.WOWCHATTRANSLATOR("on")                          # manual start
    assert len(g.textures) == bridge.COLS * bridge.ROWS


def test_savedvars_dump_roundtrip(tmp_path):
    data = {"WoWChatTranslatorDB": {"companionSeen": 1731670000, "overlayRect": {"x": 0.1, "y": 0.7, "w": 0.2, "h": 0.2},
                                    "player": 'Ela "Borer"\\', "flag": True, "list": {1: "a", 2: "b"}}}
    path = tmp_path / "WoWChatTranslator.lua"
    savedvars.save(path, data)
    assert savedvars.load(path) == data


def test_addon_update_from_flat_layout(tmp_path):
    """An addon of an earlier version (every file at its root) is updated to the folders, and
    keeps the companion's live state."""
    flavor_dir = tmp_path / "_forever_"
    target = flavor_dir / "Interface" / "AddOns" / "WoWChatTranslator"
    target.mkdir(parents=True)
    for name in ("Locales.lua", "Bridge.lua", "Chat.lua", "WoWChatTranslator.lua"):
        (target / name).write_text("-- old", encoding="utf-8")
    (target / "Companion.lua").write_text("WoWChatTranslatorCompanion = { seen = 42 }", encoding="utf-8")
    flavor = Flavor(tmp_path, flavor_dir, "wowf")
    assert installer.install(flavor) is True
    assert not any((target / n).exists() for n in ("Locales.lua", "Bridge.lua", "Chat.lua", "Companion.lua"))
    assert (target / "Core" / "Bridge.lua").is_file() and (target / "Locales" / "fr.lua").is_file()
    assert "seen = 42" in (target / "Data" / "Companion.lua").read_text(encoding="utf-8")
    assert installer.install(flavor) is False


def test_companion_state_file(tmp_path):
    pytest.importorskip("lupa")
    flavor_dir = tmp_path / "_forever_"
    (flavor_dir / "Interface" / "AddOns").mkdir(parents=True)
    flavor = Flavor(tmp_path, flavor_dir, "wowf")
    assert installer.install(flavor) is True
    target = flavor_dir / "Interface/AddOns/WoWChatTranslator/Data/Companion.lua"
    assert "seen = 0" in target.read_text(encoding="utf-8")
    installer.write_companion_state(flavor, 1731670000, {"x": 0.8, "y": 0.75, "w": 0.16, "h": 0.17})
    text = target.read_text(encoding="utf-8")
    assert "seen = 1731670000" in text and "overlayRect = { x = 0.8, y = 0.75, w = 0.16, h = 0.17 }" in text
    assert installer.install(flavor) is False          # live state is not overwritten nor "updated"
    assert "seen = 1731670000" in target.read_text(encoding="utf-8")
    import lupa
    lua = lupa.LuaRuntime()
    lua.execute(text)
    assert lua.globals().WoWChatTranslatorCompanion.overlayRect.x == 0.8


def test_addon_toggle_binding():
    pytest.importorskip("lupa")
    from tests.lua_harness import cells, load_addon
    lua = load_addon()
    g = lua.globals()
    lua.execute("WoWChatTranslatorCompanion = { seen = 1 }")
    g.FireEvent("ADDON_LOADED", "WoWChatTranslator")
    g.FireEvent("PLAYER_LOGIN")
    assert g.bindings["ALT-F6"] == "WOWCHATTRANSLATOR_TOGGLE"      # default suggested binding
    g.WoWChatTranslator_Toggle()                                    # hide
    assert g.WoWChatTranslatorDB.hidden is True
    g.FireEvent("CHAT_MSG_SAY", "dropped while hidden", "Bob Stone")
    g.WoWChatTranslator_Toggle()                                    # show again
    g.FireEvent("CHAT_MSG_SAY", "kept", "Bob Stone")
    g.Tick(0.2)
    texts = [l.text for l in bridge.parse_payload(bridge.decode(cells(lua))[3])]
    assert texts == ["kept"]


def test_bridge_probe_finds_grid_at_expected_position():
    import numpy as np
    from wctc import bridge

    cells = bridge.encode(3, 1, b"")
    screen = np.full((400, 900, 3), 30, dtype=np.int16)
    gx, gy = 600, 37
    for index, value in enumerate(cells):
        row, col = divmod(index, bridge.COLS)
        color = [bridge.BASE[c] + (bridge.DELTA if (value >> (2 - c)) & 1 else 0) for c in range(3)]
        y, x = gy + row * bridge.CELL, gx + col * bridge.CELL
        screen[y:y + bridge.CELL, x:x + bridge.CELL] = color

    class FakeCapture:
        name = "dxgi"
        grabs = []

        def grab(self, left, top, width, height):
            self.grabs.append((width, height))
            return screen[top:top + height, left:left + width].copy()

    capture = FakeCapture()
    pb = bridge.PixelBridge(lambda lines: None)
    pb.expected_origins = lambda: [(gx + 10, gy - 5)]
    packet = pb._probe(capture, (0, 0, 900, 400))
    assert packet and pb.grid_origin == (gx, gy)
    assert all(w < 300 and h < 120 for w, h in capture.grabs)   # small region only


def test_chat_links_kept_for_tooltips():
    from wctc.chatparser import parse_links, strip_escapes

    raw = "WTS |cffa335ee|Hitem:19019::::|h[Thunderfury]|h|r and |cff71d5ff|Hspell:7857|h[Enchant]|h|r"
    links = parse_links(raw)
    assert [(l.kind, l.id, l.name, l.color) for l in links] == [
        ("item", 19019, "Thunderfury", "#a335ee"), ("spell", 7857, "Enchant", "#71d5ff")]
    assert strip_escapes(raw) == "WTS [Thunderfury] and [Enchant]"


def test_wowhead_tooltip_html():
    from wctc.wowhead import html_to_lines

    markup = ('<table><tr><td><b class="q4">Sword</b><br>Item Level 80</td></tr></table>'
              '<table><tr><td>One-Hand</td><th>Sword</th></tr></table>'
              'Sell Price: <span class="moneygold">25</span> <span class="moneysilver">3</span>')
    lines = html_to_lines(markup)
    assert lines[0] == [("Sword", "#a335ee")]
    assert "".join(t for t, _ in lines[1]) == "Item Level 80"
    assert "".join(t for t, _ in lines[2]) == "One-Hand    Sword"
    assert ("25", "#ffd100") in lines[3]


def test_addon_reports_open_game_windows():
    pytest.importorskip("lupa")
    from tests.lua_harness import cells, load_addon
    lua = load_addon()
    g = lua.globals()
    lua.execute("""
        WoWChatTranslatorCompanion = { seen = 1 }
        bag = CreateFrame(nil, "ContainerFrame1"); bag.mouse = true; bag.strata = "MEDIUM"; bag.parent = UIParent
        bag.GetLeft = function() return 400 end; bag.GetRight = function() return 600 end
        bag.GetTop = function() return 300 end; bag.GetBottom = function() return 100 end
        hidden = CreateFrame(); hidden.mouse = true; hidden.strata = "HIGH"; hidden.shown = false
        hidden.GetRight = function() return 300 end; hidden.GetTop = function() return 200 end
        hidden.GetBottom = function() return 150 end
        container = CreateFrame(); container.strata = "MEDIUM"   -- not mouse enabled: ignored
        container.GetRight = function() return 300 end; container.GetTop = function() return 200 end
        container.GetBottom = function() return 150 end
        forbidden = CreateFrame(); forbidden.forbidden = true; forbidden.mouse = true; forbidden.strata = "DIALOG"
        UIParent.children = { ChatFrame1, forbidden, bag, hidden, container }
    """)
    g.FireEvent("ADDON_LOADED", "WoWChatTranslator")
    g.FireEvent("PLAYER_LOGIN")
    g.Tick(0.2)
    g.Tick(0.2)                       # the grid moved: kept a moment for the companion to find it
    payload = bridge.decode(cells(lua))[3]
    covers = bridge.parse_covers(payload)
    # Pixel scale 768/1440: the bag spans x 750..1125, y 877.5..1252.5 (rounded out to even
    # pixels), wherever the overlay is.
    assert covers == [(750, 876, 376, 378)]


def test_frames_always_on_screen_are_no_covers():
    """A damage meter or an action bar under the overlay is no window: no cut-out, and the
    bridge does not pause (the player put the overlay over it on purpose). A frame closed
    with Escape is one."""
    pytest.importorskip("lupa")
    from tests.lua_harness import cells, load_addon
    lua = load_addon()
    g = lua.globals()
    lua.execute("""
        WoWChatTranslatorCompanion = { seen = 1 }
        UISpecialFrames = { "MyAddonWindow" }
        local function Big(name)
            local f = CreateFrame(nil, name); f.mouse = true; f.strata = "MEDIUM"; f.parent = UIParent
            f.GetLeft = function() return 0 end; f.GetRight = function() return 1834 end
            f.GetTop = function() return 768 end; f.GetBottom = function() return 0 end
            return f
        end
        meter, bar = Big("DetailsBaseFrame1"), Big("ElvUI_Bar1")
        UIParent.children = { ChatFrame1, meter, bar }
    """)
    g.FireEvent("ADDON_LOADED", "WoWChatTranslator")
    g.FireEvent("PLAYER_LOGIN")
    g.Tick(0.2)
    g.Tick(0.2)
    assert bridge.parse_covers(bridge.decode(cells(lua))[3]) == []
    lua.execute("""
        local f = CreateFrame(nil, "MyAddonWindow"); f.mouse = true; f.strata = "MEDIUM"; f.parent = UIParent
        f.GetLeft = function() return 400 end; f.GetRight = function() return 600 end
        f.GetTop = function() return 300 end; f.GetBottom = function() return 100 end
        UIParent.children = { ChatFrame1, f }
    """)
    for _ in range(30):
        g.Tick(0.2)
    assert bridge.parse_covers(bridge.decode(cells(lua))[3]) == [(750, 876, 376, 378)]


def test_toggle_message_uses_player_binding():
    pytest.importorskip("lupa")
    from tests.lua_harness import load_addon
    lua = load_addon()
    g = lua.globals()
    lua.execute("WoWChatTranslatorCompanion = { seen = 1 }; GetLocale = function() return 'frFR' end")
    g.FireEvent("ADDON_LOADED", "WoWChatTranslator")
    g.FireEvent("PLAYER_LOGIN")
    lua.execute("bindings = { F9 = 'WOWCHATTRANSLATOR_TOGGLE' }")
    g.WoWChatTranslator_Toggle()
    message = list(g.printed.values())[-1]
    assert "F9" in message and "Alt+F6" not in message


def test_cover_record_fits_in_one_packet():
    payload_room = (bridge.COLS * bridge.ROWS - len(bridge.SYNC)) * 3 // 8 - 6
    record = "cover\x1f" + "A" * 8 * 40 + "\x1f\x1f"
    assert len(record.encode()) <= payload_room
    assert bridge.parse_covers(b"cover\x1f" + b"00010203" + b"\x1f\x1f") == [(0, 2, 4, 6)]


def test_grid_moves_away_from_game_windows():
    pytest.importorskip("lupa")
    from tests.lua_harness import load_addon
    lua = load_addon()
    g = lua.globals()
    lua.execute("""
        WoWChatTranslatorCompanion = { seen = 1 }
        UIParent.children = { ChatFrame1 }
        bag = CreateFrame(nil, "ContainerFrame1"); bag.mouse = true; bag.strata = "MEDIUM"; bag.shown = false
        bag.GetLeft = function() return 380 end; bag.GetRight = function() return 600 end
        bag.GetTop = function() return 300 end; bag.GetBottom = function() return 200 end
        table.insert(UIParent.children, bag)
        function GridPoint()
          for _, f in ipairs(frames) do
            if rawget(f, "x") then return f.x, f.y end
          end
        end
    """)
    g.FireEvent("ADDON_LOADED", "WoWChatTranslator")
    g.FireEvent("PLAYER_LOGIN")
    g.Tick(0.2)
    top_right = tuple(lua.eval("{GridPoint()}").values())
    assert top_right == (866 - 192 - 4, 1440 - 971 - 4)   # chat top-right corner
    lua.execute("bag.shown = true")
    g.Tick(0.2)
    assert tuple(lua.eval("{GridPoint()}").values()) == (60 + 4, 1440 - 971 - 4)    # moved to the free top-left corner
    # Now the bag covers the whole chat: nothing is sent, the line waits.
    lua.execute("bag.GetLeft = function() return 0 end; bag.GetBottom = function() return 100 end")
    g.Tick(0.2)
    g.FireEvent("CHAT_MSG_SAY", "paused", "Bob Stone")
    g.Tick(0.2)
    from tests.lua_harness import cells
    assert not bridge.parse_payload(bridge.decode(cells(lua))[3])
    lua.execute("bag.shown = false")
    g.Tick(0.2)
    g.Tick(0.2)
    texts = [l.text for l in bridge.parse_payload(bridge.decode(cells(lua))[3])]
    assert texts == ["paused"] and tuple(lua.eval("{GridPoint()}").values()) == top_right


def test_bridge_reports_vanished_grid_at_once():
    import numpy as np
    from wctc import bridge

    screen = np.full((300, 600, 3), 30, dtype=np.int16)

    def draw(gx, gy):
        for index, value in enumerate(bridge.encode(1, 1, b"")):
            row, col = divmod(index, bridge.COLS)
            color = [bridge.BASE[c] + (bridge.DELTA if (value >> (2 - c)) & 1 else 0) for c in range(3)]
            screen[gy + row * 3:gy + row * 3 + 3, gx + col * 3:gx + col * 3 + 3] = color

    class FakeCapture:
        name = "dxgi"

        def grab(self, left, top, width, height):
            return screen[top:top + height, left:left + width].copy()

    draw(300, 20)
    covers = []
    pb = bridge.PixelBridge(lambda lines: None, covers.append)
    pb._game_client = lambda: (0, 0, 600, 300)
    pb.expected_origins = lambda: [(300, 20), (20, 20)]
    capture = FakeCapture()
    pb._tick(capture)
    assert pb.active and pb.grid_origin == (300, 20)
    screen[:] = 30                       # a bag opens over the whole overlay
    for _ in range(bridge.GONE_AFTER_MISSES):
        pb._tick(capture)
    assert not pb.active and covers[-1] == []
    draw(20, 20)                         # closed: the grid is back, in another corner
    pb._tick(capture)
    assert pb.active and pb.grid_origin == (20, 20)


def test_grid_hidden_during_game_screenshot():
    pytest.importorskip("lupa")
    from tests.lua_harness import load_addon
    lua = load_addon()
    g = lua.globals()
    lua.execute("""
        WoWChatTranslatorCompanion = { seen = 1 }
        function GridAlpha()
          for _, f in ipairs(frames) do if rawget(f, "x") then return f.alpha end end
        end
    """)
    g.FireEvent("ADDON_LOADED", "WoWChatTranslator")
    g.FireEvent("PLAYER_LOGIN")
    g.Tick(0.1)
    g.Screenshot()
    # The original runs untouched (no taint), the grid is hidden right after the call.
    assert g.shots == 1 and lua.eval("GridAlpha()") == 0


def test_screenshot_lifts_exclusion_only_when_needed(monkeypatch):
    import sys as _sys
    import types

    import numpy as np
    from wctc import screenshot, winutil

    game = np.full((100, 300, 4), 40, dtype=np.uint8)
    for index, value in enumerate(bridge.encode(1, 1, b"")):
        row, col = divmod(index, bridge.COLS)
        rgb = [bridge.BASE[c] + (bridge.DELTA if (value >> (2 - c)) & 1 else 0) for c in range(3)]
        game[10 + row * 3:13 + row * 3, 50 + col * 3:53 + col * 3, :3] = rgb[::-1]   # BGRA
    state = {"excluded": True}
    calls = []

    class FakeMss:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def grab(self, region):
            return game if state["excluded"] else np.full_like(game, 11)   # overlay drawn

    monkeypatch.setitem(_sys.modules, "mss", types.SimpleNamespace(mss=FakeMss))

    def exclude(hwnd, exclude=True):
        calls.append(exclude)
        state["excluded"] = exclude
        return True

    monkeypatch.setattr(winutil, "exclude_from_capture", exclude)
    img = screenshot.capture_with_overlay((0, 0, 300, 100), [123])
    assert calls == [False, True] and int(img[0, 0, 0]) == 11 and state["excluded"]


def test_screenshot_key_bound_in_game_reaches_companion():
    pytest.importorskip("lupa")
    from tests.lua_harness import cells, load_addon
    lua = load_addon()
    g = lua.globals()
    lua.execute("WoWChatTranslatorCompanion = { seen = 1 }")
    g.FireEvent("ADDON_LOADED", "WoWChatTranslator")
    g.FireEvent("PLAYER_LOGIN")
    assert g.bindings["CTRL-PRINTSCREEN"] == "WOWCHATTRANSLATOR_SCREENSHOT"   # changeable in game
    g.Tick(0.2)
    g.WoWChatTranslator_Screenshot()
    g.Tick(0.2)
    assert bridge.parse_requests(bridge.decode(cells(lua))[3]) == ["shot"]


def test_quest_link_with_level_prefix():
    from wctc.chatparser import parse_links, strip_escapes
    from wctc.glossary import Glossary

    raw = "LFG |cffffff00|Hquest:97250:23|h[[23+] Accusé à tort, corrigé à raison]|h|r"
    assert [(l.kind, l.id, l.name) for l in parse_links(raw)] == [
        ("quest", 97250, "[23+] Accusé à tort, corrigé à raison")]
    masked, chunks = Glossary().protect(strip_escapes(raw))
    assert chunks[0] == "[[23+] Accusé à tort, corrigé à raison]" and "Accusé" not in masked


def test_addon_announcements_kept_out():
    pytest.importorskip("lupa")
    from tests.lua_harness import load_addon
    lua = load_addon()
    g = lua.globals()
    lua.execute("WoWChatTranslatorCompanion = { seen = 1 }")
    g.FireEvent("ADDON_LOADED", "WoWChatTranslator")
    q = "|cffffff00|Hquest:97250:23|h[[23+] Accusé à tort, corrigé à raison]|h|r"
    done = "|cffffff00|Hquest:97250:23|h[[23+] Accusé à tort, corrigé à raison (Terminée)]|h|r"
    is_addon = g.addon_ns.IsAddonAnnouncement
    assert is_addon(f"1/1 Outraged Pillager slain for {q}!")
    assert is_addon(f"Soldat envahissant : 2/2 personnages tués pour {done} !")
    assert is_addon("Questie: quête acceptée")
    assert is_addon(f"|cff00ccffQuestie|r : Quête Terminée : {q}")
    assert is_addon(f"{{rt3}} Questie : Quête Terminée : {q}")
    assert is_addon("{rt3} RestedXP Guides: Flying to Orgrimmar, Durotar ETA 6 minutes 25 seconds")
    assert is_addon("Polestar : |cffffff00|Hquest:6461:29|h[ON RECHERCHE : Arnak Totem-sinistre]|h|r est prête à rendre")
    assert not is_addon("anyone seen the pole star tonight?")
    assert is_addon(f"|TInterface\\Icons\\INV_Misc_Note_01:0|t Questie : Quête Terminée : {q}")
    assert not is_addon(f"LFM {q} 3/5 need heal")
    assert not is_addon(f"qui pour {q} ?")


def test_glued_chat_words_are_split():
    from wctc.glossary import Glossary

    g = Glossary()
    assert g.split_glued("needtank for WC 20 +") == "need tank for WC 20 +"
    assert g.split_glued("LFMheal rfc") == "LFM heal rfc"
    assert g.split_glued("Bonjour tout le monde, needed") == "Bonjour tout le monde, needed"


def test_shorthand_converted_per_language():
    from wctc.glossary import Glossary

    g = Glossary()
    masked, chunks = g.protect("mdr merci")
    assert g.foreign_shorthand(chunks, "en") and g.restore(masked, chunks, "en") == "lol thanks"
    masked, chunks = g.protect("lol thx")
    assert not g.foreign_shorthand(chunks, "en")          # English reader: left as typed
    masked, chunks = g.protect("ищу танка, спс")
    assert g.restore(masked, chunks, "fr") == "ищу tank, merci"


def test_other_eu_languages_detected():
    from wctc.detector import LanguageDetector

    d = LanguageDetector()
    assert d.detect("Cześć, ktoś chce iść do lochu?", hint="fr")[0] == "pl"
    assert d.detect("Привіт, хто йде в підземелля?", hint="fr")[0] == "uk"
    assert d.detect("Ahoj, kdo jde do dungeonu?", hint="fr")[0] == "cs"
    assert d.detect("in de stad", hint="fr")[0] != "nl"            # too short to be sure
    assert d.detect("je cherche un groupe pour rfc", hint="fr")[0] == "fr"


def test_packet_kept_while_companion_finds_moved_grid():
    pytest.importorskip("lupa")
    from tests.lua_harness import cells, load_addon
    lua = load_addon()
    g = lua.globals()
    lua.execute("""
        WoWChatTranslatorCompanion = { seen = 1 }
        bag = CreateFrame(nil, "ContainerFrame1"); bag.mouse = true; bag.strata = "MEDIUM"; bag.shown = false
        bag.GetLeft = function() return 380 end; bag.GetRight = function() return 600 end
        bag.GetTop = function() return 300 end; bag.GetBottom = function() return 200 end
        UIParent.children = { ChatFrame1, bag }
    """)
    g.FireEvent("ADDON_LOADED", "WoWChatTranslator")
    g.FireEvent("PLAYER_LOGIN")
    g.Tick(0.3)
    g.FireEvent("CHAT_MSG_SAY", "first line", "Bob Stone")
    g.Tick(0.1)
    lua.execute("bag.shown = true")                 # the grid moves to another corner
    g.FireEvent("CHAT_MSG_SAY", "second line", "Bob Stone")
    g.Tick(0.1)
    texts = lambda: [l.text for l in bridge.parse_payload(bridge.decode(cells(lua))[3])]
    assert "second line" not in texts()             # time for the companion to find the grid
    g.Tick(0.3)
    g.Tick(0.1)
    assert "second line" in texts()


def test_old_glossary_copy_replaced_by_template(tmp_path, monkeypatch):
    import json
    from wctc import glossary

    monkeypatch.setattr(glossary, "config_dir", lambda: tmp_path)
    old = {"keep": ["tank", "heal", "dps", "wts", "spriest", "lf"],
           "concepts": [{"en": "dungeon"}, {"en": "healer"}, {"en": "guild"}], "map": {}}
    (tmp_path / "glossary.json").write_text(json.dumps(old), encoding="utf-8")
    g = glossary.Glossary()
    assert "_info" in json.loads((tmp_path / "glossary.json").read_text(encoding="utf-8"))
    assert (tmp_path / "glossary.old.json").is_file()
    assert "lf" not in g.keep                      # written out by "expand" instead


def test_class_names_in_reader_language():
    from wctc.glossary import Glossary

    g = Glossary()
    masked, chunks = g.protect("LFM rogue and hunt for SM, 5g each, pst")
    assert g.restore(masked, chunks, "de") .count("Schurke") == 1 and "Jäger" in g.restore(masked, chunks, "de")
    masked, chunks = g.protect("ищу лока и шама")
    restored = g.restore(masked, chunks, "fr")
    assert "démoniste" in restored and "chaman" in restored


def test_extra_reading_languages():
    from wctc import LANGUAGES
    from wctc.detector import LanguageDetector
    from wctc.glossary import Glossary

    assert "pl" in LANGUAGES and "tr" in LANGUAGES
    g = Glossary()
    masked, chunks = g.protect("thx, LFM rogue")
    restored = g.restore(masked, chunks, "pl")
    assert restored == "dzięki, looking for more players rogue"   # own word, else the English game term
    masked, chunks = g.protect("tak, idę")           # Polish "yes": not "thanks"
    assert "tak" not in [c.lower() for c in chunks]
    # A Polish reader: short Polish lines are his own language, left untouched.
    assert LanguageDetector().detect("idę do lochu", hint="pl")[0] == "pl"


def test_ui_strings_for_every_reading_language():
    import string
    from wctc import LANGUAGES
    from wctc.i18n import STRINGS

    reference = STRINGS["en"]
    for lang in LANGUAGES:
        table = STRINGS[lang]
        assert set(table) == set(reference), lang
        for key, text in table.items():
            fields = {f for _, f, _, _ in string.Formatter().parse(text) if f}
            expected = {f for _, f, _, _ in string.Formatter().parse(reference[key]) if f}
            assert fields == expected, (lang, key)


def test_addon_speaks_companion_language():
    pytest.importorskip("lupa")
    from tests.lua_harness import load_addon
    lua = load_addon()
    g = lua.globals()
    lua.execute('WoWChatTranslatorCompanion = { seen = 1, lang = "pl" }')
    g.FireEvent("ADDON_LOADED", "WoWChatTranslator")
    g.FireEvent("PLAYER_LOGIN")
    g.WoWChatTranslator_Toggle()
    assert "Nakładka tłumaczenia" in list(g.printed.values())[-1]
    lua.execute('WoWChatTranslatorCompanion.lang = "fr"')        # English client, French reader
    g.WoWChatTranslator_Toggle()
    assert "Surcouche de traduction" in list(g.printed.values())[-1]


def test_addon_locales_complete():
    import re
    folder = Path(__file__).resolve().parents[2] / "addon" / "WoWChatTranslator" / "Locales"
    keys = {}
    for path in folder.glob("*.lua"):              # one file per language
        name, body = re.search(r"ns\.Locales\.(\w+) = \{\n(.*?)\n\}", path.read_text(encoding="utf-8"), re.S).groups()
        keys[name] = set(re.findall(r"^\s+(\w+) = ", body, re.M))
    assert len(keys) == 21
    for name, found in keys.items():
        assert found == keys["enUS"], name


def test_addon_language_needs_displayable_letters():
    pytest.importorskip("lupa")
    from tests.lua_harness import load_addon
    # 7: same width as the "missing letter" box -> not displayable; 0: not drawn; 9: real letters.
    for width, expected in ((0, "Surcouche de traduction"), (7, "Surcouche de traduction"), (9, "Шар перекладу")):
        lua = load_addon()
        g = lua.globals()
        lua.execute(f"""
            WoWChatTranslatorCompanion = {{ seen = 1, lang = "uk" }}
            UIParent.CreateFontString = function()
              local text = ""
              return {{ SetFontObject = function() end, SetText = function(_, t) text = t end, Hide = function() end,
                        GetStringWidth = function() return text == "\\238\\128\\128" and 7 or {width} end }}
            end
        """)
        g.FireEvent("ADDON_LOADED", "WoWChatTranslator")
        g.FireEvent("PLAYER_LOGIN")
        g.WoWChatTranslator_Toggle()
        assert expected in list(g.printed.values())[-1]


def test_short_lines_in_reader_language():
    from wctc.glossary import Glossary

    g = Glossary()
    masked, chunks = g.protect("morning")
    assert g.foreign_shorthand(chunks, "uk") and g.restore(masked, chunks, "uk") == "доброго ранку"
    assert not g.foreign_shorthand(g.protect("thx")[1], "en")       # English reader: as typed
    masked, chunks = g.protect("un mage dispo pour un tp?")
    assert masked == "un ZX1 disponible pour un ZX2?"


def test_english_shorthand_written_out():
    from wctc.glossary import Glossary

    g = Glossary()
    masked, chunks = g.protect("can sb port me to UC ?")
    assert g.residual_text(masked) == "can somebody me to" and "UC" in chunks   # "port" -> portal term
    masked, _ = g.protect("Wir sind im Raid")                 # German "im" left alone
    assert "im Raid" in masked or "im" in masked


def test_long_lines_split_into_sentences():
    from wctc.engine import split_sentences
    from wctc.pipeline import _soften_caps

    text = ("(Foxes Fortune) is looking for English speaking, friendly people to play the game with, "
            "We plan on doing all content. Relaxed NON toxic Helpful fun people. All are welcome, "
            "Discord available for groups and Raids. Come Join us today! Send me a tell!")
    parts = split_sentences(text)
    assert len(parts) == 5 and parts[-1] == "Send me a tell!"
    assert split_sentences("Ok! ZX1 for WC? pst") == ["Ok! ZX1 for WC? pst"]
    assert _soften_caps("Relaxed NON toxic ZX1 for WC") == "Relaxed non toxic ZX1 for WC"


def test_model_choice(monkeypatch, tmp_path):
    from wctc import models

    monkeypatch.setattr(models, "models_dir", lambda: tmp_path / "exe_models")
    monkeypatch.setattr(models, "fallback_models_dir", lambda: tmp_path / "appdata_models")
    standard = tmp_path / "exe_models" / models.MODELS["standard"]["dir"]
    standard.mkdir(parents=True)
    (standard / "model.bin").write_bytes(b"x")
    monkeypatch.setattr(models, "machine_suits_quality", lambda: True)
    monkeypatch.setattr(models, "machine_is_modest", lambda: False)
    assert models.wanted_model("auto") == "standard"                  # never asks for a download
    assert models.usable_model("auto") == ("standard", standard)
    assert models.usable_model("quality") == ("standard", standard)   # chosen but not downloaded
    quality = tmp_path / "appdata_models" / models.MODELS["quality"]["dir"]
    quality.mkdir(parents=True)
    (quality / "model.bin").write_bytes(b"x")
    assert models.usable_model("auto") == ("quality", quality)
    assert models.usable_model("standard") == ("standard", standard)
    monkeypatch.setattr(models, "machine_suits_quality", lambda: False)
    assert models.usable_model("auto")[0] == "standard"
    monkeypatch.setattr(models, "machine_is_modest", lambda: True)
    assert models.usable_model("auto") == ("light", standard)        # same files, lighter settings


def test_no_model_installed(monkeypatch, tmp_path):
    from wctc import models
    monkeypatch.setattr(models, "models_dir", lambda: tmp_path / "exe_models")
    monkeypatch.setattr(models, "fallback_models_dir", lambda: tmp_path / "appdata_models")
    monkeypatch.setattr(models, "machine_suits_quality", lambda: False)
    monkeypatch.setattr(models, "machine_is_modest", lambda: False)
    assert models.installed_models() == []
    assert models.usable_model("auto") == ("standard", None)        # nothing to load: offer a download
    assert models.files_key("light") == "standard" and models.MODELS["standard"]["asset"]
    quality = tmp_path / "exe_models" / models.MODELS["quality"]["dir"]
    quality.mkdir(parents=True)
    (quality / "model.bin").write_bytes(b"x")
    # Only Quality downloaded: used even by "auto" or "standard" on a modest PC.
    assert models.usable_model("auto") == ("quality", quality)
    assert models.usable_model("standard") == ("quality", quality)
    assert models.recommended_model() == "standard"


def test_model_texts_complete():
    from wctc import LANGUAGES
    from wctc.i18n import STRINGS
    from wctc.i18n_models import MODEL_TEXTS
    from wctc.i18n_help import KEYS, LABEL_KEYS
    keys = set(MODEL_TEXTS["en"]) | set(KEYS) | set(LABEL_KEYS) | {"menu_class_colors", "help_class_colors", "menu_notifications", "help_notifications", "menu_translation_log", "help_translation_log"}
    for lang in LANGUAGES:
        assert keys <= set(STRINGS[lang]), lang
        for key in keys:
            STRINGS[lang][key].format(name="X", size=1, done=1, total=2, path="p", version="1", percent=5, error="e", n=3)


def test_models_folder_write_check(tmp_path):
    from wctc import models
    assert models.folder_writable(tmp_path / "models")
    blocker = tmp_path / "file"
    blocker.write_text("x")
    assert not models.folder_writable(blocker / "models")     # cannot be created


def test_model_output_tidy():
    from wctc.engine import _tidy
    assert _tidy("Quelqu' un peut-il m' aider ?") == "Quelqu'un peut-il m'aider ?"


def test_official_place_names():
    from wctc.glossary import Glossary

    g = Glossary()
    for text, lang, expected in (
            ("hillsbrad foothills", "fr", "Contreforts de Hautebrande"),
            ("Todesminen", "en", "Deadmines"),
            ("stonetalon", "fr", "Serres-Rocheuses"),
            ("the crossroads", "fr", "La Croisée"),
            ("Ashenvale", "pl", "Ashenvale")):            # no Polish client: English name
        masked, chunks = g.protect(text)
        assert g.restore(masked, chunks, lang) == expected, text
    masked, chunks = g.protect("I need a camp fire")          # everyday words are not places
    assert "camp" not in [c.lower() for c in chunks]


def test_short_lines_language_from_small_words():
    from wctc.detector import LanguageDetector
    d = LanguageDetector()
    assert d.detect("I have", hint="fr")[0] == "en"
    assert d.detect("Got page D", hint="fr")[0] == "en"
    assert d.detect("ich bin gleich da", hint="fr")[0] == "de"
    assert d.detect("je suis là", hint="en")[0] == "fr"


def test_smileys_recognised():
    from wctc.emoji import SMILEY_RE, emoji_for
    found = [m.group(0) for m in SMILEY_RE.finditer("ok :D <3 ^^ xD http://a.b/c :p 3:30 x:3")]
    assert found == [":D", "<3", "^^", "xD", ":p"]
    assert emoji_for(":D") == "😄"


def test_tray_menu_builds_with_real_config(monkeypatch, tmp_path):
    """Every label and check mark of the tray menu must work with the real Config (a failing
    one stops the icon's thread: the icon then vanishes when the mouse passes over it)."""
    import sys as _sys
    import types
    from wctc import config as config_module

    monkeypatch.setattr(config_module, "config_dir", lambda: tmp_path)
    cfg = config_module.Config()

    class Item:
        def __init__(self, text, action=None, checked=None, radio=False, **kw):
            self.text, self.checked = text, checked
            self.submenu = action if isinstance(action, Menu) else None

    class Menu:
        SEPARATOR = object()

        def __init__(self, *items):
            self.items = [i for i in items if i is not Menu.SEPARATOR]

    fake = types.SimpleNamespace(Menu=Menu, MenuItem=Item, Icon=lambda *a, **k: types.SimpleNamespace())
    monkeypatch.setitem(_sys.modules, "pystray", fake)
    import importlib
    from wctc import tray as tray_module
    importlib.reload(tray_module)

    class Dispatch:
        def __call__(self, *a):
            pass

        def __getattr__(self, name):
            return lambda *a: False

    tray = tray_module.Tray(cfg, lambda key, **kw: key, Dispatch(), ["WoW Forever"])

    def walk(menu):
        for item in menu.items:
            label = item.text(item) if callable(item.text) else item.text
            assert isinstance(label, str)
            if item.checked:
                item.checked(item)
            if item.submenu:
                walk(item.submenu)

    walk(tray._menu())


def test_downloads_checked_against_github_sha256(tmp_path):
    import hashlib
    import pytest
    from wctc import updater
    good = tmp_path / "file.zip"
    good.write_bytes(b"genuine")
    asset = {"name": "file.zip", "digest": "sha256:" + hashlib.sha256(b"genuine").hexdigest()}
    updater.verify_sha256(good, asset)                      # matches: kept
    assert good.is_file()
    bad = tmp_path / "bad.zip"
    bad.write_bytes(b"tampered")
    with pytest.raises(updater.IntegrityError):
        updater.verify_sha256(bad, asset)
    assert not bad.exists()                                  # never unpacked
    for missing in ({"name": "x"}, {"name": "x", "digest": "sha1:abc"}, None):
        with pytest.raises(updater.IntegrityError):
            updater.expected_sha256(missing)                 # no digest: download refused


def test_parse_payload_class_field():
    record = "say\x1fBob dit\x1fBob\x1fhello there\x1fwarlock"
    assert bridge.parse_payload(record.encode())[0].player_class == "WARLOCK"
    old = "say\x1fBob dit\x1fBob\x1fhello there"                   # addon without the class field
    assert bridge.parse_payload(old.encode())[0].player_class == ""


def test_tidy_space_before_full_stop():
    from wctc.engine import _tidy
    assert _tidy("C'est plutôt cool .") == "C'est plutôt cool."
    assert _tidy("Quelqu' un , ici ?") == "Quelqu'un, ici ?"        # French space before ? kept


def test_detection_ignores_expanded_shorthand():
    from wctc.glossary import Glossary
    g = Glossary()
    # "LFM" expands to English: the language is decided by what the player wrote himself.
    assert "looking" not in g.detection_text("LFM Tank pour Dalaran")
    assert g.detection_text("LFM Tank pour Dalaran").split() == ["pour"]
    assert g.detection_text("LFM tank SFK") == ""        # only shorthand: the expansion decides


def test_translation_log(caplog):
    import logging
    from wctc.chatparser import ChatLine
    from wctc.glossary import Glossary
    from wctc.pipeline import TranslationPipeline

    class Detector:
        def detect(self, text, hint=None):
            return "en", 0.99

    class Engine:
        def translate(self, text, source, target):
            return "Bonjour tout le monde"

    p = TranslationPipeline(None, None, Glossary(), lambda: "fr", None, None)
    p.detector, p.engine = Detector(), Engine()
    line = ChatLine("", "", "[1. General] Bob", "Bob", "hello everyone there", "channel")
    with caplog.at_level(logging.INFO, logger="wctc.translations"):
        p.process(line)
        assert not caplog.records                     # off by default
        p.trace_enabled = lambda: True
        p.process(line)
    text = caplog.records[-1].getMessage()
    assert "'hello everyone there'" in text and "en (0.99) -> fr" in text
    assert "shown: 'Bonjour tout le monde' (translated)" in text


def test_craftsman_and_profession_kept_apart():
    from wctc.glossary import Glossary
    g = Glossary()
    for word, fr in (("miner", "mineur"), ("mining", "minage"), ("tailor", "couturier"), ("tailoring", "couture"),
                     ("blacksmith", "forgeron"), ("skinner", "dépeceur"), ("Ragefire", "Gouffre de Ragefeu")):
        masked, chunks = g.protect(f"need {word} now")
        assert g.restore(masked, chunks, "fr") == f"need {fr} now", word


def test_craft_ad_shorthand():
    from wctc.glossary import Glossary
    g = Glossary()
    masked, chunks = g.protect("Enchanting your mats + tips welcome")
    assert "your materials" in masked
    assert "(pourboire bienvenu)" in g.restore(masked, chunks, "fr")


def test_finish_touches():
    from wctc.pipeline import _finish
    assert _finish("à la recherche de enchanteur", "LF enchanter", "fr") == "À la recherche d'enchanteur"
    assert _finish("Je le fabrique, (paiement bienvenu).", "can craft, tips welcome", "fr") == "Je le fabrique (paiement bienvenu)"
    assert _finish("C'est fini.", "it is done.", "fr") == "C'est fini."
    assert _finish("Où puis-je acheter une canne ?", "where can i buy", "fr") == "Où puis-je acheter une canne ?"


def test_free_phrases_go_whole_to_the_model():
    from wctc.glossary import Glossary
    g = Glossary()
    masked, chunks = g.protect("no fishing pole at the general goods vendor")
    assert "fishing rod" in masked and chunks == ["general goods vendor"]
    assert g.restore(masked, chunks, "fr").endswith("vendeur de fournitures générales")


def test_gm_greeting_only_when_alone():
    from wctc.glossary import Glossary
    g = Glossary()
    assert g.protect("gm !")[0].startswith("ZX1") and g.restore(*g.protect("gm !"), "fr") == "bonjour !"
    assert "GM" in g.restore(*g.protect("ask a GM about it"), "fr")       # Game Master stays


def test_glued_greetings():
    from wctc.glossary import Glossary
    g = Glossary()
    for text, fr in (("goodmorning", "bonjour"), ("goodnight", "bonne nuit"), ("goodmorning all", "bonjour à tous")):
        masked, chunks = g.protect(text)
        assert g.restore(masked, chunks, "fr") == fr, text


def test_corpus_is_valid_and_glossary_checks_pass():
    """tests/corpus.jsonl: well-formed; its "mask" entries hold without a model (the full run
    with the model is build/check_translations.py)."""
    sys.path.insert(0, str(ROOT / "build"))
    from check_translations import load_corpus
    g = Glossary()
    entries = list(load_corpus())
    assert len(entries) > 30
    for entry in entries:
        assert set(entry) <= {"text", "target", "translated", "expect", "forbid", "mask", "allow", "line_number"}, entry
        if "mask" in entry:
            _, chunks = g.protect(entry["text"])
            lowered = [c.lower() for c in chunks]
            for term in entry["mask"]:
                assert term.lower() in lowered, (entry["text"], term, chunks)


def test_lost_term_retried_piece_by_piece():
    """The model drops a last sentence or a trailing term: each sentence is translated alone,
    then the line without its trailing terms, which are put back after it."""
    from wctc.glossary import Glossary
    from wctc.pipeline import TranslationPipeline

    class Engine:
        calls = []

        def translate(self, text, source, target):
            self.calls.append(text)
            return {"qualcuno per ZX1?": "Quelqu'un pour ZX1 ?",
                    "need a resurrection": "J'ai besoin d'une résurrection"}.get(text, "perdu")

    p = TranslationPipeline(None, None, Glossary(), lambda: "fr", None, None)
    p.engine = Engine()
    chunks = ["RFC", "grazie"]
    assert p._retry_lost("qualcuno per ZX1? ZX2", chunks, "it", "fr") == "Quelqu'un pour RFC ? merci"
    assert "ZX2" not in p.engine.calls                     # a lone term is not sent to the model
    assert p._retry_lost("need a resurrection ZX1", ["pls"], "en", "fr") == "J'ai besoin d'une résurrection stp"
    assert p._retry_lost("ZX1", ["pls"], "en", "fr") is None


def test_shorthand_detection_helpers():
    from wctc.glossary import Glossary
    g = Glossary()
    assert g.split_glued("stop trolling") == "stop trolling"           # no "st op"
    assert g.split_glued("needtank") == "need tank"
    assert g.detection_text("WTB Mithril Bar x20, pst").split() == []  # "x20" is no word
    assert g.expanded("gz on 60!") == "congratulations on reaching level 60!"
    masked, chunks = g.protect("WTB Mithril Bar x20, pst")
    assert g.concept_count(chunks) == 3                   # WTB, Mithril Bar, pst


def test_grid_tinted_by_low_health_flash_is_still_there():
    """The red low-health flash saturates the red channel: the packet cannot be read, but the
    grid is not hidden (no reason to hide the overlay). A window over it shows no pattern."""
    import numpy as np
    from wctc import bridge
    cells = bridge.encode(1, 1, b"hello")
    img = np.zeros((bridge.HEIGHT, bridge.WIDTH, 3), dtype=np.int16)
    for i, value in enumerate(cells):
        y, x = (i // bridge.COLS) * bridge.CELL, (i % bridge.COLS) * bridge.CELL
        img[y:y + bridge.CELL, x:x + bridge.CELL] = [
            bridge.BASE[c] + (bridge.DELTA if (value >> (2 - c)) & 1 else 0) for c in range(3)]
    assert bridge.decode(bridge.sample_cells(img, 0, 0))
    tinted = img.copy()
    tinted[:, :, 0] = 255                                  # red saturated
    tinted[:, :, 1:] = tinted[:, :, 1:] // 3               # green and blue dimmed
    assert bridge.sample_cells(tinted, 0, 0) is None
    assert bridge.sync_visible(tinted)
    window = np.full_like(img, 90)
    assert not bridge.sync_visible(window)


def test_french_plural_place_names_get_contracted_article():
    from wctc.glossary import Glossary
    g = Glossary()
    masked, chunks = g.protect("One tank and go Wailing caverns")
    assert "and we go" in masked
    out = masked.replace("One", "Un").replace("and we go", "et on va à").replace("tank", "tank")
    restored = g.restore(out.replace("ZX1", "ZX1", 1), chunks, "fr")
    assert "aux Cavernes des lamentations" in restored
    masked, chunks = g.protect("go to Tanaris")
    assert g.restore("aller à ZX1", chunks, "fr") == "aller à Tanaris"


def test_terms_spelled_out_and_glued_links():
    from wctc.glossary import Glossary
    g = Glossary()
    masked, chunks = g.protect("i play wow forever at work")
    assert g.spelled_out(masked, chunks) == "i play Wow Forever at work"
    masked, chunks = g.protect("WTB[Fiery War Axe]30g")
    assert g.core_text(masked) == ""                      # only terms: no model needed
    assert g.restore(masked, chunks, "fr") == "J'achète [Fiery War Axe] 30g"


def test_french_finishing_touches():
    from wctc.pipeline import _finish, _soften_caps
    assert _finish("mp pour un invitation", "/w for an invite", "fr") == "mp pour une invitation"
    assert _finish("- Oui, oui", "Yes", "fr") == "Oui"
    assert _finish("- Comment ?", "How?", "fr") == "Comment ?"
    assert _soften_caps("GaMe Is EaSY Im PaRt Of ThE EliTe") == "game is easy im part of the elite"
    assert _soften_caps("LF McDonald guild") == "LF McDonald guild"


def test_missed_lines_read_back_from_chat_log(tmp_path):
    """Lines sent while the game was out of sight come back from Logs/WoWChatLog.txt, without
    the ones the bridge delivered, nor crafting, loot or NPC lines."""
    import os
    import time
    from datetime import datetime
    from wctc.chatlog import ChatLogRecovery, parse_line
    from wctc.chatparser import ChatLine

    def stamp(t):
        d = datetime.fromtimestamp(t)
        return d.strftime("%m/%d %H:%M:%S.") + f"{d.microsecond // 1000:03d}"

    now = time.time()
    (tmp_path / "Logs").mkdir()
    log_file = tmp_path / "Logs" / "WoWChatLog.txt"
    log_file.write_text("\n".join([
        f"{stamp(now - 600)}  [1. Général] Old Timer : too old",
        f"{stamp(now - 50)}  [2. Commerce] Bob Stone : WTS [Copper Ore] x50",
        f"{stamp(now - 40)}  Augustus Volodymyr crée Barre de cuivre.",
        f"{stamp(now - 35)}  Thrall crie : Honorez vos héros !",
        f"{stamp(now - 30)}  [Guilde] Ann Lee : anyone up for RFC?",
        f"{stamp(now - 20)}  Kim Tan chuchote : hi there",
        f"{stamp(now - 10)}  [1. Général] Seen Already : delivered by the bridge",
    ]) + "\n", encoding="utf-8")
    recovery = ChatLogRecovery([tmp_path])
    recovery.delivered([ChatLine("", "", "[1. Général] Seen Already", "Seen Already",
                                 "delivered by the bridge", "channel")])
    assert recovery.logging_since(now - 60)
    lines = recovery.missed_lines(now - 60, now)
    assert [(l.kind, l.prefix, l.text) for l in lines] == [
        ("channel", "[2. Commerce] Bob Stone", "WTS [Copper Ore] x50"),
        ("guild", "[Guilde] Ann Lee", "anyone up for RFC?"),
        ("whisper", "Kim Tan chuchote", "hi there"),
    ]
    assert recovery.missed_lines(now - 60, now) == []          # each line comes back once
    os.utime(log_file, (now - 3600, now - 3600))
    assert not recovery.logging_since(now - 60)                # log not written: logging off
    assert parse_line("11/19 11:02:08.762  Expérience gagnée : 900.", 2026) is None


def test_chat_log_state_from_addon_and_to_addon(tmp_path):
    """The addon reports whether the game logs its chat; the option is written for it."""
    from wctc import bridge, installer
    from wctc.wow import Flavor
    payload = "state\x1fchatlog=1\x1f\x1f".encode()
    assert bridge.parse_state(payload) == {"chatlog": "1"}
    assert bridge.parse_state(b"cover\x1f\x1f\x1f") == {}
    assert bridge.parse_state("state\x1fchatlog=0,key=ALT-F6\x1f\x1f".encode()) == {"chatlog": "0", "key": "ALT-F6"}
    assert bridge.parse_payload(payload) == []                 # no chat line in it
    flavor = Flavor(tmp_path, tmp_path / "_classic_", "wow")
    (flavor.addons_dir / installer.ADDON_NAME).mkdir(parents=True)
    path = flavor.addons_dir / installer.ADDON_NAME / installer.COMPANION_FILE
    installer.write_companion_state(flavor, 100, None, "fr", None)
    assert "chatLog" not in path.read_text(encoding="utf-8")   # left to the player
    installer.write_companion_state(flavor, 100, None, "fr", True)
    assert "chatLog = true" in path.read_text(encoding="utf-8")
    installer.write_companion_state(flavor, 100, None, "fr", False)
    assert "chatLog = false" in path.read_text(encoding="utf-8")


def test_update_is_only_offered_never_downloaded_alone(monkeypatch):
    """The periodic check only tells about a new version; downloading waits for the player."""
    from wctc import updater
    events = []
    monkeypatch.setattr(updater, "latest_release", lambda: {"tag_name": "v9.9.9", "assets": []})
    monkeypatch.setattr(updater, "download_update", lambda *a, **k: pytest.fail("downloaded without consent"))
    checker = updater.Updater("1.0.0", lambda kind, version: events.append((kind, version)))
    checker._check()
    checker._check()                                    # the same version is offered once
    assert events == [("available", "v9.9.9")]


def test_update_script_without_restart_when_closing():
    from pathlib import Path
    from wctc import updater
    new_build = Path("C:/Users/x/AppData/Roaming/WCT/update/new/WoWChatTranslatorCompagnion")
    closing = updater.update_script(1, new_build, Path("C:/Games/WCT"), "WoWChatTranslatorCompagnion.exe", restart=False)
    assert "robocopy" in closing and "--after-update" not in closing
    assert "--after-update" in updater.update_script(1, new_build, Path("C:/Games/WCT"), "WoWChatTranslatorCompagnion.exe")


def test_product_from_folder_name_without_flavor_info(tmp_path):
    from wctc import wow
    folder = tmp_path / "_classic_era_"
    folder.mkdir()
    assert wow.read_product(folder) == "wow_classic_era"
    assert wow.read_product(tmp_path / "_forever_") == ""
