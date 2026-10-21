# Four-lot consolidation - status and history

**The four lots and the README were merged into `main`.** This document records that delivery milestone, not the latest test count or repository state.

| Delivery | Status | Reference |
|---|---|---|
| Lot 1 | Merged | [PR #3](https://github.com/mukunde/bioprocess-assistant/pull/3) |
| Lot 2 | Merged | [PR #4](https://github.com/mukunde/bioprocess-assistant/pull/4) |
| Lot 3 | Merged | [PR #5](https://github.com/mukunde/bioprocess-assistant/pull/5) |
| Lot 4 | Merged, 23 files | [PR #6](https://github.com/mukunde/bioprocess-assistant/pull/6), commit `0f76d14` |
| README | Merged separately, one file | [PR #7](https://github.com/mukunde/bioprocess-assistant/pull/7), commit `521088a` |

The README was in the initial lot 4 list, but was delivered separately and not included again. PR #6 contains the other 22 initial files and the compatibility update aligning `docs/CLAIM-CONTRACT-V02.md` with the PDF launcher arguments. The manifest records this scope in `lot_4_delivery_files`; `pending_review_files` is empty for all four delivered lots.

Final main verification at commit `937a656dc478e14c91f1c3e92321cf6f520a5e0a`: the five delivery commits are present and the expected content of 69 files is confirmed. All 106 principal tests pass on a clean copy; seven historical checks pass with local evidence and skip without it. No paid model/API call or database write occurred during verification. Local details: `data/consolidation/main-final-verification.json`.

Lots were integrated in order 1 → 2 → 3 → 4. Initial lists assigned each file once; the deliveries and compatibility correction above explain subsequent differences. Exclusion rules originally belonged to lot 2, and the README/general plan to lot 4; the README was later delivered separately. Cross-lot documentation links are available on main.

## File organization

| Content | Location |
|---|---|
| Application code and evaluations | existing files, `grounding.py`, `eval/`, `tests/` |
| Ingestion and claim contract | `ingestion/`, `docs/INGESTION.md`, `docs/CLAIM-CONTRACT-V02.md` |
| Ontology and readable examples | `docs/ontology/` |
| Experiment code | `experiments/cytiva/` |
| Diagnostic/comparison reports | `docs/experiments/` |
| Single active plan | `docs/ROADMAP.md` |
| Historical methodology review | `docs/decisions/2026-10-roadmap-review.md` |
| Raw results for pages 97–99 | `data/experiments/cytiva/pages-097-099-v01/` (ignored) |
| Unexecuted pages 100–102 archive (earlier prompt) | `data/experiments/cytiva/pages-100-102-v02/` (ignored) |
| JSON reference cards | `data/experiments/cytiva/reference-v01/` (ignored) |
| Docling Graph reference checkout | `.local-tools/docling-graph-reference/` (ignored) |
| Inventory, hashes and relocation journal | `data/consolidation/` (ignored) |

## Duplicates and overlaps

- **Confirmed exact duplicate:** old `resultat-sonnet.json` matches `resultat-sonnet-original.json`. The original is authoritative; the alias is retained in `archive/resultat-sonnet-alias.json`. Scripts no longer recreate it.
- **Degraded capture:** old `resultat-sonnet-brut.txt` contains typographic quotes. Retained as `archive/resultat-sonnet-accessibility.txt`, excluded from grading.
- **Overlapping roadmaps:** ROADMAP.md is the current plan; the earlier methodology review is explicitly marked as a historical decision archive.
- **Ontology and schema:** complementary, not duplicates. The ontology defines domain meaning; v0.2 defines serialization and checks.
- **Review Markdown and JSON:** retained for different purposes. Complete data remains local; selected reports are repository artifacts.
- No original model response, PDF or human decision was deleted or rewritten. Navigation text was adjusted to the new paths. Frozen inputs/responses retained their hashes.

## Initial lots and delivery messages

### Lot 1 - Reliability and evaluations (23 files)

Proposed message:

```text
fix: enforce grounded answers and reliable evaluations

Render only validated graph selections, fail malformed evaluations and make seed loading additive and transactional. Preserve explicit refusal and threshold behavior.
```

Files:

- `.chainlit/config.toml`
- `AGENTS.md`
- `CLAUDE.md`
- `agent.py`
- `app.py`
- `chainlit.md`
- `docs/ADR-001-knowledge-graph-grounding.md`
- `docs/ADR-002-multilingual-retrieval.md`
- `eval/README.md`
- `eval/cases.yaml`
- `eval/judge.py`
- `eval/requirements.txt`
- `eval/run_eval.py`
- `eval/threshold_sweep.py`
- `graph/schema.cypher`
- `graph/seed.cypher`
- `grounding.py`
- `scripts/load_graph.py`
- `tests/test_reliability.py`
- `tests/test_app.py`
- `tools.py`
- `compose.neo4j.yaml`
- `docs/LOCAL-NEO4J.md`

Checks:

- `python -m unittest discover -s tests -p test_reliability.py -v`
- `python -m unittest discover -s tests -p test_app.py -v`

### Lot 2 - PDF ingestion, provenance and review (15 files)

Proposed message:

```text
feat: stage PDF extractions with provenance and manual review

Isolate the optional Docling Graph runtime, ground extraction evidence in immutable PDF conversions and require append-only manual review before exporting a separate evidence graph.
```

Files:

- `.dockerignore`
- `.gitignore`
- `docs/INGESTION.md`
- `ingestion/__init__.py`
- `ingestion/__main__.py`
- `ingestion/evidence.py`
- `ingestion/local.example.json`
- `ingestion/pipeline.py`
- `ingestion/publish.py`
- `ingestion/review.html`
- `ingestion/review.py`
- `ingestion/schema.py`
- `ingestion/store.py`
- `requirements-ingestion.txt`
- `tests/test_ingestion.py`

Checks:

- `python -m unittest discover -s tests -p test_ingestion.py -v`

### Lot 3 - Ontology, v0.2 contract and quarantine (8 files)

Proposed message:

```text
feat: define versioned troubleshooting claims and source quarantine

Separate normative force, purpose, applicability and quantities. Validate evidence and typed conditions, block source conflicts per claim, and keep all candidates pending human review.
```

Files:

- `docs/CLAIM-CONTRACT-V02.md`
- `docs/ontology/examples-v0.1.md`
- `docs/ontology/v0.1.md`
- `ingestion/claim_bundle.py`
- `ingestion/claim_contract.py`
- `ingestion/claim_prompt_v02.txt`
- `ingestion/claim_validation.py`
- `tests/test_claim_contract.py`

Checks:

- `python -m unittest discover -s tests -p test_claim_contract.py -v`

### Lot 4 - Consolidated experiments/documentation (initial 23-file list)

Proposed message:

```text
test: consolidate Cytiva experiments and prepare the v0.2 benchmark

Keep experiment tooling and curated reports in the repository, move local evidence into ignored data directories, archive duplicate captures and prepare a frozen new-page test without model calls.
```

Files:

- `README.md`
- `docs/CONSOLIDATION.md`
- `docs/README.md`
- `docs/ROADMAP.md`
- `docs/commit-lots.json`
- `docs/decisions/2026-10-roadmap-review.md`
- `docs/experiments/cytiva-local-extraction-diagnostic.md`
- `docs/experiments/cytiva-v01-fidelity.md`
- `docs/experiments/cytiva-v01-results.md`
- `experiments/__init__.py`
- `experiments/cytiva/README.md`
- `experiments/cytiva/__init__.py`
- `experiments/cytiva/build_reference_cards.py`
- `experiments/cytiva/paths.py`
- `experiments/cytiva/requirements.txt`
- `experiments/cytiva/v01/__init__.py`
- `experiments/cytiva/v01/build_fidelity_audit.py`
- `experiments/cytiva/v01/check_result.py`
- `experiments/cytiva/v01/compare_saved.py`
- `experiments/cytiva/v01/prepare.py`
- `experiments/cytiva/v01/test_preparation.py`
- `ingestion/prepare_claim_test.py`
- `tests/test_experiment_preparation.py`

Checks:

- `python -m unittest discover -s tests -v`
- `python -m unittest discover -s experiments/cytiva/v01 -p test_*.py -v`

## Lot 4 follow-up review

- Historical audit bound to exact response, corpus, prompt, PDF excerpt and source-map hashes: changed inputs are rejected before verdicts are written.
- Cards generated only in a new `--output` directory, without overwriting annotations or the repository ontology document.
- Document/version metadata and page-selection rationale required and recorded as operator supplied; date calculated in UTC. Resume requires identical source, pages and metadata.
- At this historical checkpoint, `pages-100-102-v02` was preserved unchanged and `pages-100-102-v02-r2` still needed preparation with the corrected prompt. No new model was launched at that checkpoint.
- Suite at that checkpoint: 106 principal tests (34 reliability, 6 Chainlit, 29 ingestion, 29 contract, 8 preparation/audit/cards). Seven additional historical checks require local evidence and explicitly skip without it. Follow-up review: `data/consolidation/lot-4-fixed-review.json`; post-merge verification: `data/consolidation/main-final-verification.json`.

## Historical validation (not the current suite)

Lot 1 after integration: error handling added in `app.py`, with six tests in `tests/test_app.py`. The 34 reliability tests, six application tests and 14 local Chainlit HTTP/callback checks passed with simulated model/Neo4j results. At this historical checkpoint, real Neo4j integration was blocked by DNS resolution of the configured host. No paid API call occurred.

After checking the Aura console, the user chose local Neo4j in Docker. Sixteen checks passed on a temporary Neo4j Community 5.26.32 database, including nine lexical cases, idempotence and real rollback. The Chainlit round trip used real Neo4j and a simulated model. The temporary database was removed; `compose.neo4j.yaml` and `docs/LOCAL-NEO4J.md` describe persistent development storage. The old Aura URI no longer blocks local validation. The old remote graph was not recovered.

During initial consolidation, each lot was applied to a disposable copy of the latest commit without changing the index or creating commits. Historical cumulative results, before Chainlit error-handling corrections:

| Copy checked | Principal tests | Result |
|---|---:|---|
| Lots 1 through 1 | 34 | OK |
| Lots 1 through 2 | 58 | OK |
| Lots 1 through 3 | 81 | OK |
| Lots 1 through 4 | 82 | OK |

The seven historical comparison checks also passed with local evidence. Frozen v0.1/v0.2 inputs and original responses retained their hashes. No new model was called. Tests mock models/database access; review HTTP tests stay local. Local Markdown links and Python syntax were checked.

## Excluded local artifacts

Manuals/PDFs, conversions, complete responses, full review journals, model weights and machine-specific tools remain in ignored local storage. Exclusions were checked.

Lot 4 retains only selected tooling/reports. A fresh clone does not contain private data: principal tests use synthetic fixtures, and the seven historical checks report missing evidence explicitly.

Other files in the parent folder belong to another project and were excluded. Old empty directories may remain visible under OneDrive because Windows refused their removal; they no longer contain relocated work and empty directories are not tracked by Git.

Consolidation checks were recorded locally in `data/consolidation/validation.json`. Machine-readable lists are in [commit-lots.json](commit-lots.json).
