# Politique de sécurité (Français)

Français | [English](#security-policy-english)

## Versions prises en charge

Seule la **dernière release** de WoWChatTranslator (addon + compagnon) reçoit des correctifs de sécurité. Le compagnon se met à jour tout seul depuis GitHub : gardez cette option activée.

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

- le compagnon `WoWChatTranslatorCompagnion.exe` (mise à jour automatique, téléchargement des modèles, vérification SHA-256, installation de l'addon) ;
- l'addon `WoWChatTranslator` ;
- les workflows GitHub Actions qui compilent et publient les releases.

Pour savoir quelles données sortent de votre PC, voir la page [Confidentialité et sécurité](https://github.com/Emzime/WoWChatTranslator/wiki/Confidentialité-et-sécurité) du wiki.

---

# Security policy (English)

[Français](#politique-de-sécurité-français) | English

## Supported versions

Only the **latest release** of WoWChatTranslator (addon + companion) receives security fixes. The companion updates itself from GitHub: keep that option turned on.

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

- the `WoWChatTranslatorCompagnion.exe` companion (auto-update, model downloads, SHA-256 checks, addon installation);
- the `WoWChatTranslator` addon;
- the GitHub Actions workflows that build and publish releases.

To see which data leaves your PC, see the [Privacy and security](https://github.com/Emzime/WoWChatTranslator/wiki/Privacy-and-security) wiki page.
