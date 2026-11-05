# Protein A/G Sepharose documentary candidate — implementation

Historical initial implementation report. Its test counts and preparation refer
to the pre-review version. The later two findings and their corrections are
recorded in the [corrected review](SEPHAROSE-CANDIDATE-CORRECTIONS.md); the corrected
preparation uses a separate v02 directory without overwriting the initial one.

Date: 5 November 2026. Baseline: merged `main` at `2877513`.
This local working-tree implementation adds a separate candidate, not an activated
release, new source approval, runtime freeze or scientific validation.

## Delivered behavior

- `serving/sepharose_candidate.py` prepares and checks a separate staged directory.
  It pins the reviewed cleaning package, original source/review files and relevant
  runtime code. Expected source/mapping values are reconstructed and compared on
  lookup, with a recheck before returning content. No activation method exists;
  the default service refuses delivery unless the operator explicitly requests
  candidate preview. Active-authority markers are rejected.
- Q01 supplies the pressure-related cleaning indication without diagnosing a cause.
  Q02 retains the precipitated/denatured-protein sequence. Q03 and Q04 retain the
  detergent example and separate ethanol alternative, including its pressure
  precaution. Q09 supports clarification/product discrimination. Conditions,
  quantities, exact quotations and original scoped human decisions remain intact.
- The registered source set contains **12 excerpts**, with PDF identity, PDF and
  printed page metadata, source offsets/page-text hash, quotation hash and original
  review records. The full manual is not redistributed.
- `demo/chainlit_sepharose.py` provides explicit controls under the server-selected
  `BIOPROCESS_MODE=sepharose_candidate`, using `SEPHAROSE_CANDIDATE_ROOT`. Candidate
  status appears on every response/source. It rejects free-text interpretation,
  forged settings, stale tokens/results and cross-mode actions. Source clicks read
  current candidate integrity; failures do not supply cached quotes. Waits are
  bounded to 15 seconds with manual retry.
- The default graph chat and approved MabSelect route remain separate. No recipe
  transfers between Protein A/G Sepharose and MabSelect, no deposit is inferred
  from pressure alone, and no numerical pressure limit, missing flow/volume,
  contact time, performance guarantee or operational authorization is invented.

## Non-activation and withdrawal boundary

Preparation creates only `release.json`, `sources.json` and `mapping.json` in a
fresh directory. State is `staged`, `awaiting_user_review`, `not_authorized`.
It never writes an active pointer or approval, overwrites a previous candidate,
touches private MabSelect authority or installs dependencies/models.

Server-side withdrawal simulations can create a different candidate withholding
source/review units. Missing E166-W or Q04 suppresses the complete ethanol option
and its procedural quote while Q03 detergent support survives. Missing Q01 blocks
pressure-journey procedures dependent on that indication. Candidate edits after
opening fail closed. These are immutable candidate scenarios, **not a live,
durable revocation feed or an activated serving registry**. A later activation
requires review and a separate explicitly authorized transition; none is provided
or performed here. Original review publication flags remain unchanged.

## Tests and retained history

The 16 service tests cover all product/context combinations, source provenance,
quantities/immediacy, alternatives, no recipe transfer, clarification, scoped
pressure refusal, missing/changed authority, immutable preparation, joint quote/
digest tampering, mid-request changes and source/review withdrawal simulations.
The 12 Chainlit tests use real service lookups and captured transport over temporary
candidate directories, including exact source/review rendering, submitted scope,
manual retry, stale results, forged controls and cross-mode isolation. Network
connections and graph-agent calls are guarded against in those callback tests.

The first 58-test focused run had one assertion failure because a rendered source
ID was checked without its existing Markdown escape. The assertion now checks
the literal renderer's escaped value; the withdrawal case also checks actual
source-action references. Outside-product wording and focused missing-field text
were clarified before final verification. That initial log is preserved.

A candidate-focused run passed **58 tests** in **78.615 seconds**: 16 service,
12 candidate UI, 24 existing MabSelect UI and six legacy app tests. This is known-
source conformance evidence, not a blinded answer-quality or independent benchmark.

A separate ignored candidate was prepared at
`.local-tools/sepharose-backpressure-candidate-v01`. Its three artifact byte hashes
match a fresh preparation with the same version and code. A read-only Protein G
hydrophobic/pressure query returned partial support with `serving_activated=false`.
No active pointer exists. Prepared artifacts/raw logs stay local; code and the
guide reproduce them without credentials or a PDF.

The browser smoke on the separate staged candidate confirmed unknown-field
clarification without a recipe, a Protein G hydrophobic/pressure request with
separate alternatives and pressure abstention, and E166-W's exact warning, PDF
page 166 and Q04 provenance. Every result/source showed the non-activated notice.
The console retained three `Unauthorized` entries during sign-in/startup; the
authenticated scenarios completed. The tab and loopback test server were closed;
candidate artifacts persist read-only for review. No error-free-console or
independent acceptance score is claimed. Screenshots and logs remain ignored.
Legacy extraction-level pending flags are preserved, with scoped documentary
decisions displayed separately; no global source approval is fabricated.

Complete-suite confirmation and preservation results follow the retained race
diagnostic below.

## Existing tracing test race exposed by the full run

The first full run executed **1,043 tests** in **602.378 seconds**, with one error
and one optional PDFium skip. The existing
`test_evaluation_has_real_parent_child_spans_and_correlating_header` raised
`StopIteration` because its collector did not yet contain the HTTP SERVER parent.
The same unchanged test passed in isolation (1.039 seconds); that alone was not
treated as proof of resolution.

A new controlled regression holds the root span immediately before `end()` after
the client has received the response bytes. It failed against the original test
fixture: `flush()` returned the child before the root had ended. The fixture now
tracks active HTTP handlers with a condition and waits, bounded to five seconds,
for handler completion before flushing. The real production request/trace code,
parent/child assertions, export handling and Windows protections are unchanged.
The regression uses events rather than adding a blanket sleep or retry. Initial
failed-suite, isolated-diagnostic and red-regression logs remain separate.
The subsequent focused verification passed **87 tests** in **147.154 seconds**:
29 tracing tests (including the new race regression), 16 service tests, 12 new UI
tests, 24 MabSelect UI tests and six legacy app tests. No candidate/runtime code
changed for the tracing-fixture correction; the prepared candidate's hashes remain
valid. A new full confirmation is performed rather than treating the isolated
pass as a clean complete suite.

## Final confirmation and preservation

The corrected complete suite executed **1,044 tests: 1,043 passed, one optional
PDFium preview skip**, no failures/errors, in **602.186 seconds**. All runtime and
test code was stable during this confirmation. This includes 16 service tests,
12 candidate UI tests and the additional existing-tracing race regression.
Timings are descriptive, not a performance comparison.

Both original freezes verify with their recorded environment: v03 keeps 36 pins
and MabSelect 52. Byte inventories match for the nine private registry files,
636 original workspace files (including the 16 excluded notes) and 109 active
pilot/previous-trial files. The three prepared candidate artifacts remain byte-
identical to their reproducible preparation, with no active pointer, approval or
activation. Existing source/review data, serving registry/core and MabSelect UI
code are unchanged; the only existing production file extended is `app.py`.
The other existing-file correction is solely in the tracing test fixture.
New operator/report links resolve and the tracked diff has no whitespace errors.

The separate candidate is ready for human review of mapping/scope and the future
activation boundary. No live Protein A/G release, durable withdrawal authority,
scientific approval, commit or push is claimed or performed.

## Use and remaining gate

See [the candidate operator guide](../CHAINLIT-SEPHAROSE-CANDIDATE.md). The next
human gate is review of this separate candidate and its mapping/limits, **not**
approval to expand the active private MabSelect registry. Public deployment,
persistent chat resume, new model/architecture evaluation and production withdrawal
authority are outside this implementation. No commit or push was performed.
