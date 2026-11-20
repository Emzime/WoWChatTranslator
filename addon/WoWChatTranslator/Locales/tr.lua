local _, ns = ...

-- Addon messages (tr). English (en.lua) is the fallback for any missing line.
ns.Locales = ns.Locales or {}
ns.Locales.tr = {
    RELOAD_PROMPT = "Sohbetin konumu değişti. Çevirinin sohbetle hizalanması için arayüz yeniden yüklensin mi?",
    RELOAD = "Yeniden yükle",
    LATER = "Daha sonra",
    BRIDGE_ON = "Yardımcı programa köprü: |cff00ff00etkin|r (%d mesaj bekliyor)",
    TEST_SENT = "Test mesajı yardımcı programa gönderildi.",
    HELP = "Komutlar: /wct (durum), /wct on (başlat), /wct test (test mesajı), /wct pos (sohbet konumunu hizala), /wct toggle (göster/gizle)",
    COMPANION_OFF = "Yardımcı program bulunamadı: çeviri kapalı. WoWChatTranslatorCompagnion'u başlatın, ardından /wct on yazın.",
    BINDING_TOGGLE = "Çeviri katmanını göster / gizle",
    BINDING_SCREENSHOT = "Çeviri katmanıyla ekran görüntüsü",
    SCREENSHOT_OFF = "Çeviri katmanı yok: ekran görüntüsü alınamıyor.",
    OVERLAY_HIDDEN = "Çeviri katmanı gizlendi (göstermek için %s veya /wct toggle).",
    OVERLAY_HIDDEN_NOKEY = "Çeviri katmanı gizlendi (göstermek için /wct toggle).",
    OVERLAY_SHOWN = "Çeviri katmanı gösteriliyor.",
}
