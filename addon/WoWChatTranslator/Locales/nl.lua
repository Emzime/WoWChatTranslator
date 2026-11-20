local _, ns = ...

-- Addon messages (nl). English (en.lua) is the fallback for any missing line.
ns.Locales = ns.Locales or {}
ns.Locales.nl = {
    RELOAD_PROMPT = "De positie van de chat is gewijzigd. De interface herladen zodat de vertaling bij je chat past?",
    RELOAD = "Herladen",
    LATER = "Later",
    BRIDGE_ON = "Brug naar de companion: |cff00ff00actief|r (%d bericht(en) in wachtrij)",
    TEST_SENT = "Testbericht naar de companion gestuurd.",
    HELP = "Commando's: /wct (status), /wct on (starten), /wct test (testbericht), /wct pos (chatpositie opnieuw instellen), /wct toggle (tonen/verbergen)",
    COMPANION_OFF = "Companion niet gevonden: vertaling uit. Start WoWChatTranslatorCompagnion en typ daarna /wct on.",
    BINDING_TOGGLE = "Vertaaloverlay tonen / verbergen",
    BINDING_SCREENSHOT = "Schermafbeelding met de vertaaloverlay",
    SCREENSHOT_OFF = "Geen vertaaloverlay: schermafbeelding niet mogelijk.",
    OVERLAY_HIDDEN = "Vertaaloverlay verborgen (%s of /wct toggle om te tonen).",
    OVERLAY_HIDDEN_NOKEY = "Vertaaloverlay verborgen (/wct toggle om te tonen).",
    OVERLAY_SHOWN = "Vertaaloverlay getoond.",
}
