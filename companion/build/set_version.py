"""Writes the release version (from the git tag, e.g. v1.2.0) into the companion and the addon.

The updater compares this embedded version with the latest GitHub release tag, so both must match.
Usage: python build/set_version.py v1.2.0
"""

import re
import sys
from pathlib import Path

COMPANION = Path(__file__).resolve().parent.parent
TOC = COMPANION.parent / "addon" / "WoWChatTranslator" / "WoWChatTranslator.toc"
INIT = COMPANION / "wctc" / "__init__.py"


def main():
    match = re.search(r"\d+\.\d+\.\d+", sys.argv[1] if len(sys.argv) > 1 else "")
    if not match:
        sys.exit("Expected a version like v1.2.0")
    version = match.group(0)
    INIT.write_text(re.sub(r'__version__ = "[^"]*"', f'__version__ = "{version}"', INIT.read_text(encoding="utf-8")), encoding="utf-8")
    TOC.write_text(re.sub(r"^## Version:.*$", f"## Version: {version}", TOC.read_text(encoding="utf-8"), flags=re.MULTILINE), encoding="utf-8")
    print(f"Version set to {version}")


if __name__ == "__main__":
    main()
