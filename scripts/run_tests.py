"""Run the maintained unittest suite with an explicit temporary workspace."""
import argparse
from contextlib import contextmanager
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


@contextmanager
def test_workspace(base, *, windows=None):
    base = Path(base).resolve()
    windows = os.name == 'nt' if windows is None else windows
    if windows and len(str(base)) > 60:
        raise ValueError('Temporary root is too long for nested Windows fixtures; choose a writable path of at most 60 characters with --temp-root')
    base.mkdir(parents=True, exist_ok=True)
    previous = tempfile.tempdir
    with tempfile.TemporaryDirectory(prefix='bpa-', dir=base) as workspace:
        tempfile.tempdir = workspace
        try:
            yield Path(workspace)
        finally:
            tempfile.tempdir = previous


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--temp-root', type=Path, default=Path(tempfile.gettempdir()))
    parser.add_argument('modules', nargs='*', default=['tests'])
    args = parser.parse_args(argv)
    # Direct script execution must resolve the repository's test package.
    sys.path.insert(0, str(ROOT))
    try:
        with test_workspace(args.temp_root) as workspace:
            print('Temporary fixture workspace: ' + str(workspace), flush=True)
            suite = unittest.defaultTestLoader.loadTestsFromNames(args.modules)
            result = unittest.TextTestRunner(verbosity=2).run(suite)
    except (OSError, ValueError) as exc:
        parser.exit(2, str(exc) + '\n')
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())
