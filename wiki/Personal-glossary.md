`%APPDATA%\WoWChatTranslatorCompagnion\glossary.json` receives your additions, on top of the built-in glossary:
- `keep`: words never translated;
- `concepts`: one word in each language, shown in the reader's language;
- `expand`: abbreviation replaced by the full text before translation;
- `free`: phrase left to the model even if it contains a glossary word (`"fishing rod"` translated as a whole, not "rod" + a protected word);
- `whole`: abbreviation replaced only when it is the whole message (`"gm"` → "good morning" when the player writes just "gm", not in "gm all").

Example:

```json
{
  "keep": ["zug zug"],
  "concepts": [{"en": "invite", "fr": "invitation", "de": "Einladung", "forms": ["inv", "invite"]}],
  "expand": {"lf heal": "looking for a healer"},
  "free": ["fishing rod"],
  "whole": {"gn": "good night"}
}
```

After editing: Options → **Reload glossary**.
