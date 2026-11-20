"""Companion UI strings, in the player's reading language (missing ones fall back to English)."""

STRINGS = {
    "fr": {
        "menu_fade": 'Estomper le chat inactif',
        "fade_off": 'Jamais',
        "fade_seconds": 'Après {n} s',
        "fade_minutes": 'Après {n} min',
        "model_light": 'Léger (PC modestes)',
        "model_too_slow_light": 'Traduction trop lente sur ce PC : passage au mode Léger.',
        "loading": "Chargement du moteur de traduction…",
        "ready": "Prêt : le chat est traduit en {lang}.",
        "engine_error": "Erreur : impossible de charger le moteur de traduction. Détails : {log}",
        "addon_updated": "Addon WoWChatTranslator installé ou mis à jour : tapez /reload en jeu.",
        "wow_not_found": "World of Warcraft est introuvable. Choisissez le dossier « World of Warcraft ».",
        "wow_not_found_exit": "Aucune installation de World of Warcraft trouvée. Le compagnon va se fermer.",
        "already_running": "WoWChatTranslatorCompagnion est déjà lancé (icône près de l'horloge).",
        "edit_hint": "Mode déplacement : faites glisser la fenêtre, redimensionnez avec ◢, puis décochez « Déplacer / redimensionner ».",
        "menu_enabled": "Traduction active",
        "menu_lang": "Traduire vers",
        "overlay_moved": "Surcouche déplacée : tapez /reload en jeu pour finaliser.",
        "menu_original": "Afficher le message d'origine",
        "menu_edit": "Déplacer / redimensionner",
        "menu_reset": "Recaler sur le chat du jeu",
        "menu_opacity": "Opacité",
        "menu_font": "Taille du texte",
        "menu_autostart": "Lancer avec Windows",
        "menu_glossary": "Modifier le glossaire",
        "menu_reload_glossary": "Recharger le glossaire",
        "menu_logs": "Ouvrir le journal",
        "menu_quit": "Quitter",
        "menu_model": "Modèle de traduction",
        "model_auto": "Automatique (selon ce PC)",
        "model_standard": "Standard (rapide)",
        "model_quality": "Qualité (téléchargement ~1,4 Go)",
        "model_too_slow": "Traduction trop lente sur ce PC avec le modèle Qualité : retour au modèle Standard.",
        "menu_screenshot": "Capture d'écran avec la traduction",
        "screenshot_soon": "Capture dans 3 secondes : revenez dans le jeu.",
        "screenshot_saved": "Capture enregistrée : {path}",
        "screenshot_failed": "Capture impossible : le jeu n'est pas affiché.",
        "quit_in_game": "Un personnage est en jeu : sans le compagnon, la grille de l'addon redevient visible "
                        "(le jeu ne peut pas savoir que le compagnon est fermé).\n\n"
                        "Pour la masquer : touche du raccourci de la surcouche, /wct toggle, ou /reload.\n\n"
                        "Quitter quand même ?",
        "menu_launch": "Lancer {game}",
        "menu_launch_group": "Lancer le jeu",
        "menu_updates": "Rechercher une mise à jour",
        "menu_auto_update": "Mises à jour automatiques",
        "update_available": "Nouvelle version {version} disponible sur GitHub.",
        "update_ready": "Mise à jour {version} téléchargée : elle sera installée dès que vous ne serez plus en jeu.",
        "update_applying": "Installation de la mise à jour {version}…",
        "launch_failed": "Impossible de lancer le jeu (exécutable introuvable).",
        "reload_needed": "Le compagnon ne reçoit rien de l'addon. Tapez /wct en jeu : si le pont est inactif, tapez /wct on.",
    },
    "en": {
        "menu_fade": 'Fade the idle chat',
        "fade_off": 'Never',
        "fade_seconds": 'After {n} s',
        "fade_minutes": 'After {n} min',
        "model_light": 'Light (modest PCs)',
        "model_too_slow_light": 'Translation too slow on this PC: switching to Light mode.',
        "loading": "Loading translation engine…",
        "ready": "Ready: chat is translated to {lang}.",
        "engine_error": "Error: the translation engine could not be loaded. Details: {log}",
        "addon_updated": "WoWChatTranslator addon installed or updated: type /reload in game.",
        "wow_not_found": "World of Warcraft was not found. Please select the \"World of Warcraft\" folder.",
        "wow_not_found_exit": "No World of Warcraft installation found. The companion will close.",
        "already_running": "WoWChatTranslatorCompagnion is already running (icon near the clock).",
        "edit_hint": "Move mode: drag the window, resize with ◢, then untick \"Move / resize\".",
        "menu_enabled": "Translation on",
        "menu_lang": "Translate to",
        "overlay_moved": "Overlay moved: type /reload in game to finish.",
        "menu_original": "Show original message",
        "menu_edit": "Move / resize",
        "menu_reset": "Snap back to the game chat",
        "menu_opacity": "Opacity",
        "menu_font": "Text size",
        "menu_autostart": "Start with Windows",
        "menu_glossary": "Edit glossary",
        "menu_reload_glossary": "Reload glossary",
        "menu_logs": "Open log",
        "menu_quit": "Quit",
        "menu_model": "Translation model",
        "model_auto": "Automatic (based on this PC)",
        "model_standard": "Standard (fast)",
        "model_quality": "Quality (~1.4 GB download)",
        "model_too_slow": "Translation too slow on this PC with the Quality model: back to the Standard model.",
        "menu_screenshot": "Screenshot with the translation",
        "screenshot_soon": "Screenshot in 3 seconds: go back to the game.",
        "screenshot_saved": "Screenshot saved: {path}",
        "screenshot_failed": "Screenshot impossible: the game is not displayed.",
        "quit_in_game": "A character is in the world: without the companion, the addon's grid becomes visible "
                        "again (the game cannot know that the companion was closed).\n\n"
                        "To hide it: the overlay key binding, /wct toggle, or /reload.\n\n"
                        "Quit anyway?",
        "menu_launch": "Launch {game}",
        "menu_launch_group": "Launch the game",
        "menu_updates": "Check for updates",
        "menu_auto_update": "Automatic updates",
        "update_available": "New version {version} available on GitHub.",
        "update_ready": "Update {version} downloaded: it will be installed as soon as you leave the game world.",
        "update_applying": "Installing update {version}…",
        "launch_failed": "Cannot launch the game (executable not found).",
        "reload_needed": "The companion receives nothing from the addon. Type /wct in game: if the bridge is inactive, type /wct on.",
    },
}


from .i18n_more import MORE  # noqa: E402
from .i18n_models import MODEL_TEXTS  # noqa: E402

STRINGS.update(MORE)
from .i18n_help import CLASS_COLOR_TEXTS, NOTIFY_TEXTS, TRANSLATION_LOG_TEXTS, CHAT_LOG_TEXTS, CANCEL_TEXTS, UPDATE_KEYS, UPDATE_TEXTS, UPDATE_EXIT_TEXTS, HELP_TEXTS, KEYS as _HELP_KEYS, LABELS, LABEL_KEYS  # noqa: E402

for _lang, _texts in MODEL_TEXTS.items():
    STRINGS.setdefault(_lang, {}).update(_texts)
    STRINGS[_lang].update(zip(_HELP_KEYS, HELP_TEXTS[_lang]))
    STRINGS[_lang].update(zip(LABEL_KEYS, LABELS[_lang]))
    STRINGS[_lang].update(zip(("menu_class_colors", "help_class_colors"), CLASS_COLOR_TEXTS[_lang]))
    STRINGS[_lang].update(zip(("menu_notifications", "help_notifications"), NOTIFY_TEXTS[_lang]))
    STRINGS[_lang].update(zip(("menu_translation_log", "help_translation_log"), TRANSLATION_LOG_TEXTS[_lang]))
    STRINGS[_lang].update(zip(("menu_chat_log", "help_chat_log", "chat_log_reload"), CHAT_LOG_TEXTS[_lang]))
    STRINGS[_lang]["cancel"] = CANCEL_TEXTS[_lang]
    STRINGS[_lang].update(zip(UPDATE_KEYS, UPDATE_TEXTS[_lang]))
    STRINGS[_lang].update(zip(("upd_now_quit", "upd_quit_only"), UPDATE_EXIT_TEXTS[_lang]))


class Texts:
    def __init__(self, get_lang):
        self._get_lang = get_lang

    def __call__(self, key, **kwargs):
        table = STRINGS.get(self._get_lang(), STRINGS["en"])
        return table.get(key, STRINGS["en"].get(key, key)).format(**kwargs)
