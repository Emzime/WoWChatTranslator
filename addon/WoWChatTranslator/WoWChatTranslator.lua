local ADDON_NAME, ns = ...
local L = ns.L

-- Data contract with the companion (read from SavedVariables after /reload or logout).
-- Bump DATA_VERSION if the structure of WoWChatTranslatorDB changes.
local DATA_VERSION = 1
local PREFIX = "|cff33ccff[WoWChatTranslator]|r "

local function Print(msg)
    DEFAULT_CHAT_FRAME:AddMessage(PREFIX .. msg)
end

-- Returns the frame that visually holds the main chat (ElvUI panel or default ChatFrame1).
local function GetChatContainer()
    if _G.ElvUI and _G.LeftChatPanel and _G.LeftChatPanel:IsShown() then
        return _G.LeftChatPanel
    end
    return _G.ChatFrame1
end
ns.GetChatContainer = GetChatContainer

-- Converts a frame rectangle into screen fractions (0..1, origin top-left)
-- so the companion can map it onto the game window whatever the resolution or UI scale.
local function GetScreenFractions(frame)
    if not frame or not frame:GetLeft() then
        return nil
    end
    local scale = frame:GetEffectiveScale()
    local screenW = UIParent:GetWidth() * UIParent:GetEffectiveScale()
    local screenH = UIParent:GetHeight() * UIParent:GetEffectiveScale()
    if screenW <= 0 or screenH <= 0 then
        return nil
    end

    local left = frame:GetLeft() * scale
    local top = frame:GetTop() * scale
    local width = frame:GetWidth() * scale
    local height = frame:GetHeight() * scale

    -- Include the tab bar above the default chat frame so the overlay covers it too.
    local tab = _G.ChatFrame1Tab
    if frame == _G.ChatFrame1 and tab and tab:IsShown() and tab:GetTop() then
        local tabTop = tab:GetTop() * tab:GetEffectiveScale()
        if tabTop > top then
            height = height + (tabTop - top)
            top = tabTop
        end
    end

    return {
        x = left / screenW,
        y = 1 - (top / screenH),
        w = width / screenW,
        h = height / screenH,
    }
end

local function SaveGeometry()
    local rect = GetScreenFractions(GetChatContainer())
    if rect then
        WoWChatTranslatorDB.chat = rect
    end
    return rect
end

-- True when the companion's copy (read from disk) no longer matches the real chat position.
local function GeometryChanged(old, new)
    if not new then
        return false
    end
    if not old then
        return true
    end
    for _, key in ipairs({ "x", "y", "w", "h" }) do
        if math.abs((old[key] or -1) - new[key]) > 0.003 then
            return true
        end
    end
    return false
end

-- SavedVariables are only written on /reload or logout: offer a one-click reload
-- so the companion receives the chat position without typing anything.
StaticPopupDialogs.WOWCHATTRANSLATOR_RELOAD = {
    text = L.RELOAD_PROMPT,
    button1 = L.RELOAD,
    button2 = L.LATER,
    OnAccept = function()
        ReloadUI()
    end,
    timeout = 0,
    whileDead = true,
    hideOnEscape = true,
    preferredIndex = 3,
}

local diskGeometry -- chat position as last written to disk (what the companion knows)

local function CheckGeometry()
    if InCombatLockdown() then
        C_Timer.After(5, CheckGeometry)
        return
    end
    local rect = SaveGeometry()
    if GeometryChanged(diskGeometry, rect) then
        StaticPopup_Show("WOWCHATTRANSLATOR_RELOAD")
    end
end

-- While it runs, the companion rewrites Companion.lua every few seconds with a timestamp
-- (and the overlay position). WoW reads it at login and on /reload. Without a recent
-- signature the addon stays completely idle: no grid, no message capture.
local COMPANION_MAX_AGE = 30

local function CompanionState()
    local state = _G.WoWChatTranslatorCompanion
    return type(state) == "table" and state or {}
end

local function IsCompanionSignatureFresh()
    local seen = CompanionState().seen
    return type(seen) == "number" and math.abs(time() - seen) <= COMPANION_MAX_AGE
end

local function ValidRect(rect)
    if type(rect) ~= "table" then
        return nil
    end
    for _, key in ipairs({ "x", "y", "w", "h" }) do
        if type(rect[key]) ~= "number" then
            return nil
        end
    end
    return rect
end

function ns.GetOverlayRect()
    return ValidRect(CompanionState().overlayRect)
end

-- The game's chat log (/chatlog, Logs/WoWChatLog.txt): the companion reads back from it the
-- lines it missed while the game was out of sight. Turned on or off from the companion's
-- options (applied here at login / reload), and its state is reported to the companion so that
-- its switch follows a /chatlog typed in the game.
local CHATLOG_REPORT = 10 -- resend even without change (a packet may have been missed)

local function ApplyChatLog()
    local wanted = CompanionState().chatLog
    if type(wanted) == "boolean" and type(LoggingChat) == "function" and LoggingChat() ~= wanted then
        LoggingChat(wanted)
    end
end

local chatLogTicker

local function ReportChatLog()
    if chatLogTicker or type(LoggingChat) ~= "function" then
        return
    end
    local last, lastSent = nil, 0
    chatLogTicker = C_Timer.NewTicker(2, function()
        -- Also the key that shows / hides the overlay: the companion names it when it closes
        -- while a character is in the world (the grid shows again until it is pressed).
        local key = GetBindingKey("WOWCHATTRANSLATOR_TOGGLE") or ""
        local state = (LoggingChat() and "chatlog=1" or "chatlog=0") .. ",key=" .. key:gsub(",", "")
        if state ~= last or GetTime() - lastSent >= CHATLOG_REPORT then
            last, lastSent = state, GetTime()
            ns.BridgeState(state)
        end
    end)
end

local function StartBridge()
    ns.BridgeStart()
    ns.BridgeSetShown(not WoWChatTranslatorDB.hidden)
    ApplyChatLog()
    ReportChatLog()
end

-- ---------------------------------------------------------------------------------------
-- Show / hide the overlay from the game (key binding, Alt+F6 by default, or /wct toggle).

local TOGGLE_ACTION = "WOWCHATTRANSLATOR_TOGGLE"
local DEFAULT_TOGGLE_KEY = "ALT-F6"
BINDING_HEADER_WOWCHATTRANSLATOR = "WoWChatTranslator"
BINDING_NAME_WOWCHATTRANSLATOR_TOGGLE = L.BINDING_TOGGLE
BINDING_NAME_WOWCHATTRANSLATOR_SCREENSHOT = L.BINDING_SCREENSHOT
local SCREENSHOT_ACTION = "WOWCHATTRANSLATOR_SCREENSHOT"
local DEFAULT_SCREENSHOT_KEY = "CTRL-PRINTSCREEN"

-- Asks the companion for a screenshot of the game *with* its overlay (the game's own
-- screenshots cannot contain it). Key set in the game's key bindings.
function WoWChatTranslator_Screenshot()
    if not ns.BridgeIsShown() then
        Print(L.SCREENSHOT_OFF)
        return
    end
    ns.BridgeRequest("shot")
end

-- Mentions the key the player actually bound (F9, Alt+F6...), as the game displays it.
local function HiddenMessage()
    local key = GetBindingKey(TOGGLE_ACTION)
    if not key then
        return L.OVERLAY_HIDDEN_NOKEY
    end
    return L.OVERLAY_HIDDEN:format(GetBindingText and GetBindingText(key) or key)
end

function WoWChatTranslator_Toggle()
    if not ns.BridgeStatus() then
        Print(L.COMPANION_OFF)
        return
    end
    local shown = not ns.BridgeIsShown()
    WoWChatTranslatorDB.hidden = not shown
    ns.BridgeSetShown(shown)
    Print(shown and L.OVERLAY_SHOWN or HiddenMessage())
end

-- Suggests a key once per action, only if the player has not bound it and the key is free.
local function SuggestBinding(flag, action, key)
    if WoWChatTranslatorDB[flag] then
        return false
    end
    WoWChatTranslatorDB[flag] = true
    if GetBindingKey(action) then
        return false
    end
    local current = GetBindingAction(key)
    if current == nil or current == "" then
        SetBinding(key, action)
        return true
    end
    return false
end

local function SetDefaultBinding()
    if InCombatLockdown() then
        return
    end
    local changed = SuggestBinding("bindingDefaulted", TOGGLE_ACTION, DEFAULT_TOGGLE_KEY)
    changed = SuggestBinding("screenshotBindingDefaulted", SCREENSHOT_ACTION, DEFAULT_SCREENSHOT_KEY) or changed
    if changed then
        SaveBindings(GetCurrentBindingSet())
    end
end

local frame = CreateFrame("Frame")
frame:RegisterEvent("ADDON_LOADED")
frame:RegisterEvent("PLAYER_LOGIN")
frame:RegisterEvent("PLAYER_LOGOUT")

frame:SetScript("OnEvent", function(_, event, arg1)
    if event == "ADDON_LOADED" and arg1 == ADDON_NAME then
        WoWChatTranslatorDB = WoWChatTranslatorDB or {}
        WoWChatTranslatorDB.dataVersion = DATA_VERSION
        -- Keys from older versions (the companion state now lives in Companion.lua).
        for _, key in ipairs({ "npcNames", "npcCount", "session", "companionSeen", "overlayRect" }) do
            WoWChatTranslatorDB[key] = nil
        end
        diskGeometry = WoWChatTranslatorDB.chat
    elseif event == "PLAYER_LOGIN" then
        SetDefaultBinding()
        if IsCompanionSignatureFresh() then
            StartBridge()
        else
            Print(L.COMPANION_OFF)
        end
        WoWChatTranslatorDB.locale = GetLocale()
        WoWChatTranslatorDB.player = UnitName("player")
        WoWChatTranslatorDB.realm = GetNormalizedRealmName and GetNormalizedRealmName() or GetRealmName()
        WoWChatTranslatorDB.addonVersion = C_AddOns and C_AddOns.GetAddOnMetadata(ADDON_NAME, "Version") or nil
        -- Layout addons (ElvUI...) move the chat after login, so capture it a bit later.
        C_Timer.After(5, CheckGeometry)
    elseif event == "PLAYER_LOGOUT" then
        SaveGeometry()
        WoWChatTranslatorDB.savedAt = time()
    end
end)

SLASH_WOWCHATTRANSLATOR1 = "/wct"
SlashCmdList.WOWCHATTRANSLATOR = function(msg)
    msg = strlower(strtrim(msg or ""))
    if msg == "pos" then
        local rect = SaveGeometry()
        if rect then
            Print(format("x=%.4f y=%.4f w=%.4f h=%.4f", rect.x, rect.y, rect.w, rect.h))
        end
        StaticPopup_Show("WOWCHATTRANSLATOR_RELOAD")
    elseif msg == "on" then
        StartBridge()
        Print(format(L.BRIDGE_ON, 0))
    elseif msg == "covers" then
        -- Diagnostics: game windows seen over the overlay and where the grid is.
        Print(ns.BridgeCoversDebug and ns.BridgeCoversDebug() or "-")
    elseif msg == "toggle" then
        WoWChatTranslator_Toggle()
    elseif msg == "test" then
        ns.BridgeSend("say", "WoWChatTranslator", "WoWChatTranslator", "Hello, this is a translation test.")
        Print(L.TEST_SENT)
    else
        local active, pending = ns.BridgeStatus()
        Print(active and format(L.BRIDGE_ON, pending) or L.COMPANION_OFF)
        Print(L.HELP)
    end
end
