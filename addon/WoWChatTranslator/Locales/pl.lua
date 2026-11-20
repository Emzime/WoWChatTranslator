local _, ns = ...

-- Addon messages (pl). English (en.lua) is the fallback for any missing line.
ns.Locales = ns.Locales or {}
ns.Locales.pl = {
    RELOAD_PROMPT = "Pozycja czatu się zmieniła. Przeładować interfejs, aby tłumaczenie pasowało do czatu?",
    RELOAD = "Przeładuj",
    LATER = "Później",
    BRIDGE_ON = "Most do towarzysza: |cff00ff00aktywny|r (%d wiadomości w kolejce)",
    TEST_SENT = "Wiadomość testowa wysłana do towarzysza.",
    HELP = "Polecenia: /wct (stan), /wct on (włącz), /wct test (wiadomość testowa), /wct pos (wyrównaj pozycję czatu), /wct toggle (pokaż/ukryj)",
    COMPANION_OFF = "Nie wykryto towarzysza: tłumaczenie wyłączone. Uruchom WoWChatTranslatorCompagnion, potem wpisz /wct on.",
    BINDING_TOGGLE = "Pokaż / ukryj nakładkę tłumaczenia",
    BINDING_SCREENSHOT = "Zrzut ekranu z nakładką tłumaczenia",
    SCREENSHOT_OFF = "Brak nakładki tłumaczenia: zrzut niemożliwy.",
    OVERLAY_HIDDEN = "Nakładka tłumaczenia ukryta (%s lub /wct toggle, aby pokazać).",
    OVERLAY_HIDDEN_NOKEY = "Nakładka tłumaczenia ukryta (/wct toggle, aby pokazać).",
    OVERLAY_SHOWN = "Nakładka tłumaczenia pokazana.",
}
