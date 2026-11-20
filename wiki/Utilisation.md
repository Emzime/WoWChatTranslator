## Ce que ça fait

- Traduit en direct les messages des autres joueurs dans votre langue, dans une fenêtre qui remplace le chat du jeu (la « surcouche »).
- Fonctionne **sur votre PC, sans serveur ni compte** : la traduction est faite par un modèle d'intelligence artificielle installé avec le compagnon. Aucun message n'est envoyé sur Internet.
- 21 langues de lecture : français, anglais, allemand, espagnol, italien, portugais, russe, polonais, néerlandais, suédois, danois, norvégien, finnois, tchèque, slovaque, roumain, hongrois, turc, grec, ukrainien, bulgare.
- Garde le jargon du jeu tel quel (tank, heal, DPS, M+, WTS, noms de donjons…) et remet les termes courants dans votre langue (classes, métiers, « merci », « lol »…).
- Infobulles Wowhead (base WoW Forever, dans votre langue) au survol des liens d'objets, de sorts et de quêtes.
- Capture d'écran avec la traduction (raccourci réglable dans le jeu).


## Canaux traduits

Canaux numérotés (Général, Commerce…), Dire, Chuchoter (reçus et envoyés, Battle.net compris), Guilde, Officier, Groupe, Raid, Instance.

Ne sont **pas** traduits : cris, émotes, PNJ, métiers, butin, hauts faits, messages système, et les annonces automatiques d'addons (Questie, DBM…).

## Comment ça marche

World of Warcraft ne permet pas à un addon de communiquer en direct avec un programme extérieur. Le projet a donc deux parties :

1. **L'addon WoWChatTranslator** (dans le jeu) lit les messages du chat et les affiche sous forme d'une petite grille de pixels colorés, placée sous la surcouche.
2. **Le compagnon WoWChatTranslatorCompagnion** (programme Windows) lit cette grille à l'écran, traduit les messages et les affiche dans la surcouche, par-dessus le jeu.

La grille est cachée par la surcouche : vous ne la voyez pas en jouant. Les fenêtres du jeu (sacs, fiche personnage, métiers, carte, menus, fenêtres d'addons fermées par Échap…) passent devant la surcouche comme devant le chat normal. Les éléments toujours affichés (compteurs de dégâts comme Details!, barres d'action, cadres d'unité) restent sous la surcouche si vous la placez dessus.

L'addon ne fonctionne que si le compagnon est lancé.

## Icône du compagnon (près de l'horloge)

Un clic sur l'icône ouvre les **Options**. Le clic droit garde l'essentiel pour jouer : lancer le jeu, traduction activée, capture d'écran avec la traduction (dans `Images\WoWChatTranslator`), déplacer / redimensionner la surcouche (puis `/reload` en jeu), Options, Quitter.

## Dans le jeu

| Commande | Rôle |
|---|---|
| `/wct` | État du pont avec le compagnon |
| `/wct on` | Démarre le pont (si le compagnon a été lancé après le jeu) |
| `/wct toggle` | Affiche / masque la surcouche |
| `/wct test` | Envoie un message de test |
| `/wct pos` | Recale la position sur le chat |
| `/wct covers` | Diagnostic : fenêtres du jeu détectées par-dessus la surcouche |

Raccourcis (Options → Raccourcis → AddOns → WoWChatTranslator) :
- **Afficher / masquer la surcouche** : Alt+F6 par défaut.
- **Capture d'écran avec la surcouche** : Ctrl+Impr. écran par défaut.
