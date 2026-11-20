"""Source language detection restricted to the supported languages (more reliable on short chat lines).

py3langid is used instead of heavier detectors: same accuracy on short chat lines once
restricted to our languages, for ~4 MB instead of ~300 MB in the executable.
"""

import re

from py3langid.langid import MODEL_FILE, LanguageIdentifier

from . import EXTRA_LANGUAGES, LANGUAGES, WOW_LANGUAGES, stopwords

_CYRILLIC_RE = re.compile(r"[Ѐ-ӿ]")
_UKRAINIAN_RE = re.compile(r"[іїєґІЇЄҐ]")
_BULGARIAN_RE = re.compile(r"[ъЪ]")   # common in Bulgarian, rare in Russian
# Polish, Czech, Turkish... (unless it is the player's language) are only kept when clearly recognised: on a few words, the
# extra languages are often wrongly guessed for English or German ("in", "kan", "die"...).
EXTRA_MIN_CONFIDENCE = 0.65
# Close languages share their score for that check (a Czech line is often half "Slovak").
FAMILIES = ({"cs", "sk"}, {"da", "no", "sv"})


class LanguageDetector:
    def __init__(self, min_confidence=0.5, hint_margin=0.25):
        self.min_confidence = min_confidence
        self.hint_margin = hint_margin
        self._identifier = LanguageIdentifier.from_pickled_model(MODEL_FILE, norm_probs=True) \
            if hasattr(LanguageIdentifier, "from_pickled_model") \
            else LanguageIdentifier.from_model_file(MODEL_FILE, norm_probs=True)
        self._identifier.set_languages(list(LANGUAGES))

    def detect(self, text, hint=None):
        """Returns (code, confidence) or (None, confidence) when unsure.

        `hint` is the player's own language: when it is close behind the best guess (short lines
        like "ok merci"), it wins, so messages already readable are left untouched.
        """
        # Short lines: their small grammatical words ("I have 5", "ich bin da") are more reliable
        # than statistics on two or three words.
        if len(text.split()) <= 6:
            guessed = stopwords.guess(text)
            if guessed:
                return guessed, 0.99
        if _CYRILLIC_RE.search(text):
            if _UKRAINIAN_RE.search(text):
                return "uk", 1.0
            if _BULGARIAN_RE.search(text) and not re.search(r"[ыэЫЭ]", text):
                return "bg", 1.0
            return "ru", 1.0
        ranking = [(c, p) for c, p in self._identifier.rank(text) if c not in ("uk", "bg")]
        if not ranking:
            return None, 0.0
        code, confidence = ranking[0]
        if confidence < EXTRA_MIN_CONFIDENCE:
            # Statistics unsure (no accents typed: "len sa netes este som to nekupil"): small
            # grammatical words decide when they clearly point to one language.
            guessed = stopwords.guess(text)
            if guessed:
                return guessed, 0.9
        family = next((f for f in FAMILIES if code in f), {code})
        family_confidence = sum(p for c, p in ranking if c in family)
        if code in EXTRA_LANGUAGES and code != hint and family_confidence < EXTRA_MIN_CONFIDENCE:
            # Not sure enough: best of the main languages (or the player's own) instead.
            ranking = [(c, p) for c, p in ranking if c in WOW_LANGUAGES or c == hint]
            code, confidence = ranking[0] if ranking else (None, 0.0)
        if hint and code != hint:
            hint_score = next((p for c, p in ranking if c == hint), 0.0)
            if confidence - hint_score < self.hint_margin:
                return hint, hint_score
        if confidence < self.min_confidence:
            return None, confidence
        return code, confidence
