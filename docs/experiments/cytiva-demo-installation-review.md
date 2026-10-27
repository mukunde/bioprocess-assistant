# Windows demo installation review

Date: 27 October 2026. Local implementation based on merged `main` at `3fc97da`;
no commit, push or model call performed for this work.

## Delivery

`Install-CytivaDemo.ps1` bootstraps `demo.setup` with CPython 3.13.0 x64. It creates
an ignored `.venv-demo`, installs the twelve unchanged v03 dependency versions
using the SHA-256 wheel hashes in `demo/requirements-windows.lock`, checks package
compatibility and prepares the tokenizer cache. The installer uses PyPI and the
official public encoding-asset endpoint only for package/static-data downloads.
The existing launcher and engine remain offline and unmodified.

The tokenizer is verified against the unchanged v03 SHA-256 before atomic cache
publication. Corrupt existing assets are rejected rather than overwritten.
Offline installation accepts a wheelhouse and a tokenizer file; pip uses
`--no-index`, `--require-hashes`, `--only-binary=:all:` and `--no-deps`.

## Observed checks

- Created a fresh Git clone of local merged main without its ignored environment,
  tokenizer cache, PDF, credentials or sixteen older notes. Copied only the four
  pending installation files into it: installer, Python setup module, dependency
  lock and `.gitignore`. This is an uncommitted working-copy overlay, not a claim
  that the installer already exists on remote main.
- Installed all twelve dependencies into that clone's new `.venv-demo`. Pip
  could reuse its user-level wheel cache; the previous project environment was
  not copied or used as an installation source. Downloaded the tokenizer from
  the public endpoint and verified its frozen hash.
- `pip check` and `Start-CytivaDemo.ps1 -CheckOnly` passed. Automatic discovery
  selected the clone's own `.venv-demo`; all 36 pinned files verified.
- The real Windows PowerShell 5.1 installation completed. Repeating the setup
  under PowerShell 7 reported the environment/cache already ready, without
  package installation. A separate offline dependency installation also passed
  in the original checkout's new `.venv-demo`, using local wheels and its existing
  verified tokenizer.
- Ten installer regressions passed: exact dependency inventory, malformed lock,
  offline copy/reuse, invalid downloads, missing offline data, corrupt existing
  cache preservation, out-of-clone destination, freeze drift, existing-environment
  isolation and offline pip arguments.
- The complete maintained suite passed **790/790 tests**, with no failures,
  errors, skips or external connection attempts (48 loopback operations).
  This includes the ten new installer tests. It is an offline regression result,
  separate from the explicit setup downloads and the browser walkthrough.

## Browser and HTTP walkthrough

Started the clone's original Windows launcher on loopback port 8767 and exercised
the unchanged UI in the in-app browser. Seven corresponding HTTP results were
saved privately under `.local-tools/cytiva-fresh-clone-walkthrough.json`.

| Scenario | Observed result |
|---|---|
| Default washing flow, 1 mL | Support 1/1; all five source passages and Blue Sepharose warning retained |
| Flow, volumes and end-of-washing criteria | Support 3/3; common source bundle retained |
| Washing flow plus pressure and equilibration | Supported / missing source / quarantined; support 1/3 and eligible context 1/1 remain distinct |
| Unspecified format | Clarification, no assumed format or returned binding; correction button focuses the format selector |
| Explicit 5 mL | Supported binding belongs to 5 mL; source text retains both documented formats |
| French example | Supported washing request with original English quotations |
| Coordinated buffer formulations | Incomplete inventory and clarification; no silently selected buffer purpose |

Citation navigation reached the matching source anchor. Editing inputs displayed
the stale-result notice until resubmission. DOM text for all five displayed French
example quotations exactly matched their HTTP source quotations, including text
split by highlighting. E118-I and E121-EQ were absent from every admitted bundle.
All seven saved responses report zero model calls and EUR 0 API cost. No blocking
walkthrough anomaly was observed.

## Limits and next check

This verifies an isolated clone on the same Windows x64 workstation, with an
already installed CPython 3.13.0 and possibly cached wheels. It is not a clean-OS,
second physical-machine, ARM64 or hosted-deployment certification. The next check
is for another person/machine to follow the setup and five-minute guide, retaining
any prerequisite/download diagnostics. The installer does not install Python,
change execution policy, relax the freeze or expand the reviewed corpus.

The frozen method/engine and the sixteen older local notes retain their original
hashes. Historical trial scores and quarantine decisions are unchanged. Private
wheels, environments, tokenizer data, screenshots and raw walkthrough responses
remain ignored. See [the installation and walkthrough guide](../DEMO-FIRST.md).

## Compact delivery inventory

The proposed delivery contains exactly twelve files:

| File | Purpose |
|---|---|
| `.gitignore` | Exclude the clone-local `.venv-demo` |
| `Install-CytivaDemo.ps1` | Windows setup entry point and Python discovery |
| `demo/setup.py` | Isolated installation and verified tokenizer preparation |
| `demo/requirements-windows.lock` | Twelve exact dependency versions and Windows x64 wheel hashes |
| `tests/test_cytiva_setup.py` | Ten installer integrity/isolation regressions |
| `README.md` | Setup entry point and distinction between merged and local work |
| `docs/DEMO-FIRST.md` | Online/offline installation, prerequisites and walkthrough |
| `docs/ROADMAP.md` | Same-PC evidence and remaining second-machine gate |
| `docs/experiments/cytiva-demo-installation-review.md` | Installation, browser, test and preservation report |
| `experiments/cytiva/compositional-navigation-v04-results/manifest.json` | Updated README documentation digest only |
| `experiments/cytiva/reviewed-v05-evaluation/manifest.json` | Updated README/roadmap documentation digests only |
| `experiments/cytiva/free-text-v02-comparison-v01/package-manifest.json` | Updated documentation digests and manifest cross-links only |

Proposed branch: `codex/cytiva-windows-installation`.

Proposed commit message:

```text
feat: add reproducible Windows setup for the frozen Cytiva demo
```

The existing `Start-CytivaDemo.ps1`, demo renderer, frozen runtime, source and
decision payloads are outside the diff. The sixteen older notes and all ignored
installation/test artifacts are outside this inventory. The 790-test result
belongs to the implementation checks above; this inventory adds documentation
only and does not represent a new full-suite run.
