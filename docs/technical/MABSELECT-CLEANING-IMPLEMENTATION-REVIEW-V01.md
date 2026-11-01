# MabSelect journey — implementation review v01

Reviewed 31 October 2026 against the uncommitted implementation on `main`
`9b4bd25`. No application, tests, design-decision records or source files were
corrected during this review. Mutation probes substituted data in memory only.

Conclusion: the examined documentary branches conform to the validated product,
context, alternative and quantity rules. No new recipe transfer, invented value
or restricted-alkali scope extension was found. Two medium-priority validation
and portability gaps should be resolved before a runtime freeze. This review is
not scientific or operational approval and does not amend human decisions.

## Findings

### MR01 — P2: make the approved design record independently replayable

`mabselect-cleaning-review-v01.json` binds the pre-review contract hash
`1506c3e1d3045d97b0fa0ee53e81b4a4bb3dbad92093f00e2d0ac6752de61f9c`.
That exact contract is present only in the ignored local audit copy; none of the
current portable Git-visible files matches it. The editable contract has since
been annotated with approval and implementation status. A future clone of the
proposed package cannot independently resolve this historical binding.

MC12 checks only the twelve decision IDs and their validated status. A controlled
probe changed the original human message, C4's statement and both the dossier and
pre-review contract hashes in memory; MC12 still passed. This does not change the
current runtime's chemical rules, but the test's claim to preserve the recorded
design approval is too broad.

Required correction: retain a portable immutable snapshot of the exact approved
contract (or an equivalent version-addressed artifact), verify that historical
binding and the unchanged dossier binding, and add tamper regressions for the
human event, decision contents and referenced artifacts. Keep the existing human
message and decision semantics unchanged; do not silently replace the historical
contract digest with the current edited document's digest.

### MR02 — P2: cover the actual MabSelect interface in MC12

MC01–MC12 exercise Python responses and frozen-engine separation, but none reads
or executes the HTML form. Under an in-memory substitution of the pre-MabSelect
HTML, all twelve MC tests still passed and performed zero HTML reads. The current
browser walkthrough supplies useful manual evidence; it does not provide an
automated regression against losing the entry point or JavaScript wiring.

Required correction: supplement MC12 with an interface/integration regression
that detects disappearance of the MabSelect entry point, wrong product/context
payload wiring, loss of the separate general/restricted blocks, source-navigation
breakage, stale-result handling and failure to return to existing routes. Verify
actual observable behavior using the existing UI/HTTP facilities; do not merely
assert that the Python selector returned an options list. Preserve the prior
Protein A/G and frozen-v03 routes.

## Requirement assessment

| Requirement | Assessment |
|---|---|
| MS01 | Separate mode/module and product-specific scope; page-166 cleaning indication is not attributed to MabSelect |
| MS02 / C1 | Exact plain/SuRe/SuRe LX identities are separate; unknown family has no recipe; other/conflicting labels do not activate a procedure |
| MS03 | Four source-backed alternatives, exact concentration pairings, 2 CV, minimum 10 min and immediate following wash retained |
| MS04 / C2 | Restricted block appears only for SuRe/SuRe LX in precipitated context; three steps remain ordered and separate from general alternatives |
| MS05 | Detergent/solvent alternatives, solvent OR, example status and distinct air-bubble/backpressure precautions preserved |
| MS06 / C3 | Unknown/mixed context produces clarification; known product retained; no diagnosis or combined chemical sequence |
| C4 | Follow-up buffer pH and bounded missing-parameter notes preserved; no adjustment or numeric calculation is implemented |
| MS07 | Runtime review/source bundles and reservations are retained; approval-record portability/integrity guard needs MR01 |
| MS08 | No frozen-v03 or legacy-chat change, model, new parser or publication; MC12 interface guard needs MR02 |

MC02–MC08 cover the examined branch quantities/scopes. MC01/MC09/MC10 cover
clarification and invalid selectors. MC11 verifies exact source snapshots,
reservations, alternative spans and source/review tampering. MC12 verifies
engine separation and part of the prior path, but its approval-record and UI
coverage is incomplete as described above. The broad snapshot/source checks are
against saved evidence, not a new PDF interpretation or independent evaluation.

## Verification and separate transport observation

- Fresh unmodified targeted run: **29 tests passed in 7.343 seconds**, including
  all twelve MC tests and seventeen existing journey/demo regressions.
- Earlier complete suite: **812 tests, 811 passed, one optional PDFium skip**.
  No new complete-suite execution was needed for this read-only review.
- Approval-record mutation probe: MC12 still passed with four categories of
  provenance/decision alterations; no disk files changed.
- HTML mutation probe: all twelve MC tests passed with old HTML substituted in
  memory; none read the HTML.
- A broader 29-test HTML-substitution probe produced 28 passes and one existing
  forbidden-Origin HTTP-test error, **WinError 10053**. The error occurs in the
  transport rejection assertion, not an assertion about the MabSelect interface.
  This is consistent with the separately retained local transport-reliability
  work; do not treat it as proof that MC12 detected the removed interface. Track
  transport integration separately and do not weaken Origin checks or Windows
  protections. The first targeted run above passed without this error.
- Frozen v03 environment and all 36 pins verified; 16 excluded notes and the
  original checkout's 636 file hashes remain unchanged.

Only this review report is added by the review task. No source/runtime/test fixes,
LLM/API requests, commit or push were performed. Private probes/checks are recorded
under the original checkout's ignored
`.local-tools/backpressure-commit/mabselect-implementation-review-v01/` directory.
