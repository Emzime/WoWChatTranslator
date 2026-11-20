local _, ns = ...

-- Addon messages (ruRU). English (en.lua) is the fallback for any missing line.
ns.Locales = ns.Locales or {}
ns.Locales.ruRU = {
    RELOAD_PROMPT = "Положение чата изменилось. Перезагрузить интерфейс, чтобы перевод совпал с чатом?",
    RELOAD = "Перезагрузить",
    LATER = "Позже",
    BRIDGE_ON = "Мост к компаньону: |cff00ff00активен|r (сообщений в очереди: %d)",
    TEST_SENT = "Тестовое сообщение отправлено компаньону.",
    HELP = "Команды: /wct (состояние), /wct test (тестовое сообщение), /wct pos (выровнять положение чата), /wct toggle (показать/скрыть)",
    COMPANION_OFF = "Компаньон не найден: перевод выключен. Запустите WoWChatTranslatorCompagnion и введите /wct on.",
    BINDING_TOGGLE = "Показать / скрыть слой перевода",
    BINDING_SCREENSHOT = "Снимок экрана со слоем перевода",
    SCREENSHOT_OFF = "Нет слоя перевода: снимок невозможен.",
    OVERLAY_HIDDEN = "Слой перевода скрыт (%s или /wct toggle, чтобы показать).",
    OVERLAY_HIDDEN_NOKEY = "Слой перевода скрыт (/wct toggle, чтобы показать).",
    OVERLAY_SHOWN = "Слой перевода показан.",
}
