"""Builds data/places.json: official zone, dungeon and raid names of WoW Forever in every client
language, from the game's own tables (AreaTable and Map DB2, exported by wago.tools).

Usage (developer machine, when Blizzard adds or renames places):
    python build/build_places.py [build]       # default: latest WoW Forever build known below

Languages without a WoW client (Polish, Dutch...) have no official names: their players use the
English ones, which the glossary gives them.
"""

import csv
import io
import json
import re
import sys
import urllib.request
from collections import Counter
from pathlib import Path

BUILD = "1.60.1.70938"          # WoW Forever (product wowf)
URL = "https://wago.tools/db2/{table}/csv?build={build}&locale={locale}"
LOCALES = {"en": "enUS", "fr": "frFR", "de": "deDE", "es": "esES", "it": "itIT", "pt": "ptBR", "ru": "ruRU"}
EXTRA_FORMS = {"es": "esMX"}    # Latin American Spanish names also recognised
# Names players also know from other versions of the game: the German client of Classic kept the
# English names ("Ironforge"), the later clients translated them ("Eisenschmiede"); Italian has a
# client there only. Recognised in chat, but the reader still gets the WoW Forever name.
ALIAS_BUILDS = {"retail": "12.1.5.70783", "mists classic": "5.5.4.70631"}
ALIAS_LOCALES = {**LOCALES, "es_x": "esMX"}
# Nicknames players use for a place (not in the game tables).
NICKNAMES = {
    "Ragefire Chasm": ["Ragefire", "Ragefeu", "Rage feu", "Rage fire"],
    "Wailing Caverns": ["WC", "Lam", "Lams"],
    "Orgrimmar": ["Org", "OG", "Ogri", "Orgri", "Orgrim"],
    "Undercity": ["UC"],
    "Thunder Bluff": ["TB"],
    "Warsong Gulch": ["WSG"],
}
OUTPUT = Path(__file__).resolve().parent.parent / "data" / "places.json"

JUNK_RE = re.compile(r"unused|prototype|\*|test|delete|dnd|\[|<|programmer|designer|gm island|^zz|copy|\bph\b|\bdev\b|\btmp\b|\bnyi\b",
                     re.I)
# Place names that are also everyday words: translated as words, not as places.
COMMON_WORDS = {"blacksmith", "camp", "city", "crafting", "farm", "lighthouse", "mine", "mines", "moonwell", "nine",
                "prison", "ruins", "stables", "waterworks", "brill", "outland",
                # names of other versions that are everyday words in their language
                "cimetière", "cimitero", "rayons", "réserve", "réservoir", "santuario", "segheria", "sanctum",
                "l’arène", "arène", "l’anneau", "anneau", "l’avancée", "avancée", "springflut"}
# Zones are often named by their first word ("stonetalon", "silverpine"): added when that word is
# distinctive enough (not an adjective or a word shared by several zones).
FIRST_WORD_STOPLIST = {"thousand", "burning", "eastern", "western", "northern", "southern", "searing", "swamp", "blasted",
                       "thunder", "ruins", "isle", "island", "mount", "mountains", "valley", "forest", "lake", "great",
                       "black", "blackrock", "molten", "shadow", "scarlet", "sunken", "dire", "wailing", "ragefire",
                       "razorfen", "caverns", "temple", "crystal", "storm", "demon", "starfall", "nightmare", "excavation",
                       "manor", "drowned", "alcaz", "deadwind", "emerald", "onyxia's", "zul'gurub", "stormwind", "city",
                       "battle", "shark-infested", "half-pint", "champions'"}
ARTICLES_RE = re.compile(r"^(?:(?:the|les|le|la|der|die|das|los|las|el|lo|il|gli|os|as|o|i)\s+|l['’]\s*)", re.I)
PARENTHESES_RE = re.compile(r"\s*\([^)]*\)\s*$")


def _same_place(name, other):
    """Two English names of one identifier still name the same place ("The Barrens" and
    "Northern Barrens"), not a reused one ("Westfall" and "Utgarde Keep")."""
    words = lambda text: {w for w in re.findall(r"[a-z']{4,}", text.lower())}
    return bool(words(name) & words(other))


def fetch(table, locale, build):
    url = URL.format(table=table, build=build, locale=locale)
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "WoWChatTranslator"}), timeout=60) as r:
        return {row["ID"]: row for row in csv.DictReader(io.StringIO(r.read().decode("utf-8")))}


def main():
    build = sys.argv[1] if len(sys.argv) > 1 else BUILD
    names = {}   # ID key -> {lang: name}
    for table, column, keep in (("AreaTable", "AreaName_lang", lambda r: True),
                                ("Map", "MapName_lang", lambda r: r["InstanceType"] in ("1", "2", "3", "4"))):
        if table == "AreaTable":
            zones = set()
        tables = {lang: fetch(table, loc, build) for lang, loc in {**LOCALES, **{f"{k}_x": v for k, v in EXTRA_FORMS.items()}}.items()}
        for ident, row in tables["en"].items():
            if not keep(row):
                continue
            entry = {lang: (rows.get(ident) or {}).get(column, "").strip() for lang, rows in tables.items()}
            names[f"{table}:{ident}"] = entry
            if table == "AreaTable" and row.get("ParentAreaID") == "0":
                zones.add(entry["en"].lower())

    aliases = {}   # ID key -> names of the same place in the other versions
    for version, alias_build in ALIAS_BUILDS.items():
        for table, column in (("AreaTable", "AreaName_lang"), ("Map", "MapName_lang")):
            try:
                tables = {lang: fetch(table, loc, alias_build) for lang, loc in ALIAS_LOCALES.items()}
            except OSError as exc:
                print(f"{version} {table}: skipped ({exc})")
                continue
            for lang, rows in tables.items():
                for ident, row in rows.items():
                    key = f"{table}:{ident}"
                    if key not in names or not _same_place(names[key]["en"], tables["en"].get(ident, {}).get(column, "")):
                        continue      # identifier reused for another place in that version
                    value = PARENTHESES_RE.sub("", row.get(column, "").strip())
                    if key in names and value and not JUNK_RE.search(value) and len(value) >= 4 \
                            and value.lower() not in COMMON_WORDS:
                        aliases.setdefault(key, set()).add(value)

    concepts = {}
    for key_id, entry in names.items():
        english = entry["en"]
        if not english or JUNK_RE.search(english) or english.lower() in COMMON_WORDS or len(english) < 4:
            continue
        concept = concepts.setdefault(english.lower(), {"votes": {lang: Counter() for lang in LOCALES}, "forms": set()})
        for lang in LOCALES:
            if entry.get(lang) and not JUNK_RE.search(entry[lang]):
                concept["votes"][lang][entry[lang]] += 1
        for lang, value in entry.items():
            if value and not JUNK_RE.search(value):
                concept["forms"].add(value)
        concept["aliases"] = concept.get("aliases", set()) | aliases.get(key_id, set())

    # A name of another version that is (or names) a different place here stays out: retail
    # renamed and reused some areas.
    taken = {v.lower() for entry in names.values() for v in entry.values() if v}
    for key, concept in concepts.items():
        own = {v.lower() for votes in concept["votes"].values() for v in votes}
        for alias in concept.pop("aliases", set()):
            if alias.lower() in own or alias.lower() not in taken:
                concept["forms"].add(alias)

    for name, nicknames in NICKNAMES.items():
        if name in concepts:
            concepts[name]["forms"].update(nicknames)

    first_words = Counter(k.split()[0] for k in concepts if k in zones and " " in k)
    result = []
    for key, concept in sorted(concepts.items()):
        values = {lang: votes.most_common(1)[0][0] for lang, votes in concept["votes"].items() if votes}
        # "Forêt des Pins argentés (Silverpine Forest)": the reader gets the name alone.
        values = {lang: PARENTHESES_RE.sub("", value) or value for lang, value in values.items()}
        if "en" not in values:
            continue
        forms = set(concept["forms"])
        for form in list(forms):
            bare = PARENTHESES_RE.sub("", form)         # "Forêt des Pins argentés (Silverpine Forest)"
            if bare != form and len(bare) >= 5:
                forms.add(bare)
                form = bare
            short = ARTICLES_RE.sub("", form)           # "The Barrens" -> "Barrens"
            if short != form and len(short) >= 5 and short.lower() not in COMMON_WORDS:
                forms.add(short)
        words = values["en"].split()
        if key in zones and len(words) > 1:
            first = words[0].lower()
            if len(first) >= 6 and first_words[first] == 1 and first not in FIRST_WORD_STOPLIST and first not in concepts and first not in COMMON_WORDS:
                forms.add(words[0])                     # "Stonetalon Mountains" -> "Stonetalon"
        forms -= set(values.values())
        result.append({**values, "forms": sorted(forms, key=str.lower)})

    OUTPUT.write_text(json.dumps({
        "_source": f"WoW Forever build {build}, AreaTable and Map tables (wago.tools); other names from "
                   f"{', '.join(f'{k} {v}' for k, v in ALIAS_BUILDS.items())}. Generated by build/build_places.py.",
        "concepts": result,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(result)} places written to {OUTPUT}")


if __name__ == "__main__":
    main()
