"""Runs the real addon Lua files in lupa with a minimal mocked WoW API (test helper)."""

from pathlib import Path

import lupa

ADDON_DIR = Path(__file__).resolve().parents[2] / "addon" / "WoWChatTranslator"

WOW_MOCK = r'''
bit = {
  band = function(a, b) return a & b end, bor = function(a, b) return a | b end,
  bxor = function(a, b) return a ~ b end, lshift = function(a, n) return a << n end,
  rshift = function(a, n) return a >> n end,
}
now = 0
function GetTime() return now end
function GetPhysicalScreenSize() return 3440, 1440 end
function GetLocale() return "frFR" end
function UnitName() return "Ela Borer" end
function GetNormalizedRealmName() return "R" end
function time() return 1 end
function InCombatLockdown() return false end
function ReloadUI() end
function Ambiguate(name) return (name:gsub("%-.*$", "")) end
format = string.format
function strlower(s) return s:lower() end
function strtrim(s) return s end
StaticPopupDialogs = {}
function StaticPopup_Show() end
printed = {}
DEFAULT_CHAT_FRAME = { AddMessage = function(_, m) table.insert(printed, m) end }
C_Timer = { After = function() end }
unpack = unpack or table.unpack
shots = 0
function Screenshot() shots = shots + 1 end
function hooksecurefunc(name, hook)
  local original = _G[name]
  _G[name] = function(...) local r = original(...); hook(...); return r end
end
C_AddOns = { GetAddOnMetadata = function() return "test" end }
CHAT_SAY_GET = "%s dit : "
CHAT_EMOTE_GET = "%s "
CHAT_GUILD_GET = "|Hchannel:GUILD|h[Guilde]|h %s : "
CHAT_WHISPER_GET = "%s chuchote : "
CHAT_WHISPER_INFORM_GET = "À %s : "
CHAT_PARTY_GET = "|Hchannel:PARTY|h[Groupe]|h %s : "

frames, textures = {}, {}
local function NewRegion()
  local r = {}
  setmetatable(r, { __index = function(t, k) return function() end end })
  return r
end
function CreateFrame(_, name)
  local f = NewRegion()
  f.name = name
  f.GetName = function(self) return rawget(self, "name") end
  f.events = {}
  f.RegisterEvent = function(self, e) self.events[e] = true end
  f.SetScript = function(self, what, fn) self[what] = fn end
  f.shown = true
  f.SetShown = function(self, v) self.shown = v end
  f.IsShown = function(self) return self.shown end
  f.GetLeft = function() return 32 end
  f.alpha = 1
  f.SetAlpha = function(self, a) self.alpha = a end
  f.IsVisible = function(self)
    if rawget(self, "forbidden") then error("Attempt to access forbidden object") end
    return self.shown
  end
  f.IsForbidden = function(self) return rawget(self, "forbidden") or false end
  f.GetFrameStrata = function(self) return rawget(self, "strata") or "LOW" end
  f.IsObjectType = function(self, t) return rawget(self, "objectType") == t end
  f.IsMouseEnabled = function(self) return rawget(self, "mouse") or false end
  f.GetEffectiveAlpha = function() return 1 end
  f.GetEffectiveScale = function() return 1 end
  f.GetParent = function(self) return rawget(self, "parent") end
  f.children = {}
  f.GetChildren = function(self) return (unpack or table.unpack)(self.children) end
  f.CreateTexture = function()
    local t = NewRegion()
    t.SetColorTexture = function(self, r, g, b)
      self.rgb = { math.floor(r * 255 + 0.5), math.floor(g * 255 + 0.5), math.floor(b * 255 + 0.5) }
      self.value = (self.rgb[1] > 12 and 4 or 0) + (self.rgb[2] > 15 and 2 or 0) + (self.rgb[3] > 19 and 1 or 0)
    end
    table.insert(textures, t)
    return t
  end
  table.insert(frames, f)
  return f
end
UIParent = CreateFrame()
UIParent.GetEffectiveScale = function() return 1 end
UIParent.GetWidth = function() return 1834 end
-- Font probe: every letter drawn (9 px), except the private-use "missing letter" box (7 px).
UIParent.CreateFontString = function()
  local text = ""
  return { SetFontObject = function() end, SetText = function(_, t) text = t end, Hide = function() end,
           GetStringWidth = function() return text == "\238\128\128" and 7 or 9 end }
end
UIParent.GetHeight = function() return 768 end
bindings = {}
function GetBindingKey(action) for k, a in pairs(bindings) do if a == action then return k end end end
function GetBindingAction(key) return bindings[key] or "" end
function SetBinding(key, action) bindings[key] = action end
function SaveBindings() end
function GetCurrentBindingSet() return 1 end
ChatFrame1 = CreateFrame()
ChatFrame1.GetEffectiveScale = function() return 1 end
ChatFrame1.GetTop = function() return 250 end
ChatFrame1.GetRight = function() return 462 end
ChatFrame1.GetBottom = function() return 130 end
ChatFrame1.parent = UIParent
ChatFrame1.GetWidth = function() return 430 end
ChatFrame1.GetHeight = function() return 120 end
SlashCmdList = {}
function FireEvent(event, ...)
  for _, f in ipairs(frames) do
    if f.events[event] and f.OnEvent then f.OnEvent(f, event, ...) end
  end
end
function Tick(dt)
  now = now + dt
  for _, f in ipairs(frames) do if f.OnUpdate then f.OnUpdate(f, dt) end end
end
function Cells()
  local out = {}
  for i, t in ipairs(textures) do out[i] = t.value or 0 end
  return out
end
'''


def load_addon():
    lua = lupa.LuaRuntime()
    lua.execute(WOW_MOCK)
    ns = lua.table()
    toc = (ADDON_DIR / "WoWChatTranslator.toc").read_text(encoding="utf-8")
    files = [l.strip().replace("\\", "/") for l in toc.splitlines() if l.strip().endswith(".lua")]
    for name in files:
        chunk = lua.execute("return load(...)", (ADDON_DIR / name).read_text(encoding="utf-8"), name)
        chunk("WoWChatTranslator", ns)
    lua.globals().addon_ns = ns
    return lua


def cells(lua):
    return [int(v) for v in lua.globals().Cells().values()]
