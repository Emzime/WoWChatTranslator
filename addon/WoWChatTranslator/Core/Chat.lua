local _, ns = ...

--[[
Collects the chat messages to translate and hands them to the pixel bridge.
Only player conversation is forwarded: channels (General, Trade, LocalTrade...), Say, Whisper,
Guild, Officer, Party, Raid and Instance. Yells, emotes, NPCs, crafting, loot, achievements and
system messages are never sent.
Each message is sent with a display prefix built from the game's own localised formats
(e.g. "Ela Borer dit", "[2. Commerce] Ela Borer").
]]

-- event -> { kind for the companion, global format string used for the prefix }
local EVENTS = {
    CHAT_MSG_SAY = { "say", "CHAT_SAY_GET" },
    CHAT_MSG_GUILD = { "guild", "CHAT_GUILD_GET" },
    CHAT_MSG_OFFICER = { "officer", "CHAT_OFFICER_GET" },
    CHAT_MSG_PARTY = { "party", "CHAT_PARTY_GET" },
    CHAT_MSG_PARTY_LEADER = { "party", "CHAT_PARTY_LEADER_GET" },
    CHAT_MSG_RAID = { "raid", "CHAT_RAID_GET" },
    CHAT_MSG_RAID_LEADER = { "raid", "CHAT_RAID_LEADER_GET" },
    CHAT_MSG_RAID_WARNING = { "raid", "CHAT_RAID_WARNING_GET" },
    CHAT_MSG_INSTANCE_CHAT = { "instance", "CHAT_INSTANCE_CHAT_GET" },
    CHAT_MSG_INSTANCE_CHAT_LEADER = { "instance", "CHAT_INSTANCE_CHAT_LEADER_GET" },
    -- Battleground chat of older clients (registered only if the client knows the event).
    CHAT_MSG_BATTLEGROUND = { "instance", "CHAT_BATTLEGROUND_GET" },
    CHAT_MSG_BATTLEGROUND_LEADER = { "instance", "CHAT_BATTLEGROUND_LEADER_GET" },
    CHAT_MSG_WHISPER = { "whisper", "CHAT_WHISPER_GET" },
    CHAT_MSG_WHISPER_INFORM = { "whisper_out", "CHAT_WHISPER_INFORM_GET" },
    CHAT_MSG_BN_WHISPER = { "whisper", "CHAT_BN_WHISPER_GET" },
    CHAT_MSG_BN_WHISPER_INFORM = { "whisper_out", "CHAT_BN_WHISPER_INFORM_GET" },
    CHAT_MSG_CHANNEL = { "channel" },
}

local function IsSecret(value)
    -- Midnight clients hide some chat content from addons in combat ("secret values").
    return issecretvalue ~= nil and issecretvalue(value)
end

local function DisplayName(sender)
    if type(sender) ~= "string" then
        return ""
    end
    return Ambiguate and Ambiguate(sender, "none") or sender
end

-- "Ela Borer dit : " -> "Ela Borer dit" (the companion adds its own separator).
local function FormatPrefix(formatName, name)
    local fmt = formatName and _G[formatName]
    if type(fmt) ~= "string" or not fmt:find("%%s") then
        return name
    end
    local prefix = fmt:format(name)
    return (prefix:gsub("%s*:%s*$", ""):gsub("%s+$", ""))
end

-- Automatic announcements of other addons (Questie, quest progress sharing...) are sent as
-- ordinary chat messages: they are not conversation, keep them out of the overlay.
-- "1/1 Outraged Pillager slain for [[23+] Quest]!", "[[23+] Quest (Complete)]", "Questie: ..."
local ADDON_TAGS = { "questie", "<dbm>", "dbm:", "bigwigs", "details!", "<rsa>",
    "restedxp", "<rxp>", "rxp:", "zygor", "guidelime", "<nit>", "novainstancetracker", "polestar" }

-- Text as displayed, without colours, icons, raid marks and link codes
-- ("|cff..Questie|r : ...", "{rt3} Questie : ...").
local function PlainText(text)
    return (text:gsub("|c%x%x%x%x%x%x%x%x", ""):gsub("|cn[%w_]+:", ""):gsub("|r", "")
        :gsub("|T.-|t", ""):gsub("|A.-|a", ""):gsub("|H.-|h(.-)|h", "%1"):gsub("{[^}]*}", ""))
end

local function IsAddonAnnouncement(text)
    local lower = PlainText(text):lower()
    for _, tag in ipairs(ADDON_TAGS) do
        if lower:find("^[%s%p]*" .. tag) then
            return true
        end
    end
    if text:find("|Hquest:") then
        -- Quest progress: a counter, and the message ends with the quest link
        -- ("2/2 Encroaching Soldier slain for [Quest]!"). "LFM [Quest] 3/5" stays.
        local plain = text:gsub("|r", "")
        if plain:find("%d+/%d+") and plain:find("|Hquest:[^|]*|h%[.-%]|h%s*!?%s*$") then
            return true
        end
        if text:find("|Hquest:[^|]*|h%[.-%(.-%)%]|h") then
            return true
        end
    end
    return false
end
ns.IsAddonAnnouncement = IsAddonAnnouncement

-- Battle.net whispers: the sender is a protected "|K...|k" name that only the game can show.
-- Use the friend's character name, else the readable part of the BattleTag ("Name#1234").
local function BattleNetName(bnSenderID)
    if not (bnSenderID and C_BattleNet and C_BattleNet.GetAccountInfoByID) then
        return nil
    end
    local ok, info = pcall(C_BattleNet.GetAccountInfoByID, bnSenderID)
    if not ok or type(info) ~= "table" then
        return nil
    end
    local game = info.gameAccountInfo
    if game and type(game.characterName) == "string" and game.characterName ~= "" and not IsSecret(game.characterName) then
        return game.characterName
    end
    if type(info.battleTag) == "string" and not IsSecret(info.battleTag) then
        return (info.battleTag:match("^[^#]+"))
    end
    return nil
end

-- Class of the sender ("MAGE"...), for his name in the companion's class colour. Unknown for
-- Battle.net whispers (no character GUID) and for players the client has no data about.
local function ClassToken(guid)
    if type(guid) ~= "string" or guid == "" or IsSecret(guid) or not GetPlayerInfoByGUID then
        return nil
    end
    local ok, _, englishClass = pcall(GetPlayerInfoByGUID, guid)
    if ok and type(englishClass) == "string" and not IsSecret(englishClass) then
        return englishClass
    end
    return nil
end

local function OnChatEvent(_, event, text, sender, _, _, _, _, _, channelIndex, channelBaseName, _, _, guid, bnSenderID)
    local spec = EVENTS[event]
    if not spec or type(text) ~= "string" or IsSecret(text) or IsSecret(sender) then
        return
    end
    if IsAddonAnnouncement(text) then
        return
    end
    local kind = spec[1]
    local name = DisplayName(sender)
    if event == "CHAT_MSG_BN_WHISPER" or event == "CHAT_MSG_BN_WHISPER_INFORM" then
        name = BattleNetName(bnSenderID) or name
    end
    local prefix

    if kind == "channel" then
        prefix = ("[%s. %s] %s"):format(tostring(channelIndex or "?"), tostring(channelBaseName or ""), name)
    else
        prefix = FormatPrefix(spec[2], name)
    end
    ns.BridgeSend(kind, prefix, name, text, ClassToken(guid))
end

local frame = CreateFrame("Frame")
for event in pairs(EVENTS) do
    pcall(frame.RegisterEvent, frame, event)
end
frame:SetScript("OnEvent", OnChatEvent)
