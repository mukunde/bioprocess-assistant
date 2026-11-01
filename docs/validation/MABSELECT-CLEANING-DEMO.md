# MabSelect cleaning journey — implementation verification

Local development work on 31 October 2026, based on merged `main` at `9b4bd25`.
This implementation is not committed or merged. It follows the
[validated design](../technical/MABSELECT-CLEANING-JOURNEY-V01.md) and
[recorded MS01–MS08 / C1–C4 approval](../technical/mabselect-cleaning-review-v01.json).
The original human message is retained verbatim. This approves application design,
not new source facts, scientific suitability or industrial operating procedures.

## Run and scope

Start this checkout with the existing launcher or prepared Python environment.
Choose **MabSelect · cleaning guidance** under Input, or open
`http://127.0.0.1:8766/#mabselect-controls` at the default port. The agent's local
verification instance uses port **8777** to leave the older 8776 server untouched.
An older running server or Sandbox clone does not acquire these edits automatically.
Reloading the form resets unsaved selections. No persistent request history exists.

The new route uses neither a model nor a database. It admits only exact MabSelect,
SuRe and SuRe LX identities in the reviewed edition, with separate unknown-family,
other-product and conflicting-label states. Unknown/mixed context yields
clarification, not a recipe or established diagnosis. It never reattributes the
page-166 Protein A/G backpressure cleaning indication to MabSelect.

The general precipitated/denatured block displays four separate formulations,
sharing the original 2-CV, minimum-contact and immediate following-wash conditions.
Each displayed formulation is an exact source substring with its own offsets and
quote hash; the complete original block remains visible. For SuRe/SuRe LX, the
additional three-step sequence is a separate block, never concatenated, ranked or
presented as a fifth general formulation. Hydrophobic context shows detergent
versus solvents, ethanol OR 2-propanol, following washes and both precautions.
pH belongs to the following binding buffer; no dose, pressure/flow value, solvent
duration, gradient, CV-to-mL conversion or suitability choice is invented.

The runtime validates both existing Q and N review packages, then rechecks loaded
evidence/review snapshots against their file bindings. Q05/Q06/N06/N07/Q09
reservations and complete required source bundles are retained. Recipe responses
contain page-167 source bundles only; clarification bundles preserve separately
labelled page-166/page-167 context required by Q09. The source dossier and original
pending preparation flags are unchanged; existing scoped review decisions are not
rewritten as unrestricted passage approvals. No new extraction or publication.

## Tests

MC01–MC12 are implemented as twelve development conformance tests in
[test_mabselect_journey.py](../../tests/test_mabselect_journey.py). They cover:

- product identity, general alternatives and complete conditions;
- separate SuRe/SuRe LX sequence and no general sodium-hydroxide ban;
- detergent/solvent scope, examples, alternatives and distinct precautions;
- unknown/mixed/conflicting inputs and rejection of source/policy overrides;
- exact quote/span/PDF provenance, review reservations and fail-closed tampering;
- frozen-engine separation, the prior Sepharose path and recorded design approval.

These twelve plus the seventeen existing journey/demo tests passed: **29/29**.
Network connections are blocked within the conformance tests. Browser verification
uses loopback only. Tests are against known reviewed sources and code; they are
not independent retrieval, free-text understanding or generated-answer evaluation.

The complete suite ran **812 tests in 134.426 seconds: 811 passed, one skipped,
no failures or errors**. The skip is the existing optional PDFium preview
dependency. This result is a local regression check, not a new prospective score.

## Real-browser verification

The normal narrow in-app viewport was used without an override. Checks passed:

| Case | Observation |
|---|---|
| MabSelect family, unknown variant | Exact-product clarification, no recipe cards |
| Exact plain MabSelect + precipitated substances | Four separate formulations in the general block; restricted block absent |
| SuRe + precipitated substances | General and restricted blocks distinct; no succession or ranking implied |
| SuRe LX + hydrophobic context | Detergent and solvent alternatives; no stronger-alkali block; example and original quotations retained |
| Mixed context | Known SuRe LX identity retained; clarification button focuses the context field; no recipe |
| Other product | Outside-scope explanation without incompatibility claim; no recipe |
| Citation E167-W | Opens the page-167 MabSelect scope and original lower-flow warning |
| Input changed | Previous results explicitly marked stale |
| Return to old guided route | Frozen-v03 badge, 1/1 supported request and five full source cards |
| Return to Protein A/G route | Original alternatives and page-166 12-hour stand retained |

No console warnings or errors were observed. These are agent browser checks,
not another human scientific approval, physical second-PC result or broad browser
certification. The static onboarding video still shows the earlier guided route.
Private screenshots, test logs and preservation checks remain in the ignored
`.local-tools/backpressure-commit/mabselect-runtime-v01/` directory of the original
checkout; they are not source data or dependencies to publish.

## Preservation and next review

Frozen v03, the old Protein A/G runtime module, original evidence/review events,
source quarantines, past trial results and the sixteen excluded notes are preserved.
The user should review this local UI before a new versioning lot is prepared.
No default Neo4j chat behavior or source publication is changed. This remains
bounded documentary support, not treatment selection or operational authorization.

## Post-review corrections — MR01/MR02

The first implementation review remains historical in
[MabSelect implementation review v01](../technical/MABSELECT-CLEANING-IMPLEMENTATION-REVIEW-V01.md).
Its two findings were addressed without changing approved human messages, source
quotations, constraints or frozen v03:

- MR01: portable exact pre-review contract snapshot plus independently anchored
  verifier for contract, dossier and original decision record; the MabSelect
  runtime refuses an altered approval before loading source reviews.
- MR02: MC12 DOM/HTTP integration executes the shipped HTML/JavaScript against
  the actual loopback `Demo`. It checks form payloads, separate blocks, warnings,
  source/return navigation, stale results and return to prior paths. Five in-memory
  mutants must fail; unmodified UI must pass. This is DOM behavior, not visual
  browser/layout certification. The HTML itself was not changed by these fixes.

[Setup and commands](../../tests/ui/README.md): Node/jsdom is an explicit test-only
requirement with its own npm lock. Neither dependency is added to the twelve
runtime Python packages or required to launch the demo. No silent MC12 skip if
those development tools are absent.

The new [re-review](../technical/MABSELECT-CLEANING-IMPLEMENTATION-REVIEW-V02.md)
records the current verification; previous 29/29 and 812-test results above remain
historical. No runtime freeze or publication is created by these corrections.

Latest correction checkpoint: **823 tests, 822 passed, one optional PDFium skip**,
with both MR01/MR02 resolved. See the v02 re-review for the test-only Node setup
and portable approval replay. Earlier complete-suite counts are historical.
