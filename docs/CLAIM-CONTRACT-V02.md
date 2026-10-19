# Claim contract v0.2 — extraction before human review

Selected strong extractor: **GPT‑6.1 Sol**, medium effort, provisionally based on the documentary review of pages 97–99. Everyday inference remains a separate model decision. An earlier-prompt package on pages 100–102 is archived and unexecuted. The corrected-prompt r2 test used one subscription generation and now has a [curated documentary review](../experiments/cytiva/reviewed-r2/README.md): 33 corrected claims, 19 validated and 14 with reservations. The original generated 32 claims; c33 separates a pH target from c16. No API execution or publication is included.

Lot 3 implementation: `ingestion/claim_contract.py`, `ingestion/claim_prompt_v02.txt`, `ingestion/claim_validation.py`. The PDF preparation command `ingestion/prepare_claim_test.py` was delivered in lot 4; both lots are now merged into `main`. Frozen-input integrity lives in `ingestion/claim_bundle.py`, independently of PDF conversion. The generated JSON schema is obtained from `ClaimExtraction.model_json_schema()`, so the test input uses the same definitions as local validation.

## Changes from the first comparison

- `force` is separate from `purposes`: recommended, required, possible, prohibited and descriptive statements retain their different meanings. Full `statement` preserves negation and qualifications.
- Purposes cannot have the applicability/trigger role. Applicability and triggers are in `condition_groups`: OR between groups, AND inside each group. Missing context evaluates to unknown; it never authorizes an action.
- Numerical comparisons have typed decimal-string operands and explicit units. Inclusive ranges require explicit support. Non-computable wording uses `source_text` and remains unknown. Categorical equality compares short category codes, never sentences. No automatic unit conversion.
- `RECOMMENDED_FOR` needs an observed-symptom trigger in every OR branch, not a future risk. An applicability-only branch cannot bypass the trigger. General prevention uses a procedure with a stated purpose. `PREVENTS_BUILDUP_OF` is limited to actual accumulation.
- Cleaning and CIP remain distinct. A removal purpose is not automatically a `CAN_REMOVE` capability. Descriptive benefits may use `DESCRIPTIVE` instead of invented instructions.
- Products have an explicit `product_kind` and each claim has product/phase IDs with scope evidence. Product identity, column size and phase must not be merged by name similarity.
- Parameters retain full `value_text`, quantities, comparators, units, denominators and materials. `parameter_logic` preserves all/any/and_or/sequence. Per-parameter and per-quantity evidence is required.

These structural distinctions constrain representation; they do not prove semantic fidelity. A model can still label a purpose as a condition or confuse cleaning and CIP. Documentary review remains necessary, as does checking omitted numbers and table/figure associations.

## Quarantine is a blocker, not a global warning

Each source issue has an ID, kind, evidence and affected claim IDs. Each affected claim links back to the issue and has `disposition=quarantine`. Valid ordinary candidates have `review_required`; the schema has no approved state.

The local validator separates `review_queue_ids` from `quarantine_ids`. It quarantines unresolved product scope and every affected source issue. Application-provided `source_flags` block any claim using a flagged item even when the model omits the issue, removes its link or claims ordinary review status. Malformed batches do not enter the normal review queue. Quarantine granularity is conservatively the source item: a long item mixing clear and unclear instructions may over-block; splitting it into independently evidenced passages needs a new reviewed corpus version.

The known ambiguous items of the old pages are documented in the local artifact `data/experiments/cytiva/pages-097-099-v01/quarantaine-source-v02.json`: syringe elution buffer wording (item 67), malformed initial equilibration volume (item 64). These are scoped to the original PDF/excerpt hash; their item IDs must never be applied to another conversion merely because IDs look identical. A v0.2 replay must freeze these flags into the corresponding corpus, with a matching source hash. They are not injected into the new-page prompt.

A source-text condition such as “if required” is not automatically a source error: the meaning may be clear while its evaluation in the user's context is unknown. That condition stays unknown without inventing its trigger.

No candidate is publishable from this module, including a structurally valid candidate. Lifting a quarantine needs a separate human-reviewed source clarification and versioned revalidation. It cannot be done by changing the model's disposition. This patch does not provide a publication bypass or reinterpret previous manual decisions.

## Deterministic checks and their limits

The validator checks unique IDs, evidence existence, domain/range, product/phase scope types, normative context, issue consistency and quarantine. It checks declared number/unit mentions in cited text for quantities and decimal conditions, preserving M versus mM, written small integers and explicit denominators. Each decimal condition is checked against its own evidence references. Scientific literals such as `1e-3`, `1 × 10^-3` and `1 × 10⁻³` are read as their full decimal value; their mantissa and exponent do not become independent supporting numbers. This is a lexical grounding guard, not a proof that a quantity belongs to the stated material, phase, comparator or table row. It also cannot prove every source number was extracted. Semantic review is always pending.

`evaluate_conditions` is a pure helper providing true/false/unknown over the structured DNF, with exact unit matching. It has no source corpus: use it only after successful candidate validation; it cannot approve claims or update separate human decisions. A true result cannot repair failed evidence checks. It does not interpret `source_text`, infer necessity, normalize categories from free text or authorize procedures. Never use a true condition result as a publication or industrial approval.

## Fresh test preparation and validation

**Preparation and validation dependencies:** the preparation launcher delivered in lot 4 (`ingestion/prepare_claim_test.py`) is available on `main`. It requires the documented ingestion environment, cached model artifacts and a local PDF. Manuals, model weights and frozen experiment packages are not bundled in Git. The validator delivered in lot 3 can independently validate an existing compatible frozen corpus and candidate without PDF conversion.

From the repository directory, with the ingestion environment and cached conversion weights installed:

```powershell
& '.\.venv-ingestion\Scripts\python.exe' -m ingestion.prepare_claim_test 'references/manual.pdf' --output 'data/experiments/cytiva/pages-100-102-v02-r2' --pages 100 101 102 --document-reference 'CY13981-25Jan21-HB' --document-version '25Jan21' --selection-reason 'Next complete product section; scope, conditions, negation and quantities'
```

Read the document reference and edition from the PDF before supplying `--document-reference` and `--document-version`; they are marked operator-supplied, not independently verified. `--selection-reason` is required, and the preparation date is generated in UTC. Metadata is frozen in the source map, corpus and plan. This refuses an existing output directory. `--resume-failed` is restricted to an identical source, pages and metadata in an incomplete preparation with no prepared inputs. The existing preloaded artifacts are read from `.local-tools/docling-models`; `--artifacts` can select another existing directory. The converter uses CPU and embedded text, with OCR and table inference disabled for these three non-tabular, born-digital pages; the profile is recorded. No fallback to a different converter or network download happens silently.

The package contains its PDF excerpt, original-page mapping, full Docling document, raw item provenance/bounding boxes, body tree, groups and ordered elements. The model input has the source text and contract, without previous extractions or reference answers. A manifest freezes their hashes; a changed input or contract fails verification. Updated prompts must be used in a new versioned package; do not overwrite the prompt or manifest of an existing frozen experiment. The preparation command makes no LLM calls and includes no API launcher.

After saving the single subscription response as a new `resultat-sol.json` in that package:

```powershell
& '.\.venv-ingestion\Scripts\python.exe' -m ingestion.claim_validation 'data/experiments/cytiva/pages-100-102-v02-r2/resultat-sol.json' --corpus 'data/experiments/cytiva/pages-100-102-v02-r2/input.json' --output 'data/experiments/cytiva/pages-100-102-v02-r2/validation-sol.json'
```

The report must be a new file. A valid report provides a review queue, a quarantine queue and resolved source items; `publication_allowed` remains false. An empty result is labeled `empty_candidate`, not a successful extraction. The new PDF pages have been selected and inspected during preparation, so this is a fresh development test, not a blinded held-out evaluation. One generation is planned, with no automatic retry. API use is not authorized by preparing this subscription test.

## Integration boundary

This is the active contract for the new strong-model test and its staging validator. The original `ingestion/schema.py` remains the legacy Docling Graph dense extraction template used by the existing review database. Its `INDICATES`/`RESOLVED_BY` records are not automatically converted to the new ontology. A reviewed adapter into immutable review records and the existing manual-review UI is a later migration step; v0.2 candidates cannot be passed directly to the existing publisher.
