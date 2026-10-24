# Scoped source-context variant after H02/H09 failures

Prepared and measured on 24 October 2026. **Development correction after opening
H01–H10 results; not a new independent benchmark.** The original frozen candidate,
its ten human decisions and its 8/10 result remain unchanged. No application
default, source approval, reference answer or historical result is updated.

## Changes and scope

The opt-in [runtime](../../ingestion/scoped_passage_context.py) and
[v03b configuration](../../experiments/cytiva/section_navigation_v03.json) add:

1. A declared FR/EN lexical projection on both query and index text, retaining
   original quotations/provenance separately. It includes albumin/transferrin,
   antibody/host terms and phase wording; this is a finite dictionary, not a
   translation model or semantic retriever.
2. Source-role navigation for underspecified contaminant questions, without
   requiring two named techniques. General principles and applicability passages
   can be restored through explicit source-role links even if they rank poorly.
3. Scope/phase filtering instead of automatically appending the first section
   encountered among global lexical hits. Loading, washing, elution, formulations
   and equilibration are separate roles. Warnings, headings and notes remain
   transitive atomic dependencies. Unavailable roles are reported, never replaced
   with another phase's settings.
4. A limited explicit contrast rule: when a main phase precedes `rather than` or
   `plutôt que`, phase names in the excluded tail are not selected as requested
   phases. This is not a general negation or comparison parser.

Runtime receives source corpus, source policy, navigation configuration and query
text only. No H/C IDs, expected answers, required-source sets or human decision
messages enter ranking or assembly. The source-role map and route rules are
manually prepared experimental navigation policy, not newly approved scientific
facts or an automatically learned ontology. Supported families are currently
limited to the reviewed general/bovine/albumin/Blue corpus.

BM25 k1=1.2/b=0.75 and the 2,048-token serialized-context cap are retained. Up to
six **scope-selected seed units** are assembled with dependencies: this is a new
navigation strategy, not unchanged global top-six retrieval. Results preserve
raw lexical top-six hits separately from selected seeds, filtered hits, route
reason, unavailable roles and exclusions. Full dependency bundles are skipped
rather than truncated if over budget. No named route means a bounded strong-hit
fallback within the best hit's source family, with no automatic section overview;
its relative-score cutoff of 0.65 remains an uncalibrated development choice.

## Preserved development iterations

Both new ignored runs retain their exact code/config/reference snapshots:

- `data/experiments/cytiva/section-navigation-v03/runs/development-a/`
- `data/experiments/cytiva/section-navigation-v03/runs/development-b/`

Preparation regressions first exposed unrecognized French `je charge` in C10;
that explicit loading phrase was added before measured run A. A recovered H02
and H09 but still retained loading/washing passages for H10 because those phases
were mentioned as alternatives the question explicitly sets aside. Its noise
proxy nevertheless read zero: those passages are allowed additions in the fixed
H10 reference. Inspection therefore motivated the explicit contrast rule and a
new regression, measured as B in a new directory. A and its inputs are archived,
not overwritten; H10 reference annotations are not tightened after the fact.

The final code/configuration corresponds to revision B. To inspect A, use its
`input-snapshot`, not the current source files. The [original frozen trial](cytiva-section-evaluation-results.md)
and its `locked-run` are neither modified nor re-executed by the new launcher.

## Development results

All values below concern required source presence, not answer correctness.
Both languages are required for a complete intent; language pairs are not
independent observations. H and C were already known during development.

| Metric | Recorded section-only | Development A | Development B |
|---|---:|---:|---:|
| H intents complete in both languages | 8/10 | 10/10 | 10/10 |
| H EN / FR complete | 9/10 / 8/10 | 10/10 / 10/10 | 10/10 / 10/10 |
| H mean context tokens | 1578.65 | 643.40 | 593.40 |
| H maximum context tokens | 2000 | 993 | 993 |
| H contexts outside annotated acceptable IDs | 19/20 | 0/20 | 0/20 |
| C intents complete in both languages | 10/10 | 10/10 | 10/10 |
| C mean context tokens | 1725.70 | 733.20 | 733.20 |
| C maximum context tokens | 2027 | 1222 | 1222 |

Revision B reduces mean H context by **62.41%** and mean C context by **57.51%**
against their recorded section-only baselines, without losing indispensable
sources on these known references. C has no equivalent reviewed acceptable-extra
annotation, so its context-noise/precision measure is **unknown**, not zero.
For H, zero outside-reference IDs is a scoped proxy, not independently validated
precision or proof that every retained token is necessary, as A's H10 illustrates.

### Corrections and remaining source limit

- **H02 FR:** the general-characteristics route retains E118-C and E118-M with
  E118-USE; both languages have the same three IDs in a 614-token context. The
  new lexical bridge also aligns the previously mismatched French terms.
- **H09 EN/FR:** unknown identity wording plus purification context reserves
  E118-USE/E118-C/E118-M without naming IEX/HIC/SEC. Both contexts are 614 tokens;
  there is no diagnosis or answering-status decision in this navigation rule.
- **H10:** revision B keeps only E120-H/E120-W/E120-P/E121-PH (493 tokens in each
  language). Requested equilibration is reported unavailable; loading, washing,
  elution and E121-EQ are absent. The two unavailable-role records correspond to
  this expected source-review boundary, not execution errors.

**E118-I and E121-EQ remain excluded from index statistics and every context.**
No source approval or new scientific claim was inferred. H10 source-scope success
still does not demonstrate an actual model's refusal or review-status explanation.

## Validation and preservation

**21 new regression tests pass; the full local suite passes 381 tests.** Existing
application/ingestion dependency environments were used, not a fresh installation.
Tests cover the H02/H09 fixes, all seen H/C references, role/phase scope, explicit
phase contrasts, source quote identity, atomic notes/warnings, pending-source
blocking, missing-role reporting, budgets, no-positive-hit behaviour, output
collision, reference gates and complete result denominators.

Measured runs use cached cl100k_base tokenization, no inference model, embeddings,
paid API, model download or database mutation. Python network/DNS attempts were
zero. Contexts are serialized before reference scoring; all forty contexts per
revision retain exact quotes/provenance, whole dependencies and token counts.
The helper records three timing repetitions without choosing the best result;
old versus new timings are not a controlled causal latency comparison.

Run A verified 1,268 earlier files unchanged; B verified 1,313, including A's
snapshots and outputs. All archived input hashes, output hashes and original
frozen-package digests have been checked. Each run includes a pre-measurement
manifest, input snapshots, source corpus, human-review snapshot, unscored contexts,
scored results and metrics. An existing output directory is refused before any
measurement. These checks establish consistency, not reviewer authentication.

## Reproduction and dependencies

The new runner depends on the preceding `section-evaluation-v01` package,
`section_evaluation.py`, the reviewed contaminant package and the local human
review record. It is not a standalone replacement for the chat or for the frozen
trial. Recorded H/C baselines and complete raw runs stay ignored locally; an
ordinary clone alone does not reproduce this paired historical comparison.
No new package installation is needed in the existing ingestion environment.

From the repository root, PowerShell:

```powershell
.\.venv-ingestion\Scripts\python.exe -m unittest tests.test_scoped_passage_context tests.test_section_navigation_runner -v
$env:PYTHONHASHSEED = '0'
.\.venv-ingestion\Scripts\python.exe -m experiments.cytiva.section_navigation_retrieval --output data/experiments/cytiva/section-navigation-v03/runs/development-new --review data/experiments/cytiva/section-evaluation-v01/human-review.json --c-baseline data/experiments/cytiva/contaminants-pilot-v01/runs/vocabulary-section-20261024-b/results.json
```

Only use a new directory for a deliberately authorized additional development
measurement; do not erase A, B or the original frozen output to repeat a score.

## Limits and next step

This combined policy changes vocabulary, routing and filtering together. There
is no factorial ablation attributing the gain to one factor. It uses manually
curated roles and finite phrase lists, and was adjusted on opened questions;
H/C success is a regression result, not a fresh generalization benchmark. The
contrast rule handles only the declared construction, not arbitrary negation,
multi-product conditions, conjunctions, conflicting instructions or every way
of expressing uncertainty. Exact source retention alone does not validate
scientific applicability or a safe generated answer.

Keep B as an opt-in candidate. Before considering adoption, freeze its policy
and evaluate separately prepared questions, including paraphrases, benign
out-of-scope requests, indirect negations, product/phase ambiguities and mixed
questions. Preserve this development history and the original failed gate. The
serving adapter, actual answers/abstentions and independent relevance review
remain separate work; no default change is justified solely by these scores.
