local _, ns = ...

-- Addon messages (bg). English (en.lua) is the fallback for any missing line.
ns.Locales = ns.Locales or {}
ns.Locales.bg = {
    RELOAD_PROMPT = "Позицията на чата се промени. Да се презареди ли интерфейсът, за да съвпада преводът с чата?",
    RELOAD = "Презареждане",
    LATER = "По-късно",
    BRIDGE_ON = "Мост към помощника: |cff00ff00активен|r (%d съобщения на опашка)",
    TEST_SENT = "Тестово съобщение е изпратено до помощника.",
    HELP = "Команди: /wct (състояние), /wct on (включване), /wct test (тестово съобщение), /wct pos (подравняване на чата), /wct toggle (показване/скриване)",
    COMPANION_OFF = "Помощникът не е открит: преводът е изключен. Стартирайте WoWChatTranslatorCompagnion, след това въведете /wct on.",
    BINDING_TOGGLE = "Показване / скриване на слоя за превод",
    BINDING_SCREENSHOT = "Екранна снимка със слоя за превод",
    SCREENSHOT_OFF = "Няма слой за превод: снимката е невъзможна.",
    OVERLAY_HIDDEN = "Слоят за превод е скрит (%s или /wct toggle, за да го покажете).",
    OVERLAY_HIDDEN_NOKEY = "Слоят за превод е скрит (/wct toggle, за да го покажете).",
    OVERLAY_SHOWN = "Слоят за превод е показан.",
}
