# Frozen v05 challenge X01-X12: pending human review

Prepared 25 October 2026 from main a6026ca. **No X query has been searched,
planned, ranked, assembled or scored. All twelve references await human review.**
The method lock was written before the new question/reference JSON files.

## Locked method

The exact `ingestion.polarity_passage_context.CompositionalContextIndex`, v05
configuration, inherited lexical/assembly code, reviewed source policy and local
tokenization helpers are bound by LF-normalized SHA-256 in `method-lock.json`.
The harness and inherited evaluation helpers are separately bound by `manifest.json`.
No alias, negation rule, task routing, conflict behavior or threshold was changed
while preparing this packet.

BM25 k1=1.2/b=0.75, six seeds, fallback ratio 0.65, family round-robin ordering
and the 2,048-token serialized-context limit are unchanged. This limit excludes
any future prompt/answer. Python 3.13.0, PYTHONHASHSEED=0, tiktoken 0.12.0 and the
cached cl100k_base asset hash are recorded. There is no download fallback.
Active evaluation tests are outside immutable method dependencies, so future
fixture maintenance need not rewrite a historical lock.

## What this challenge tests

Twelve intents have English and French formulations: 24 correlated cases, not
24 independent observations. The author knows the implementation and earlier
C/H/V/W failures. The source facts overlap those development questions. This is
a new wording/composition challenge on the same 25 reviewed excerpts from PDF
pages 118-121, not independent authorship, a new manual/section or a blind benchmark.
Reference scope is derived from the question and documentary passages, not from
observed navigation outputs. No result is predicted or used to change the method.

| ID | Focus | Documentary seeds |
|---|---|---|
| X01 | Unresolved protein identity and unchosen intended application | E118-USE, E118-C, E118-M |
| X02 | Different interference conditions for two laboratory preparations | E118-USE |
| X03 | Washing with an omit instruction for other phases | E121-W |
| X04 | Sample application instead of elution | E121-L |
| X05 | Binding formulations plus loading, without other operating phases | E121-B, E121-L |
| X06 | Loading/washing requests for separate column sizes | E121-L, E121-W |
| X07 | A negated exclusion that still requests both washing and elution | E121-W, E121-E |
| X08 | A product named only to rule it out of scope | E119-A, E119-I, E119-H |
| X09 | Two supported phase requests plus unavailable pressure | E121-L, E121-W |
| X10 | Two withheld source roles plus supported general/washing context | E118-M, E121-W |
| X11 | Separate-task inclusion/exclusion is not a global contradiction | E121-E, E120-A |
| X12 | Same-task contradictory washing instructions require clarification | E120-P, E121-PH |

X11 and X12 are labelled synthetic scope controls. Their task instructions are
not claims that the manual contradicts itself. X11 deliberately distinguishes
valid scopes assigned to separate preparations from X12's same-task conflict.
The parser's known limits are disclosed, but no actual X plan is inspected.

## Reference material and human decisions

`questions.json` holds ID, family, bilingual question and synthetic-case flag only.
`references.json` contains expected answers, transitive required source bundles,
acceptable additions, explicitly unrequested sources, diagnostic expectations,
reservations and related earlier intents. These references never enter ranking.
All 25 eligible original quotes are copied with document identity, PDF page/index,
text offsets and quote hashes. No new PDF conversion or visual inspection is
claimed. The existing source review manifest is bound unchanged.

Required bundles preserve headings, cross-page scope, warnings and footnotes.
Whole atoms can include adjacent material not requested in an answer: the buffer
atom includes both binding and elution formulations, and the loading/footnote
atoms include two column sizes. Keep those atoms intact; answer reservations
prohibit transferring settings or adding unwanted instructions.

E118-I and E121-EQ remain excluded from indexing and context, including indirect
dependencies. X10 does not approve either source. E119-I is a different, eligible
excerpt. X09's pressure absence is limited to the 25 eligible excerpts, not the
whole manual, product documentation or every passage on those pages.

Review each X intent against both language formulations, its exact passages,
expected answer, required/acceptable/excluded sources and diagnostic criteria.
Record actual decisions separately in the ignored local file
`data/experiments/cytiva/v05-evaluation-v01/human-review.json`, preserving original
human quotations, UTC recording times, canonical question/reference hashes and
reservations. No approval record is created during preparation. The original
pending flags and preparation manifest must remain historical after review.

If review changes question/reference content, preserve this packet and create a
new reference version with fresh bindings; do not silently mutate the reviewed
freeze. A source or method change requires a new method version and challenge.

## Evaluation gate and execution, only after review

The default command verifies integrity only:

```powershell
.\.venv-ingestion\Scripts\python.exe -S -m experiments.cytiva.v05_evaluation
```

Do not run the following until all twelve decisions have been recorded and the
user has requested execution:

```powershell
$env:PYTHONHASHSEED = '0'
.\.venv-ingestion\Scripts\python.exe -m experiments.cytiva.v05_evaluation --run --review data/experiments/cytiva/v05-evaluation-v01/human-review.json
```

The runner verifies the freeze and all human decisions before runtime creation
or output reservation. It exclusively reserves `locked-run/`, snapshots inputs
and review, and blocks network access. Each formulation has three timing repeats;
serialized results must agree, with no best-repeat selection. All 24 contexts
are saved before reference scoring. Any failure retains partial results and
blocks retry/overwrite; earlier trials remain protected by hashes.

The predeclared gate requires all twelve intents to have a complete required
source set in both languages, zero explicitly unrequested-source violations and
zero required diagnostic failures. Report per-question missing IDs, source
coverage, outside-reference noise, tokens, budget/cap exclusions, unavailable
roles and timings. Outside-reference context is a noise proxy, not validated
precision. Missing source support can be an expected diagnostic rather than a
failure, as for X09/X10.

Diagnostics include phase conflicts, unavailable roles, source limitations,
navigation/source-support completeness, and the planner's clarification flag.
X07/X11 require no false clarification conflict; X12 requires a true conflict and
withholding of operating sources. These are context/metadata checks, not tests
of an actual generated clarification or correct per-sample answer attribution.
Expected response statuses are human reference labels, not predicted outputs.
Answer quality is not evaluated and automatic adoption remains disabled.

Only source bundles may be token-counted during preparation to check feasibility;
no X query is used for that check. Synthetic harness tests use synthetic text and
temporary outputs, with no real X retrieval. Frozen v04, v05 development attempts,
their reviews and their results remain unchanged.
