# Free-text design checkpoint: proposed 20-file delivery

Date: 26 October 2026. Prepared for review; this preparation does not stage or
publish files. The merged baseline remains main at `1b852f4` (PR #42). The
documents below describe approved design choices and explicitly pending fixture
review, not implemented free-text functionality.

## Exact proposed files

- `README.md`
- `docs/ROADMAP.md`
- `docs/decisions/2026-10-26-free-text-interface-review.json`
- `docs/decisions/2026-10-26-free-text-machine-design-review.json`
- `docs/decisions/2026-10-26-structured-free-text-protocol-review.json`
- `docs/experiments/free-text-design-package-v01.md`
- `docs/experiments/free-text-interface-examples-v01.json`
- `docs/experiments/free-text-interface-group-review-v01.md`
- `docs/experiments/structured-free-text-cases-v01.md`
- `docs/experiments/structured-free-text-comparison-v01.json`
- `docs/experiments/structured-free-text-comparison-v01.md`
- `docs/technical/FREE-TEXT-INTERFACE-V01.md`
- `docs/technical/FREE-TEXT-MACHINE-DESIGN-V01.md`
- `docs/technical/free-text-input-v01.schema.json`
- `docs/technical/free-text-interpretation-v01.schema.json`
- `docs/technical/free-text-machine-design-checks-v01.json`
- `docs/technical/free-text-machine-design-checks-v02.json`
- `docs/technical/free-text-outcome-v01.schema.json`
- `experiments/cytiva/compositional-navigation-v04-results/manifest.json`
- `experiments/cytiva/reviewed-v05-evaluation/manifest.json`

## Scope and approval boundary

- The three actual collective messages approve CP01-CP06, FI01-FI06/IF01-IF14
  and MC01-MC06 with their respective clarifications. Original French quotations
  remain exact; no new approval is inferred for individual revised fixtures.
- GR01-GR04 cover sixteen refined expectations and three invalid inputs; all
  group decisions are pending. Focused origins, absence/default reasons and
  external boundary/fault conditions are ready for that review.
- README and roadmap now separate merged X/S evidence, the approved local
  design, pending fixture decisions and future implementation/serving work.
- The two existing manifests change only documentation-support digests: README
  in the v04 development export, README and roadmap in the reviewed v05 export.
  No native result, method, source, claim, decision or provenance digest changes.
- The v01 static report remains historical. The v02 report binds the refined
  examples; no parser, bridge or IF implementation test was executed by preparing
  either report. Root caller input cannot activate the test-condition fields.

## Verification and practical limits

The baseline complete suite passed 556 tests with no skip or external connection.
The package's static checks validate three schemas, sixteen design examples,
three invalid caller inputs, focused-origin geometry/reference/accounting checks
and external test-condition separation. Semantic interpretation and actual
documentary results remain untested for this unimplemented interface.

The current working-tree verification passed all 556 maintained tests, with no
errors, failures, skips or external connection attempts. Loopback HTTP/Windows
socket tests were allowed in an isolated verification environment. No real S
trial was repeated. All 103 local link targets checked are present; both updated
export manifests and the unchanged structured export verify. The exact scope is
20 files, with an empty Git index and all sixteen excluded notes unchanged.
This execution report is kept separately from the historical merged-baseline
and frozen-trial records; no evidence score or runtime method was updated.

No runtime code, original structured schema/catalog/source policy, source PDF,
model asset, credential, raw trial or old private review journal is included.
The sixteen older local S preparation/review notes remain byte-for-byte unchanged
and outside the file list. Nothing is automatically deleted or archived by this
delivery preparation. Git-operation rules remain in AGENTS.md.

## Proposed commit

```text
docs(cytiva): specify structured and free-text comparison interface

Record the approved CP/FI/MC decisions and refined machine design.
Prepare grouped fixture review with focused origins and external test conditions.
Refresh README, roadmap and documentation digests while preserving frozen evidence.
```

Suggested branch: `codex/free-text-interface-design`.

The next functional step is GR01-GR04 review, then a separately requested minimal
deterministic implementation. Do not treat this design commit as a passing S/F
trial or approval to activate a new chat path.
