local _, ns = ...

-- Addon messages (deDE). English (en.lua) is the fallback for any missing line.
ns.Locales = ns.Locales or {}
ns.Locales.deDE = {
    RELOAD_PROMPT = "Die Chatposition hat sich geändert. Oberfläche neu laden, damit die Übersetzung auf deinem Chat liegt?",
    RELOAD = "Neu laden",
    LATER = "Später",
    BRIDGE_ON = "Brücke zum Begleiter: |cff00ff00aktiv|r (%d Nachricht(en) wartend)",
    TEST_SENT = "Testnachricht an den Begleiter gesendet.",
    HELP = "Befehle: /wct (Status), /wct test (Testnachricht), /wct pos (Chatposition abgleichen), /wct toggle (ein-/ausblenden)",
    COMPANION_OFF = "Begleiter nicht erkannt: Übersetzung aus. Starte WoWChatTranslatorCompagnion und gib /wct on ein.",
    BINDING_TOGGLE = "Übersetzungsoverlay ein-/ausblenden",
    BINDING_SCREENSHOT = "Screenshot mit dem Übersetzungsoverlay",
    SCREENSHOT_OFF = "Kein Übersetzungsoverlay: Screenshot nicht möglich.",
    OVERLAY_HIDDEN = "Übersetzungsoverlay ausgeblendet (%s oder /wct toggle zum Einblenden).",
    OVERLAY_HIDDEN_NOKEY = "Übersetzungsoverlay ausgeblendet (/wct toggle zum Einblenden).",
    OVERLAY_SHOWN = "Übersetzungsoverlay eingeblendet.",
}
