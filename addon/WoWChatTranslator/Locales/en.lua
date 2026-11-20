local _, ns = ...

-- Addon messages (enUS). English (en.lua) is the fallback for any missing line.
ns.Locales = ns.Locales or {}
ns.Locales.enUS = {
    RELOAD_PROMPT = "The chat position has changed. Reload the interface so the translation lines up with your chat?",
    RELOAD = "Reload",
    LATER = "Later",
    BRIDGE_ON = "Bridge to the companion: |cff00ff00active|r (%d message(s) waiting)",
    TEST_SENT = "Test message sent to the companion.",
    HELP = "Commands: /wct (status), /wct on (start), /wct test (test message), /wct pos (re-sync chat position), /wct toggle (show/hide)",
    COMPANION_OFF = "Companion not detected: translation off. Start WoWChatTranslatorCompagnion, then type /wct on.",
    BINDING_TOGGLE = "Show / hide the translation overlay",
    BINDING_SCREENSHOT = "Screenshot with the translation overlay",
    SCREENSHOT_OFF = "No translation overlay: screenshot not possible.",
    OVERLAY_HIDDEN = "Translation overlay hidden (%s or /wct toggle to show it).",
    OVERLAY_HIDDEN_NOKEY = "Translation overlay hidden (/wct toggle to show it).",
    OVERLAY_SHOWN = "Translation overlay shown.",
}
