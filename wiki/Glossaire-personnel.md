`%APPDATA%\WoWChatTranslatorCompagnion\glossary.json` reçoit vos ajouts, en plus du glossaire intégré :
- `keep` : mots jamais traduits ;
- `concepts` : un mot dans chaque langue, rendu dans la langue du lecteur ;
- `expand` : abréviation remplacée par le texte complet avant traduction ;
- `free` : expression laissée au modèle même si elle contient un mot du glossaire (`"fishing rod"` traduit en entier, et non « canne » + mot protégé) ;
- `whole` : abréviation remplacée seulement quand elle forme tout le message (`"gm"` → « good morning » quand le joueur écrit juste « gm », pas dans « gm all »).

Exemple :

```json
{
  "keep": ["zug zug"],
  "concepts": [{"en": "invite", "fr": "invitation", "de": "Einladung", "forms": ["inv", "invite"]}],
  "expand": {"lf heal": "looking for a healer"},
  "free": ["fishing rod"],
  "whole": {"gn": "good night"}
}
```

Après modification : Options → **Recharger le glossaire**.
