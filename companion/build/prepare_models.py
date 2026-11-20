"""Downloads and converts the translation models to CTranslate2 int8 (build machine only).

Usage:
    python build/prepare_models.py                     # NLLB-200 distilled 600M (all language pairs)
    python build/prepare_models.py --quality           # + NLLB-200 1.3B (Quality, release download)
    python build/prepare_models.py --opus en-fr,de-fr  # + optional OPUS-MT pairs

Requires: pip install ctranslate2 transformers[sentencepiece] torch
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
# NLLB-200 (Meta, CC-BY-NC 4.0: free, non-commercial use only). Better than M2M-100 418M at a
# similar size and speed.
NLLB_REPO = "facebook/nllb-200-distilled-600M"          # Standard: "models" release download
NLLB_QUALITY_REPO = "facebook/nllb-200-distilled-1.3B"  # Quality: separate release download
QUALITY_DIR = MODELS_DIR.parent / "models_quality"


def convert(repo, output, copy_files):
    if (output / "model.bin").is_file():
        print(f"[skip] {output.name} already converted")
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable, "-m", "ctranslate2.converters.transformers",
        "--model", repo, "--output_dir", str(output), "--quantization", "int8",
        "--copy_files", *copy_files, "--force",
    ]
    print("[run]", " ".join(cmd))
    subprocess.run(cmd, check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--opus", default="", help="comma separated OPUS-MT pairs, e.g. en-fr,de-fr")
    parser.add_argument("--clean", action="store_true")
    parser.add_argument("--quality", action="store_true", help="also convert the Quality model (models_quality/)")
    parser.add_argument("--quality-only", action="store_true", help="skip the Standard model")
    args = parser.parse_args()

    if args.clean and MODELS_DIR.exists():
        shutil.rmtree(MODELS_DIR)

    if not args.quality_only:
        convert(NLLB_REPO, MODELS_DIR / "nllb-200-distilled-600m", ["sentencepiece.bpe.model"])
    old = MODELS_DIR / "m2m100_418m"   # previous model, replaced
    if old.exists():
        shutil.rmtree(old, ignore_errors=True)
    if args.quality or args.quality_only:
        convert(NLLB_QUALITY_REPO, QUALITY_DIR / "nllb-200-distilled-1.3b", ["sentencepiece.bpe.model"])
    for pair in filter(None, (p.strip() for p in args.opus.split(","))):
        convert(f"Helsinki-NLP/opus-mt-{pair}", MODELS_DIR / f"opus-mt-{pair}", ["source.spm", "target.spm"])

    for base in (MODELS_DIR, QUALITY_DIR):
        for leftover in base.rglob(".cache"):
            shutil.rmtree(leftover, ignore_errors=True)


if __name__ == "__main__":
    main()
