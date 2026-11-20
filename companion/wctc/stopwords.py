"""Language of very short chat lines ("I have 5", "Got page 6?", "ich bin da") from their small
grammatical words, which statistical detection cannot judge on two or three words."""

import re

_WORDS = {
    "en": """i i'm im you have has got the is are was were can anyone want need any my your what where how who
             it this that do does don't dont yes yeah get will would with for and of to if just know they them
             some there here thanks please sorry guys he she we our anybody someone lets let's go why how yes nope nah not or from with into tonight today tomorrow later soon""",
    "fr": """je j'ai tu elle nous vous est c'est les des une pour qui quoi avec pas oui moi toi mais et ou dans
             sur quelqu'un bonjour salut merci ça ca suis peux veux faut y'a aussi très tout quelqu'un""",
    "de": """ich du wir ihr ist nicht und der das hat habe wer mit ja nein auch noch kann bin sind für ein eine
             gibt jemand bitte danke mir dich mich""",
    "es": """yo tengo quien quién el los las por hay alguien estoy pero como cómo gracias también muy hola busco grupo para necesito vamos""",
    "it": """io sono chi che gli per ho qualcuno ciao grazie anche molto sei siamo c'è perché dove""",
    "pt": """eu você voce tenho quem os não nao alguém alguem obrigado também muito tá oi""",
    "pl": """ja ty mam nie jest się czy na do już idę ktoś proszę dzięki może jak co jestem szukam gildii grupy potrzebuję""",
    "nl": """ik het een niet wel ben heb iemand wie wat dank bedankt jij jullie""",
    "cs": """jsem jsi jsme jste není neni proč proc když kdyz taky teď ted díky diky""",
    "sk": """som sme ste este ešte preco prečo ked keď len aj teraz ďakujem dakujem""",
}
_TOKEN_RE = re.compile(r"[\w']+", re.UNICODE)


def _distinct_sets():
    sets = {lang: set(words.split()) for lang, words in _WORDS.items()}
    shared = {w for lang, words in sets.items() for w in words
              if any(w in other for o, other in sets.items() if o != lang)}
    return {lang: words - shared for lang, words in sets.items()}   # only words of one language


STOPWORDS = _distinct_sets()


def guess(text):
    """The language its small words clearly point to, else None."""
    tokens = [t.lower() for t in _TOKEN_RE.findall(text)]
    if not tokens:
        return None
    counts = {lang: sum(t in words for t in tokens) for lang, words in STOPWORDS.items()}
    ranked = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    (best, first), (_, second) = ranked[0], ranked[1]
    if first >= 2 and first > 2 * second:
        return best
    if first == 1 and second == 0 and len(tokens) <= 4:
        return best
    return None
