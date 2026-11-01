# Current complete test suite

For the MC12 interface regressions, install Node.js >=22.12 and the isolated
locked test dependencies first (no browser or model download). From the repository
root, run:

```powershell
npm ci --prefix tests/ui --ignore-scripts --no-audit --no-fund
.\.venv\Scripts\python.exe -m unittest tests -v
```

Root discovery (`python -m unittest discover -v`) also uses the package hook.
Choose the project's environment with its required application/ingestion
packages. No LLM or paid API is required. Node/jsdom is a development-test
requirement only; the Cytiva runtime installer and its twelve Python dependencies
are unchanged. MC12 fails rather than silently skipping if the tools are absent.
See the [UI test guide](ui/README.md) for DOM/HTTP scope and mutation witnesses.

## Windows temporary paths

Nested synthetic snapshots can exceed legacy Windows path limits when TEMP points
inside a deep checkout. The maintained runner validates a short root, creates a
unique owned child, restores Python's prior temp setting and removes only that
child on exit. It neither changes the system TEMP setting nor deletes existing
root contents. Choose a writable root of at most 60 characters. For example:

```powershell
python scripts/run_tests.py --temp-root "$env:LOCALAPPDATA\Temp"
```

The normal `python -m unittest tests -v` entry point remains supported when its
system temporary path is suitable. This runner changes fixture placement only;
it does not alter frozen methods, skip tests or retry failures.

## Frozen historical fixture

`test_v03b_evaluation.py` is itself covered by the original V01-V12 freeze. Its
preparation-stage assertion that the real locked-run directory must not exist
became obsolete after the authorized run. The file, manifest, hashes and saved
results remain byte-for-byte unchanged.

The current suite uses unittest's package `load_tests` hook and an explicit
`CurrentSuiteLoader`. For that one module it loads a subclass defined in
`v03b_review_gate_suite.py`: all eleven historical test names remain, ten methods
are inherited unchanged, and only the obsolete fixture is overridden. Nothing
is skipped, expected-failed or globally monkeypatched to hide the directory.

The corrected test verifies the real freeze, then exercises the real incomplete
review gate in temporary fixtures with an absent output and an existing completed
output. It checks that runtime construction is never reached, no new output is
created, and existing output bytes and inventory are unchanged.
`test_current_suite.py` checks the loader inventory and the single override.

The direct preparation-era command `python -m unittest discover -s tests` bypasses
the package hook and is not the current complete-suite entry point. Executing the
historical module directly retains its original preparation-only assumption.
Use `python -m unittest tests` to run the maintained complete suite.
