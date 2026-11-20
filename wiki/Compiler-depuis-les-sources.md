La compilation est faite par GitHub Actions :
- `.github/workflows/build.yml` : tests, conversion du modèle Standard, création de l'exécutable et de la release à chaque tag `v*`.
- `.github/workflows/models.yml` : à lancer à la main (onglet Actions → **Publish translation models** → **Run workflow**), une seule fois. Il publie les modèles Standard et Qualité dans la release `models`, d'où le compagnon les télécharge quand un joueur en choisit un. Le zip du compagnon ne contient que l'exécutable.
- `.github/workflows/wiki.yml` : publie le dossier `wiki/` dans ce wiki à chaque push qui le modifie. Les pages se modifient dans `wiki/`, jamais dans l'onglet Wiki (elles y seraient écrasées).

En local (Windows, Python 3.12) :

```
cd companion
pip install -r requirements.txt pyinstaller pytest
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install "transformers[sentencepiece]"
python build/prepare_models.py            # modèle Standard (ajoutez --quality pour le modèle Qualité)
python -m pytest -q tests
python build/check_translations.py --all  # corpus de phrases de chat passé dans le vrai modèle
python main.py                            # lancer depuis les sources
python build/make_icon.py
pyinstaller --noconfirm build/WoWChatTranslatorCompagnion.spec
```

Structure :
- `addon/WoWChatTranslator` : l'addon (Lua).
- `companion/wctc` : le compagnon (Python).
- `companion/data/glossary.json` : le glossaire intégré (jargon et abréviations de chat dans plusieurs langues).
- `companion/data/places.json`, `companion/data/names.json` : noms officiels des zones, donjons, races, réputations et objets dans chaque langue, extraits des tables du jeu par `python build/build_places.py` et `python build/build_names.py`.
- `companion/tests/corpus.jsonl` : phrases de chat avec les mots attendus ou interdits dans leur traduction. `build/check_translations.py [dossier du modèle] [--only TEXTE] [--all] [--trace]` les traduit avec le vrai modèle et signale ce qui ne va pas ; `--trace` montre chaque étape (masquage, langue détectée, texte envoyé au modèle). Ajoutez-y chaque phrase mal traduite avant de corriger le glossaire.
- `companion/build` : compilation (spec PyInstaller, modèles, icône).
- `wiki` : les pages de ce wiki.
- `docs/images` : les captures du README et du wiki (`python build/readme_screenshots.py`).
