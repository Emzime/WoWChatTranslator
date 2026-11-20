local _, ns = ...

-- Addon messages (hu). English (en.lua) is the fallback for any missing line.
ns.Locales = ns.Locales or {}
ns.Locales.hu = {
    RELOAD_PROMPT = "A chat helyzete megváltozott. Újratöltöd a felületet, hogy a fordítás a chatre illeszkedjen?",
    RELOAD = "Újratöltés",
    LATER = "Később",
    BRIDGE_ON = "Híd a kísérőprogramhoz: |cff00ff00aktív|r (%d üzenet vár)",
    TEST_SENT = "Tesztüzenet elküldve a kísérőprogramnak.",
    HELP = "Parancsok: /wct (állapot), /wct on (bekapcsolás), /wct test (tesztüzenet), /wct pos (chat helyzetének igazítása), /wct toggle (megjelenítés/elrejtés)",
    COMPANION_OFF = "A kísérőprogram nem található: a fordítás ki van kapcsolva. Indítsd el a WoWChatTranslatorCompagnion programot, majd írd be: /wct on.",
    BINDING_TOGGLE = "Fordítási réteg megjelenítése / elrejtése",
    BINDING_SCREENSHOT = "Képernyőkép a fordítási réteggel",
    SCREENSHOT_OFF = "Nincs fordítási réteg: képernyőkép nem lehetséges.",
    OVERLAY_HIDDEN = "Fordítási réteg elrejtve (%s vagy /wct toggle a megjelenítéshez).",
    OVERLAY_HIDDEN_NOKEY = "Fordítási réteg elrejtve (/wct toggle a megjelenítéshez).",
    OVERLAY_SHOWN = "Fordítási réteg megjelenítve.",
}
