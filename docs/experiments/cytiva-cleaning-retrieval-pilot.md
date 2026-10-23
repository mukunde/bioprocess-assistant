# Cytiva cleaning: retrieval and context-assembly pilot

Prepared 23 October 2026. **Candidate human reference; not reviewed, published or benchmarked.**

## Scope and selection

Appendix 5: **Cleaning of Protein G and Protein A Sepharose media** (page 166), with the adjacent **Cleaning of MabSelect media** (page 167) as a product-boundary comparator. PDF one-based and visible printed page numbers match; API indices are 165 and 166. The source PDF has 183 pages; its verified SHA-256 is `a6fd949e904ec0bafbcc7d85a3be1660f2bea8949098e86c57ae43d06492946a`. Edition labels are inherited registry metadata.

This is a troubleshooting-oriented cleaning subsection, not a complete troubleshooting matrix. It explicitly links increased backpressure to cleaning, but does not establish a unique foulant diagnosis. Seven documentary-answer intents, one clarification and two scoped refusals test that distinction. No symptoms, causal intermediate nodes or performance guarantees are invented.

The two full pages were rendered and visually inspected. Native extraction places some headings after their procedures (especially the SuRe/SuRe LX block); visual association, not string order, defines the reference. No Docling conversion, OCR, LLM/VLM, embedding, paid API, database write or retrieval execution was performed. Poppler and pypdf were used deterministically.

## Files and source contract

- [Evidence](../../experiments/cytiva/retrieval-pilot-v01/evidence.json): exact extracted quotations, page indices, Unicode offsets, quote/page-text hashes, product scope and visual regions.
- [Questions](../../experiments/cytiva/retrieval-pilot-v01/questions.json): ten English/French pairs, expected statuses, necessary evidence sets, answer points, critical checks and prohibited inferences.
- [Manifest](../../experiments/cytiva/retrieval-pilot-v01/manifest.json): file digests and preparation scope.

Each required evidence set is an AND bundle; multiple sets would be OR alternatives. IDs are candidate reference anchors, not Docling item refs, published claims or human approvals. Product/deposit headings must accompany recipes. Exact offsets resolve only against the recorded pypdf text artifact, not a differently normalized or Docling text export. Page text and source renders remain local under ignored `data/experiments/cytiva/retrieval-pilot-v01/source-text/` and `tmp/pdfs/cytiva-retrieval-reference/`; they are excluded from the compact package.

## Evaluation plan and readiness

1. Review each question, source association, expected status and indispensable evidence with the user; record original decisions separately. No human approval is implied by this preparation.
2. Build candidate corpus passages from source evidence only, including headings, immediate follow-up washes and associated warnings. Never index questions, expected answers, evaluation labels or this review document. Freeze the corpus and adapter before measurement.
3. Start with a local lexical passage baseline and compare retrieval before/after a common context assembler. Score evidence coverage by canonical source spans, not literal reference-ID emission. Make candidate chunk boundaries independently of question answers; overlapping source excerpts must be deduplicated. This preparatory step does not implement the baseline.
4. Measure complete indispensable-evidence coverage before and after assembly, status correctness, product/alternative/condition/unit errors, quarantine leakage, latency and actual serialized-context tokens. For numeric/cause refusals, evaluate refusal correctness; do not treat these as no-relevant-evidence questions because their bounded justifications have source anchors.
5. Use a proposed common 2048-token assembled-context budget only after feasibility and user review; record tokenizer and full serialization. If a complete bundle does not fit, mark incomplete and clarify/abstain rather than truncate a warning. Q07 deliberately stresses a two-page evidence bundle. No target latency or score threshold has been accepted yet.

This ten-intent pilot is entirely development data, not the locked 24-intent LightRAG comparison. The [three-arm protocol](retrieval-comparison-protocol.md) remains separate; no LightRAG installation or new architectural choice follows here. The [roadmap](../ROADMAP.md) still requires reference approval, instrumentation and serving adapters. Cases from pages 77/88/104/152–153 can later be added as separately labelled regressions; they are not silently included in these ten questions.

Limits: this reference selects useful excerpts but is not an exhaustive omission audit of the manual. Refusals mean unsupported in the selected pages, not universally impossible. Documentary fidelity does not establish operational suitability. All records remain pending human review and publication is false.

## Ten review dossiers

### Q01 — symptom_action_without_invented_cause

**FR:** La contre-pression augmente sur Protein A Sepharose. Que recommande cette section et que permet-elle de dire sur la cause ?

**EN:** Backpressure increases on Protein A Sepharose. What does this section recommend, and what can it say about the cause?

**Expected status:** `answer`

**Indispensable passages:** E166-H, E166-T

**E166-H — page 166, top title**

> Cleaning of Protein G and Protein A Sepharose media

**E166-T — page 166, Cleaning in place paragraph**

> When an increase in backpressure is seen, the medium should be cleaned. In some applications, substances like 
> denatured proteins or lipids do not elute in the regeneration procedure.

**Expected answer points**

- The medium should be cleaned when backpressure increases.
- In some applications denatured proteins or lipids do not elute during regeneration; this is contextual information, not a confirmed diagnosis.

**Critical checks**

- Retain product scope and the words in some applications.
- Do not select a deposit-specific recipe without the corresponding context.

**Do not infer**

- The increase proves lipid fouling.
- A quantitative pressure trigger is given.

Human decision: **pending**.

### Q02 — quantity_and_sequence

**FR:** Pour Protein G ou Protein A Sepharose, quelle séquence de nettoyage vise les protéines précipitées ou dénaturées ?

**EN:** For Protein G or Protein A Sepharose, what cleaning sequence removes precipitated or denatured proteins?

**Expected status:** `answer`

**Indispensable passages:** E166-H, E166-PH, E166-P

**E166-H — page 166, top title**

> Cleaning of Protein G and Protein A Sepharose media

**E166-PH — page 166, heading above first CIP box**

> To remove precipitated or denatured proteins:

**E166-P — page 166, first CIP box**

> 1. Wash the medium with 2 column volumes of 6 M guanidine hydrochloride.
> 2. Immediately wash with at least 5 column volumes of binding buffer.

**Expected answer points**

- Wash with 2 column volumes of 6 M guanidine hydrochloride.
- Immediately wash with at least 5 column volumes of binding buffer.

**Critical checks**

- Keep 2 CV, 6 M, immediately and at least 5 CV together.

**Do not infer**

- Add a contact time or flow rate absent from the cited block.
- Transfer the 10 mM NaOH combination from page 167.

Human decision: **pending**.

### Q03 — example_force_and_conditions

**FR:** Pour des protéines hydrophobes fortement liées, lipoprotéines et lipides sur Protein A Sepharose, quelle voie avec détergent est décrite ?

**EN:** For strongly bound hydrophobic proteins, lipoproteins and lipids on Protein A Sepharose, what detergent route is described?

**Expected status:** `answer`

**Indispensable passages:** E166-H, E166-LH, E166-D

**E166-H — page 166, top title**

> Cleaning of Protein G and Protein A Sepharose media

**E166-LH — page 166, heading above second CIP box**

> To remove strongly bound hydrophobic proteins, lipoproteins and lipids:

**E166-D — page 166, second CIP box, steps 1 and 2**

> 1. Wash with a nonionic detergent, for example, 0.1% Triton X-100 at 37°C for 1 min.
> 2. Immediately wash with at least 5 column volumes of sterile binding buffer.

**Expected answer points**

- Wash with a nonionic detergent; 0.1% Triton X-100 at 37°C for 1 min is the example given.
- Immediately wash with at least 5 column volumes of sterile binding buffer.

**Critical checks**

- Example remains an example.
- Retain temperature, duration, sterility and immediate wash.

**Do not infer**

- Every nonionic detergent has the same validated conditions.
- Invent a detergent volume absent here.

Human decision: **pending**.

### Q04 — recipe_plus_separate_warning

**FR:** Quelle voie alternative utilisant l’éthanol est décrite pour ces dépôts sur Protein A Sepharose, avec la précaution de contre-pression ?

**EN:** What ethanol alternative is described for those deposits on Protein A Sepharose, including the backpressure precaution?

**Expected status:** `answer`

**Indispensable passages:** E166-H, E166-LH, E166-E, E166-W

**E166-H — page 166, top title**

> Cleaning of Protein G and Protein A Sepharose media

**E166-LH — page 166, heading above second CIP box**

> To remove strongly bound hydrophobic proteins, lipoproteins and lipids:

**E166-E — page 166, second CIP box, step 2a**

> 2a. Alternatively, wash the column with 70% ethanol and let it stand for 12 h. After treatment, wash with at least  
> 5 column volumes of binding buffer.

**E166-W — page 166, bottom warning**

> Washing with 70% ethanol will increase backpressure. Use a lower flow rate when cleaning with 70% ethanol.

**Expected answer points**

- Wash with 70% ethanol and let the column stand for 12 h.
- After treatment wash with at least 5 column volumes of binding buffer.
- 70% ethanol increases backpressure; use a lower flow rate.

**Critical checks**

- Retrieve the warning outside the recipe box.
- Retain 12 h and distinguish this route from page 167.

**Do not infer**

- Invent a numerical lower flow rate.
- Treat this as an additional mandatory step after the detergent route.

Human decision: **pending**.

### Q05 — alternative_grouping

**FR:** Pour des substances précipitées ou dénaturées sur les milieux MabSelect, quelles alternatives et quel lavage final sont indiqués ?

**EN:** For precipitated or denatured substances on MabSelect media, what alternatives and follow-up wash are listed?

**Expected status:** `answer`

**Indispensable passages:** E167-H, E167-PH, E167-P

**E167-H — page 167, title and all-MabSelect introduction**

> Cleaning of MabSelect media
> All MabSelect media can be cleaned using the following procedures:

**E167-PH — page 167, heading above first box**

> To remove precipitated or denatured substances:

**E167-P — page 167, first box**

> 1.  Wash the medium with 2 column volumes of 50 mM sodium hydroxide in 500  mM sodium sulfate, or 50 mM   
> sodium hydroxide in 1 M sodium chloride, or 100 mM sodium phosphate, or 6 M guanidine hydrochloride in  
> 10 mM sodium hydroxide. Contact time: at least 10 min. 
> 2. Immediately wash with at least 5 column volumes of sterile filtered binding buffer at pH 7.0 to 8.0.

**Expected answer points**

- Use 2 column volumes of one alternative: 50 mM NaOH in 500 mM sodium sulfate; 50 mM NaOH in 1 M NaCl; 100 mM sodium phosphate; or 6 M guanidine hydrochloride in 10 mM NaOH.
- Contact time: at least 10 min.
- Immediately wash with at least 5 column volumes of sterile filtered binding buffer at pH 7.0 to 8.0.

**Critical checks**

- Preserve the four OR alternatives and each concentration pairing.
- Preserve minimum contact time, pH, sterility and filtration.

**Do not infer**

- Mix all four alternatives.
- Assign 50 mM NaOH to the phosphate alternative.
- Replace at least 10 min with exactly 10 min.

Human decision: **pending**.

### Q06 — product_scope_and_reading_order

**FR:** Quelle séquence de nettoyage plus alcalin est spécifiquement décrite pour MabSelect SuRe et MabSelect SuRe LX ?

**EN:** What stronger-alkali cleaning sequence is specifically described for MabSelect SuRe and MabSelect SuRe LX?

**Expected status:** `answer`

**Indispensable passages:** E167-H, E167-PH, E167-SH, E167-S

**E167-H — page 167, title and all-MabSelect introduction**

> Cleaning of MabSelect media
> All MabSelect media can be cleaned using the following procedures:

**E167-PH — page 167, heading above first box**

> To remove precipitated or denatured substances:

**E167-SH — page 167, paragraph above middle box; text extraction puts it after recipes**

> MabSelect SuRe and MabSelect SuRe LX are alkali-tolerant, allowing the use of more concentrated solutions of sodium 
> hydroxide:

**E167-S — page 167, middle box**

> 1. Wash with 3 column volumes of binding buffer. 
> 2. Wash with at least 2 column volumes of 100 mM to 500 mM sodium hydroxide. Contact time: 10 to 15 min. 
> 3. Immediately wash with at least 5 column volumes of sterile and filtered binding buffer at  pH 7.0 to 8.0.

**Expected answer points**

- The stronger-alkali block follows the precipitated/denatured-substances subsection; do not generalize it to every deposit class.
- The more concentrated NaOH procedure is explicitly scoped to MabSelect SuRe and MabSelect SuRe LX.
- Wash with 3 column volumes of binding buffer.
- Then at least 2 column volumes of 100–500 mM NaOH, contact time 10–15 min.
- Immediately wash with at least 5 column volumes of sterile and filtered binding buffer at pH 7.0–8.0.

**Critical checks**

- Recover the scope paragraph despite displaced native extraction order.
- Retain all three ordered steps and range endpoints.

**Do not infer**

- Generalize the stronger-alkali block to every Protein A product.
- Convert this into a maximum lifetime or reuse guarantee.

Human decision: **pending**.

### Q07 — cross_page_scope_conflict

**FR:** Pour des dépôts hydrophobes, peut-on recopier le maintien de 12 heures de la page 166 dans la voie solvant MabSelect de la page 167 ?

**EN:** For hydrophobic deposits, can the 12-hour ethanol hold on page 166 be copied to the MabSelect solvent route on page 167?

**Expected status:** `answer`

**Indispensable passages:** E166-H, E166-LH, E166-E, E166-W, E167-H, E167-LH, E167-E, E167-W

**E166-H — page 166, top title**

> Cleaning of Protein G and Protein A Sepharose media

**E166-LH — page 166, heading above second CIP box**

> To remove strongly bound hydrophobic proteins, lipoproteins and lipids:

**E166-E — page 166, second CIP box, step 2a**

> 2a. Alternatively, wash the column with 70% ethanol and let it stand for 12 h. After treatment, wash with at least  
> 5 column volumes of binding buffer.

**E166-W — page 166, bottom warning**

> Washing with 70% ethanol will increase backpressure. Use a lower flow rate when cleaning with 70% ethanol.

**E167-H — page 167, title and all-MabSelect introduction**

> Cleaning of MabSelect media
> All MabSelect media can be cleaned using the following procedures:

**E167-LH — page 167, heading above last box**

> To remove strongly bound hydrophobic proteins, lipoproteins, and lipids:

**E167-E — page 167, last box, step 2a**

> 2a. Alternatively, wash with 3 to 4 column volumes of 70% ethanol or 30% 2-propanol. Wash immediately with at 
> least 5 column volumes of sterile filtered binding buffer at pH 7.0 to 8.0. Apply increasing gradients to avoid air 
> bubble formation when using high concentrations of organic solvents.

**E167-W — page 167, bottom warning**

> Washing with 70% ethanol and 30% 2-propanol will increase backpressure. Use a lower flow rate when cleaning 
> with 70% ethanol or 30% 2-propanol.

**Expected answer points**

- No transfer of the 12 h hold is supported. Page 166 describes 70% ethanol and a 12 h stand for the Protein G/A Sepharose route.
- Page 167 gives 3–4 column volumes of 70% ethanol OR 30% 2-propanol, followed immediately by at least 5 column volumes of sterile filtered binding buffer at pH 7.0–8.0.
- Page 167 requires increasing gradients to avoid air bubbles at high organic-solvent concentrations and lower flow because these solvents increase backpressure.

**Critical checks**

- Assemble both product scopes and both separate warnings.
- Retain alternative status, immediacy and the gradient precaution.

**Do not infer**

- Invent a 12 h hold or another contact time for the page-167 solvent route.
- Claim the manual explicitly prohibits every other contact time.

Human decision: **pending**.

### Q08 — unsupported_numeric_request

**FR:** Pour le nettoyage de Protein A Sepharose à l’éthanol 70 %, donne le débit réduit exact en mL/min et le seuil de pression déclenchant le nettoyage.

**EN:** For Protein A Sepharose cleaning with 70% ethanol, give the exact reduced flow in mL/min and the pressure threshold that triggers cleaning.

**Expected status:** `refuse`

**Indispensable passages:** E166-H, E166-T, E166-W

**E166-H — page 166, top title**

> Cleaning of Protein G and Protein A Sepharose media

**E166-T — page 166, Cleaning in place paragraph**

> When an increase in backpressure is seen, the medium should be cleaned. In some applications, substances like 
> denatured proteins or lipids do not elute in the regeneration procedure.

**E166-W — page 166, bottom warning**

> Washing with 70% ethanol will increase backpressure. Use a lower flow rate when cleaning with 70% ethanol.

**Expected answer points**

- The selected section specifies neither a numerical pressure threshold nor a reduced flow in mL/min.
- It says to clean when backpressure increases and to use a lower flow rate with 70% ethanol; cannot supply the requested numbers.

**Critical checks**

- Refusal is limited to unsupported numeric values, not all documentary help.
- Missing-value conclusion is scoped to these two pages.

**Do not infer**

- Invent numbers.
- Import a value from a different product or another section without evidence.

Human decision: **pending**.

### Q09 — missing_context

**FR:** La contre-pression de ma colonne augmente. Quelle recette de nettoyage dois-je utiliser ?

**EN:** My column has increasing backpressure. Which cleaning recipe should I use?

**Expected status:** `clarify`

**Indispensable passages:** E166-H, E166-T, E166-PH, E166-LH, E167-H, E167-PH, E167-SH, E167-LH

**E166-H — page 166, top title**

> Cleaning of Protein G and Protein A Sepharose media

**E166-T — page 166, Cleaning in place paragraph**

> When an increase in backpressure is seen, the medium should be cleaned. In some applications, substances like 
> denatured proteins or lipids do not elute in the regeneration procedure.

**E166-PH — page 166, heading above first CIP box**

> To remove precipitated or denatured proteins:

**E166-LH — page 166, heading above second CIP box**

> To remove strongly bound hydrophobic proteins, lipoproteins and lipids:

**E167-H — page 167, title and all-MabSelect introduction**

> Cleaning of MabSelect media
> All MabSelect media can be cleaned using the following procedures:

**E167-PH — page 167, heading above first box**

> To remove precipitated or denatured substances:

**E167-SH — page 167, paragraph above middle box; text extraction puts it after recipes**

> MabSelect SuRe and MabSelect SuRe LX are alkali-tolerant, allowing the use of more concentrated solutions of sodium 
> hydroxide:

**E167-LH — page 167, heading above last box**

> To remove strongly bound hydrophobic proteins, lipoproteins, and lipids:

**Expected answer points**

- Ask for exact resin/product and the deposit/problem context before selecting a recipe.
- The section distinguishes Protein G/A Sepharose, MabSelect and the SuRe/SuRe LX stronger-alkali scope, and different deposit classes.

**Critical checks**

- Return clarification rather than assume a product or foulant.
- Do not require the user to assert an already confirmed scientific diagnosis.

**Do not infer**

- Pick a NaOH or ethanol recipe from backpressure alone.

Human decision: **pending**.

### Q10 — causality_and_performance_overclaim

**FR:** La contre-pression a augmenté sur Protein A Sepharose après régénération. Confirme que les lipides sont la cause unique et que le nettoyage rétablira la capacité initiale.

**EN:** Backpressure rose on Protein A Sepharose after regeneration. Confirm that lipids are the sole cause and that cleaning will restore the original capacity.

**Expected status:** `refuse`

**Indispensable passages:** E166-H, E166-T

**E166-H — page 166, top title**

> Cleaning of Protein G and Protein A Sepharose media

**E166-T — page 166, Cleaning in place paragraph**

> When an increase in backpressure is seen, the medium should be cleaned. In some applications, substances like 
> denatured proteins or lipids do not elute in the regeneration procedure.

**Expected answer points**

- The section supports cleaning on increased backpressure, not a unique diagnosis of lipids.
- It provides no guarantee of restored original capacity; decline those confirmations.

**Critical checks**

- Distinguish possible residual substances from established causal diagnosis.
- No performance guarantee from a cleaning recommendation.

**Do not infer**

- Assert lipids as sole cause.
- Guarantee recovery, reuse count or contamination-free operation.

Human decision: **pending**.

