local _, ns = ...

-- Addon messages (itIT). English (en.lua) is the fallback for any missing line.
ns.Locales = ns.Locales or {}
ns.Locales.itIT = {
    RELOAD_PROMPT = "La posizione della chat è cambiata. Ricaricare l'interfaccia per allineare la traduzione alla chat?",
    RELOAD = "Ricarica",
    LATER = "Più tardi",
    BRIDGE_ON = "Ponte verso il compagno: |cff00ff00attivo|r (%d messaggio/i in attesa)",
    TEST_SENT = "Messaggio di prova inviato al compagno.",
    HELP = "Comandi: /wct (stato), /wct test (messaggio di prova), /wct pos (riallinea la posizione della chat), /wct toggle (mostra/nascondi)",
    COMPANION_OFF = "Compagno non rilevato: traduzione disattivata. Avvia WoWChatTranslatorCompagnion e digita /wct on.",
    BINDING_TOGGLE = "Mostra / nascondi il livello di traduzione",
    BINDING_SCREENSHOT = "Screenshot con il livello di traduzione",
    SCREENSHOT_OFF = "Nessun livello di traduzione: screenshot impossibile.",
    OVERLAY_HIDDEN = "Livello di traduzione nascosto (%s o /wct toggle per mostrarlo).",
    OVERLAY_HIDDEN_NOKEY = "Livello di traduzione nascosto (/wct toggle per mostrarlo).",
    OVERLAY_SHOWN = "Livello di traduzione visibile.",
}
