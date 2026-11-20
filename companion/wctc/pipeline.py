"""Chat line -> parsed -> language detection -> translation -> display queue."""

import logging
import re
import queue
import threading
import time
from dataclasses import dataclass

from . import stopwords
from .chatparser import ChatLine

log = logging.getLogger(__name__)

MIN_WORDS = 2                  # words of 3+ letters needed to translate a line...
SHORT_LINE_CONFIDENCE = 0.95   # ...unless the language is detected with this confidence
EXPANDED_LINE_CONFIDENCE = 0.5  # ...or, once its known shorthand is written out, this one


# Sentences of a masked line, a sentence made only of protected terms ("ZX2", "ZX1 !"), and the
# protected terms ending a line ("... ZX1", "...? ZX2 ZX3").
_SENTENCE_RE = re.compile(r"(?<=[.!?…])\s+(?=\S)")
_ONLY_TERMS_RE = re.compile(r"^[\s\W]*(?:ZX\d+[\s\W]*)+$")
_TRAILING_TERMS_RE = re.compile(r"(?:[\s,.!?…]*\bZX\d+)+[\s.!?…:()\-]*$")

_SHOUTED_RE = re.compile(r"\b[A-ZÀ-ÖØ-ÞА-ЯЁ]{3,}\b")


# Below this, the language found on the player's few own words is a guess (often just the
# reader's language as hint): their small words or the whole line decide instead.
UNSURE_CONFIDENCE = 0.3


def _soften_caps(text):
    """Words in capitals ("NON toxic", "WTS CHEAP") are rarer in the model's training text and
    get odd translations: lower-cased (glossary terms are already placeholders)."""
    if _mocking_case(text):
        return text.lower()
    return _SHOUTED_RE.sub(lambda m: m.group(0).lower(), text)


_MIXED_WORD_RE = re.compile(r"\b\w*[a-zà-ÿ][A-ZÀ-Þ]\w*\b")


def _mocking_case(text):
    """"GaMe Is EaSY": mocking alternate capitals, which the model reads as names and drops."""
    words = re.findall(r"[^\W\d_]{2,}", text)
    return len(words) >= 3 and len(_MIXED_WORD_RE.findall(text)) * 2 >= len(words)


translation_log = logging.getLogger("wctc.translations")


def _note(trace, **values):
    if trace is not None:
        trace.update(values)


def _log_trace(line, result, trace):
    """One block per chat line in the companion's log (Options > General > Translation log)."""
    parts = [f"[{line.kind}] {line.speaker or '?'}: {line.text!r}"]
    if "source" in trace:
        confidence = trace.get("confidence") or 0
        parts.append(f"  language: {trace['source'] or 'unknown'} ({confidence:.2f}) -> {trace.get('target')}, "
                     f"detected on {trace.get('detected_on', '')!r}")
    if "model_input" in trace:
        parts.append(f"  sent to the model: {trace['model_input']!r}")
        parts.append(f"  model output: {trace['model_output']!r}")
    if "retry" in trace:
        parts.append(f"  {trace['retry']}")
    parts.append(f"  shown: {result.text!r} ({trace.get('reason', '')})")
    translation_log.info("\n".join(parts))


# French elision around glossary terms put back after the model: "de enchanteur" -> "d'enchanteur",
# "le ingénieur" -> "l'ingénieur" (the model only saw a placeholder there).
_FR_ELIDABLE = {"de": "d'", "le": "l'", "la": "l'", "que": "qu'", "je": "j'", "ne": "n'", "me": "m'", "te": "t'", "se": "s'"}


def _fr_elide(text):
    def repl(m):
        word = m.group(0).rstrip()
        out = _FR_ELIDABLE.get(word.lower())
        if not out:
            return m.group(0)
        return (out[0].upper() + out[1:]) if word[0].isupper() else out
    # Not after a hyphen: "puis-je acheter" stays as it is.
    return re.sub(r"(?<![\w'’-])(?:[Dd]e|[Ll][ea]|[Qq]ue|[JjNnMmTtSs]e) (?=[aeiouyàâéèêëîïôûœAEIOUYÀÂÉÈÊËÎÏÔÛŒ])", repl, text)


_DOUBLED_RE = re.compile(r"^(\w+), (?i:\1)(\W*)$")
# Feminine French nouns of the glossary the model gives a masculine article ("un invitation",
# "le guilde"): it never saw the word, only a placeholder.
_FR_FEMININE = "guilde|invitation|quête|instance|zone|faction|réputation|profession|enchère|couche"
_FR_GENDER_RE = re.compile(r"(?<![\w'’])(un|Un|le|Le|du|Du|au|Au) (?=(?:" + _FR_FEMININE + r")\b)")
_FR_FEMININE_ARTICLE = {"un": "une", "le": "la", "du": "de la", "au": "à la"}


def _fr_gender(text):
    def article(match):
        word = match.group(1)
        new = _FR_FEMININE_ARTICLE[word.lower()]
        return (new[0].upper() + new[1:] if word[0].isupper() else new) + " "
    return _FR_GENDER_RE.sub(article, text)


def _finish(text, original, target):
    """Last touches: French elision, a capital first letter when the player wrote one, no full
    stop the player did not write, no "+" or comma before a bracketed glossary term."""
    if target == "fr":
        text = _fr_elide(_fr_gender(text))
    text = re.sub(r"\s*[+,]\s+(?=\()", " ", text)
    if text.startswith(("- ", "– ")) and not original.lstrip().startswith(("-", "–")):
        text = text[2:]                       # dialogue dash the model adds to short lines
    duplicate = _DOUBLED_RE.match(text)
    if duplicate and len(original.split()) == 1:
        text = duplicate.group(1) + duplicate.group(2)   # "Yes" -> "Oui, oui" -> "Oui"
    if text.endswith(".") and not text.endswith("...") and not original.rstrip().endswith((".", "…")):
        text = text[:-1]
    if text and original[:1].isupper() and text[0].islower():
        text = text[0].upper() + text[1:]
    return text


def _normalise(text):
    return " ".join(text.lower().split()).strip(" .!?")


@dataclass
class DisplayLine:
    line: ChatLine
    text: str                 # what to show (translation or original)
    translated: bool
    source_lang: str = ""


_RELOAD = object()
SLOW_SAMPLE = 20          # lines measured before judging the speed
SLOW_AVERAGE_S = 1.5      # average time per line above which the PC is too slow for the model


class TranslationPipeline(threading.Thread):
    def __init__(self, engine_factory, detector_factory, glossary, get_target_lang, on_display, on_status):
        super().__init__(name="TranslationPipeline", daemon=True)
        self._engine_factory = engine_factory
        self._detector_factory = detector_factory
        self._glossary = glossary
        self._get_target_lang = get_target_lang
        self._on_display = on_display     # callable(DisplayLine)
        self._on_status = on_status       # callable(str key, **kwargs)
        self._queue = queue.Queue(maxsize=2000)
        self._stop = threading.Event()
        self.engine = None
        self.detector = None
        self.on_slow = None               # callable(average seconds): translations lag
        self.trace_enabled = lambda: False  # Options > General > Translation log
        self._timings = []

    def submit(self, line: ChatLine):
        try:
            self._queue.put_nowait(line)
        except queue.Full:
            log.warning("Translation queue full, dropping a line")

    def stop(self):
        self._stop.set()
        self._queue.put(None)

    def run(self):
        self._on_status("loading")
        try:
            self.detector = self._detector_factory()
            self.engine = self._engine_factory()
        except Exception:
            log.exception("Engine failed to load")
            self._on_status("engine_error")
            return
        self._on_status("ready")
        while not self._stop.is_set():
            line = self._queue.get()
            if line is None:
                break
            if line is _RELOAD:
                self._reload_engine()
                continue
            started = time.monotonic()
            try:
                self._on_display(self.process(line))
            except Exception:
                log.exception("Failed to process line: %r", line)
            self._timings.append(time.monotonic() - started)
            if len(self._timings) >= SLOW_SAMPLE and self.on_slow:
                average = sum(self._timings) / len(self._timings)
                self._timings.clear()
                if average > SLOW_AVERAGE_S:
                    log.warning("Translations take %.2f s on average", average)
                    self.on_slow(average)

    def reload_engine(self):
        """Loads the engine again from the factory (another model chosen), between two lines."""
        self._queue.put(_RELOAD)

    def _reload_engine(self):
        self._on_status("loading")
        try:
            engine = self._engine_factory()
        except Exception:
            log.exception("Engine failed to load, keeping the previous one")
            self._on_status("ready")
            return
        self.engine = engine
        self._timings.clear()
        self._on_status("ready")

    def process(self, line: ChatLine):
        trace = {} if self.trace_enabled() else None
        result = self._process(line, trace)
        if trace is not None:
            _log_trace(line, result, trace)
        return result

    def _translate_segments(self, text, source, target):
        """Lists cut by "|" ("Chest:+8 Sta|Boots:+4 Agi") are translated piece by piece: the
        model reads a bar as nothing and runs the pieces into each other. A sentence made only
        of glossary terms ("Tips welcome." -> "ZX6.") is kept as is: the model gives it an
        article or drops it."""
        if "|" not in text:
            sentences = [s for s in _SENTENCE_RE.split(text) if s.strip()]
            if len(sentences) > 1 and any(_ONLY_TERMS_RE.match(s) for s in sentences):
                return " ".join(s if _ONLY_TERMS_RE.match(s) else self.engine.translate(s, source, target)
                                for s in sentences)
            return self.engine.translate(text, source, target)
        return "|".join(self.engine.translate(part, source, target) if self._glossary.core_text(part) else part
                        for part in text.split("|"))

    def _sure_once_expanded(self, text, source, target):
        """A short line whose shorthand, written out, leaves no doubt ("gz on 60!" ->
        "congratulations on 60!")."""
        expanded = self._glossary.expanded(text)
        if expanded == text:
            return False
        found, confidence = self.detector.detect(expanded, hint=target)
        return found == source and confidence >= EXPANDED_LINE_CONFIDENCE

    def _retry_lost(self, masked, chunks, source, target):
        """The model drops a sentence or a trailing term it cannot read ("qualcuno per ZX1?
        ZX2", "need a resurrection ZX1"): translate each sentence alone, then the line without
        its trailing terms, which are put back after it. None if the term is still lost."""
        sentences = [s for s in _SENTENCE_RE.split(masked) if s.strip()]
        if len(sentences) > 1:
            parts = [s if _ONLY_TERMS_RE.match(s) else self.engine.translate(s, source, target)
                     for s in sentences]
            restored = self._glossary.restore(" ".join(parts), chunks, target)
            if restored is not None:
                return restored
        tail = _TRAILING_TERMS_RE.search(masked)
        if tail and tail.start() > 0 and self._glossary.residual_text(masked[:tail.start()]):
            head = self.engine.translate(masked[:tail.start()], source, target)
            return self._glossary.restore(head + tail.group(0), chunks, target)
        return None

    def _process(self, line: ChatLine, trace):
        """`trace` (dict or None) receives the steps of the decision, for the translation log."""
        if not line.translatable:
            _note(trace, reason="not translated (channel or message type)")
            return DisplayLine(line, line.text, False)

        target = self._get_target_lang()
        masked, chunks = self._glossary.protect(line.text, target)
        residual = self._glossary.residual_text(masked)
        _note(trace, target=target, masked=masked)
        if len(self._glossary.core_text(masked)) < 2:
            # Only jargon, links, numbers or emotes: nothing to translate, but another
            # language's shorthand ("mdr", "jaja", "спс") still gets the reader's own form.
            if self._glossary.foreign_shorthand(chunks, target):
                restored = self._glossary.restore(masked, chunks, target)
                if restored:
                    restored = _finish(restored, line.text, target)
                if restored and _normalise(restored) != _normalise(line.text):
                    _note(trace, reason="shorthand put in the reader's language")
                    return DisplayLine(line, restored, True, "")
            _note(trace, reason="nothing to translate (jargon, links, numbers or emotes only)")
            return DisplayLine(line, line.text, False)

        # Detected on the player's own words; the expanded shorthand only when there is nothing
        # else ("LFM tank SFK").
        own_words = self._glossary.detection_text(line.text)
        source, confidence = self.detector.detect(own_words or residual, hint=target)
        if own_words and (source is None or confidence < UNSURE_CONFIDENCE):
            # Too few words of his own to tell: their small words decide ("pour" -> French, kept
            # as typed); without any, the whole line with its shorthand written out does.
            expanded = self._glossary.expanded(line.text)
            guessed = stopwords.guess(own_words) or stopwords.guess(expanded)
            if guessed:
                source, confidence = guessed, 0.9
            else:
                source, confidence = self.detector.detect(expanded, hint=target)
        _note(trace, detected_on=own_words or residual, source=source, confidence=confidence)
        if source is None or source == target:
            _note(trace, reason="already in the reader's language" if source else "language not recognised")
            return DisplayLine(line, line.text, False, source or "")
        # "Le ZIG", "et zob", "zug zug"...: too short to know the language, leave as is.
        real_words = [w for w in residual.split() if len(w) >= 3]
        if (len(real_words) + self._glossary.concept_count(chunks) < MIN_WORDS
                and confidence < SHORT_LINE_CONFIDENCE
                and not self._sure_once_expanded(line.text, source, target)):
            _note(trace, reason="too short to be sure of the language")
            return DisplayLine(line, line.text, False, "")

        if source != "en":
            # Not English: its two-letter words are not English shorthand ("u" in Czech).
            masked, chunks = self._glossary.protect(line.text, target, english=False)
        if source == "en":
            masked = self._glossary.place_first(masked, chunks)
        model_input = _soften_caps(masked).replace("—", " - ").replace("–", " - ")
        model_input = re.sub(r"[ \t]{2,}", " ", model_input)   # "310g!  60g": a double space makes it ramble
        translated = self._translate_segments(model_input, source, target)
        restored = self._glossary.restore(translated, chunks, target)
        _note(trace, model_input=model_input, model_output=translated)
        if restored is None:
            restored = self._retry_lost(model_input, chunks, source, target)
            if restored is not None:
                _note(trace, retry="a protected term was lost: translated again piece by piece")
        if restored is None:
            log.debug("Placeholder lost, retrying with the terms spelled out: %r", line.text)
            _note(trace, retry="a protected term was lost: translated again with the terms written as names")
            restored = self.engine.translate(self._glossary.spelled_out(model_input, chunks), source, target)
        restored = _finish(restored, line.text, target)
        if _normalise(restored) == _normalise(line.text):
            _note(trace, reason="translation identical to the original")
            return DisplayLine(line, line.text, False, source)
        _note(trace, reason="translated")
        return DisplayLine(line, restored, True, source)
