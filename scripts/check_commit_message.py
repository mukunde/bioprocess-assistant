"""Check the subject of a Git commit message."""
import re
import subprocess
import sys
from pathlib import Path


SUBJECT = re.compile(r"(?:build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test)(?:\([a-z0-9][a-z0-9._/-]*\))?!?: \S.*")
GENERATED = re.compile(r'Merge .+|Revert ".+"|(?:fixup|squash|amend)! .+')


def main():
    message = Path(sys.argv[1]).read_bytes()
    stripped = subprocess.run(
        ["git", "stripspace", "--strip-comments"], input=message, capture_output=True, check=True
    ).stdout.decode("utf-8-sig", errors="replace")
    header = stripped.splitlines()[0] if stripped else ""
    if SUBJECT.fullmatch(header) or GENERATED.fullmatch(header):
        return 0
    print("Use type(scope): subject or type: subject, for example docs(cytiva): clarify setup.",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
