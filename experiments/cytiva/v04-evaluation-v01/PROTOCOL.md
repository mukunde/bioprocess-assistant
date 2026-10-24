# Frozen v04 prospective challenge W01-W12

Prepared 24 October 2026 from main 081a30d. **No W question has been searched,
planned, ranked, assembled or scored. All twelve question/reference associations
await human review.** The method lock was written before query/reference JSON.

## What is frozen

The unchanged CompositionalContextIndex and v04 configuration, inherited lexical
and atomic-assembly dependencies, reviewed source policy and local tokenization
helpers are bound by LF-normalized SHA-256 in method-lock.json. The harness and
its legacy evaluation helpers are separately bound by the preparation manifest.
BM25 k1=1.2/b=0.75, six selected seeds, 0.65 fallback cutoff, finite FR/EN aliases,
clause/negation rules, family composition and round-robin order are unchanged.
Full serialized context is capped at 2,048 cl100k_base tokens; this excludes any
future prompt/answer. Python 3.13.0, tiktoken 0.12.0, the cached asset hash and
PYTHONHASHSEED=0 are recorded. No model/tokenizer download fallback is permitted.

The active W test file is deliberately outside immutable method dependencies.
Tests do not participate in retrieval; future fixture maintenance must not force
a rewrite of a method lock, historical manifest or saved result. Existing v03b
preparation/results and v04 development artifacts remain unchanged. The original
pending preparation flags remain historical; later human decisions belong in a
separate ignored review record. No such approval record is generated here.

## Scope and novelty limits

Twelve intents have EN/FR formulations (24 correlated cases, not 24 independent
observations). The corpus remains the same 25 eligible reviewed source atoms on
pages 118-121. The author knows the v03b failures and v04 implementation. Related
C/H/V intents and overlapping source facts are disclosed. This is a prospective
same-corpus challenge with new wording/compositions, not independent authorship,
a new section/manual, a blind benchmark or a scientific evaluation.

| ID | New challenge |
|---|---|
| W01 | Unresolved identity and unspecified intended application |
| W02 | Direct-use permission and a separate Blue applicability decision |
| W03 | Elution comparison with a postposed exclusion of washing |
| W04 | Imperative exclusion of loading and elution |
| W05 | Binding formulations combined with washing, without elution settings |
| W06 | Loading range and the column-specific approximate syringe note |
| W07 | HIC screening combined with a separate Blue buffer-preparation task |
| W08 | Conditional IEX residual-contaminant explanation and HIC alternative |
| W09 | Supported washing plus an unavailable pressure parameter |
| W10 | Pending IEX pH/pI condition without reconstruction |
| W11 | Pending equilibration combined with supported washing |
| W12 | Labelled synthetic contradictory include/exclude request |

No W query or reference is fed to development search or navigation during
preparation. Only exact source bundles may be token-counted for feasibility.
No result prediction is used to change reference scope or the method.

## Reference review

questions.json holds text, ID, family and a synthetic-case flag only. Reference
answers, source requirements and criteria are separate in references.json.
All 25 eligible original quotations are included with PDF identity, page labels,
text offsets and quote hashes. Each question has required source sets including
transitive headings/warnings, acceptable additions, explicitly unrequested source
IDs, expected answer, reservations and overlap disclosure. The English expected
answer is a review reference, never a model output.

A whole source atom may contain adjacent information not requested in the answer.
For example, the buffer atom includes both binding and elution formulations, and
the loading/footnote atoms include both column sizes. Such text is retained intact;
answer reservations prohibit transferring or adding those settings. Source-level
noise is not a sentence-level answer correctness measure.

E118-I and E121-EQ remain excluded from indexing and context, including indirect
dependencies. W10/W11 validation does not approve them. W09's pressure absence
assertion applies only to the 25 eligible excerpts; it does not cover whole pages,
the full manual or external product documentation. A lexical absence check is
preparation support, not a substitute for human semantic review.

W12 is synthetic test data, never a manual fact or harness instruction. Review
whether its contradictory request should allow only neutral protocol scope and
warning before clarification. The recorded phase-conflict flag is assessed, but
no generated clarification or refusal is evaluated.

For W09-W12 the frozen reference also specifies observable diagnostic criteria:
selected-corpus/source limitations, unavailable roles, or conflict/incomplete
navigation flags. These are evaluated from saved metadata; the verifier does not
call a language parser or regenerate a navigation plan to score them. Human
review covers these criteria as well as passages and answers.

## Separate human review and execution guard

Use a separate local ignored human-review.json at
`data/experiments/cytiva/v04-evaluation-v01/`. It must bind the final preparation
manifest and method-lock digests and contain exactly W01-W12, each with a validated
or validated_with_reservation decision, original human quotation, UTC timestamp,
canonical question/reference hashes and the exact retained reservations.
Canonical hashing is compact sorted JSON with ensure_ascii=False. No status or
quote is fabricated. Hashes establish consistency, not reviewer authentication.

Incomplete, duplicate, altered or wrong-freeze decisions block runtime creation
and measurement output. All decisions plus an explicit instruction to execute
are required. If references need correction before measurement, keep this packet
and create a distinct revision with the same method lock. After inspecting
results, any tuning becomes development and needs another prospective set.

## Fixed execution and acceptance rule

One exclusive run directory:
`data/experiments/cytiva/v04-evaluation-v01/locked-run/` (not created now).
W01-W12 in order, EN then FR. Three timing repetitions must return identical
complete results, including navigation metadata; never choose a best repeat.
Setup time is separate from warm retrieval/assembly timing. There is no retry,
refreeze or overwrite command. Preserve partial contexts and failure diagnostics,
with all unexecuted formulations counted against the planned 24.

Retrieve using query text only, with no reference answer/required IDs/decision
in the index or query. Save every unscored context before applying gold reference
metrics. Preserve input/review snapshots and record exact contexts, raw top-six
hits, seeds, dropped roles, whole-bundle budget exclusions, token counts,
source-support limitations, phase conflicts and all timing samples. Verify quote
serialization, dependencies, token cap, source eligibility, no network attempts,
unchanged review, unchanged freeze and byte-level preservation of earlier files.

Report completeness by intent and language, required-source coverage,
outside-acceptable context (a noise proxy, not validated precision), explicitly
unrequested sources and reference diagnostic failures. Expected answer statuses
remain unscored references. No LLM, embeddings, paid API, database mutation,
scientific answerability score or generated-answer evaluation is involved.

**Predeclared gate:** complete required evidence for all twelve intents in both
languages, zero explicit unrequested-source intersections and zero failed
reference diagnostic criteria, with no hard invariant violation. Other
outside-acceptable context is reported separately; no unreviewed precision
threshold is added. A pass permits considering a limited end-to-end pilot only;
it never automatically adopts the retriever or proves generalization.

The original six-seed cap and structural navigation flags remain unchanged. Any
dropped requested seed stays visible even if reference completeness passes;
a source-support limitation may be expected without being an execution error.

## Commands from the repository root

Integrity only, no search or planning:

```powershell
.\.venv-ingestion\Scripts\python.exe -S -m experiments.cytiva.v04_evaluation
```

Synthetic harness/integrity tests only; no real W wording reaches retrieval:

```powershell
.\.venv-ingestion\Scripts\python.exe -m unittest tests.test_v04_evaluation -v
```

Later, only after the complete human review and authorization to execute:

```powershell
$env:PYTHONHASHSEED = '0'
.\.venv-ingestion\Scripts\python.exe -m experiments.cytiva.v04_evaluation --run --review data/experiments/cytiva/v04-evaluation-v01/human-review.json
```

This measurement command has not been executed. No original PDF, model weights,
private local inventory or complete raw runs are added to Git. See the
[v04 development report](../../../docs/experiments/cytiva-compositional-context-results.md),
[reviewed source package](../reviewed-contaminant-questions/README.md), and
[previous frozen v03b outcome](../reviewed-v03b-evaluation/README.md).
