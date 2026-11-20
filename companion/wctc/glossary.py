"""Protects WoW jargon, item links and URLs from the translation model.

Protected chunks are replaced by placeholders (ZX1, ZX2...) that the translation model copies
verbatim, then restored after translation (optionally with a per-language form).
"""

import json
import logging
import re

from .paths import config_dir, resource_dir

log = logging.getLogger(__name__)

_PLACEHOLDER_RE = re.compile(r"Z\s?X\s?(\d+)", re.IGNORECASE)
_ALWAYS_PROTECT_RE = re.compile(
    r"\[(?:[^\[\]]|\[[^\[\]]{0,20}\]){1,100}\]"   # links: [Flask of Power], quests [[23+] Name]
    r"|https?://\S+|www\.\S+"          # URLs
    r"|\b\d+(?:[.,]\d+)?[kKm]\b"       # prices like 25k, 1.5m
    r"|\b\d+(?:[.,]\d+)?\s?(?:g|s|c|po|pa|pc)\b"   # gold, silver, copper: 310g, 50s, 2,5g (not grams)
    r"|(?<!\w)(?:[:;=8][-']?[()\[\]DPpOoc3|/\\*]+|<3|\^\^|[xX]D+|[oO]_[oO]|-_-)(?!\w)"   # :D :) ;p <3 ^^ xD
)
_WORD_CHARS = r"[\w+]"
_ARTICLE_RE = re.compile(r"^(?:(?:the|les|le|la|der|die|das|los|las|el|lo|il|gli|os|as|o|a|i)\s+|l['’]\s*)",
                         re.IGNORECASE)

USER_FILE_NAME = "glossary.json"
# Words often glued to a role or a jargon word: "needtank", "lookingheal", "plusheal".
GLUE_PREFIXES = {"need", "needs", "looking", "want", "more", "plus", "last", "one", "1", "2", "3"}
# French names put back without their article ("Cavernes des lamentations", "Mortemines"): the
# model writes "à" / "de" before them as before a city ("aller à ZX1"), which a plural name
# turns into "aux" / "des". Plural: a first word ending in "es" ("Tanaris", "Darnassus" are not).
_FR_PLURAL_NAME_RE = re.compile(r"^[A-ZÀ-Ýa-zà-ÿ][\w'-]{2,}(?:es|eurs|ants|ents)\b")


def _fr_plural_names(text, values):
    for value in {v for v in values if v and _FR_PLURAL_NAME_RE.match(v)}:
        pattern = re.compile(r"(?<![\w'’])([àÀ]|[Dd]e) " + re.escape(value))
        text = pattern.sub(lambda m: ("aux " if m.group(1) in "àÀ" else "des ") + value, text)
        text = re.sub(r"(?<![\w'’])([Aa]u|[Dd]u|à la|de la) " + re.escape(value),
                      lambda m: ("aux " if m.group(1).lower() in ("au", "à la") else "des ") + value, text)
        # "l'armes de pugilat", "le armes": a plural noun takes "les" / "des".
        text = re.sub(r"(?<![\w'’])([Ll]['’] ?|[Ll][ea] |[Uu]ne? )" + re.escape(value),
                      lambda m: ("des " if m.group(1).lower().startswith("u") else "les ") + value, text)
    return text


# Words a place name often comes before in English chat ("BFD prequests", "WC quests").
_PLACE_HEADS = {"prequests", "attunement", "quests", "quest", "key", "boss", "bosses"}
_PLACE_HEAD_RE = re.compile(r"\b(ZX\d+) (ZX\d+|" + "|".join(sorted(_PLACE_HEADS, key=len, reverse=True)) + r")\b",
                            re.IGNORECASE)


def _fr_city_names(text, values):
    """"dans le Fossoyeuse", "chez Orgrimmar": a name the game writes without an article is a
    place one goes "à"."""
    for value in {v for v in values if v and not _ARTICLE_RE.match(v) and not _FR_PLURAL_NAME_RE.match(v)}:
        text = re.sub(r"(?<![\w'’])(?:dans|chez) (?:le |la |l['’])?" + re.escape(value) + r"\b", "à " + value, text)
    return text


_GLUED_LINK_RE = re.compile(r"(?<=\w)(?=\[)|(?<=\])(?=[\w\[])")


_LINK_RE = re.compile(r"\[(?:[^\[\]]|\[[^\[\]]{0,20}\])*\]")


def _outside_links(text, change):
    """Applies change() to the text between item links only: "[Iron Lockbox]" stays the game's
    name, its words are not shorthand to write out."""
    parts, last = [], 0
    for link in _LINK_RE.finditer(text):
        parts += [change(text[last:link.start()]), link.group(0)]
        last = link.end()
    parts.append(change(text[last:]))
    return "".join(parts)


def _unglue_links(text):
    """"WTB[Fiery War Axe]30g": a space each side of the link, or "WTB" is no word of its own."""
    return _GLUED_LINK_RE.sub(" ", text)


_AMOUNT_RE = re.compile(r"(?<!\w)[x×]?\d\w*", re.IGNORECASE)
_GLUED_RE = re.compile(r"(?<![\w+])[A-Za-z0-9]{4,20}(?![\w+])")


USER_TEMPLATE = {
    "_info": "Vos ajouts au glossaire intégré / your additions to the built-in glossary. "
             "keep: mots jamais traduits / never translated. "
             "concepts: {\"en\": ..., \"fr\": ..., \"de\": ..., \"es\": ..., \"it\": ..., \"pt\": ..., \"ru\": ..., "
             "\"forms\": [autres formes / other forms]}: rendu dans la langue du lecteur / shown in the reader's language. "
             "expand: abréviation -> texte anglais à traduire / abbreviation -> English text to translate.",
    "keep": [],
    "concepts": [],
    "expand": {},
}
# Built-in entries of the versions that copied the whole glossary into the player's folder.
_OLD_DEFAULT_MARKERS = ({"tank", "heal", "dps", "wts", "spriest"}, {"dungeon", "healer", "guild"})


def _is_old_default_copy(path):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    if "_info" in data:
        return False
    keep = {k.lower() for k in data.get("keep", [])}
    concepts = {c.get("en") for c in data.get("concepts", [])}
    if not (_OLD_DEFAULT_MARKERS[0] <= keep and _OLD_DEFAULT_MARKERS[1] <= concepts):
        return False
    backup = path.with_name("glossary.old.json")   # kept in case the player had added words
    try:
        path.replace(backup)
    except OSError:
        return False
    log.info("Old copy of the built-in glossary moved to %s", backup)
    return True


# A message made of one shorthand, with only punctuation or a smiley around it.
_WHOLE_RE = re.compile(r"^(\W*)([^\W\d_]+(?: [^\W\d_]+)?)(\W*)$")


def _trie_pattern(terms):
    """One regular expression for thousands of terms (place names...), as a letter tree: a plain
    "a|b|c..." alternation would try every term at every position of every message. Longest
    matches win, like the sorted alternation it replaces."""
    trie = {}
    for term in terms:
        node = trie
        for char in term.lower():
            node = node.setdefault(char, {})
        node[""] = True

    def build(node):
        end = node.get("", False)
        branches = [re.escape(char) + build(child) for char, child in sorted(node.items()) if char]
        if not branches:
            return ""
        body = branches[0] if len(branches) == 1 else "(?:" + "|".join(branches) + ")"
        return f"(?:{body})?" if end else body

    return build(trie)


class Glossary:
    def __init__(self):
        self.keep = set()
        self.map = {}
        self.expand = {}
        self._term_re = None
        self._expand_re = None
        self.reload()

    @staticmethod
    def user_file():
        """The player's own additions, merged over the built-in glossary (which is updated with
        the companion). Older versions copied the whole built-in glossary there: such an
        untouched copy is replaced by an empty template, since it would bring back old entries."""
        path = config_dir() / USER_FILE_NAME
        if not path.exists() or _is_old_default_copy(path):
            path.write_text(json.dumps(USER_TEMPLATE, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def reload(self):
        """Loads every glossary again. Returns (number of the player's own entries, error message
        of his file or None), shown in the Options window."""
        self.keep, self.map, self.expand, self.free, self.whole = set(), {}, {}, set(), {}
        self._chat_concepts = set()       # ids of the glossary's own concepts (not official names)
        user_entries, user_error = 0, None
        # Official place names first (zones, dungeons, raids), then the glossary, then the player's
        # additions: a later entry wins when the same word is in both.
        data_dir = resource_dir() / "data"
        # Official names first (places, then items, races, reputations), the glossary's words and
        # slang over them, the player's own file last.
        for path in (data_dir / "places.json", data_dir / "names.json", data_dir / "glossary.json", self.user_file()):
            try:
                with open(path, encoding="utf-8") as fh:
                    data = json.load(fh)
            except (OSError, ValueError) as error:
                log.exception("Cannot read glossary %s", path)
                if path == self.user_file():
                    user_error = str(error)
                continue
            if path == self.user_file():
                user_entries = sum(len(data.get(k, [])) for k in ("keep", "map", "expand", "concepts"))
            self.keep.update(t.lower() for t in data.get("keep", []))
            # Ordinary phrases containing a glossary word, left whole to the model, which
            # translates them better: "fishing rod" -> "canne à pêche", not "poteau pêche".
            self.free.update(t.lower() for t in data.get("free", []))
            # Shorthand with this meaning only when it is the whole message: "gm" (good morning)
            # alone, but "ask a GM" stays Game Master.
            self.whole.update({k.lower(): v for k, v in data.get("whole", {}).items()})
            self.map.update({k.lower(): v for k, v in data.get("map", {}).items()})
            # English chat abbreviations written out, so the model can translate them:
            # "LF people" -> "looking for people" -> "cherche des gens".
            self.expand.update({k.lower(): v for k, v in data.get("expand", {}).items()})
            # A concept lists the word in every language: any form is restored in the target language.
            chat = path.name == "glossary.json" or path == self.user_file()
            for concept in data.get("concepts", []):
                forms = {k: v for k, v in concept.items() if k != "forms" and isinstance(v, str)}
                if chat:
                    self._chat_concepts.add(id(forms))
                for word in list(forms.values()) + concept.get("forms", []):
                    # One-letter gold marks ("o", "з") are also everyday words ("Forgiardente o
                    # Sepulcra", Ukrainian "з"): only "g" is recognised alone.
                    if len(word) == 1 and word.lower() != "g":
                        continue
                    self.map[word.lower()] = forms
        if self.expand:
            self._expand_re = re.compile(rf"(?<!{_WORD_CHARS})(?:{_trie_pattern(self.expand)})(?!{_WORD_CHARS})",
                                         re.IGNORECASE)
        else:
            self._expand_re = None
        # Two-letter English shorthand ("u", "ur", "w/") is a word of other languages (Czech "u"):
        # only written out in English lines.
        longer = {k: v for k, v in self.expand.items() if len(k) > 2}
        self._expand_long_re = (re.compile(rf"(?<!{_WORD_CHARS})(?:{_trie_pattern(longer)})(?!{_WORD_CHARS})",
                                           re.IGNORECASE) if longer else None)
        terms = self.keep | set(self.map) | self.free
        if terms:
            self._term_re = re.compile(rf"(?<!{_WORD_CHARS})(?:{_trie_pattern(terms)})(?!{_WORD_CHARS})", re.IGNORECASE)
        else:
            self._term_re = None
        return user_entries, user_error

    def split_glued(self, text):
        """Chat words typed without their space ("needtank", "lfheal", "wtsore") are unknown to
        the model, which then guesses ("needtank" -> "Résultat"): split them when both halves
        are known words."""
        def split(match):
            word = match.group(0)
            lower = word.lower()
            if lower in self.keep or lower in self.map or lower in self.expand:
                return word
            for cut in range(2, len(word) - 1):
                head, tail = lower[:cut], lower[cut:]
                known_head = head in self.keep or head in self.expand or head in GLUE_PREFIXES
                if known_head and len(tail) >= 3 and (tail in self.keep or tail in self.map):
                    return f"{word[:cut]} {word[cut:]}"
            return word
        return _GLUED_RE.sub(split, text)

    def _whole_message(self, text):
        """"gm", "GM !", "gm :)" -> "good morning" (the rest of the message kept)."""
        core = _WHOLE_RE.match(text)
        if core and core.group(2).lower() in self.whole:
            return core.group(1) + self.whole[core.group(2).lower()] + core.group(3)
        return text

    def protect(self, text, target=None, english=True):
        """Returns (masked_text, placeholders) where placeholders[i] is the original chunk.
        target: the reader's language; english: the line is (or may be) English, so that its
        shortest shorthand ("u", "ur") is written out."""
        text = self._whole_message(self.split_glued(_unglue_links(text)))
        expand_re = self._expand_re if english else self._expand_long_re
        if expand_re:
            text = _outside_links(text, lambda part: expand_re.sub(lambda m: self.expand[m.group(0).lower()], part))
        chunks = []

        def substitute(match):
            chunks.append(match.group(0))
            return f"ZX{len(chunks)}"

        def substitute_term(match):
            word = match.group(0)
            if word.lower() in self.free:
                return word
            forms = self.map.get(word.lower())
            if (target and target != "en" and isinstance(forms, dict) and id(forms) in self._chat_concepts
                    and not forms.get(target) and forms.get("en") and not forms["en"].isupper()):
                # A chat word with no form in the reader's language (Polish, Dutch...): its
                # English meaning goes to the model, which translates it, rather than English
                # in the middle of the line. Official names keep their English game name.
                return forms["en"].strip("()")
            return substitute(match)

        masked = _ALWAYS_PROTECT_RE.sub(substitute, text)
        if self._term_re:
            masked = self._term_re.sub(substitute_term, masked)
        return masked, chunks

    def detection_text(self, text):
        """Words the player typed himself, for language detection: expanded shorthand is left
        out, since its English full form ("LFM" -> "looking for more players") would make
        "LFM Tank pour Dalaran" look English. Expanded phrases of real words ("suche Gruppe",
        "sold out") stay as typed: they are the player's language."""
        text = self.split_glued(text)
        if self._whole_message(text) != text:
            return ""              # a greeting shorthand alone: its expansion decides
        if self._expand_re:
            text = self._expand_re.sub(self._typed_phrase, text)
        masked = _ALWAYS_PROTECT_RE.sub(" ZX0 ", text)
        if self._term_re:
            masked = self._term_re.sub(lambda m: m.group(0) if m.group(0).lower() in self.free else " ZX0 ", masked)
        masked = _AMOUNT_RE.sub(" ", masked)       # "x20", "5g": their letter is no word
        return self.residual_text(masked)

    def spelled_out(self, masked, chunks):
        """The masked line with each term written back as a name the model keeps ("ZX1 at work"
        -> "Wow Forever at work"): links as typed, concepts in English, other jargon with
        capitals. Last chance when the model drops a placeholder."""
        def name(match):
            chunk = chunks[int(match.group(1)) - 1]
            forms = self.map.get(chunk.lower())
            if isinstance(forms, dict) and forms.get("en"):
                return forms["en"]
            return chunk.title() if chunk.islower() else chunk
        return _PLACEHOLDER_RE.sub(name, masked)

    def place_first(self, masked, chunks):
        """English puts a place before the word it qualifies ("blackfathom prequests", "DM
        quests"); the model then keeps that order in French. Written "prequests of Blackfathom"
        before translation."""
        def is_place(index):
            forms = self.map.get(chunks[index - 1].lower())
            return isinstance(forms, dict) and id(forms) not in self._chat_concepts

        def head(match):
            place, word = match.group(1), match.group(2)
            if not is_place(int(place[2:])):
                return match.group(0)
            if word.startswith("ZX"):
                forms = self.map.get(chunks[int(word[2:]) - 1].lower())
                if not (isinstance(forms, dict) and forms.get("en", "").lower() in _PLACE_HEADS):
                    return match.group(0)
            return f"{word} of {place}"
        return _PLACE_HEAD_RE.sub(head, masked)

    def core_text(self, masked):
        """The player's own words of a masked line, amounts ("x20", "30g") left out: empty for
        "ZX1[ZX2]30g" (WTB [item] 30g), a line made only of game terms."""
        return self.residual_text(_AMOUNT_RE.sub(" ", masked))

    def expanded(self, text):
        """The line with its shorthand written out but nothing masked ("stop trolling pls" ->
        "stop trolling please"): last resort to tell the language of a line with few words."""
        text = self._whole_message(self.split_glued(text))
        if self._expand_re:
            text = self._expand_re.sub(lambda m: self.expand[m.group(0).lower()], text)
        return text

    def concept_count(self, chunks):
        """Protected chunks that are game terms with a translation (not links, names or
        numbers): words of the line too when judging if it is long enough to translate."""
        return sum(isinstance(self.map.get(chunk.lower()), dict) for chunk in chunks)

    def _typed_phrase(self, match):
        """Expanded phrase kept for detection only when made of ordinary words ("suche Gruppe",
        "sold out"), not around shorthand ("gm all", "your mats")."""
        words = match.group(0).lower().split()
        known = self.keep.union(self.expand)
        return match.group(0) if len(words) > 1 and not any(w in known for w in words) else " "

    def foreign_shorthand(self, chunks, target_lang):
        """True if a protected chunk is another language's own form of a concept ("mdr" for an
        English reader): such a line is worth converting even when there is nothing else to
        translate."""
        for chunk in chunks:
            forms = self.map.get(chunk.lower())
            if not isinstance(forms, dict):
                continue
            own = forms.get(target_lang)
            if own and own.lower() == chunk.lower():
                continue                       # already the reader's word
            if any(lang != target_lang and value.lower() == chunk.lower() for lang, value in forms.items()):
                return True                    # another language's word ("mdr" for an English reader)
            if own and target_lang != "en":
                return True                    # a common form ("morning", "thx") with the reader's own word
        return False

    def restore(self, translated, chunks, target_lang):
        """Puts protected chunks back. Returns None if the model lost a placeholder."""
        found = set()

        def substitute(match):
            index = int(match.group(1))
            if not 1 <= index <= len(chunks):
                return match.group(0)
            found.add(index)
            original = chunks[index - 1]
            forms = self.map.get(original.lower())
            if isinstance(forms, dict):
                # Languages without their own form (Polish...) get the English game term.
                value = forms.get(target_lang) or forms.get("en") or original
                # Place names: "Les Tarides" when the player wrote "the Barrens", "Tarides" when
                # he wrote "Barrens" (his sentence may have its own article: "das Brachland").
                if not _ARTICLE_RE.match(original):
                    value = _ARTICLE_RE.sub("", value, count=1) or value
                return value
            return original

        result = _PLACEHOLDER_RE.sub(substitute, translated)
        if len(found) != len(chunks):
            return None
        if target_lang == "fr":
            result = _fr_plural_names(result, [self._value(chunks[i - 1], "fr") for i in found])
            places = [self._value(chunks[i - 1], "fr") for i in found
                      if isinstance(self.map.get(chunks[i - 1].lower()), dict)
                      and id(self.map[chunks[i - 1].lower()]) not in self._chat_concepts]
            result = _fr_city_names(result, places)
        return result

    def _value(self, chunk, target_lang):
        forms = self.map.get(chunk.lower())
        return forms.get(target_lang) or "" if isinstance(forms, dict) else ""

    @staticmethod
    def residual_text(masked):
        """Text left once placeholders, digits and punctuation are removed."""
        stripped = _PLACEHOLDER_RE.sub(" ", masked)
        return re.sub(r"[\W\d_]+", " ", stripped).strip()
