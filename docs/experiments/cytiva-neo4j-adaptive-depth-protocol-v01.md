# Neo4j adaptive retrieval depth protocol

**Status** Draft for review.

This experiment compares fixed depth 16, fixed depth 32, and adaptive depth
16→32 on the same 42 reviewed passages. Use the expanded Neo4j index, the
parameterized full-text query, the frozen tie-break, the common dependency
assembler, and the 4,096-token context limit. Each depth applies to both the
ranked list and the assembled context. Record the new policy and question
set as a separate configuration tied to the original freeze ID and digest.
[XC results](cytiva-expanded-heldout-results-v01.md)

## Proposed trigger

1. Retrieve and assemble at depth 16. Read the assembler's recorded
   exclusions. Expand when at least one exclusion has
   `passage_cap=true` and the excluded seed is still absent from the final
   depth-16 context. The check is against the final context because a seed
   may be added later as a dependency of another bundle.
2. On expansion, run the frozen retrieval query at depth 32 and assemble
   from that ranking with the depth-32 cap. Use that context as the
   adaptive result. Allow one expansion per request.
3. Otherwise, return the depth-16 context. Log an empty retrieval
   separately when the ranking is empty.

The trigger treats a rejected dependency bundle as a sign that the passage
budget may have removed useful evidence. It has no access to the expected
evidence, answer labels, or case IDs. A relevant passage ranked beyond
16 can still be missed when the assembler records no qualifying exclusion.
A token-cap-only exclusion is a separate condition because the token
budget stays at 4,096. An exclusion can qualify when both caps apply.
The initial test evaluates this observable signal without a score cutoff
or an additional relevance model.

## Comparison and success criteria

Run one coverage pass and three warm timing passes per case and variant,
rotating variant order. All variants use the same input, local Neo4j
instance, corpus, resource guard, and trace settings. Validate the same
corpus inventory before execution. For the adaptive variant, time the
whole request including the initial search, assembly, trigger, and any
second search and assembly. Report search and assembly separately where
the timing records allow it.

- **Primary measure** Complete evidence in the final context. Require
  every reference passage including the document dependencies. Report
  recall before assembly and missing reference IDs after assembly.
- **Coverage gate** Preserve every case covered by fixed 32, and every
  case covered by fixed 16. Apply this gate to the 10 new cases.
- **Efficiency gate** Expand on at most 5 of the 10 new cases. Require
  lower median total latency and lower median final evidence tokens than
  fixed 32. Report the warm sample count, median, and range, plus tokens
  processed during both assembly attempts when available.
- **Trigger diagnosis** Count unnecessary expansions where fixed 16
  already covers the reference, missed opportunities where adaptive
  stays at 16 and fixed 32 covers the reference, and regressions where
  the second context loses a reference already retained at 16. Separate
  passage-cap, token-cap, and ranking losses.
- **Integrity** Record the reason, both ranked and assembled ID lists
  when expanded, and resource or retrieval errors. Count failures in
  coverage denominators and report successful timing samples explicitly.
  Capture case-to-trace mapping in the journal.

The five-expansion limit is a proposed target for review. The small
English set evaluates document retrieval. The expected answer,
clarification, and refusal labels describe the source boundary for
human review. They do not score an answer generator. There are no
model calls in any variant.

## Regression XC06

Reuse the exact question and references from the reviewed XC set. The
reference contains `E167-H`, `E167-P`, `E167-PH`, `E167-S`, and
`E167-SH`. Expect fixed 16 to miss complete coverage and fixed 32 to
cover it, as in the historical run. The adaptive variant must expand
and recover the complete bundle. Record XC06 separately from the 10
new cases and their efficiency gate.
[Reviewed XC06](cytiva-expanded-heldout-questions-v01.md#xc06)

## New questions

Each entry gives the exact English input, the expected documentary
behavior, and the full reference set including source dependencies.
Page numbers refer to the printed Cytiva manual. The passages
`E118-I` and `E121-EQ` remain excluded from the corpus.

### AD01

**Question** For strongly bound lipid deposits, which solvent choices does the manual list for MabSelect, and which choice is described for Protein A Sepharose? Keep the handling precautions with each medium.

**Expected behavior** Answer. Protein A Sepharose describes 70% ethanol with a 12 h hold. MabSelect gives 3–4 CV of either 70% ethanol or 30% 2-propanol, an immediate rinse, and increasing gradients at high organic-solvent concentrations to avoid air bubbles. Both have a lower-flow warning in their respective solvent routes.

**Direct evidence** `E166-E`, `E167-E`.

**Complete evidence set** `E166-E`, `E166-H`, `E166-LH`, `E166-W`, `E167-E`, `E167-H`, `E167-LH`, `E167-W`. Printed pages 166, 167.

### AD02

**Question** A Protein G Sepharose regeneration left material behind. Which cleaning route would the manual point to for precipitated protein versus strongly bound lipid, if the deposit type can be established?

**Expected behavior** Answer. Residual material alone leaves the cause unresolved. The precipitated-protein route uses guanidine. The lipid section gives detergent and the ethanol alternative, with its warning. Treat the routes as conditional options.

**Direct evidence** `E166-T`, `E166-P`, `E166-D`, `E166-E`.

**Complete evidence set** `E166-D`, `E166-E`, `E166-H`, `E166-LH`, `E166-P`, `E166-PH`, `E166-T`, `E166-W`. Printed pages 166.

### AD03

**Question** The MabSelect detergent route specifies 2 CV of detergent. Can I reuse that detergent volume for the Protein A Sepharose Triton example?

**Expected behavior** Refuse. The MabSelect volume is scoped to its detergent route. The Protein A Sepharose example specifies concentration, temperature, and time, with no detergent volume in the cited passage.

**Direct evidence** `E167-D`, `E166-D`.

**Complete evidence set** `E166-D`, `E166-H`, `E166-LH`, `E167-D`, `E167-H`, `E167-LH`. Printed pages 166, 167.

### AD04

**Question** How does the common MabSelect contact-time instruction differ from the stronger sodium hydroxide instruction for MabSelect SuRe LX?

**Expected behavior** Answer. The common route gives at least 10 min. The stronger alkali option for SuRe and SuRe LX gives 10–15 min. Keep the contact times attached to their respective routes.

**Direct evidence** `E167-P`, `E167-S`.

**Complete evidence set** `E167-H`, `E167-P`, `E167-PH`, `E167-S`, `E167-SH`. Printed pages 167.

### AD05

**Question** I wrote down 'sterile filtered binding buffer at pH 7.0–8.0' after detergent cleaning, but my notes mix Protein G Sepharose and MabSelect. What product detail matters before I use that instruction?

**Expected behavior** Clarify. Confirm the medium. The cited MabSelect detergent route specifies sterile filtered buffer at pH 7.0–8.0. The Protein G Sepharose detergent route specifies sterile binding buffer, with filtration and pH unspecified in that passage.

**Direct evidence** `E166-D`, `E167-D`.

**Complete evidence set** `E166-D`, `E166-H`, `E166-LH`, `E167-D`, `E167-H`, `E167-LH`. Printed pages 166, 167.

### AD06

**Question** For a murine antibody that co-purifies with bovine immunoglobulins, how should I interpret the seven-media HiTrap HIC kit and the Phenyl HP result in the example?

**Expected behavior** Answer. The similarity to the target calls for selection and optimization. Screen media with different hydrophobicities. The kit contains seven media. Phenyl HP was optimal in the illustrated example.

**Direct evidence** `E119-BI`, `E119-S`, `E119-X`.

**Complete evidence set** `E119-BH`, `E119-BI`, `E119-S`, `E119-X`. Printed pages 119.

### AD07

**Question** Albumin may hide other UV peaks in my sample, but my target has similar hydrophobicity to albumin. Which of those two facts governs the Blue Sepharose decision?

**Expected behavior** Refuse. Potential UV masking is a stated use case. Similar target hydrophobicity triggers the explicit instruction against using Blue Sepharose.

**Direct evidence** `E120-U`, `E120-W`.

**Complete evidence set** `E120-H`, `E120-U`, `E120-W`. Printed pages 120.

### AD08

**Question** For HiTrap Blue HP, does the potassium-based binding buffer formulation determine the matching potassium-based elution formulation? List the potassium-based formulations with their roles.

**Expected behavior** Refuse. The binding option is 50 mM potassium hydrogen phosphate (KH2PO4), pH 7.0. The elution option is 0.05 M potassium hydrogen phosphate plus 1.5 M potassium chloride, pH 7.0. The source lists alternatives by role without prescribing a pairing. Preserve source nomenclature.

**Direct evidence** `E121-B`.

**Complete evidence set** `E120-H`, `E120-P`, `E120-W`, `E121-B`, `E121-BH`. Printed pages 120, 121.

### AD09

**Question** With a HiTrap Blue HP 5 mL column, is 5 mL/min listed for both syringe loading and washing? Explain which end of each range it falls on and how the wash ends.

**Expected behavior** Answer. 5 mL/min is the upper end of the 0.5–5 mL/min loading range and lower end of the 5–10 mL/min washing range. Wash with binding buffer, generally at least 5–10 CV, until steady absorbance or no material remains in the effluent. Keep the syringe note in scope.

**Direct evidence** `E121-L`, `E121-W`.

**Complete evidence set** `E120-H`, `E120-P`, `E120-W`, `E121-F`, `E121-L`, `E121-PH`, `E121-W`. Printed pages 120, 121.

### AD10

**Question** The only observation in my affinity-purification notes is a minor impurity. What should I establish before deciding whether to use the sample directly or choose a separation method?

**Expected behavior** Clarify. Check whether the impurity interferes with the intended application and whether the sample is in the stated laboratory-scale scope. If further separation is warranted, identify the contaminant and the relevant difference from the target before selecting a method.

**Direct evidence** `E118-USE`, `E118-C`, `E118-M`.

**Complete evidence set** `E118-C`, `E118-M`, `E118-USE`. Printed pages 118.
