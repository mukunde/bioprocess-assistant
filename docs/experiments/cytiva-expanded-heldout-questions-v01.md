# Cytiva held-out retrieval questions

**Status** Draft for human review.

These 12 English questions use the 42 reviewed passages pinned by the expanded candidate. They cover six cleaning cases and six contaminant or chromatography cases. Each case lists one required evidence set.

The direct evidence identifies the substantive passages. The complete evidence set adds all source dependencies required by the common assembler. Source locations below use printed Cytiva page numbers.

Coverage requires the entire evidence set in the final context. Report retrieval recall, coverage, latency, and both token counts at depths 8, 16, and 32 under the frozen settings. The expected behavior records the documentary boundary for review. The retrieval run measures evidence access.

All reference sets fit the depth-eight assembly limit and the 4,096-token cap in a reference-only check. The largest set contains 514 context tokens using the frozen tokenizer.

Review the wording, expected behavior, and completeness of each evidence set before execution.

## XC01

**Question** For strongly bound lipid deposits, compare the nonionic detergent wash on Protein G Sepharose with the one on MabSelect. Which quantities and conditions are stated for each?

**Expected behavior** Answer. Protein G Sepharose gives 0.1% Triton X-100 at 37 °C for 1 min as an example, followed immediately by at least 5 CV of sterile binding buffer. MabSelect specifies 2 CV of nonionic detergent, with 0.1% as an example, then immediately at least 5 CV of sterile filtered binding buffer at pH 7.0–8.0. Keep the two conditions and examples scoped to their respective media.

**Direct evidence** E166-D, E167-D.

**Complete evidence set** E166-D, E166-H, E166-LH, E167-D, E167-H, E167-LH. Printed pages 166, 167.

## XC02

**Question** Both cleaning sections mention 6 M guanidine hydrochloride for precipitated or denatured material. How do the Protein A Sepharose and MabSelect versions differ?

**Expected behavior** Answer. Protein A Sepharose lists 2 CV of 6 M guanidine hydrochloride, followed immediately by at least 5 CV of binding buffer. The MabSelect guanidine alternative specifies 6 M guanidine hydrochloride in 10 mM sodium hydroxide, 2 CV and at least 10 min contact, followed immediately by at least 5 CV of sterile filtered binding buffer at pH 7.0–8.0. The compared Protein A passage gives no contact time.

**Direct evidence** E166-P, E167-P.

**Complete evidence set** E166-H, E166-P, E166-PH, E167-H, E167-P, E167-PH. Printed pages 166, 167.

## XC03

**Question** For the MabSelect solvent route, a colleague wants to apply 30% 2-propanol abruptly and keep the usual flow. What does the manual say about these two choices?

**Expected behavior** Answer. The passage calls for increasing gradients at high organic-solvent concentrations to avoid air bubbles, and for a lower flow when cleaning with 30% 2-propanol because backpressure rises. It provides no exact gradient profile or reduced flow rate.

**Direct evidence** E167-E, E167-W.

**Complete evidence set** E167-E, E167-H, E167-LH, E167-W. Printed pages 167.

## XC04

**Question** The label in my notes just says MabSelect, and I am considering the stronger sodium hydroxide option. What product detail should I verify before deciding?

**Expected behavior** Clarify. Verify whether the medium is MabSelect SuRe or MabSelect SuRe LX. The stronger alkali option is scoped to those two media. Ask for the exact variant before applying it.

**Direct evidence** E167-SH.

**Complete evidence set** E167-H, E167-PH, E167-SH. Printed pages 167.

## XC05

**Question** On Protein G Sepharose, does the source support treating the detergent wash and the 70% ethanol hold as consecutive steps of one recipe?

**Expected behavior** Refuse. Decline to present a combined sequence. The ethanol passage describes an alternative. Preserve its 12 h hold and lower-flow warning if describing it. Do not infer compatibility or prescribe both routes.

**Direct evidence** E166-D, E166-E.

**Complete evidence set** E166-D, E166-E, E166-H, E166-LH, E166-W. Printed pages 166.

## XC06

**Question** For MabSelect, what does the source require of the binding-buffer rinse after the standard denatured-material wash and after the stronger alkali option?

**Expected behavior** Answer. Both say to wash immediately with at least 5 CV of sterile filtered binding buffer at pH 7.0–8.0. The stronger alkali option applies to SuRe and SuRe LX. Keep the preceding treatments distinct.

**Direct evidence** E167-P, E167-S.

**Complete evidence set** E167-H, E167-P, E167-PH, E167-S, E167-SH. Printed pages 167.

## XC07

**Question** At laboratory scale, why might I use an affinity-purified sample with minor contaminants directly, yet consider HiTrap Blue HP for a different sample whose known albumin masks other UV peaks?

**Expected behavior** Answer. Direct use can be appropriate when minor contaminants do not interfere with the intended application. Known high albumin that might mask other UV peaks is a stated use for HiTrap Blue HP. Preserve the warning for a target with hydrophobicity similar to albumin, and keep the two samples distinct.

**Direct evidence** E118-USE, E120-U, E120-W.

**Complete evidence set** E118-USE, E120-H, E120-U, E120-W. Printed pages 118, 120.

## XC08

**Question** In the HIC strategy for albumin and transferrin and the Blue Sepharose strategy for albumin, which component is intended to bind in each case?

**Expected behavior** Answer. In the stated HIC strategy most monoclonal antibodies are more hydrophobic and can bind while albumin and transferrin wash through. In the Blue Sepharose route albumin binds to the ligand through electrostatic and/or hydrophobic interactions. Preserve the qualifier most and the albumin scope.

**Direct evidence** E119-H, E120-A.

**Complete evidence set** E119-AH, E119-H, E120-A, E120-H. Printed pages 119, 120.

## XC09

**Question** I am considering an albumin-removal step before another purification step, but I have not assessed my target's hydrophobicity. What can the manual establish, and what detail is needed before choosing Blue Sepharose?

**Expected behavior** Clarify. The source allows albumin removal before or after other purification steps. Ask whether target hydrophobicity is similar to albumin before choosing Blue Sepharose, since the manual says not to use it in that condition. Do not presume suitability.

**Direct evidence** E120-A, E120-W.

**Complete evidence set** E120-A, E120-H, E120-W. Printed pages 120.

## XC10

**Question** On HiTrap Blue HP 1 mL, the wash and elution flow ranges look identical. How do I distinguish the wash endpoint from the guidance for step or gradient elution?

**Expected behavior** Answer. Both use 1–2 mL/min. Wash uses binding buffer, generally at least 5–10 CV until either a steady absorbance baseline or no material in the effluent. Elution uses elution buffer, generally 5 CV for one-step or 10–20 CV for linear gradient. Preserve the Blue Sepharose warning inherited from the protocol.

**Direct evidence** E121-W, E121-E.

**Complete evidence set** E120-H, E120-P, E120-W, E121-E, E121-PH, E121-W. Printed pages 120, 121.

## XC11

**Question** For syringe loading on HiTrap Blue HP 5 mL at 0.5 mL/min, can I use the footnote to state an exact drop rate at that flow?

**Expected behavior** Refuse. 0.5 mL/min is within the stated loading range of 0.5–5 mL/min. The syringe note gives approximately 120 drops/min at 5 mL/min for the 5 mL column. It provides no exact drop rate at 0.5 mL/min. Do not interpolate or borrow the 1 mL column example.

**Direct evidence** E121-L, E121-F.

**Complete evidence set** E120-H, E120-P, E120-W, E121-F, E121-L, E121-PH. Printed pages 120, 121.

## XC12

**Question** Antibody aggregates are one possible contaminant after affinity capture. Which separation principle would address a demonstrated size difference, and does this section specify a recipe for my sample?

**Expected behavior** Answer. Antibody aggregates are listed among possible contaminants. SEC is the technique associated with differences in size. The stated principle is conditional on a demonstrated size difference. The passages give no sample-specific SEC recipe or guarantee.

**Direct evidence** E118-C, E118-M.

**Complete evidence set** E118-C, E118-M. Printed pages 118.
