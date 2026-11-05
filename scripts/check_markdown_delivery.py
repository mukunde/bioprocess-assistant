"""Reject new delivery notes in Markdown. The baseline records legacy matches."""

import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "scripts" / "markdown-delivery-baseline.json"
RULES = {
    "delivery-heading": r"^\s*#{1,6}\s+.*(?:versioning lot|commit[- ]ready (?:lot|package)|proposed (?:git metadata|branch|commit)|git delivery|commit proposal|(?:prepared|proposed) (?:delivery|commit) lot)\b",
    "proposed-git-action": r"^\s*(?:[-*]\s+)?\**proposed\s+(?:branch|commit(?: message| subject)?|git metadata)\**\s*[:.]",
    "pending-personal-approval": r"\b(?:awaiting (?:the )?user(?:'s)? (?:approval|usability review|confirmation)|prepared for user approval|without (?:the )?user(?:'s)? explicit (?:agreement|approval))\b",
    "internal-git-status": r"\b(?:no staging, commit|no (?:git )?commit or push (?:was|were|is|has been|performed)|(?:the )?(?:sixteen|16) (?:excluded|old) (?:old )?notes)\b",
}
COMPILED = {name: re.compile(pattern, re.IGNORECASE) for name, pattern in RULES.items()}


def matches(content):
    for number, line in enumerate(content.splitlines(), start=1):
        for name, pattern in COMPILED.items():
            if pattern.search(line):
                digest = hashlib.sha256(line.strip().encode("utf-8")).hexdigest()
                yield number, f"{name}:{digest}"


def main(paths):
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    failed = False
    for path in paths:
        file = Path(path).resolve()
        name = file.relative_to(ROOT).as_posix()
        allowance = Counter(baseline.get(name, {}))
        for number, key in matches(file.read_text(encoding="utf-8-sig")):
            if allowance[key]:
                allowance[key] -= 1
                continue
            failed = True
            print(f"{name}:{number}: {key.split(':', 1)[0]}: "
                  "put delivery and approval notes in the PR or local work log.")
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
