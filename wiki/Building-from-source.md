The build is done by GitHub Actions:
- `.github/workflows/build.yml`: tests, conversion of the Standard model, creation of the executable and of the release on each `v*` tag.
- `.github/workflows/models.yml`: to be run by hand (Actions tab → **Publish translation models** → **Run workflow**), only once. It publishes the Standard and Quality models in the `models` release, from which the companion downloads them when a player chooses one. The companion zip contains only the executable.
- `.github/workflows/wiki.yml`: publishes the `wiki/` folder to this wiki on every push that changes it. Pages are edited in `wiki/`, never in the Wiki tab (they would be overwritten there).

Locally (Windows, Python 3.12):

```
cd companion
pip install -r requirements.txt pyinstaller pytest
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install "transformers[sentencepiece]"
python build/prepare_models.py            # Standard model (add --quality for the Quality model)
python -m pytest -q tests
python build/check_translations.py --all  # chat phrase corpus run through the real model
python main.py                            # run from source
python build/make_icon.py
pyinstaller --noconfirm build/WoWChatTranslatorCompagnion.spec
```

Layout:
- `addon/WoWChatTranslator`: the addon (Lua).
- `companion/wctc`: the companion (Python).
- `companion/data/glossary.json`: the built-in glossary (chat jargon and abbreviations in several languages).
- `companion/data/places.json`, `companion/data/names.json`: official names of zones, dungeons, races, reputations and items in each language, extracted from the game tables by `python build/build_places.py` and `python build/build_names.py`.
- `companion/tests/corpus.jsonl`: chat phrases with the words expected or forbidden in their translation. `build/check_translations.py [model folder] [--only TEXT] [--all] [--trace]` translates them with the real model and reports what goes wrong; `--trace` shows each step (masking, detected language, text sent to the model). Add every badly translated phrase to it before fixing the glossary.
- `companion/build`: build (PyInstaller spec, models, icon).
- `wiki`: the pages of this wiki.
- `docs/images`: screenshots of the README and the wiki (`python build/readme_screenshots.py`).
