## What it does

- Translates other players' messages live into your language, in a window that replaces the game chat (the "overlay").
- Runs **on your PC, with no server or account**: translation is done by an artificial intelligence model installed with the companion. No message is sent over the Internet.
- 21 reading languages: French, English, German, Spanish, Italian, Portuguese, Russian, Polish, Dutch, Swedish, Danish, Norwegian, Finnish, Czech, Slovak, Romanian, Hungarian, Turkish, Greek, Ukrainian, Bulgarian.
- Keeps game jargon as typed (tank, heal, DPS, M+, WTS, dungeon names…) and puts common terms back into your language (classes, professions, "thanks", "lol"…).
- Wowhead tooltips (WoW Forever database, in your language) when hovering item, spell and quest links.
- Screenshots that include the translation (key binding set in game).


## Translated channels

Numbered channels (General, Trade…), Say, Whisper (received and sent, Battle.net included), Guild, Officer, Party, Raid, Instance.

**Not** translated: yells, emotes, NPCs, professions, loot, achievements, system messages, and automatic addon announcements (Questie, DBM…).

## How it works

World of Warcraft does not let an addon talk to an outside program in real time. The project therefore has two parts:

1. **The WoWChatTranslator addon** (in the game) reads chat messages and draws them as a small grid of coloured pixels, placed under the overlay.
2. **The WoWChatTranslatorCompagnion companion** (Windows program) reads that grid from the screen, translates the messages and shows them in the overlay, on top of the game.

The grid is hidden by the overlay: you do not see it while playing. Game windows (bags, character sheet, professions, map, menus, addon windows closed with Escape…) are drawn over the overlay, as over the normal chat. Elements always on screen (damage meters such as Details!, action bars, unit frames) stay under the overlay if you place it over them.

The addon only works while the companion is running.

## Companion icon (near the clock)

A click on the icon opens the **Options**. The right-click menu keeps what is needed while playing: launch the game, translation on/off, screenshot with the translation (in `Pictures\WoWChatTranslator`), move / resize the overlay (then `/reload` in game), Options, Quit.

## In game

| Command | Purpose |
|---|---|
| `/wct` | Status of the bridge with the companion |
| `/wct on` | Starts the bridge (if the companion was started after the game) |
| `/wct toggle` | Shows / hides the overlay |
| `/wct test` | Sends a test message |
| `/wct pos` | Snaps the position back to the chat |
| `/wct covers` | Diagnostics: game windows detected over the overlay |

Key bindings (Options → Keybindings → AddOns → WoWChatTranslator):
- **Show / hide the overlay**: Alt+F6 by default.
- **Screenshot with the overlay**: Ctrl+Print Screen by default.
