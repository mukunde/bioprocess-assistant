# Frozen section-only candidate and prospective questions

Prepared 24 October 2026. **Not executed; all ten question references await human
review.** No extraction LLM, embedding model, paid API or database is used.

## Scope

This is a prospective **same-corpus challenge**, not an unseen-section, blind or
statistically independent validation. Sources on pages 118–121 and C01–C10 were
already inspected. H01–H10 introduce applicability decisions, combinations and
eligibility boundaries but reuse facts; references disclose related development
intents. FR/EN are paired formulations of ten intents, not twenty independent
observations. The drafting assistant knows the method and corpus: authorship is
not independent. No query ranking or new-query result was inspected in preparation.

`questions.json` contains query text only. `references.json` contains expected
answers, required sources, acceptable additional context, reservations and exact
source quotes/page offsets/hashes. New associations and FR/EN equivalence need
human review. Historical source preparation flags are copied unchanged; current
scoped source decisions reside in the existing reviewed-contaminant package.

## Frozen method

`candidate.json` selects the existing ablation's **section** arm: BM25 k1=1.2,
b=0.75, six positive hits, original bilingual bridge, source ancestry in index
text, **no new vocabulary projection**, unchanged section/unknown-contaminant
rules. The original retrieve function is reused with `sections=True` and
`VocabularyIndex(..., None)`. Atomic dependencies, whole overviews, score/ID
ordering and the 2,048-token serialized-context cap remain unchanged. No quote
truncation, gold-reference expansion, query rewriting, default change or tuning.
The cap excludes a future answer prompt/output. E118-I and E121-EQ remain excluded
from index and contexts, including indirect dependencies. H10 does not require
excluded evidence to pass: it checks located reviewed protocol scope while the
future answer must withhold unreviewed equilibration settings.

The manifest pins LF-normalized SHA-256 of method, source policies, corpus,
existing review, questions, references, protocol and safety tests. Python and
tokenizer versions, cached tokenizer asset and hash seed are pinned. Hashes
establish consistency, not identity authentication or independent review. There
is no refreeze command. The existing application and experiments are unchanged.

## Human reference review before any measurement

1. Run integrity verification below; do not search H01–H10 during preparation or
   review, and do not inspect their rankings or scores.
2. Review each question against its preserved passages: bilingual equivalence,
   indispensable and acceptable sources, quantities/conditions, expected status,
   answer and reservations. Keep source uncertainty explicit.
3. Record decisions separately, bound to the exact manifest digest. The runner
   requires JSON with `manifest_sha256_lf` and exactly ten `decisions`; each needs
   `question_id`, `decision` (validated or validated_with_reservation), original
   `human_quote` and `reviewed_at_utc`. These records document decisions, not
   cryptographic reviewer authentication. No approval is supplied by preparation.
4. A correction before measurement creates a new reference/package version with
   the same method and archived v1. Rejected/changed references block this version.
   A new semantic reservation must be in the reviewed reference, not only a log.
   Once results are opened, any correction/tuning becomes a new development trial
   requiring different prospective questions; never replace this trial's results.

## Fixed measurement and decision gate

One candidate, H01–H10 in order, EN then FR. Reuse the original three-repetition
retrieve function for same-process timings (not three independent question
samples); keep its returned context, never the best repetition. Report setup
separately; per-question timings are not a production cold-start benchmark.
Save every unscored context before loading references for scoring. Only source
quotes/metadata and query text enter retrieval and assembly.

The fixed ignored `locked-run` directory is created exclusively. Existing success,
failed or interrupted output blocks another run for this ID. No automatic retry,
removal, fallback provider, source-status promotion or post-result method change.
Network connections/DNS are guarded in Python; this is not an OS firewall.

Report raw results per intent/language:

- required evidence coverage, missing IDs and completeness for EN, FR and both;
- IDs outside pre-annotated acceptable context; subset tokens include their own
  JSON wrapper, not marginal token cost. This is a reference-dependent noise
  proxy, not validated precision or a judgment that extra text is false;
- exact context tokens, whole-bundle exclusions, overview status and warm timings;
- pending-source leakage, quote/provenance identity and atomic dependency checks.

A hard error stops the trial and records remaining formulations as unexecuted,
not successful or removed from the planned denominator of twenty. Expected
answer statuses remain references: no answer generation, semantic refusal score,
scientific validation or industrial suitability is evaluated.

**Pilot gate:** any missing indispensable source or hard invariant violation
blocks adoption. Preserve failures for diagnosis without changing this method.
Even 10/10 only supports considering a small end-to-end pilot, not generalization
or automatic adoption. This is a conservative pilot gate prepared for human
review, not an industrial acceptance standard.

## Commands (repository root, PowerShell)

Standard-library integrity verification performs no search:

```powershell
.\.venv-ingestion\Scripts\python.exe -m experiments.cytiva.section_evaluation
.\.venv-ingestion\Scripts\python.exe -m unittest tests.test_section_evaluation -v
```

Only **after complete recorded human review**, with the pinned local environment
and cached tokenizer (not executed during preparation):

```powershell
$env:PYTHONHASHSEED = '0'
.\.venv-ingestion\Scripts\python.exe -m experiments.cytiva.section_evaluation --run --review data/experiments/cytiva/section-evaluation-v01/human-review.json
```

Outputs remain ignored local artifacts. Original trials, reviews and serving
knowledge stay unchanged. Source PDF and model weights are not redistributed.
See [the latest ablation](../../../docs/experiments/cytiva-contaminants-context-results.md)
and [the roadmap](../../../docs/ROADMAP.md).
