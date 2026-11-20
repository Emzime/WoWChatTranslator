"""Minimal parser for WoW SavedVariables files (Lua table literals only)."""

import re

_TOKEN_RE = re.compile(
    r"""\s*(?:
        (?P<comment>--[^\n]*)
      | (?P<string>"(?:\\.|[^"\\])*")
      | (?P<number>-?(?:0x[0-9a-fA-F]+|\d+\.?\d*(?:[eE][-+]?\d+)?|\.\d+(?:[eE][-+]?\d+)?))
      | (?P<name>[A-Za-z_][A-Za-z0-9_]*)
      | (?P<sym>[{}\[\]=,;])
    )""",
    re.VERBOSE,
)

_ESCAPES = {"n": "\n", "t": "\t", "r": "\r", "\\": "\\", '"': '"', "'": "'", "\n": "\n"}


def _unescape(raw):
    out, i = [], 0
    while i < len(raw):
        ch = raw[i]
        if ch == "\\" and i + 1 < len(raw):
            nxt = raw[i + 1]
            if nxt.isdigit():
                digits = re.match(r"\d{1,3}", raw[i + 1:]).group(0)
                out.append(chr(int(digits)))
                i += 1 + len(digits)
                continue
            out.append(_ESCAPES.get(nxt, nxt))
            i += 2
            continue
        out.append(ch)
        i += 1
    # WoW writes UTF-8 bytes as escaped decimals; rebuild the text from those bytes.
    text = "".join(out)
    try:
        return text.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text


def _tokenize(text):
    pos, tokens = 0, []
    while pos < len(text):
        match = _TOKEN_RE.match(text, pos)
        if not match or match.end() == pos:
            if text[pos:].strip() == "":
                break
            raise ValueError(f"Unexpected character at {pos}: {text[pos:pos + 20]!r}")
        pos = match.end()
        kind = match.lastgroup
        if kind == "comment":
            continue
        tokens.append((kind, match.group(kind)))
    return tokens


class _Parser:
    def __init__(self, tokens):
        self.tokens, self.i = tokens, 0

    def peek(self):
        return self.tokens[self.i] if self.i < len(self.tokens) else (None, None)

    def take(self, value=None):
        tok = self.peek()
        if value is not None and tok[1] != value:
            raise ValueError(f"Expected {value!r}, got {tok[1]!r}")
        self.i += 1
        return tok

    def value(self):
        kind, val = self.take()
        if kind == "string":
            return _unescape(val[1:-1])
        if kind == "number":
            return int(val, 16) if val.lower().startswith(("0x", "-0x")) else (float(val) if any(c in val for c in ".eE") else int(val))
        if kind == "name":
            return {"true": True, "false": False, "nil": None}.get(val, val)
        if val == "{":
            return self.table()
        raise ValueError(f"Unexpected token {val!r}")

    def table(self):
        result, index = {}, 1
        while self.peek()[1] != "}":
            kind, val = self.peek()
            if val == "[":
                self.take("[")
                key = self.value()
                self.take("]")
                self.take("=")
                result[key] = self.value()
            elif kind == "name" and self.i + 1 < len(self.tokens) and self.tokens[self.i + 1][1] == "=":
                self.take()
                self.take("=")
                result[val] = self.value()
            else:
                result[index] = self.value()
                index += 1
            if self.peek()[1] in (",", ";"):
                self.take()
        self.take("}")
        return result


def parse(text):
    """Returns {global_name: value} for every top-level assignment."""
    parser = _Parser(_tokenize(text))
    result = {}
    while parser.peek()[0] is not None:
        _, name = parser.take()
        parser.take("=")
        result[name] = parser.value()
    return result


def load(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        return parse(fh.read())


# ----- writing ------------------------------------------------------------------------------

def _lua_string(text):
    out = ['"']
    for ch in text:
        if ch in '"\\':
            out.append("\\" + ch)
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\r":
            out.append("\\r")
        elif ord(ch) < 32:
            out.append(f"\\{ord(ch)}")
        else:
            out.append(ch)
    out.append('"')
    return "".join(out)


def _lua_value(value, indent):
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, str):
        return _lua_string(value)
    if isinstance(value, dict):
        pad = "\t" * (indent + 1)
        items = []
        for key, item in value.items():
            if item is None:
                continue
            lua_key = _lua_string(key) if isinstance(key, str) else repr(key)
            items.append(f"{pad}[{lua_key}] = {_lua_value(item, indent + 1)},")
        if not items:
            return "{\n" + "\t" * indent + "}"
        return "{\n" + "\n".join(items) + "\n" + "\t" * indent + "}"
    raise TypeError(f"Cannot serialise {type(value).__name__}")


def dump(variables):
    """Serialises {global_name: value} the way WoW writes SavedVariables."""
    return "\n".join(f"{name} = {_lua_value(value, 0)}" for name, value in variables.items() if value is not None) + "\n"


def save(path, variables):
    """Atomic write (WoW may read the file at any login)."""
    from pathlib import Path
    path = Path(path)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(dump(variables), encoding="utf-8")
    tmp.replace(path)
