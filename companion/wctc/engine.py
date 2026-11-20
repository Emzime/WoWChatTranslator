"""Local translation engine: NLLB-200 distilled 600M (any pair, direct; M2M-100 418M is still
accepted if it is the model found) with optional OPUS-MT models per pair."""

import logging
import os
import re
import threading
from collections import OrderedDict
from pathlib import Path

import ctranslate2
import sentencepiece as spm

log = logging.getLogger(__name__)

NLLB_DIR_NAME = "nllb-200-distilled-600m"
M2M_DIR_NAME = "m2m100_418m"
SPM_NAMES = ("sentencepiece.bpe.model", "spm.128k.model")
# NLLB-200 language codes (FLORES-200) of the reading / source languages.
NLLB_CODES = {
    "en": "eng_Latn", "fr": "fra_Latn", "de": "deu_Latn", "es": "spa_Latn", "it": "ita_Latn",
    "pt": "por_Latn", "ru": "rus_Cyrl", "pl": "pol_Latn", "nl": "nld_Latn", "sv": "swe_Latn",
    "da": "dan_Latn", "no": "nob_Latn", "fi": "fin_Latn", "cs": "ces_Latn", "sk": "slk_Latn",
    "ro": "ron_Latn", "hu": "hun_Latn", "tr": "tur_Latn", "el": "ell_Grek", "uk": "ukr_Cyrl",
    "bg": "bul_Cyrl",
}


# Sentence ends: ". ! ?" (and their repeats) followed by a space. Long chat lines (guild
# recruitment...) are translated sentence by sentence: in one piece, the model tends to drop or
# merge the last sentences.
_SENTENCE_END_RE = re.compile(r"(?<=[.!?…])\s+(?=\S)")
MIN_SPLIT_LENGTH = 25      # shorter lines are translated in one piece


def split_sentences(text):
    if len(text) < MIN_SPLIT_LENGTH:
        return [text]
    parts = [p for p in _SENTENCE_END_RE.split(text) if p.strip()]
    # Glue very short pieces ("Ok!", "Hi.") to the next one: no context, odd translations.
    merged = []
    for part in parts:
        if merged and len(merged[-1]) < 12:
            merged[-1] = f"{merged[-1]} {part}"
        else:
            merged.append(part)
    return merged or [text]


_ELISION_RE = re.compile(r"(\w)(['’]) (?=\w)")


# A space the model leaves before a full stop or comma ("C'est plutôt cool ."): no language
# keeps it (French keeps its space only before ? ! : ;).
_SPACE_BEFORE_DOT_RE = re.compile(r"(?<=\S) +(?=[.,](?:\s|$))")


def _tidy(text):
    """Model output clean-up: "Quelqu' un" -> "Quelqu'un", "cool ." -> "cool."."""
    return _SPACE_BEFORE_DOT_RE.sub("", _ELISION_RE.sub(r"\1\2", text))


def _threads():
    return max(1, min(8, (os.cpu_count() or 2) // 2))


class _OpusModel:
    """Helsinki-NLP OPUS-MT model converted with CTranslate2 (folder opus-mt-<src>-<tgt>)."""

    def __init__(self, path: Path):
        self.translator = ctranslate2.Translator(str(path), device="cpu", compute_type="int8", intra_threads=_threads())
        self.source_sp = spm.SentencePieceProcessor(model_file=str(path / "source.spm"))
        self.target_sp = spm.SentencePieceProcessor(model_file=str(path / "target.spm"))

    def translate(self, sentences):
        batch = [self.source_sp.encode(text, out_type=str) + ["</s>"] for text in sentences]
        result = self.translator.translate_batch(batch, beam_size=4, max_decoding_length=256,
                                                 no_repeat_ngram_size=4)
        return [self.target_sp.decode(r.hypotheses[0]) for r in result]


class TranslationEngine:
    def __init__(self, models_dir: Path, main_dir: Path = None, cache_size=2000, light=False):
        self.models_dir = Path(models_dir)
        self._lock = threading.Lock()
        self._cache = OrderedDict()
        self._cache_size = cache_size
        self._opus = {}

        # Main model: the one chosen (NLLB-200 Standard or Quality), else NLLB-200 / M2M-100
        # found in the models folder (source runs, older builds).
        candidates = [Path(main_dir)] if main_dir else [self.models_dir / NLLB_DIR_NAME, self.models_dir / M2M_DIR_NAME]
        for model_dir in candidates:
            spm_file = next((model_dir / n for n in SPM_NAMES if (model_dir / n).is_file()), None)
            if (model_dir / "model.bin").is_file() and spm_file is not None:
                break
        else:
            raise FileNotFoundError(f"No translation model in {candidates}")
        name = model_dir.name
        codes = None if name.startswith("m2m") else NLLB_CODES
        self._codes = codes
        # Light mode (modest PCs): one candidate translation instead of four (about 1.7 times
        # faster, nearly the same result on chat lines) and fewer processor threads.
        self._beam = 1 if light else 4
        threads = min(2, _threads()) if light else _threads()
        self._main = ctranslate2.Translator(str(model_dir), device="cpu", compute_type="int8", intra_threads=threads)
        self._main_sp = spm.SentencePieceProcessor(model_file=str(spm_file))
        self.model_name = name
        log.info("%s loaded from %s", name, model_dir)

    def _lang_token(self, code):
        """NLLB: "fra_Latn"; M2M-100: "__fr__"."""
        return self._codes.get(code, code) if self._codes is not None else f"__{code}__"

    def _opus_for(self, src, tgt):
        key = (src, tgt)
        if key not in self._opus:
            path = self.models_dir / f"opus-mt-{src}-{tgt}"
            self._opus[key] = _OpusModel(path) if (path / "model.bin").is_file() else None
            if self._opus[key]:
                log.info("OPUS-MT %s-%s loaded", src, tgt)
        return self._opus[key]

    def _main_translate(self, sentences, src, tgt):
        source = self._lang_token(src)
        batch = [[source] + self._main_sp.encode(text, out_type=str) + ["</s>"] for text in sentences]
        result = self._main.translate_batch(
            batch,
            target_prefix=[[self._lang_token(tgt)]] * len(batch),
            beam_size=self._beam,
            max_decoding_length=256,
            repetition_penalty=1.1,
            no_repeat_ngram_size=4,
        )
        return [self._main_sp.decode(r.hypotheses[0][1:]) for r in result]

    def translate(self, text, src, tgt):
        key = (text, src, tgt)
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
                return self._cache[key]
            opus = self._opus_for(src, tgt)
            sentences = split_sentences(text)
            parts = opus.translate(sentences) if opus else self._main_translate(sentences, src, tgt)
            output = _tidy(" ".join(p.strip() for p in parts))
            self._cache[key] = output
            if len(self._cache) > self._cache_size:
                self._cache.popitem(last=False)
            return output
