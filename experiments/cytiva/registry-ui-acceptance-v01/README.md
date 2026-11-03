# MabSelect registry UI — proposed acceptance set UA01–UA08

Prepared on 3 November 2026. **Eight references await human review; no trial has
started. No requests from this set have been sent to the UI/API/registry.**
This is preparation only: no runner, score, active-store change, API/model call,
new runtime freeze, Git commit or push.

## Eight guided requests

| ID | Product / context | Questions | Proposed outcome |
|---|---|---|---|
| UA01 | MabSelect SuRe / Precipitated or denatured substances | cleaning_options, pressure_limit | partial |
| UA02 | MabSelect SuRe LX / Precipitated or denatured substances | cleaning_options | supported |
| UA03 | MabSelect SuRe LX / Hydrophobic proteins, lipoproteins or lipids | pressure_limit | abstained |
| UA04 | MabSelect SuRe / Hydrophobic proteins, lipoproteins or lipids | cleaning_options, pressure_limit | partial |
| UA05 | MabSelect family — variant unknown / Hydrophobic proteins, lipoproteins or lipids | cleaning_options, pressure_limit | needs_clarification |
| UA06 | MabSelect SuRe / Mixed / uncertain / other | cleaning_options | needs_clarification |
| UA07 | Conflicting labels / Precipitated or denatured substances | pressure_limit | needs_clarification |
| UA08 | Other product / Mixed / uncertain / other | cleaning_options, pressure_limit | abstained |

Review [the eight human cards](REVIEW.md) with exact handbook quotations, expected
content and reservations. [references.json](references.json) records machine
assertions and distinguishes reference-only evidence from emitted citations.
Accepted application-design records are separately bound by `application_policy_refs`
in the references; these ground clarification/outside-catalog decisions.
All decisions in [review.json](review.json) are pending; null human messages are
not approvals. Original source/human-review records are reused unchanged in
[evidence.json](evidence.json), with exact source-object/quote identities.

## What is new, and what this can measure

These are new acceptance records and combinations of guided controls relative
to the declared six SX examples and the current registry-UI regression scenarios.
The baseline signatures/check are recorded in the manifest. The same source
blocks and selector branches have been used in prior project development. The
author inspected the current code for interface/state compatibility. This is not
a blinded independent benchmark or a claim that no similar domain question has
ever been considered anywhere in the project.

The UI accepts only product, deposit category, cleaning options and numerical
pressure. English natural-language briefs are scenarios for the human tester,
not inputs to a text interpreter. The JSON request projection matches the actual
form, including its constant `registry-ui-request` request ID; case IDs belong to
the external acceptance record. Each case has a distinct control tuple.
No volumes, pH instructions, exclusions or extra tasks are hidden in the brief and
then assumed to have been parsed. All quantities in expected supported content
come from the existing reviewed source blocks, never from invented user inputs.

This tests the complete bounded UI/HTTP/citation assembly path. It does not test
retrieval over a new manual, generative fluency, diagnosis, scientific suitability,
whole-manual absence or regulatory qualification. E118-I/E121-EQ stay excluded.
No new scientific/source approval follows from approving an acceptance reference.

## Proposed reference and success criteria

Before execution, review all eight intent-to-control mappings, item states,
conditions/quantities, references/citations and refusal/clarification boundaries.
The response content is documentary material in the visible option/source
sections, not newly generated prose. Statuses and supported/refused items must
be intelligible in the visible page; exact reason codes, bindings and request
projection may be inspected in the collapsed audit section. Exact wording of a
new summary is not a golden-string requirement. Original quotations, scope,
reservations and warning/quantity associations are mandatory.

Proposed acceptance: **8/8 expected case outcomes**, all mandatory per-case checks
and citation resolutions pass, with **zero critical failures**. Critical failures
include an unsupported number/procedure, wrong product/context attribution,
combined alternatives presented as required succession, lost essential warning,
a citation/quote/provenance mismatch, missing required support, recipe selection
before necessary clarification, or preview fallback under invalid authority.
Report case outcomes and failure reasons; a regression count is not an acceptance
score. Record noncritical usability notes separately rather than rewriting a
reference to make an observed failure pass. No results or metrics exist yet.

For UA03 and UA08, no emitted citation/quotation is expected from an unsupported-
only request. Their handbook passages are human-reference context for a bounded
refusal, not fictitious citations the UI must manufacture. UA03's pressure
absence is limited to the selected blocks. UA08's outside-product-scope decision
comes from the application release/catalog policy; it is not a manual statement
that the medium is incompatible, unsafe or unsupported everywhere.

Q09's eight context excerpts ground product/category distinctions. Asking for
clarification is a reviewed application policy, not a verbatim manual instruction.
The expected response must not demand a confirmed scientific diagnosis.

## Baseline and no-run boundary

[method-lock.json](method-lock.json) records `04e3bd3`, exact current code/UI,
source and existing freeze-lock identities, plus the already approved private
local authority identity. It is a preparation lock, not a new runtime freeze.
The private store itself is not copied. Do not switch its release or insert real
withdrawals to exercise acceptance; no fault setup is included in these eight
normal-authority questions. Existing disposable withdrawal/timeout regressions
remain separate conformance evidence. Any future acceptance fault extension must
have its own reviewed setup in a disposable store.

The existing 18 UI regressions and SX01–SX06 are development/conformance evidence,
not eight observed acceptance outcomes. No new regression or browser requests
were executed for these questions during preparation. Static preparation checks
verify JSON shapes, UI control values, reference scope, quote hashes, novelty
within the declared comparison and preservation; they never call evaluation.

After reference review, a separate explicit instruction is required to launch.
First verify unchanged baseline/source/authority identities and the prepared
environment; drift stops the trial until reviewed. Then exercise one case at a
time with exact controls, record case ID externally and preserve actual requests,
responses, visible outcomes and opened citation identities. Use the ordinary UI
request deadline, with no automatic retry or fallback. A timeout/unavailable
result is retained and analyzed, not silently skipped or retried until success.

Do not run a case while its reference decision is pending. Human corrections
before a first run must be quoted and recorded, preserving the original proposal
and refreshing the proposed reference/decision bindings. After observing results,
do not retune the method, alter expectations or overwrite outcomes. Any later
repair/retrial is a new variant/trial retaining this baseline and its failures.
No executable runner or machine review gate is supplied by this preparation.

Files: README, human cards, questions, references, exact evidence, pending human
review, preparation lock and manifest. No trial output directory is created.
