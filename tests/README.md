# Current complete test suite

From the repository root, run:

```powershell
.\.venv\Scripts\python.exe -m unittest tests -v
```

Root discovery (`python -m unittest discover -v`) also uses the package hook.
Choose the project's environment with its required application/ingestion
packages. No LLM or paid API is required.

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
