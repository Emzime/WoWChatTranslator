local _, ns = ...

-- Addon messages (fi). English (en.lua) is the fallback for any missing line.
ns.Locales = ns.Locales or {}
ns.Locales.fi = {
    RELOAD_PROMPT = "Chatin sijainti on muuttunut. Ladataanko käyttöliittymä uudelleen, jotta käännös osuu chatin kohdalle?",
    RELOAD = "Lataa uudelleen",
    LATER = "Myöhemmin",
    BRIDGE_ON = "Silta kumppanisovellukseen: |cff00ff00käytössä|r (%d viesti(ä) jonossa)",
    TEST_SENT = "Testiviesti lähetetty kumppanisovellukselle.",
    HELP = "Komennot: /wct (tila), /wct on (käynnistä), /wct test (testiviesti), /wct pos (kohdista chatin sijainti), /wct toggle (näytä/piilota)",
    COMPANION_OFF = "Kumppanisovellusta ei löytynyt: käännös pois päältä. Käynnistä WoWChatTranslatorCompagnion ja kirjoita sitten /wct on.",
    BINDING_TOGGLE = "Näytä / piilota käännöksen peitekerros",
    BINDING_SCREENSHOT = "Kuvakaappaus käännöksen peitekerroksen kanssa",
    SCREENSHOT_OFF = "Ei käännöksen peitekerrosta: kuvakaappaus ei onnistu.",
    OVERLAY_HIDDEN = "Käännöksen peitekerros piilotettu (%s tai /wct toggle näyttää sen).",
    OVERLAY_HIDDEN_NOKEY = "Käännöksen peitekerros piilotettu (/wct toggle näyttää sen).",
    OVERLAY_SHOWN = "Käännöksen peitekerros näkyvissä.",
}
