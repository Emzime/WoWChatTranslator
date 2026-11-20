"""Runs the chat corpus (tests/corpus.jsonl) through the real translation pipeline and reports
what goes wrong: expected words missing, forbidden words present, placeholders left, lines
not translated that should be, English words left in a translation.

Usage: python build/check_translations.py [model folder] [--only TEXT] [--all] [--trace]
   (default model: models/nllb-200-distilled-600m). Exit code 1 if a line fails.

Each corpus line is a JSON object:
  {"text": "LFM Tank pour Dalaran", "target": "fr", "translated": false}
  {"text": "she sold out", "expect": ["tout vendu"], "forbid": ["vendue"]}
  {"text": "gm all", "mask": ["gm all"]}            (glossary only, checked by pytest too)
target defaults to "fr"; "translated" true/false says whether a translation must be shown.
"""
import json
import logging
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from wctc.chatparser import ChatLine  # noqa: E402
from wctc.detector import LanguageDetector  # noqa: E402
from wctc.engine import TranslationEngine  # noqa: E402
from wctc.glossary import Glossary  # noqa: E402
from wctc.pipeline import TranslationPipeline  # noqa: E402

CORPUS = ROOT / "tests" / "corpus.jsonl"
# Everyday English words that should not survive a translation into another language.
ENGLISH_LEFTOVERS = {"the", "and", "with", "for", "you", "your", "need", "looking", "anyone", "please", "what",
                     "where", "have", "selling", "buying", "price", "want", "can", "will", "pay"}


def load_corpus(path=CORPUS):
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        raw = raw.strip()
        if raw and not raw.startswith("#"):
            entry = json.loads(raw)
            entry.setdefault("target", "fr")
            entry["line_number"] = number
            yield entry


def problems(entry, shown, translated):
    found = []
    low = shown.lower()
    for word in entry.get("expect", []):
        if word.lower() not in low:
            found.append(f"missing {word!r}")
    for word in entry.get("forbid", []):
        if word.lower() in low:
            found.append(f"forbidden {word!r}")
    if re.search(r"ZX\d", shown):
        found.append("placeholder left")
    if "translated" in entry and bool(entry["translated"]) != translated:
        found.append("should be translated" if entry["translated"] else "should be left as typed")
    if translated and entry["target"] != "en":       # item links stay in the game's language
        left = sorted(w for w in re.findall(r"[a-z]+", re.sub(r"\[[^\]]*\]", " ", low)) if w in ENGLISH_LEFTOVERS
                      and w not in entry.get("allow", []))
        if left:
            found.append(f"English left: {', '.join(left)}")
    return found


def main(argv):
    show_all = "--all" in argv
    only = argv[argv.index("--only") + 1] if "--only" in argv else None
    trace = "--trace" in argv
    if trace:                                     # every pipeline step of each line
        logging.basicConfig(level=logging.INFO, format="     . %(message)s")
    paths = [a for a in argv if not a.startswith("--") and a != only]
    model = Path(paths[0]) if paths else ROOT / "models" / "nllb-200-distilled-600m"
    glossary = Glossary()
    targets = {}

    def pipeline(target):
        if target not in targets:
            p = TranslationPipeline(None, None, glossary, lambda: target, None, None)
            p.detector = LanguageDetector()
            p.engine = engine
            p.trace_enabled = lambda: trace
            targets[target] = p
        return targets[target]

    engine = TranslationEngine(Path(tempfile.mkdtemp()), model)
    failures = 0
    for entry in load_corpus():
        if only and only.lower() not in entry["text"].lower():
            continue
        if "mask" in entry and len(entry) <= 4:          # glossary-only entry: pytest checks it
            continue
        result = pipeline(entry["target"]).process(ChatLine("", "", "x", "x", entry["text"], "channel"))
        found = problems(entry, result.text, result.translated)
        failures += bool(found)
        if found or show_all:
            mark = "FAIL" if found else "ok  "
            print(f"{mark} [{entry['target']}] {entry['text']}\n     -> {result.text}")
            for problem in found:
                print(f"     ! {problem}")
    print(f"\n{failures} line(s) with problems")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
