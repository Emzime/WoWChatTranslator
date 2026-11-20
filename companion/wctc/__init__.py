"""WoWChatTranslatorCompagnion: local chat translation companion for WoWChatTranslator."""

__version__ = "1.0.0"
APP_NAME = "WoWChatTranslatorCompagnion"
ADDON_NAME = "WoWChatTranslator"

# Reading languages (the player's own). Codes are py3langid codes (mapped to NLLB-200 codes by the engine).
# The first seven are the languages of the WoW clients (addon texts, glossary forms...);
# the others are spoken by many players on EU realms and fall back to English game terms.
WOW_LANGUAGES = {
    "fr": "Français",
    "en": "English",
    "de": "Deutsch",
    "es": "Español",
    "it": "Italiano",
    "pt": "Português",
    "ru": "Русский",
}
EXTRA_LANGUAGES = {
    "pl": "Polski",
    "nl": "Nederlands",
    "sv": "Svenska",
    "da": "Dansk",
    "no": "Norsk",
    "fi": "Suomi",
    "cs": "Čeština",
    "sk": "Slovenčina",
    "ro": "Română",
    "hu": "Magyar",
    "tr": "Türkçe",
    "el": "Ελληνικά",
    "uk": "Українська",
    "bg": "Български",
}
LANGUAGES = {**WOW_LANGUAGES, **EXTRA_LANGUAGES}
