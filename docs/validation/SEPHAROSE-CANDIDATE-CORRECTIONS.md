# Protein A/G Sepharose — corrected candidate review

Reviewed on 5 November 2026 against main `28775130a9500bf202f67c60151bac53f2c8027c`.
This is a staged documentary candidate, not an activated release or new freeze.

## Findings and corrections

The pre-correction review reproduced two P2 findings using disposable candidates:

1. With Q01 held and Q09 available, the clarification bundle copied the original
   combined message and repeated Q01's cleaning indication. Conversely, holding
   Q09 left its clarification question in Q01's combined summary.
2. With Q01 held and context unknown, the guidance state became `partial`, hiding
   the focused clarification UI despite Q09 remaining eligible.

The service now gives each eligible scope its own summary. Q01 owns the cleaning
indication; Q09 owns product/context clarification or separation from MabSelect.
Neither copies the original combined message. The conditional option titles and
original quotations, quantities, source records and human decisions are unchanged.
Shared original excerpts remain readable only under a complete eligible review;
that legitimate provenance is distinct from a generated response's review scope.

An eligible Q09 clarification now retains `needs_clarification`, including when
numerical pressure is independently refused. `held_review_scopes` records missing
support separately on the guidance item. Chainlit keeps the supplied product,
asks only for the missing context and identifies the held scopes separately. A
withdrawn Q09 emits no clarification summary. When both Q01 and Q09 are held,
the response remains quarantined without bundles or citations.

## Tests and local preparation

Six regression methods were added: four service tests and two Chainlit transport
tests. They cover both directions of summary isolation, clarification combined
with a pressure refusal, complete quarantine and the rendered missing-field/hold
messages. Three selected regressions failed against the original implementation
before correction; the retained red log demonstrates reproduction.

The corrected focused run passed **64 tests in 69.190 seconds**: 20 candidate
service tests, 14 candidate UI tests, 24 existing MabSelect UI tests and six app
tests. The previous 1,044-test full-suite result belongs to the initial version;
it is preserved in the [implementation report](SEPHAROSE-CANDIDATE-IMPLEMENTATION.md).
The delivery inventory records the corrected complete-suite result separately.

The corrected complete suite executed **1,050 tests: 1,049 passed and one optional
PDFium preview test skipped**, with no failures/errors, in **631.375 seconds**.
Runtime and test code remained unchanged during that run. A separate local check
also exercised 36 product/context/question combinations against corrected v02
and verified every delivered source view. These overlapping checks are not
additional independent acceptance questions.

The corrected code was prepared in a new ignored
`.local-tools/sepharose-backpressure-candidate-v02` directory, with release ID
`sepharose-backpressure-candidate-v02`. The three original v01 files were not
overwritten. Their previous code pins refuse delivery after the correction.
Neither candidate is activated. Preparation is reproducible from the operator
command, using the existing reviewed sources; generated local artifacts are not
part of the delivery.

## Review outcome and remaining boundary

The two reproduced findings are corrected. Quantities, conditions, alternatives,
warning dependencies, source identity and scoped decisions remain intact. Holding
E166-W or Q04 still removes the whole ethanol route while independent detergent
support remains. Holding Q01 still blocks dependent procedures. Tampered material,
stale citations and missing candidate files fail closed.

These are conformance and regression checks on known reviewed excerpts, not an
independent retrieval benchmark, operational authorization or scientific review.
The existing browser smoke described in the implementation report predates these
corrections; no new browser trial is claimed. Corrected rendering is checked via
the real adapter and captured Chainlit transport.

Ready for a scoped delivery and a later explicit freeze decision. No activation
workflow or durable live withdrawal authority has been introduced. The private
registry, both frozen closures, 16 excluded notes, pilots and previous experiments
remain outside this lot. See the [delivery inventory](SEPHAROSE-CANDIDATE-PACKAGE.md)
and [operator guide](../CHAINLIT-SEPHAROSE-CANDIDATE.md).

Post-run byte inventories match for nine private-registry files, 636 original
workspace files including the notes, 109 pilot/previous-trial files and all three
original candidate artifacts. Both recorded freezes verify with their environments
and unchanged method locks (36/52 pins). HEAD and the empty index are unchanged.
