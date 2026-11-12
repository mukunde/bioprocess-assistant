# Cytiva product and procedure retrieval protocol

**Status** Draft for human review.

Compare the frozen expanded Neo4j baseline at fixed depth 32 with a new
candidate that uses product and procedure scope during ranking and
assembly. Both receive the same English question and use the same 42
reviewed passages, full-text index, canonical IDs, and context dependency
links. Keep the final limits at 32 passages and 4,096 context tokens.
Record the new candidate separately from the existing retrieval freeze.
[Adaptive-depth results](cytiva-neo4j-adaptive-depth-results-v01.md)

## Candidate selection and assembly

1. Resolve product and procedure mentions from the question using a
   reviewed deterministic vocabulary. Keep the bindings within each
   clause. For two stages of the same named product, reuse that product
   where the question clearly applies it to both stages. Never combine
   every product with every procedure. For an unclear or unsupported
   binding, use the unchanged fixed-32 baseline and record the reason.
2. Map the reviewed passages to product and procedure scopes using their
   source headings and conditions. Review the passage map and aliases
   before implementation. Keep generic MabSelect and the SuRe/SuRe LX
   alkali scope distinct. Keep loading, washing, elution, and buffer
   formulation distinct for HiTrap Blue HP. The map may include general
   material where a source supports its applicability. Preserve the
   warning and heading links through the frozen dependency assembler.
3. Run one parameterized full-text lookup. Consider its lexical matches
   across the full canonical corpus before applying the global limit.
   Group candidates into the explicitly requested scopes. Within each
   group, keep the frozen score order and ID tie-break. Place candidates
   with a source-verified scope match but no lexical hit after lexical
   hits in that group, ordered by ID and logged as metadata matches.
   Interleave the groups in question order. Count each ID once toward
   the 32-candidate limit. Retain the remaining lexical hits in frozen
   order as capacity allows.
4. Assemble the interleaved list under the common limits. For each
   requested scope, try its highest-ranked whole dependency bundle first
   before adding supplementary bundles. Keep shared dependencies once.
   When a bundle does not fit, record the exclusion and continue. Report
   any requested scope that has no retained procedure passage. A heading
   or warning alone cannot satisfy a procedure scope.

Both variants use the same unannotated question. The scope map and alias
rules describe the corpus and language generally. The candidate has no
access to case IDs, expected responses, reference IDs, or gold scope
annotations. Reference IDs are used only after each result is recorded.
The candidate may inspect more lexical matches than the baseline's
32-result output. Include that work in its latency and report the number
of lexical and metadata candidates considered and retained.

## Comparison and acceptance criteria

Run one coverage pass and three warm timing passes per question and
variant, alternating variant order. Include scope resolution, retrieval,
ranking, and assembly in end-to-end latency. Exclude index construction
for both variants. Record the resolved scopes, candidate IDs before and
after the limit, final IDs, excluded bundles, fallback reasons, errors,
latencies, and evidence tokens. Preserve the request-to-trace mapping.
All requests use local deterministic retrieval.

- **Primary measure** Complete reference coverage after assembly.
  Preserve every new case covered by fixed 32 and reach at least 7/8
  on the new set. Report the two counts and the case-by-case gains.
- **Loss diagnosis** Record separately whether a missing reference was
  outside the candidate list, reachable through a candidate dependency,
  or excluded at assembly. Report raw ranking recall and recall after
  dependency expansion before the context cap.
- **Scope integrity** Each retained procedure bundle must keep its
  product, stage, and required source dependencies. A passage for the
  wrong product, variant, or stage cannot count toward the requested
  scope. For a question with an unresolved binding, record fallback
  and report the scope as unresolved.
- **Efficiency** Compare end-to-end latency and final evidence tokens.
  The proposed guardrail is at most 1.25 times the fixed-32 warm median
  latency. Keep the same context limits and report failures in the
  coverage denominator.

The coverage and latency thresholds are proposed for review. The
experiment measures documentary retrieval on this corpus. The expected
behavior descriptions guide evidence review.

## Separate regressions

- **AD01** Replay the exact reviewed question. Check that the candidate
  makes the MabSelect solvent passage `E167-E` reachable and retains
  its warning `E167-W` with the complete Protein A Sepharose and MabSelect
  reference set. Fixed 32 previously missed `E167-E` during ranking and
  excluded `E167-W` during assembly.
  [Reviewed AD01](cytiva-neo4j-adaptive-depth-protocol-v01.md#ad01)
- **XC06** Replay the exact reviewed question. Preserve the full set
  from fixed 32, including `E167-P` for the common wash and `E167-S`
  for the stronger alkali option. Keep the SuRe/SuRe LX restriction
  attached to the latter. [Reviewed XC06](cytiva-expanded-heldout-questions-v01.md#xc06)

Score these two cases separately from the eight new questions.

## New questions

Each question has one required evidence set with the source dependencies
used by the assembler. Page numbers refer to the printed manual.

### SP01

**Question** For Protein G Sepharose solvent cleaning and MabSelect detergent cleaning of strongly bound lipids, which route specifies a hold and which specifies a detergent volume? Give the follow-up wash for each.

**Expected behavior** Answer. The Sepharose solvent route uses 70% ethanol with a 12 h hold, then at least 5 CV of binding buffer. Keep its lower-flow warning. The MabSelect detergent route specifies 2 CV of a nonionic detergent, followed immediately by at least 5 CV of sterile filtered binding buffer at pH 7.0–8.0.

**Direct evidence** `E166-E`, `E167-D`.

**Complete evidence set** `E166-E`, `E166-H`, `E166-LH`, `E166-W`, `E167-D`, `E167-H`, `E167-LH`. Printed pages 166, 167.

### SP02

**Question** For precipitated protein on Protein A Sepharose and for the stronger alkali route on MabSelect SuRe LX, which procedure specifies a binding-buffer wash before the cleaning reagent?

**Expected behavior** Answer. The SuRe LX route starts with 3 CV of binding buffer before the stronger alkali wash. The cited Sepharose procedure starts with the guanidine wash. Keep each sequence under its own product.

**Direct evidence** `E166-P`, `E167-S`.

**Complete evidence set** `E166-H`, `E166-P`, `E166-PH`, `E167-H`, `E167-PH`, `E167-S`, `E167-SH`. Printed pages 166, 167.

### SP03

**Question** My notes say MabSelect and list solvent cleaning for strongly bound lipids, but they also give the 10–15 min contact time from the SuRe alkali procedure. Does that contact time apply to the solvent cleaning?

**Expected behavior** Refuse transfer. The 10–15 min contact time is tied to the stronger alkali step for SuRe and SuRe LX. The cited MabSelect solvent route gives solvent volumes, an immediate rinse, gradient guidance, and a flow warning. It supplies no matching 10–15 min contact time.

**Direct evidence** `E167-E`, `E167-S`.

**Complete evidence set** `E167-E`, `E167-H`, `E167-LH`, `E167-PH`, `E167-S`, `E167-SH`, `E167-W`. Printed pages 167.

### SP04

**Question** For Protein A Sepharose nonionic detergent cleaning, is 37 °C stated for the detergent example or for the immediate binding-buffer rinse?

**Expected behavior** Answer. The 37 °C condition belongs to the 0.1% Triton X-100 example for 1 min. The immediate rinse is at least 5 CV of sterile binding buffer. The passage specifies no rinse temperature.

**Direct evidence** `E166-D`.

**Complete evidence set** `E166-D`, `E166-H`, `E166-LH`. Printed pages 166.

### SP05

**Question** On HiTrap Blue HP 5 mL, which approximate syringe drop rate is given during sample loading, and what elution volume is usually sufficient for a one-step elution?

**Expected behavior** Answer. The loading footnote associates 5 mL/min with about 120 drops/min for the 5 mL column using a syringe. One-step elution usually needs 5 CV. The loading note does not define the elution flow or drop rate.

**Direct evidence** `E121-L`, `E121-F`, `E121-E`.

**Complete evidence set** `E120-H`, `E120-P`, `E120-W`, `E121-E`, `E121-F`, `E121-L`, `E121-PH`. Printed pages 120, 121.

### SP06

**Question** For HiTrap Blue HP 1 mL, can I apply the 0.2 mL/min lower bound from sample loading to linear-gradient elution? Give the documented ranges for both stages.

**Expected behavior** Refuse transfer. Loading is 0.2–1 mL/min. Elution is 1–2 mL/min for this format, with 10–20 CV usually sufficient for a linear gradient. Preserve the syringe footnote within its own scope.

**Direct evidence** `E121-L`, `E121-E`.

**Complete evidence set** `E120-H`, `E120-P`, `E120-W`, `E121-E`, `E121-F`, `E121-L`, `E121-PH`. Printed pages 120, 121.

### SP07

**Question** For HiTrap Blue HP washing, does the manual give a binding-buffer pH option and an observable endpoint? Keep the buffer alternatives distinct from the wash criteria.

**Expected behavior** Answer. The listed binding-buffer alternatives are at pH 7.0. Wash with binding buffer, generally at least 5–10 CV, until absorbance reaches a steady baseline or no material remains in the effluent. Retain the protocol warning and avoid pairing binding and elution formulations.

**Direct evidence** `E121-B`, `E121-W`.

**Complete evidence set** `E120-H`, `E120-P`, `E120-W`, `E121-B`, `E121-BH`, `E121-PH`, `E121-W`. Printed pages 120, 121.

### SP08

**Question** I recorded a flow of 1 mL/min on HiTrap Blue HP 1 mL, but the log does not say whether it was loading or washing. Can the flow alone identify the stage?

**Expected behavior** Clarify. Ask which step was being performed. The value lies at the upper end of the loading range and the lower end of the washing range. Keep the syringe conversion specific to its documented condition.

**Direct evidence** `E121-L`, `E121-W`.

**Complete evidence set** `E120-H`, `E120-P`, `E120-W`, `E121-F`, `E121-L`, `E121-PH`, `E121-W`. Printed pages 120, 121.
