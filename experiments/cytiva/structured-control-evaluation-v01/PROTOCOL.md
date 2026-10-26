# Frozen structured-control challenge S01-S12

Preparation only, 26 October 2026. The corrected structured method, source policy,
software identities, scorer and runner are locked before the new question/form/
reference files are finalized. Human reference review is pending; no trial is run
by preparation or integrity verification.

## Scope and limitations

This challenge evaluates the S structured-control arm only. It is not v06
free-text parsing, an S/F comparison, answer generation, scientific validation,
or unrestricted retrieval over the manual. Twelve scenarios have EN/FR wording
and 24 corresponding machine submissions. Only the submitted JSON reaches the
runtime; wording and reference answers are human-review material, never runtime
prompts. Paired submissions are correlated observations, not 24 independent tests.

The author knows the method, sources, prior X results and conformance cases.
These are new compositions on the same reviewed corpus, not a blinded,
independently authored holdout or a new-section generalization claim. The old
12-plus-6 proposal is not silently treated as an approved dataset mandate; this
preparation proposes 12 cases for actual review.

The corpus is the existing 25 eligible excerpts on PDF pages 118-121, initially
HiTrap Blue HP 1 mL/5 mL plus general IEX/HIC/SEC principles. E118-I and E121-EQ
remain excluded. An unsupported/quarantined request can have a review passage
explaining its limit, without making that passage required admitted context.
Exact source quotes, page/index, document identity, offsets and hashes are copied
from the existing registry; no source review is created by this packet.

## Frozen procedure and scoring

- The method lock pins runtime, catalog, schema, role adapter, source/approval
  inputs, exclusion-scope clarification, runner/scorer, Python, dependencies,
  hash seed 0, tokenizer identity and local asset hash. Active test files are
  intentionally not immutable method dependencies.
- Each approved submission is executed exactly once in fixed S01-S12 order,
  EN then FR. No best-of repeats, hidden retries or adjustment after results.
- The runtime retains its global six-root/2,048-token budget, atomic dependencies
  and warnings, deduplication, scoped bindings and admissible-item interleaving.
- Save all 24 unscored outcomes before scoring. Runtime errors remain explicit
  failed outcomes, not omissions from denominators. Initialization/elapsed times
  are descriptive only. Runtime initialization excludes lazy tokenizer setup;
  the first evaluate call includes that setup. No p95 target or speed claim is made.
- Score exact per-unit interpretation/support/summary states, required diagnostic
  codes, per-task/stage/column/facet bindings, direct and complete supporting
  source sets, explicit aggregates, and context/source/resource integrity. Recount
  the whole serialized context including bindings using the pinned tokenizer.
- A blocked unit must have no binding or direct-source assignment, even when an
  admissible sibling legitimately shares its source atom. Adjacent printed
  formulations/column values are not themselves answer leakage; bindings and
  later answer rendering are distinct evaluation levels.
- Compare paired critical plan semantics after ignoring display reason wording
  and application request IDs. Both language scores and pair differences remain
  visible. A wholly clarifying system cannot pass supported-reference cases.
- The bounded gate requires all 24 outcomes and all 12 bilingual pairs to meet
  their reviewed references, with zero hard integrity/policy/resource violations.
  This is a challenge gate for review, not an approved production guarantee.
  Reference answers are not scored as generated answers because none are generated.
- No assertion that every proposed full bundle fits the budget is obtained by
  running it in preparation. A later budget failure remains visible and attributable;
  do not rewrite references to match outputs. Any post-run change needs a new version.

## Human review and run gate

Review each bilingual wording, actual form, task/item ownership, states, numeric
attribution, required passages and reservations. Earlier approvals do not approve
these new mappings. Decisions must quote actual human messages, preserve all
reservations and bind the question, submission and reference hashes plus method
lock and preparation manifest. Collective approval can be recorded as one actual
collective message, never fabricated as separate exchanges.

The frozen `review-template.json` has pending placeholders and cannot authorize
execution. Copy it to a separate private review file, fill actual decisions and
the manifest hash returned by verification, and preserve the template. Completing
or changing references before any run requires a new preparation manifest and
review binding; do not edit the locked method to accommodate them.

```powershell
# Integrity and schema checks only; does not construct StructuredControl.
.venv-ingestion\Scripts\python.exe -m experiments.cytiva.structured_evaluation
```

Only after the actual review and an explicit request to execute:

```powershell
$env:PYTHONHASHSEED = '0'
.venv-ingestion\Scripts\python.exe -m experiments.cytiva.structured_evaluation --run --review data/experiments/cytiva/structured-control-human-review.json
```

The gated run reserves a new private `locked-run` directory with exclusive
creation, snapshots inputs/review, blocks all network connects/DNS, preserves
earlier tracked/experimental files, and refuses existing output. Failures retain
partial output and a failure record. Verifying integrity remains safe after a
completed run and never deletes results. No model, paid API or automatic adoption
is part of this procedure.
