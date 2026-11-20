local _, ns = ...

-- Addon messages (uk). English (en.lua) is the fallback for any missing line.
ns.Locales = ns.Locales or {}
ns.Locales.uk = {
    RELOAD_PROMPT = "Положення чату змінилося. Перезавантажити інтерфейс, щоб переклад збігався з чатом?",
    RELOAD = "Перезавантажити",
    LATER = "Пізніше",
    BRIDGE_ON = "Міст до компаньйона: |cff00ff00активний|r (%d повідомлень у черзі)",
    TEST_SENT = "Тестове повідомлення надіслано компаньйону.",
    HELP = "Команди: /wct (стан), /wct on (увімкнути), /wct test (тестове повідомлення), /wct pos (вирівняти положення чату), /wct toggle (показати/приховати)",
    COMPANION_OFF = "Компаньйона не знайдено: переклад вимкнено. Запустіть WoWChatTranslatorCompagnion, потім введіть /wct on.",
    BINDING_TOGGLE = "Показати / приховати шар перекладу",
    BINDING_SCREENSHOT = "Знімок екрана з шаром перекладу",
    SCREENSHOT_OFF = "Немає шару перекладу: знімок неможливий.",
    OVERLAY_HIDDEN = "Шар перекладу приховано (%s або /wct toggle, щоб показати).",
    OVERLAY_HIDDEN_NOKEY = "Шар перекладу приховано (/wct toggle, щоб показати).",
    OVERLAY_SHOWN = "Шар перекладу показано.",
}
