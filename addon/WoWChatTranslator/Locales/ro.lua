local _, ns = ...

-- Addon messages (ro). English (en.lua) is the fallback for any missing line.
ns.Locales = ns.Locales or {}
ns.Locales.ro = {
    RELOAD_PROMPT = "Poziția chatului s-a schimbat. Reîncarci interfața ca traducerea să se potrivească pe chat?",
    RELOAD = "Reîncarcă",
    LATER = "Mai târziu",
    BRIDGE_ON = "Punte către însoțitor: |cff00ff00activă|r (%d mesaj(e) în așteptare)",
    TEST_SENT = "Mesaj de test trimis însoțitorului.",
    HELP = "Comenzi: /wct (stare), /wct on (pornește), /wct test (mesaj de test), /wct pos (realiniază poziția chatului), /wct toggle (arată/ascunde)",
    COMPANION_OFF = "Însoțitorul nu a fost detectat: traducere oprită. Pornește WoWChatTranslatorCompagnion, apoi scrie /wct on.",
    BINDING_TOGGLE = "Arată / ascunde stratul de traducere",
    BINDING_SCREENSHOT = "Captură de ecran cu stratul de traducere",
    SCREENSHOT_OFF = "Niciun strat de traducere: captură imposibilă.",
    OVERLAY_HIDDEN = "Stratul de traducere este ascuns (%s sau /wct toggle pentru a-l afișa).",
    OVERLAY_HIDDEN_NOKEY = "Stratul de traducere este ascuns (/wct toggle pentru a-l afișa).",
    OVERLAY_SHOWN = "Stratul de traducere este afișat.",
}
