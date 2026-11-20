local _, ns = ...

-- Picks the addon's message language. The messages themselves are in Locales/<language>.lua,
-- loaded before this file; English is the fallback.
local L = ns.Locales
L.enGB = L.enUS
L.esMX = L.esES
L.ptPT = L.ptBR

-- The player's reading language set in the companion (written to Data/Companion.lua, loaded after
-- this file), else the game's language. Resolved on use, once every file is loaded.
local COMPANION_LANGS = {
    en = "enUS", fr = "frFR", de = "deDE", es = "esES", it = "itIT", pt = "ptBR", ru = "ruRU",
}
-- The chat font of a game in another language may lack some letters: Greek, the extra
-- Cyrillic letters, and Latin ones like Czech "ř ě ů" or Polish "ł ż" (drawn as boxes).
-- The companion's overlay is drawn by Windows and shows every alphabet; for the addon's own
-- messages in the game's chat, a language is used only if the chat font draws its letters.
local SCRIPT_SAMPLES = {
    el = { "Α", "Γ", "Δ", "Λ", "Ω" }, uk = { "Ї", "Є", "Ґ", "ї", "є" }, bg = { "Ж", "Щ", "Ъ", "Ю", "Я" },
    pl = { "ł", "ż", "ś", "ź", "ę" }, cs = { "ř", "ě", "ů", "č", "ň" }, sk = { "ľ", "ĺ", "ŕ", "ô", "ť" },
    hu = { "ő", "ű", "Ő", "Ű", "ő" }, ro = { "ș", "ț", "ă", "Ș", "Ț" }, tr = { "ğ", "ş", "ı", "İ", "Ğ" },
}
local MISSING = "\238\128\128" -- U+E000 (private use): drawn as the "missing letter" box
local displayable = {}

local function Width(probe, char)
    probe:SetText(char)
    return probe:GetStringWidth() or 0
end

local function CanDisplay(lang)
    local sample = SCRIPT_SAMPLES[lang]
    if not sample then
        return true
    end
    if displayable[lang] == nil then
        local ok, result = pcall(function()
            local probe = UIParent:CreateFontString(nil, "BACKGROUND")
            probe:SetFontObject(ChatFontNormal or GameFontNormal)
            local box = Width(probe, MISSING)
            local missing = 0
            for _, char in ipairs(sample) do
                local width = Width(probe, char)
                -- Not drawn at all, or drawn as the same box as a missing letter.
                if width < 1 or math.abs(width - box) < 0.01 then
                    missing = missing + 1
                end
            end
            probe:SetText("")
            probe:Hide()
            return missing == 0
        end)
        displayable[lang] = ok and result
    end
    return displayable[lang]
end

local function Active()
    local state = _G.WoWChatTranslatorCompanion
    local lang = type(state) == "table" and state.lang
    if lang then
        local tbl = L[COMPANION_LANGS[lang] or lang]
        if tbl and CanDisplay(lang) then
            return tbl
        end
    end
    return L[GetLocale()] or L.enUS
end

ns.L = setmetatable({}, {
    __index = function(_, key)
        return Active()[key] or L.enUS[key] or key
    end,
})
