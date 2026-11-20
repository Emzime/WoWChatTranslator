local _, ns = ...

-- Addon messages (cs). English (en.lua) is the fallback for any missing line.
ns.Locales = ns.Locales or {}
ns.Locales.cs = {
    RELOAD_PROMPT = "Pozice chatu se změnila. Znovu načíst rozhraní, aby překlad seděl na chat?",
    RELOAD = "Znovu načíst",
    LATER = "Později",
    BRIDGE_ON = "Most ke společníkovi: |cff00ff00aktivní|r (%d zpráv ve frontě)",
    TEST_SENT = "Testovací zpráva odeslána společníkovi.",
    HELP = "Příkazy: /wct (stav), /wct on (zapnout), /wct test (testovací zpráva), /wct pos (srovnat pozici chatu), /wct toggle (zobrazit/skrýt)",
    COMPANION_OFF = "Společník nebyl nalezen: překlad vypnut. Spusťte WoWChatTranslatorCompagnion a pak napište /wct on.",
    BINDING_TOGGLE = "Zobrazit / skrýt překladovou vrstvu",
    BINDING_SCREENSHOT = "Snímek obrazovky s překladovou vrstvou",
    SCREENSHOT_OFF = "Žádná překladová vrstva: snímek není možný.",
    OVERLAY_HIDDEN = "Překladová vrstva skryta (%s nebo /wct toggle pro zobrazení).",
    OVERLAY_HIDDEN_NOKEY = "Překladová vrstva skryta (/wct toggle pro zobrazení).",
    OVERLAY_SHOWN = "Překladová vrstva zobrazena.",
}
