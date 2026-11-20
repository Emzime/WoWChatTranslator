local _, ns = ...

-- Addon messages (esES). English (en.lua) is the fallback for any missing line.
ns.Locales = ns.Locales or {}
ns.Locales.esES = {
    RELOAD_PROMPT = "La posición del chat ha cambiado. ¿Recargar la interfaz para alinear la traducción con tu chat?",
    RELOAD = "Recargar",
    LATER = "Más tarde",
    BRIDGE_ON = "Puente al compañero: |cff00ff00activo|r (%d mensaje(s) en espera)",
    TEST_SENT = "Mensaje de prueba enviado al compañero.",
    HELP = "Comandos: /wct (estado), /wct test (mensaje de prueba), /wct pos (reajustar la posición del chat), /wct toggle (mostrar/ocultar)",
    COMPANION_OFF = "Compañero no detectado: traducción desactivada. Inicia WoWChatTranslatorCompagnion y escribe /wct on.",
    BINDING_TOGGLE = "Mostrar / ocultar la capa de traducción",
    BINDING_SCREENSHOT = "Captura de pantalla con la capa de traducción",
    SCREENSHOT_OFF = "Sin capa de traducción: captura imposible.",
    OVERLAY_HIDDEN = "Capa de traducción oculta (%s o /wct toggle para mostrarla).",
    OVERLAY_HIDDEN_NOKEY = "Capa de traducción oculta (/wct toggle para mostrarla).",
    OVERLAY_SHOWN = "Capa de traducción visible.",
}
