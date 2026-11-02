# Proposed serving-contract cases v01

Prepared on 2 November 2026 against `6c8bfe0`. **All cases are proposed and pending review.** They reuse existing documentary evidence but are not new human decisions, a scored benchmark, an executed adapter trial or operational guidance. No release, search or model inference has been run.

These cases exercise the [proposed handoff contract](REVIEWED-DOSSIER-SERVING-CONTRACT-V01.md). They are design/conformance examples on a known corpus, not an independent holdout. The status names and reason codes are proposed. Inputs are structured documentary requests; wording below is explanatory, not a new free-text parser grammar.

## Representative cases

### SC01

- Request or injected test condition: Exact plain MabSelect; explore precipitated/denatured substances.
- Expected outcome: `supported` under Q05.
- Required evidence/authority: E167-H, E167-PH, E167-P.
- Review points: Retain four distinct formulations, each 2 CV and at least 10 min contact, then immediate at least 5 CV of sterile filtered binding buffer at pH 7.0–8.0. No ranking, combination, conversion or automatic pH adjustment.

### SC02

- Request or injected test condition: SuRe (or SuRe LX); explore precipitated/denatured substances.
- Expected outcome: `supported` under Q05 and Q06 as separate blocks.
- Required evidence/authority: Q05 bundle; E167-H, E167-PH, E167-SH, E167-S.
- Review points: Keep the general alternatives separate from the restricted 3 CV binding buffer → at least 2 CV of 100–500 mM sodium hydroxide for 10–15 min → immediate at least 5 CV wash. Do not present it as a fifth formulation or required successor.

### SC03

- Request or injected test condition: MabSelect family, exact variant unknown; category supplied.
- Expected outcome: `needs_clarification`: exact product.
- Required evidence/authority: Q09 context-only bundle and approved application clarification policy.
- Review points: No recipe or default SuRe. Ask for the exact product label, without requiring a confirmed diagnosis. Headings do not become selected procedures.

### SC04

- Request or injected test condition: Known SuRe LX, context unknown or mixed.
- Expected outcome: `needs_clarification`: one category to explore.
- Required evidence/authority: Q09 context-only bundle; separate product scopes retained.
- Review points: Retain the known product. Ask only for available problem/deposit/prior-treatment context; neither infer lipids from backpressure nor demand a confirmed deposit.

### SC05

- Request or injected test condition: Known supported product; hydrophobic context; ask about solvents, precautions and numerical maximum pressure.
- Expected outcome: `partial`: documentary support plus `abstained` numerical pressure.
- Required evidence/authority: E167-H, E167-LH, E167-E, E167-W (N07).
- Review points: Keep 70% ethanol OR 30% 2-propanol, 3–4 CV, immediate at least 5 CV following binding-buffer wash at pH 7.0–8.0. Increasing gradients address air bubbles; lower flow addresses increased backpressure. No numerical flow, pressure, gradient or solvent duration is supplied by this bundle.

### SC06

- Request or injected test condition: Known supported product; hydrophobic context; ask what the stated pH applies to in the detergent route.
- Expected outcome: `supported` under N06.
- Required evidence/authority: E167-H, E167-LH, E167-D.
- Review points: The pH applies to the following binding buffer, not the detergent solution. Preserve 2 CV detergent, 0.1% as an example and immediate at least 5 CV wash. No named detergent, temperature, duration or flow invented.

### SC07

- Request or injected test condition: Known MabSelect product; request the page-166 12-hour hold for its solvent route.
- Expected outcome: `abstained` on that transfer; independently requested N07 information may remain supported.
- Required evidence/authority: N07 bundle; page-166 material is not eligible as this procedure.
- Review points: Do not copy the Protein A/G hold into MabSelect or state a global 12-hour prohibition. Bound non-support to the selected MabSelect bundle.

### SC08

- Request or injected test condition: A product/edition outside the initial release catalogue.
- Expected outcome: `abstained`: outside_release_scope.
- Required evidence/authority: Release catalogue plus registered scope metadata.
- Review points: Do not infer a newer variant by substring, use an adjacent product, or claim chemical incompatibility or manufacturer discontinuation.

### SC09

- Request or injected test condition: N07 selected, but E167-W is missing, altered or its review binding cannot be loaded.
- Expected outcome: `unavailable` for the entire solvent option.
- Required evidence/authority: All N07 dependencies mandatory.
- Review points: Do not render a partial solvent recipe without its pressure warning. Do not call this missing scientific knowledge or ask the user for a pressure number. A separately requested and independently verified detergent task may remain served; global release corruption blocks all tasks.

### SC10

- Request or injected test condition: Request information dependent on E118-I or E121-EQ.
- Expected outcome: `quarantined` for the affected item; no usable held quote.
- Required evidence/authority: Existing exclusion policy, not a new approval or part of the first release.
- Review points: Never infer the held pH/pI rule or equilibration parameters from neighbouring washing steps. Other independent tasks may be served. The initial adapter does not retrieve these excluded items as admissible context.

### SC11

- Request or injected test condition: Task A has unknown product; independent task B explicitly specifies plain MabSelect and precipitated context.
- Expected outcome: Aggregate `partial`: A clarifies, B supported under Q05.
- Required evidence/authority: Q09 policy/context for A; complete Q05 bundle for B.
- Review points: No transfer of product/context/exclusions between tasks, no suppression of B and no duplicate invented task. Preserve input order and ownership.

### SC12

- Request or injected test condition: Plain MabSelect explicitly requests the SuRe/SuRe LX-only stronger-alkali block.
- Expected outcome: `abstained` for that restricted block: documented product scope does not match.
- Required evidence/authority: E167-SH and original Q06 restriction.
- Review points: Do not declare a general sodium-hydroxide ban or automatically substitute a general formulation. Only independently requested and fully supported general guidance can be served.

### SC13

- Request or injected test condition: Complete eligible N07 bundle exceeds the configured serialized-context budget.
- Expected outcome: `unavailable`: context_budget_incomplete.
- Required evidence/authority: Full bundle size with scope, warning, reviews and reservations.
- Review points: Withhold the option rather than drop E167-W, a wash, condition or review reservation. Do not report source absence. Independent complete tasks may still be served.

### SC14

- Request or injected test condition: Review withdrawn/unresolved, or a proposed selector supplies an unknown ID/private citation URL/policy override.
- Expected outcome: Review hold → `quarantined`; unresolvable integrity/selection → `unavailable`.
- Required evidence/authority: Versioned release and review authority; service-owned citation registry.
- Review points: No older-snapshot bypass, user-approved=true override, fallthrough to model prose or fabricated URL. Citation must open the versioned excerpt view. Technical source text remains escaped data, never an instruction to the service.

## Exact source locators for numerical/condition review

The records below are copied from the existing evidence snapshot without changing
quote text or offsets. Page intervals are Unicode code points in the recorded
extracted page text, start-inclusive/end-exclusive. They are not visual PDF
coordinates. Heading dependencies and complete original Q/N reservations remain
mandatory and are not replaced by these five excerpts.

Source PDF: `cytiva_affinity-chromatography-antibodies_hplc_technical-support.pdf`,
SHA-256 `a6fd949e904ec0bafbcc7d85a3be1660f2bea8949098e86c57ae43d06492946a`;
document reference `CY13981-25Jan21-HB` is inherited registry metadata, not newly
certified. See the [dossier](mabselect-cleaning-sources-v01.json) and original
[evidence snapshot](../../experiments/cytiva/retrieval-pilot-v01/evidence.json).
The full manual remains local and is not included in this proposal.

### E167-P

```json
{
  "id": "E167-P",
  "pdf_page_1based": 167,
  "pdf_page_index_0based": 166,
  "page_text_start": 144,
  "page_text_end": 515,
  "quote": "1.  Wash the medium with 2 column volumes of 50 mM sodium hydroxide in 500  mM sodium sulfate, or 50 mM   \nsodium hydroxide in 1 M sodium chloride, or 100 mM sodium phosphate, or 6 M guanidine hydrochloride in  \n10 mM sodium hydroxide. Contact time: at least 10 min. \n2. Immediately wash with at least 5 column volumes of sterile filtered binding buffer at pH 7.0 to 8.0.",
  "quote_sha256": "05a708ed6ecc676b33c1fb4b2adca690cf7bdac305bb1fccf3dbaf1142728bc8"
}
```

### E167-S

```json
{
  "id": "E167-S",
  "pdf_page_1based": 167,
  "pdf_page_index_0based": 166,
  "page_text_start": 516,
  "page_text_end": 780,
  "quote": "1. Wash with 3 column volumes of binding buffer. \n2. Wash with at least 2 column volumes of 100 mM to 500 mM sodium hydroxide. Contact time: 10 to 15 min. \n3. Immediately wash with at least 5 column volumes of sterile and filtered binding buffer at  pH 7.0 to 8.0.",
  "quote_sha256": "ba17e3092a7866df3756d0048b8005352480b7cfa9888261de356620dfa4be14"
}
```

### E167-D

```json
{
  "id": "E167-D",
  "pdf_page_1based": 167,
  "pdf_page_index_0based": 166,
  "page_text_start": 781,
  "page_text_end": 960,
  "quote": "1. Wash with 2 column volumes of a nonionic detergent (e.g., 0.1% solution).\n2 Immediately wash with at least 5 column volumes of sterile filtered binding buffer at pH 7.0 to 8.0.",
  "quote_sha256": "96bec6ca131f56609bd54960ff8518adc1525413ca791b8cb60b0402f5266e76"
}
```

### E167-E

```json
{
  "id": "E167-E",
  "pdf_page_1based": 167,
  "pdf_page_index_0based": 166,
  "page_text_start": 962,
  "page_text_end": 1258,
  "quote": "2a. Alternatively, wash with 3 to 4 column volumes of 70% ethanol or 30% 2-propanol. Wash immediately with at \nleast 5 column volumes of sterile filtered binding buffer at pH 7.0 to 8.0. Apply increasing gradients to avoid air \nbubble formation when using high concentrations of organic solvents.",
  "quote_sha256": "4ae45301795ef8ed166f21d2c38622d013e781799c1ed6ebecba1cf50f4f5af7"
}
```

### E167-W

```json
{
  "id": "E167-W",
  "pdf_page_1based": 167,
  "pdf_page_index_0based": 166,
  "page_text_start": 1461,
  "page_text_end": 1605,
  "quote": "Washing with 70% ethanol and 30% 2-propanol will increase backpressure. Use a lower flow rate when cleaning \nwith 70% ethanol or 30% 2-propanol.",
  "quote_sha256": "95d1c60e7132a6f0e08d252f8755661bb81b7bc35220e6013467357265427088"
}
```

## Acceptance checklist for future implementation

- Record the input/task IDs, release version, admitted/withheld bundles, per-item
  outcomes, reason codes and original review/source bindings.
- Compare exact scope, original quantities, warning, sequence/alternative logic,
  reservations and citation resolution; no string-only status check is sufficient.
- Check negative controls: tampered hashes, missing headings/warnings, revoked
  review, incompatible product, cross-task transfer, excluded/quarantined evidence,
  unsupported computed quantities and an over-budget complete bundle.
- Preserve the original reviews and all failed outcomes. A future pass establishes
  contract conformance only, not scientific validation or unrestricted language understanding.
