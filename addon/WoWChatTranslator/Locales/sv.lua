local _, ns = ...

-- Addon messages (sv). English (en.lua) is the fallback for any missing line.
ns.Locales = ns.Locales or {}
ns.Locales.sv = {
    RELOAD_PROMPT = "Chattens position har ändrats. Ladda om gränssnittet så att översättningen hamnar rätt över chatten?",
    RELOAD = "Ladda om",
    LATER = "Senare",
    BRIDGE_ON = "Brygga till följeslagaren: |cff00ff00aktiv|r (%d meddelande(n) i kö)",
    TEST_SENT = "Testmeddelande skickat till följeslagaren.",
    HELP = "Kommandon: /wct (status), /wct on (starta), /wct test (testmeddelande), /wct pos (justera chattens position), /wct toggle (visa/dölj)",
    COMPANION_OFF = "Följeslagaren hittades inte: översättningen är av. Starta WoWChatTranslatorCompagnion och skriv sedan /wct on.",
    BINDING_TOGGLE = "Visa / dölj översättningsöverlägget",
    BINDING_SCREENSHOT = "Skärmbild med översättningsöverlägget",
    SCREENSHOT_OFF = "Inget översättningsöverlägg: skärmbild inte möjlig.",
    OVERLAY_HIDDEN = "Översättningsöverlägget dolt (%s eller /wct toggle för att visa).",
    OVERLAY_HIDDEN_NOKEY = "Översättningsöverlägget dolt (/wct toggle för att visa).",
    OVERLAY_SHOWN = "Översättningsöverlägget visas.",
}
