local _, ns = ...

-- Addon messages (no). English (en.lua) is the fallback for any missing line.
ns.Locales = ns.Locales or {}
ns.Locales.no = {
    RELOAD_PROMPT = "Chatens posisjon er endret. Laste inn grensesnittet på nytt slik at oversettelsen passer til chatten?",
    RELOAD = "Last inn på nytt",
    LATER = "Senere",
    BRIDGE_ON = "Bro til følgesvennen: |cff00ff00aktiv|r (%d melding(er) i kø)",
    TEST_SENT = "Testmelding sendt til følgesvennen.",
    HELP = "Kommandoer: /wct (status), /wct on (start), /wct test (testmelding), /wct pos (juster chatens posisjon), /wct toggle (vis/skjul)",
    COMPANION_OFF = "Fant ikke følgesvennen: oversettelse av. Start WoWChatTranslatorCompagnion, og skriv deretter /wct on.",
    BINDING_TOGGLE = "Vis / skjul oversettelsesoverlegget",
    BINDING_SCREENSHOT = "Skjermbilde med oversettelsesoverlegget",
    SCREENSHOT_OFF = "Ikke noe oversettelsesoverlegg: skjermbilde ikke mulig.",
    OVERLAY_HIDDEN = "Oversettelsesoverlegget er skjult (%s eller /wct toggle for å vise det).",
    OVERLAY_HIDDEN_NOKEY = "Oversettelsesoverlegget er skjult (/wct toggle for å vise det).",
    OVERLAY_SHOWN = "Oversettelsesoverlegget vises.",
}
