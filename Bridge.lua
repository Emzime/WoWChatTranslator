local _, ns = ...

--[[
Pixel bridge: an addon cannot write files or use the network while the game runs, so chat
messages are sent to the companion through the screen. Each packet is drawn as a small grid
of cells (3 bits per cell: red, green, blue on or off) in the top-right corner of the chat.
The companion covers the grid with a mask window that is excluded from screen capture, and
reads the grid with DXGI capture, which ignores that mask: the player never sees the grid.
The companion calibrates on the sync cells, so any gamma/brightness setting still decodes.

Packet layout (bits, MSB first, 3 bits per cell after the sync cells):
  sync cells | session (1 byte) | seq (1 byte) | length (2 bytes) | payload | CRC16-CCITT (2 bytes)
Payload: messages separated by \30, fields separated by \31: kind, prefix, sender, text.
A "shot" record asks the companion for a screenshot with its overlay.
A "cover" record lists, in its prefix field, the game windows that are open anywhere on
screen (bags, character sheet, professions, tooltips...): 8 characters per window, x, y, w, h
in physical pixels / 2 from the top-left corner of the game, 2 base-64 digits each. The
companion cuts its overlay wherever one of them overlaps it (the overlay can be anywhere),
so these windows stay visible.
Keep these constants in sync with companion/wctc/bridge.py.
]]

local COLS, ROWS, CELL = 64, 16, 3
local SYNC = { 7, 0, 5, 2, 7, 0, 3, 4 }
local BASE = { 11 / 255, 14 / 255, 18 / 255 } -- overlay background (#0b0e12)
local DELTA = 48 / 255 -- difference between an "on" and an "off" channel
local INSET = 4 -- physical pixels from the chat's top-right corner
local REPOSITION_INTERVAL = 1
local HEADER_BYTES = 4
local CRC_BYTES = 2
local MAX_BYTES = math.floor(((COLS * ROWS - #SYNC) * 3) / 8)
local MAX_PAYLOAD = MAX_BYTES - HEADER_BYTES - CRC_BYTES
local HOLD_TIME = 0.08 -- seconds a packet stays on screen (the companion samples every ~12 ms)
local MIN_HOLD_TIME = 0.05 -- shortest hold, before an urgent packet (game window opened/closed)
-- After the grid moved or was uncovered, the packet on it stays this much longer: the companion
-- has to find the grid again before reading it (otherwise that chat line would be lost).
local RELOCATE_HOLD = 0.12
local FIELD_SEP, RECORD_SEP = "\31", "\30"

local band, bor, bxor, lshift, rshift = bit.band, bit.bor, bit.bxor, bit.lshift, bit.rshift

local function Crc16(bytes, count)
    local crc = 0xFFFF
    for i = 1, count do
        crc = bxor(crc, lshift(bytes[i], 8))
        for _ = 1, 8 do
            if band(crc, 0x8000) ~= 0 then
                crc = band(bxor(lshift(crc, 1), 0x1021), 0xFFFF)
            else
                crc = band(lshift(crc, 1), 0xFFFF)
            end
        end
    end
    return crc
end

-- Returns the list of cell values (0..7) for a packet.
local function EncodePacket(session, seq, payload)
    local bytes = { session, seq, rshift(#payload, 8), band(#payload, 0xFF) }
    for i = 1, #payload do
        bytes[#bytes + 1] = payload:byte(i)
    end
    local crc = Crc16(bytes, #bytes)
    bytes[#bytes + 1] = rshift(crc, 8)
    bytes[#bytes + 1] = band(crc, 0xFF)

    local cells = {}
    for i = 1, #SYNC do
        cells[i] = SYNC[i]
    end
    local acc, accBits = 0, 0
    for i = 1, #bytes do
        acc = bor(lshift(acc, 8), bytes[i])
        accBits = accBits + 8
        while accBits >= 3 do
            accBits = accBits - 3
            cells[#cells + 1] = band(rshift(acc, accBits), 7)
        end
        acc = band(acc, lshift(1, accBits) - 1)
    end
    if accBits > 0 then
        cells[#cells + 1] = band(lshift(acc, 3 - accBits), 7)
    end
    return cells
end
ns.EncodePacket = EncodePacket

-- ---------------------------------------------------------------------------------------
-- Display: a parentless frame (stays visible when the UI is hidden with Alt+Z) scaled so
-- that one unit equals one physical pixel.

local grid, textures
local function GetPixelScale()
    local _, physicalHeight = GetPhysicalScreenSize()
    if not physicalHeight or physicalHeight <= 0 then
        return nil
    end
    return 768 / physicalHeight
end

local STRATA_RANK = {
    BACKGROUND = 1, LOW = 2, MEDIUM = 3, HIGH = 4, DIALOG = 5, FULLSCREEN = 6,
    FULLSCREEN_DIALOG = 7, TOOLTIP = 8,
}
local STRATA_NAMES = { "BACKGROUND", "LOW", "MEDIUM", "HIGH", "DIALOG", "FULLSCREEN", "FULLSCREEN_DIALOG", "TOOLTIP" }

local function ChatStrataRank(container)
    local rank = 1
    for _, frame in ipairs({ container, ChatFrame1, GeneralDockManager }) do
        if frame and frame.GetFrameStrata then
            rank = math.max(rank, STRATA_RANK[frame:GetFrameStrata()] or 1)
        end
    end
    return rank
end

-- Full-screen effects the game draws over the whole interface (the red low-health flash): while
-- one is shown, the grid goes just above it, or its colours would be tinted and unreadable
-- (the companion would also take the grid for hidden and hide the overlay at each flash).
local SCREEN_EFFECTS = { "LowHealthFrame" }

local function ScreenEffectOver(chatRank)
    for _, name in ipairs(SCREEN_EFFECTS) do
        local frame = _G[name]
        if frame and frame.IsShown and frame:IsShown() and frame.GetFrameStrata
            and (STRATA_RANK[frame:GetFrameStrata()] or 1) >= chatRank then
            return frame
        end
    end
end

-- Game windows open on screen, in physical pixels from the top-left corner: {left, top, right, bottom}.
local coverRects = {}
local gridCovered = false
local holdUntil = 0 -- no new packet before this time (grid moved or uncovered)
local gridX, gridY -- current position of the grid (physical pixels)

local function Overlaps(a, l, t, r, b)
    return a[1] < r and l < a[3] and a[2] < b and t < a[4]
end

-- Rectangle under the companion overlay, physical pixels, top-left origin: its rectangle
-- (screen fractions, set when the player moved it) or, by default, the chat it covers.
local function OverlayArea(physicalWidth, physicalHeight, scale)
    local overlay = ns.GetOverlayRect and ns.GetOverlayRect()
    if overlay then
        return overlay.x * physicalWidth, overlay.y * physicalHeight,
            (overlay.x + overlay.w) * physicalWidth, (overlay.y + overlay.h) * physicalHeight
    end
    local container = ns.GetChatContainer and ns.GetChatContainer()
    if container and container:GetLeft() and container:GetTop() and container:GetRight() and container:GetBottom() then
        local s = container:GetEffectiveScale() / scale
        return container:GetLeft() * s, physicalHeight - container:GetTop() * s,
            container:GetRight() * s, physicalHeight - container:GetBottom() * s
    end
    return 0, 0, physicalWidth, physicalHeight
end

-- The grid sits in a corner of the overlay (top-right first), under the overlay so the player
-- never sees it, snapped to whole physical pixels so every cell covers exactly 3x3 pixels.
-- It is drawn at the chat's level: game windows (bags...) go over it, as over the overlay.
-- When one covers it, it moves to a free corner; if none is free, sending pauses until the
-- window closes (the overlay is then hidden by the windows anyway).
local function Reposition()
    local scale = GetPixelScale()
    local physicalWidth, physicalHeight = GetPhysicalScreenSize()
    local container = ns.GetChatContainer and ns.GetChatContainer()
    local chatRank = ChatStrataRank(container)
    local effect = ScreenEffectOver(chatRank)
    if effect then
        grid:SetFrameStrata(effect:GetFrameStrata())
        grid:SetFrameLevel(math.max(9000, effect:GetFrameLevel() + 10))
    else
        grid:SetFrameStrata(STRATA_NAMES[chatRank] or "BACKGROUND")
        grid:SetFrameLevel(9000)
    end
    local l0, t0, r0, b0 = OverlayArea(physicalWidth, physicalHeight, scale)
    local w, h = COLS * CELL, ROWS * CELL
    local corners = {
        { r0 - w - INSET, t0 + INSET }, { l0 + INSET, t0 + INSET },
        { r0 - w - INSET, b0 - h - INSET }, { l0 + INSET, b0 - h - INSET },
    }
    local left, top = corners[1][1], corners[1][2]
    local wasCovered = gridCovered
    gridCovered = true
    for _, corner in ipairs(corners) do
        local free = true
        for _, rect in ipairs(coverRects) do
            if Overlaps(rect, corner[1], corner[2], corner[1] + w, corner[2] + h) then
                free = false
                break
            end
        end
        if free then
            left, top, gridCovered = corner[1], corner[2], false
            break
        end
    end
    local x, y = math.floor(left + 0.5), math.floor(physicalHeight - top + 0.5)
    if (wasCovered and not gridCovered) or ((x ~= gridX or y ~= gridY) and gridX) then
        holdUntil = GetTime() + RELOCATE_HOLD
    end
    if x ~= gridX or y ~= gridY then
        gridX, gridY = x, y
        grid.x, grid.y = x, y
        grid:ClearAllPoints()
        grid:SetPoint("TOPLEFT", UIParent, "BOTTOMLEFT", x, y)
    end
end

local function CreateGrid()
    local scale = GetPixelScale()
    if not scale then
        return false
    end
    grid = CreateFrame("Frame", "WoWChatTranslatorBridge", nil)
    grid:SetScale(scale)
    grid:SetSize(COLS * CELL, ROWS * CELL)
    Reposition()
    textures = {}
    for row = 0, ROWS - 1 do
        for col = 0, COLS - 1 do
            local tex = grid:CreateTexture(nil, "OVERLAY")
            tex:SetSize(CELL, CELL)
            tex:SetPoint("TOPLEFT", grid, "TOPLEFT", col * CELL, -row * CELL)
            tex:SetColorTexture(0, 0, 0, 1)
            textures[row * COLS + col + 1] = tex
        end
    end
    return true
end

local function Draw(cells)
    for i = 1, #textures do
        local value = cells[i] or 0
        textures[i]:SetColorTexture(
            BASE[1] + (band(value, 4) ~= 0 and DELTA or 0),
            BASE[2] + (band(value, 2) ~= 0 and DELTA or 0),
            BASE[3] + (band(value, 1) ~= 0 and DELTA or 0),
            1
        )
    end
end

-- ---------------------------------------------------------------------------------------
-- Queue and sending

local queue = {}
local session = math.random(0, 255)
local seq = 0
local lastSent = 0

local function SendNext()
    local parts, size = {}, 0
    while #queue > 0 do
        local record = queue[1]
        local extra = #record + (#parts > 0 and 1 or 0)
        if #parts > 0 and size + extra > MAX_PAYLOAD then
            break
        end
        if #record > MAX_PAYLOAD then
            record = record:sub(1, MAX_PAYLOAD) -- cannot happen with chat limits, stay safe
        end
        parts[#parts + 1] = record
        size = size + extra
        table.remove(queue, 1)
    end
    seq = (seq + 1) % 256
    Draw(EncodePacket(session, seq, table.concat(parts, RECORD_SEP)))
end

local lastReposition = 0

local UpdateCovers
local coverUrgent = false

local function OnUpdate()
    if GetTime() - lastReposition >= REPOSITION_INTERVAL then
        lastReposition = GetTime()
        Reposition()
    end
    UpdateCovers()
    local hold = coverUrgent and MIN_HOLD_TIME or HOLD_TIME
    if #queue > 0 and not gridCovered and GetTime() >= holdUntil and GetTime() - lastSent >= hold then
        lastSent = GetTime()
        coverUrgent = false
        SendNext()
    end
end

-- ---------------------------------------------------------------------------------------
-- Game windows open on screen (the overlay is a separate window placed anywhere by the
-- player: without this it would be drawn over them)

local CANDIDATE_REFRESH = 1 -- the list of frames that may cover the overlay is rebuilt every second
local COVER_REFRESH = 3 -- resend even without change (a packet may have been missed)
local MAX_COVERS = 40 -- 8 bytes each: fits in one packet
local B64 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz+/"
-- Frames that belong to the chat itself.
local CHAT_PATTERNS = { "^ChatFrame", "^GeneralDock", "^LeftChat", "^RightChat", "^QuickJoinToast",
    "^FriendsMicroButton", "^ChatMenu", "^VoiceChat", "^CombatLogQuickButton" }
local lastCovers, lastCoverSent = nil, 0
local candidates, lastCandidates = {}, -math.huge

local function IsChatFrame(frame, container)
    local name = frame:GetName()
    if name then
        for _, pattern in ipairs(CHAT_PATTERNS) do
            if name:find(pattern) then
                return true
            end
        end
    end
    local parent = container
    while parent do
        if parent == frame then
            return true -- the chat container lives inside this frame
        end
        parent = parent:GetParent()
    end
    return false
end

-- Two base-64 digits for a value in physical pixels / 2 (up to 8190 pixels).
local function Encode2(value)
    value = math.max(0, math.min(4095, value))
    local high, low = math.floor(value / 64), value % 64
    return B64:sub(high + 1, high + 1) .. B64:sub(low + 1, low + 1)
end

-- Frames that may cover the overlay: windows the player opens and closes (game panels, bags,
-- menus, dialogs, windows closed with Escape) and tooltips, above the chat. Not the frames
-- always on screen (damage meters, action bars, unit frames, minimap buttons): the player put
-- the overlay over them on purpose, and taking them for windows would cut the overlay away
-- and pause the bridge (every corner "covered"). Rebuilt every second; their visibility and
-- position are checked every rendered frame, so an opening bag is noticed right away.
local BAG_PATTERNS = { "^ContainerFrame%d", "^ElvUI_ContainerFrame", "^ElvUI_BankContainerFrame", "^Bagnon",
    "^AdiBags", "^ArkInventory", "^Baganator", "^BankFrame", "^GuildBankFrame" }

local function NameSet(list)
    local set = {}
    for key, value in pairs(type(list) == "table" and list or {}) do
        set[type(key) == "string" and key or value] = true
    end
    return set
end

local function IsWindow(frame, special, panels)
    if frame:IsObjectType("GameTooltip") then
        return true
    end
    if not (frame.IsMouseEnabled and frame:IsMouseEnabled()) then
        return false -- layout containers, event frames...: nothing the player sees
    end
    if (STRATA_RANK[frame:GetFrameStrata()] or 1) >= STRATA_RANK.DIALOG then
        return true -- popups, menus, option windows
    end
    local name = frame:GetName()
    if not name then
        return false
    end
    if special[name] or panels[name] then
        return true -- closed with Escape, or a game panel (character, map, quests...)
    end
    for _, pattern in ipairs(BAG_PATTERNS) do
        if name:find(pattern) then
            return true
        end
    end
    return false
end

local function RefreshCandidates()
    local container = ns.GetChatContainer and ns.GetChatContainer()
    local chatRank = ChatStrataRank(container)
    local special, panels = NameSet(_G.UISpecialFrames), NameSet(_G.UIPanelWindows)
    local list = {}
    local function Consider(frame)
        -- Forbidden frames (Blizzard's protected dialogs) cannot even be queried by addons.
        if frame.IsForbidden and frame:IsForbidden() then
            return
        end
        if (STRATA_RANK[frame:GetFrameStrata()] or 1) <= chatRank or IsChatFrame(frame, container) then
            return
        end
        if IsWindow(frame, special, panels) then
            list[#list + 1] = frame
        end
    end
    for _, parent in ipairs({ UIParent, _G.ElvUIParent }) do
        if parent then
            for _, child in ipairs({ parent:GetChildren() }) do
                pcall(Consider, child) -- one odd frame must never break the bridge
            end
        end
    end
    candidates = list
end

local function CollectCovers()
    local pixelScale = GetPixelScale()
    local physicalWidth, physicalHeight = GetPhysicalScreenSize()
    if not pixelScale then
        coverRects = {}
        return ""
    end
    local rects, raw = {}, {}
    local function Measure(frame)
        if #rects >= MAX_COVERS or not frame:IsVisible() then
            return
        end
        if (frame.GetEffectiveAlpha and frame:GetEffectiveAlpha() or 1) < 0.05 then
            return
        end
        local left, top, right, bottom = frame:GetLeft(), frame:GetTop(), frame:GetRight(), frame:GetBottom()
        if not (left and top and right and bottom) then
            return
        end
        local s = frame:GetEffectiveScale() / pixelScale
        left, right = math.max(0, left * s), math.min(physicalWidth, right * s)
        top, bottom = math.max(0, physicalHeight - top * s), math.min(physicalHeight, physicalHeight - bottom * s)
        if right - left >= 2 and bottom - top >= 2 then
            -- Rounded outwards to even pixels: the cut-out never misses an edge of the window.
            raw[#raw + 1] = { left, top, right, bottom }
            local x, y = math.floor(left / 2), math.floor(top / 2)
            rects[#rects + 1] = Encode2(x) .. Encode2(y)
                .. Encode2(math.ceil(right / 2) - x) .. Encode2(math.ceil(bottom / 2) - y)
        end
    end
    for _, frame in ipairs(candidates) do
        pcall(Measure, frame)
    end
    coverRects = raw
    table.sort(rects)
    return table.concat(rects)
end

function UpdateCovers()
    local now = GetTime()
    if now - lastCandidates >= CANDIDATE_REFRESH then
        lastCandidates = now
        pcall(RefreshCandidates)
    end
    local ok, covers = pcall(CollectCovers)
    if not ok then
        covers = lastCovers or ""
    end
    if covers == lastCovers and now - lastCoverSent < COVER_REFRESH then
        return
    end
    if covers ~= lastCovers then
        Reposition() -- move the grid out from under the windows that just opened
        coverUrgent = true
    end
    lastCovers, lastCoverSent = covers, now
    for i = #queue, 1, -1 do
        if queue[i]:sub(1, 6) == "cover" .. FIELD_SEP then
            table.remove(queue, i)
        end
    end
    -- Ahead of the chat lines: a bag opening must show up right away.
    table.insert(queue, 1, table.concat({ "cover", covers, "", "" }, FIELD_SEP))
end
ns.CollectCovers = CollectCovers

function ns.BridgeCoversDebug()
    local names = {}
    for _, rect in ipairs(coverRects) do
        names[#names + 1] = ("%d,%d-%d,%d"):format(rect[1], rect[2], rect[3], rect[4])
    end
    local visible = {}
    for _, frame in ipairs(candidates) do
        if frame:IsVisible() then
            visible[#visible + 1] = frame:GetName() or "?"
        end
    end
    return ("candidates %d (shown: %s) | windows %d [%s] | grid %s,%s %s | queue %d"):format(
        #candidates, table.concat(visible, " "), #coverRects, table.concat(names, " "),
        tostring(gridX), tostring(gridY), gridCovered and "COVERED" or "free", #queue)
end

-- Request to the companion (e.g. "shot": screenshot with the overlay), sent first.
function ns.BridgeRequest(kind)
    if grid and grid:IsShown() then
        table.insert(queue, 1, table.concat({ kind, "", "", "" }, FIELD_SEP))
        coverUrgent = true
    end
end

-- State the companion shows (e.g. "chatlog=1": the game writes its chat log). Only the latest
-- one waits in the queue.
function ns.BridgeState(state)
    if not grid or not grid:IsShown() then
        return
    end
    for i = #queue, 1, -1 do
        if queue[i]:sub(1, 6) == "state" .. FIELD_SEP then
            table.remove(queue, i)
        end
    end
    table.insert(queue, 1, table.concat({ "state", state, "", "" }, FIELD_SEP))
end

function ns.BridgeSend(kind, prefix, sender, text, classToken)
    if not grid or not grid:IsShown() then
        return -- bridge idle (companion not running) or overlay hidden: keep nothing
    end
    if #queue >= 300 then
        table.remove(queue, 2) -- paused for a long time: drop the oldest lines (index 1 may be a cover)
    end
    queue[#queue + 1] = table.concat({ kind, prefix or "", sender or "", text or "", classToken or "" }, FIELD_SEP)
end

-- ---------------------------------------------------------------------------------------
-- Game screenshots (Print Screen in game): they only contain the game's own image, never the
-- companion overlay, so the grid is hidden for the shot instead of appearing on it.
-- (Best effort: the game may capture the frame before the grid is hidden.)

local SCREENSHOT_RESTORE_DELAY = 3 -- safety net if the game never reports the end of the shot
local shotFrame = CreateFrame("Frame")
local hiddenForShot = false

local function HideForShot()
    if grid and not hiddenForShot then
        hiddenForShot = true
        grid:SetAlpha(0)
        C_Timer.After(SCREENSHOT_RESTORE_DELAY, function()
            if hiddenForShot then
                hiddenForShot = false
                grid:SetAlpha(1)
            end
        end)
    end
end

local function RestoreAfterShot()
    if hiddenForShot then
        hiddenForShot = false
        grid:SetAlpha(1)
    end
end

-- Never replace Screenshot(): the game's key binding screen runs it in a protected way, and
-- a function replaced by an addon makes that call forbidden (ADDON_ACTION_FORBIDDEN on
-- RunBinding). A secure post-hook runs right after the call, before the frame is drawn and
-- captured, without touching the original.
if Screenshot then
    hooksecurefunc("Screenshot", HideForShot)
end

shotFrame:RegisterEvent("SCREENSHOT_STARTED")
shotFrame:RegisterEvent("SCREENSHOT_SUCCEEDED")
shotFrame:RegisterEvent("SCREENSHOT_FAILED")
shotFrame:SetScript("OnEvent", function(_, event)
    if event == "SCREENSHOT_STARTED" then
        HideForShot() -- screenshots taken another way (macro, other addon)
    else
        C_Timer.After(0.1, RestoreAfterShot)
    end
end)

function ns.BridgeStart()
    if grid or not CreateGrid() then
        return
    end
    -- An empty packet makes the grid detectable right away: the companion then knows
    -- that a character is in the world.
    Draw(EncodePacket(session, seq, ""))
    grid:SetScript("OnUpdate", OnUpdate)
    -- Follow the low-health flash at once, not at the next periodic repositioning.
    for _, name in ipairs(SCREEN_EFFECTS) do
        local frame = _G[name]
        if frame and frame.HookScript then
            frame:HookScript("OnShow", Reposition)
            frame:HookScript("OnHide", Reposition)
        end
    end
end

-- Hiding the overlay removes the grid: the companion stops seeing it and hides the overlay.
function ns.BridgeSetShown(shown)
    if grid then
        grid:SetShown(shown)
        if shown then
            queue = {}
            lastCovers = nil
        end
    end
end

function ns.BridgeIsShown()
    return grid ~= nil and grid:IsShown()
end

function ns.BridgeStatus()
    return grid ~= nil, #queue
end
