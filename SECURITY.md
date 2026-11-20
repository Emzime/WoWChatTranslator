# Politique de sécurité (Français)

Français | [English](#security-policy-english)

## Versions prises en charge

Seule la **dernière release** de WoWChatTranslator (addon + compagnon) reçoit des correctifs de sécurité. Le compagnon vérifie les nouvelles versions sur GitHub et propose de les installer (rien n'est téléchargé sans votre accord) : gardez l'option « Rechercher les mises à jour » activée et acceptez les mises à jour proposées.

| Version | Prise en charge |
| ------- | --------------- |
| Dernière release | ✅ |
| Versions plus anciennes | ❌ |

## Signaler une vulnérabilité

**N'ouvrez pas d'issue publique** pour un problème de sécurité.

1. Allez dans l'onglet **Security and quality** du dépôt.
2. Cliquez sur **Report a vulnerability**.
3. Décrivez le problème : version concernée, étapes pour le reproduire, impact possible.

Le signalement reste privé entre vous et le mainteneur. Vous recevrez une réponse dès que possible ; une fois le correctif publié, une alerte de sécurité pourra être rendue publique en vous créditant si vous le souhaitez.

## Périmètre

Sont notamment concernés :

- le compagnon `WoWChatTranslatorCompagnion.exe` (mises à jour, téléchargement des modèles, vérification SHA-256, installation de l'addon) ;
- l'addon `WoWChatTranslator` ;
- les workflows GitHub Actions qui compilent et publient les releases.

Pour savoir quelles données sortent de votre PC, voir la page [Confidentialité et sécurité](https://github.com/Emzime/WoWChatTranslator/wiki/Confidentialité-et-sécurité) du wiki.

---

# Security policy (English)

[Français](#politique-de-s%C3%A9curit%C3%A9-fran%C3%A7ais) | English

## Supported versions

Only the **latest release** of WoWChatTranslator (addon + companion) receives security fixes. The companion checks GitHub for new versions and offers to install them (nothing is downloaded without your consent): keep the "Check for updates" option turned on and accept the updates it offers.

| Version | Supported |
| ------- | --------- |
| Latest release | ✅ |
| Older versions | ❌ |

## Reporting a vulnerability

**Do not open a public issue** for a security problem.

1. Go to the repository's **Security and quality** tab.
2. Click **Report a vulnerability**.
3. Describe the problem: affected version, steps to reproduce, possible impact.

The report stays private between you and the maintainer. You will get an answer as soon as possible; once the fix is released, a security advisory may be published, crediting you if you wish.

## Scope

This includes:

- the `WoWChatTranslatorCompagnion.exe` companion (updates, model downloads, SHA-256 checks, addon installation);
- the `WoWChatTranslator` addon;
- the GitHub Actions workflows that build and publish releases.

To see which data leaves your PC, see the [Privacy and security](https://github.com/Emzime/WoWChatTranslator/wiki/Privacy-and-security) wiki page.
