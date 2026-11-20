local _, ns = ...

-- Addon messages (sk). English (en.lua) is the fallback for any missing line.
ns.Locales = ns.Locales or {}
ns.Locales.sk = {
    RELOAD_PROMPT = "Pozícia chatu sa zmenila. Znova načítať rozhranie, aby preklad sedel na chat?",
    RELOAD = "Znova načítať",
    LATER = "Neskôr",
    BRIDGE_ON = "Most k spoločníkovi: |cff00ff00aktívny|r (%d správ v poradí)",
    TEST_SENT = "Testovacia správa odoslaná spoločníkovi.",
    HELP = "Príkazy: /wct (stav), /wct on (zapnúť), /wct test (testovacia správa), /wct pos (zarovnať pozíciu chatu), /wct toggle (zobraziť/skryť)",
    COMPANION_OFF = "Spoločník sa nenašiel: preklad vypnutý. Spustite WoWChatTranslatorCompagnion a potom napíšte /wct on.",
    BINDING_TOGGLE = "Zobraziť / skryť prekladovú vrstvu",
    BINDING_SCREENSHOT = "Snímka obrazovky s prekladovou vrstvou",
    SCREENSHOT_OFF = "Žiadna prekladová vrstva: snímka nie je možná.",
    OVERLAY_HIDDEN = "Prekladová vrstva skrytá (%s alebo /wct toggle na zobrazenie).",
    OVERLAY_HIDDEN_NOKEY = "Prekladová vrstva skrytá (/wct toggle na zobrazenie).",
    OVERLAY_SHOWN = "Prekladová vrstva zobrazená.",
}
