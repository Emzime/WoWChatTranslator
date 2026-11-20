local _, ns = ...

-- Addon messages (da). English (en.lua) is the fallback for any missing line.
ns.Locales = ns.Locales or {}
ns.Locales.da = {
    RELOAD_PROMPT = "Chattens position er ændret. Genindlæs brugerfladen, så oversættelsen passer til din chat?",
    RELOAD = "Genindlæs",
    LATER = "Senere",
    BRIDGE_ON = "Bro til ledsageren: |cff00ff00aktiv|r (%d besked(er) i kø)",
    TEST_SENT = "Testbesked sendt til ledsageren.",
    HELP = "Kommandoer: /wct (status), /wct on (start), /wct test (testbesked), /wct pos (juster chattens position), /wct toggle (vis/skjul)",
    COMPANION_OFF = "Ledsageren blev ikke fundet: oversættelse slået fra. Start WoWChatTranslatorCompagnion, og skriv derefter /wct on.",
    BINDING_TOGGLE = "Vis / skjul oversættelsesoverlejringen",
    BINDING_SCREENSHOT = "Skærmbillede med oversættelsesoverlejringen",
    SCREENSHOT_OFF = "Ingen oversættelsesoverlejring: skærmbillede ikke muligt.",
    OVERLAY_HIDDEN = "Oversættelsesoverlejringen er skjult (%s eller /wct toggle for at vise den).",
    OVERLAY_HIDDEN_NOKEY = "Oversættelsesoverlejringen er skjult (/wct toggle for at vise den).",
    OVERLAY_SHOWN = "Oversættelsesoverlejringen vises.",
}
