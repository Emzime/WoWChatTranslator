local _, ns = ...

-- Addon messages (frFR). English (en.lua) is the fallback for any missing line.
ns.Locales = ns.Locales or {}
ns.Locales.frFR = {
    RELOAD_PROMPT = "La position du chat a changé. Recharger l'interface pour caler la traduction sur votre chat ?",
    RELOAD = "Recharger",
    LATER = "Plus tard",
    BRIDGE_ON = "Pont vers le compagnon : |cff00ff00actif|r (%d message(s) en attente)",
    TEST_SENT = "Message de test envoyé au compagnon.",
    HELP = "Commandes : /wct (état), /wct on (activer), /wct test (message de test), /wct pos (recaler la position du chat), /wct toggle (afficher/masquer)",
    COMPANION_OFF = "Compagnon non détecté : traduction désactivée. Lancez WoWChatTranslatorCompagnion puis tapez /wct on.",
    BINDING_TOGGLE = "Afficher / masquer la surcouche de traduction",
    BINDING_SCREENSHOT = "Capture d'écran avec la surcouche de traduction",
    SCREENSHOT_OFF = "Surcouche de traduction absente : capture impossible.",
    OVERLAY_HIDDEN = "Surcouche de traduction masquée (%s ou /wct toggle pour l'afficher).",
    OVERLAY_HIDDEN_NOKEY = "Surcouche de traduction masquée (/wct toggle pour l'afficher).",
    OVERLAY_SHOWN = "Surcouche de traduction affichée.",
}
