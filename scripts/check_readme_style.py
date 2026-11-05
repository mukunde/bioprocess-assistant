"""Check the root README's structure and heading punctuation."""

import re
import sys
from pathlib import Path

REQUIRED_SECTIONS = (
    "Watch the demo",
    "Run locally",
    "Architecture",
    "Data and sources",
    "Validation and results",
    "Limitations",
    "Documentation",
    "Ownership and license",
)
MAX_LINES = 160
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
HEADING = re.compile(r"^ {0,3}(#{1,6})[ \t]+(.+?)\s*$")


def headings(lines):
    fence = None
    for number, line in enumerate(lines, 1):
        marker = FENCE.match(line)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = None
            continue
        if marker:
            fence = marker[1]
            continue
        heading = HEADING.match(line)
        if heading:
            title = re.sub(r"[ \t]+#+$", "", heading[2]).strip()
            yield number, len(heading[1]), title


def issues(lines):
    if len(lines) > MAX_LINES:
        yield 1, f"Keep the README to {MAX_LINES} lines. Move details to a linked guide."
    parsed = list(headings(lines))
    titles = [number for number, level, _ in parsed if level == 1]
    if titles != [1]:
        yield 1, "Start with one ATX level-one title."
    sections = [title for _, level, title in parsed if level == 2 and title in REQUIRED_SECTIONS]
    if tuple(sections) != REQUIRED_SECTIONS:
        yield 1, "Use these level-two sections once, in order: " + ", ".join(REQUIRED_SECTIONS)
    for number, _, title in parsed:
        if title.endswith((".", ":")):
            yield number, "Remove the final period or colon from the heading."


def main(paths):
    failed = False
    for name in paths:
        lines = Path(name).read_text(encoding="utf-8-sig").splitlines()
        for number, message in issues(lines):
            failed = True
            print(f"{name}:{number}: {message}")
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
