# FT01-FT12: paired human-review cards

All twelve decisions are pending. These are synthetic user questions and proposed
gold forms/answers, not manual quotations or approvals. The method was locked
before authoring; no arm has been executed and no output has informed the cases.
The same author knows the corpus/code: this is not blinded independent validation.
Natural wording is retained even when outside the declared bounded grammar.

Each card requires review of both language texts, both structured forms (in
[submissions.json](submissions.json)), exact source/intent origins (in
[references.json](references.json)), expected answers, owner/selector order and
retained reservations. Do not send this review document or gold to either runtime.

One approval may cover both languages only after their equivalence is checked.
No actual decision is created by the [template](review-template.json). Execution
requires all twelve real approvals bound to the frozen candidate and these exact
payloads. P/G prior case review remains separate and pending.

## FT01 — multi_task_ownership

**Decision: pending.**

**EN input**

> D: HiTrap Blue HP 5 mL. E: HiTrap Blue HP 1 mL. Give washing flow for E and for D stopping criteria.

**FR input**

> D : HiTrap Blue HP 5 mL. E : HiTrap Blue HP 1 mL. Donne le débit de lavage pour E et pour D les critères de fin du lavage.

**Proposed structured meaning**

- D: product {"state": "provided", "value": "HiTrap Blue HP 5 mL"}; separate column {"state": "not_supplied", "value": null}.
  - operating_phase/washing: stopping_criteria; buffer use not_applicable.
- E: product {"state": "provided", "value": "HiTrap Blue HP 1 mL"}; separate column {"state": "not_supplied", "value": null}.
  - operating_phase/washing: flow_rate; buffer use not_applicable.

**Expected answer / diagnostic (EN)**

E, 1 mL: washing flow 1–2 mL/min. D: stop washing at a steady absorbance baseline OR when no material remains in the effluent. Keep preparations separate.

**Réponse / diagnostic attendu (FR)**

E, 1 mL : débit de lavage de 1 à 2 mL/min. D : terminer le lavage à une ligne de base d’absorbance stable OU lorsqu’il ne reste plus de matière dans l’effluent. Garder les préparations distinctes.

**Documentary units**

| Owner/item | Information | Expected state | Required admissible bundle |
|---|---|---|---|
| D/D-washing | stopping_criteria | supported | E120-H + E120-P + E120-W + E121-PH + E121-W |
| E/E-washing | flow_rate | supported | E120-H + E120-P + E120-W + E121-PH + E121-W |

**Retained reservations / points to validate**

- The text mentions D before E; preserve task order D/E even though the first requested information is for E.
- Do not transfer the 1 mL flow to D or infer a duration; the endpoint alternatives are not cumulative requirements.

**Original manual passages to inspect**

[E120-H — PDF p. 120](#e120-h), [E120-P — PDF p. 120](#e120-p), [E120-W — PDF p. 120](#e120-w), [E121-PH — PDF p. 121](#e121-ph), [E121-W — PDF p. 121](#e121-w)

**Exact input origins (Unicode code points, half-open)**

| Language | Origin | Interval | Exact input quote |
|---|---|---|---|
| en | gold-D-scope | [0, 22) | D: HiTrap Blue HP 5 mL |
| en | gold-E-scope | [24, 46) | E: HiTrap Blue HP 1 mL |
| en | gold-D-request-0 | [76, 99) | for D stopping criteria |
| en | gold-E-request-0 | [53, 71) | washing flow for E |
| fr | gold-D-scope | [0, 23) | D : HiTrap Blue HP 5 mL |
| fr | gold-E-scope | [25, 48) | E : HiTrap Blue HP 1 mL |
| fr | gold-D-request-0 | [85, 121) | pour D les critères de fin du lavage |
| fr | gold-E-request-0 | [59, 81) | débit de lavage pour E |

## FT02 — multi_task_ownership

**Decision: pending.**

**EN input**

> D: HiTrap Blue HP 1 mL. E: HiTrap Blue HP 5 mL. For E, I need the loading flow. For D, give washing flow.

**FR input**

> D : HiTrap Blue HP 1 mL. E : HiTrap Blue HP 5 mL. Pour E, il me faut le débit de chargement. Pour D, donne le débit de lavage.

**Proposed structured meaning**

- D: product {"state": "provided", "value": "HiTrap Blue HP 1 mL"}; separate column {"state": "not_supplied", "value": null}.
  - operating_phase/washing: flow_rate; buffer use not_applicable.
- E: product {"state": "provided", "value": "HiTrap Blue HP 5 mL"}; separate column {"state": "not_supplied", "value": null}.
  - operating_phase/sample_application: flow_rate; buffer use not_applicable.

**Expected answer / diagnostic (EN)**

E, 5 mL: loading flow 0.5–5 mL/min. D, 1 mL: washing flow 1–2 mL/min. The syringe note remains approximate and limited to its column/flow reference.

**Réponse / diagnostic attendu (FR)**

E, 5 mL : débit de chargement de 0,5 à 5 mL/min. D, 1 mL : débit de lavage de 1 à 2 mL/min. La note sur la seringue reste approximative et limitée à sa correspondance colonne/débit.

**Documentary units**

| Owner/item | Information | Expected state | Required admissible bundle |
|---|---|---|---|
| D/D-washing | flow_rate | supported | E120-H + E120-P + E120-W + E121-PH + E121-W |
| E/E-sample_application | flow_rate | supported | E120-H + E120-P + E120-W + E121-F + E121-L + E121-PH |

**Retained reservations / points to validate**

- Loading and washing are different phases with different flow ranges.
- Natural wording is retained even if outside the bounded interpreter grammar; do not rewrite it after results.
- The inherited syringe note is not a universal conversion or a requested additional unit.

**Original manual passages to inspect**

[E120-H — PDF p. 120](#e120-h), [E120-P — PDF p. 120](#e120-p), [E120-W — PDF p. 120](#e120-w), [E121-F — PDF p. 121](#e121-f), [E121-L — PDF p. 121](#e121-l), [E121-PH — PDF p. 121](#e121-ph), [E121-W — PDF p. 121](#e121-w)

**Exact input origins (Unicode code points, half-open)**

| Language | Origin | Interval | Exact input quote |
|---|---|---|---|
| en | gold-D-scope | [0, 22) | D: HiTrap Blue HP 1 mL |
| en | gold-E-scope | [24, 46) | E: HiTrap Blue HP 5 mL |
| en | gold-D-request-0 | [80, 104) | For D, give washing flow |
| en | gold-E-request-0 | [48, 78) | For E, I need the loading flow |
| fr | gold-D-scope | [0, 23) | D : HiTrap Blue HP 1 mL |
| fr | gold-E-scope | [25, 48) | E : HiTrap Blue HP 5 mL |
| fr | gold-D-request-0 | [93, 125) | Pour D, donne le débit de lavage |
| fr | gold-E-request-0 | [50, 91) | Pour E, il me faut le débit de chargement |

## FT03 — stage_vs_formulation

**Decision: pending.**

**EN input**

> D: HiTrap Blue HP 5 mL. Give loading flow and washing column volumes for D.

**FR input**

> D : HiTrap Blue HP 5 mL. Donne pour D le débit de chargement et le volume de lavage en volumes de colonne.

**Proposed structured meaning**

- D: product {"state": "provided", "value": "HiTrap Blue HP 5 mL"}; separate column {"state": "not_supplied", "value": null}.
  - operating_phase/sample_application: flow_rate; buffer use not_applicable.
  - operating_phase/washing: column_volumes; buffer use not_applicable.

**Expected answer / diagnostic (EN)**

D loading: 0.5–5 mL/min. Washing: generally at least 5–10 column volumes. Do not convert CV to mL or derive a duration.

**Réponse / diagnostic attendu (FR)**

Chargement de D : 0,5 à 5 mL/min. Lavage : généralement au moins 5 à 10 volumes de colonne. Ne pas convertir les CV en mL ni déduire de durée.

**Documentary units**

| Owner/item | Information | Expected state | Required admissible bundle |
|---|---|---|---|
| D/D-sample_application | flow_rate | supported | E120-H + E120-P + E120-W + E121-F + E121-L + E121-PH |
| D/D-washing | column_volumes | supported | E120-H + E120-P + E120-W + E121-PH + E121-W |

**Retained reservations / points to validate**

- Keep the generally/at-least qualification; the requested volume does not imply a washing-flow request.
- The inherited endpoint and syringe-note text must not become additional requested quantities.

**Original manual passages to inspect**

[E120-H — PDF p. 120](#e120-h), [E120-P — PDF p. 120](#e120-p), [E120-W — PDF p. 120](#e120-w), [E121-F — PDF p. 121](#e121-f), [E121-L — PDF p. 121](#e121-l), [E121-PH — PDF p. 121](#e121-ph), [E121-W — PDF p. 121](#e121-w)

**Exact input origins (Unicode code points, half-open)**

| Language | Origin | Interval | Exact input quote |
|---|---|---|---|
| en | gold-D-scope | [0, 22) | D: HiTrap Blue HP 5 mL |
| en | gold-D-request-0 | [29, 41) | loading flow |
| en | gold-D-request-1 | [46, 68) | washing column volumes |
| fr | gold-D-scope | [0, 23) | D : HiTrap Blue HP 5 mL |
| fr | gold-D-request-0 | [41, 60) | débit de chargement |
| fr | gold-D-request-1 | [67, 105) | volume de lavage en volumes de colonne |

## FT04 — stage_vs_formulation

**Decision: pending.**

**EN input**

> D: HiTrap Blue HP 5 mL. List the elution-buffer formulations for D; separately give the washing stopping criteria. Exclude operating elution for D.

**FR input**

> D : HiTrap Blue HP 5 mL. Liste les formulations du tampon d’élution pour D ; donne séparément les critères de fin du lavage. Exclus l’élution opératoire pour D.

**Proposed structured meaning**

- D: product {"state": "provided", "value": "HiTrap Blue HP 5 mL"}; separate column {"state": "not_supplied", "value": null}.
  - preparation/buffer_preparation: buffer_formulation; buffer use provided=elution.
  - operating_phase/washing: stopping_criteria; buffer use not_applicable.
  - Active exclusions: [{"exclusion_id": "D-ban-1", "scope": {"task_id": "D"}, "selector": {"kind": "operating_phase", "code": "elution", "information": "all"}}].

**Expected answer / diagnostic (EN)**

Elution-buffer alternatives: 0.02 M sodium phosphate with 2 M sodium chloride, pH 7.0; OR 0.05 M potassium hydrogen phosphate with 1.5 M potassium chloride, pH 7.0. Washing ends at a steady absorbance baseline OR no remaining material in the effluent. No operating-elution recipe is requested.

**Réponse / diagnostic attendu (FR)**

Tampons d’élution alternatifs : phosphate de sodium 0,02 M avec chlorure de sodium 2 M, pH 7,0 ; OU hydrogénophosphate de potassium 0,05 M avec chlorure de potassium 1,5 M, pH 7,0. Fin du lavage à une ligne de base stable OU absence de matière dans l’effluent. Aucune procédure d’élution opératoire n’est demandée.

**Documentary units**

| Owner/item | Information | Expected state | Required admissible bundle |
|---|---|---|---|
| D/D-buffer_preparation | buffer_formulation | supported | E120-H + E120-P + E120-W + E121-B + E121-BH |
| D/D-washing | stopping_criteria | supported | E120-H + E120-P + E120-W + E121-PH + E121-W |

**Retained reservations / points to validate**

- Buffer preparation is distinct from operating elution; the exclusion must not remove the formulation request.
- Preserve the manual nomenclature without silently correcting it, pairing binding/elution alternatives, or selecting a mode.

**Original manual passages to inspect**

[E120-H — PDF p. 120](#e120-h), [E120-P — PDF p. 120](#e120-p), [E120-W — PDF p. 120](#e120-w), [E121-B — PDF p. 121](#e121-b), [E121-BH — PDF p. 121](#e121-bh), [E121-PH — PDF p. 121](#e121-ph), [E121-W — PDF p. 121](#e121-w)

**Exact input origins (Unicode code points, half-open)**

| Language | Origin | Interval | Exact input quote |
|---|---|---|---|
| en | gold-D-scope | [0, 22) | D: HiTrap Blue HP 5 mL |
| en | gold-D-request-0 | [33, 66) | elution-buffer formulations for D |
| en | gold-D-request-1 | [88, 113) | washing stopping criteria |
| en | gold-D-ban-0 | [115, 146) | Exclude operating elution for D |
| fr | gold-D-scope | [0, 23) | D : HiTrap Blue HP 5 mL |
| fr | gold-D-request-0 | [35, 74) | formulations du tampon d’élution pour D |
| fr | gold-D-request-1 | [98, 123) | critères de fin du lavage |
| fr | gold-D-ban-0 | [125, 159) | Exclus l’élution opératoire pour D |

## FT05 — negation_and_restriction_scope

**Decision: pending.**

**EN input**

> D: HiTrap Blue HP 1 mL. Give washing flow for D but exclude washing stopping criteria for D. Independently, E asks for the general SEC principle.

**FR input**

> D : HiTrap Blue HP 1 mL. Donne le débit de lavage pour D mais exclus les critères de fin du lavage pour D. Indépendamment, E demande le principe général de la SEC.

**Proposed structured meaning**

- D: product {"state": "provided", "value": "HiTrap Blue HP 1 mL"}; separate column {"state": "not_supplied", "value": null}.
  - operating_phase/washing: flow_rate; buffer use not_applicable.
  - Active exclusions: [{"exclusion_id": "D-ban-1", "scope": {"task_id": "D"}, "selector": {"kind": "operating_phase", "code": "washing", "information": ["stopping_criteria"]}}].
- E: product {"state": "not_applicable", "value": null, "reason": "Not required for the explicitly requested documentary information."}; separate column {"state": "not_applicable", "value": null, "reason": "Not required for the explicitly requested documentary information."}.
  - general_topic/method_selection: principle; buffer use not_applicable.

**Expected answer / diagnostic (EN)**

D washing: 1–2 mL/min. SEC separates by size. The endpoint exclusion affects D stopping criteria only; E remains independent.

**Réponse / diagnostic attendu (FR)**

Lavage de D : 1 à 2 mL/min. La SEC sépare selon la taille. L’exclusion vise uniquement les critères de fin de lavage de D ; E reste indépendant.

**Documentary units**

| Owner/item | Information | Expected state | Required admissible bundle |
|---|---|---|---|
| D/D-washing | flow_rate | supported | E120-H + E120-P + E120-W + E121-PH + E121-W |
| E/E-method_selection | principle | supported | E118-M |

**Retained reservations / points to validate**

- Retain the positive D request before processing its exclusion; both units remain counted.
- An atomic source may contain endpoint text, but no endpoint unit may be created or bound.
- SEC principle is not selection or suitability for the sample.

**Original manual passages to inspect**

[E118-M — PDF p. 118](#e118-m), [E120-H — PDF p. 120](#e120-h), [E120-P — PDF p. 120](#e120-p), [E120-W — PDF p. 120](#e120-w), [E121-PH — PDF p. 121](#e121-ph), [E121-W — PDF p. 121](#e121-w)

**Exact input origins (Unicode code points, half-open)**

| Language | Origin | Interval | Exact input quote |
|---|---|---|---|
| en | gold-D-scope | [0, 22) | D: HiTrap Blue HP 1 mL |
| en | gold-E-scope | [108, 144) | E asks for the general SEC principle |
| en | gold-D-request-0 | [24, 47) | Give washing flow for D |
| en | gold-E-request-0 | [123, 144) | general SEC principle |
| en | gold-D-ban-0 | [52, 91) | exclude washing stopping criteria for D |
| fr | gold-D-scope | [0, 23) | D : HiTrap Blue HP 1 mL |
| fr | gold-E-scope | [123, 162) | E demande le principe général de la SEC |
| fr | gold-D-request-0 | [25, 56) | Donne le débit de lavage pour D |
| fr | gold-E-request-0 | [136, 162) | principe général de la SEC |
| fr | gold-D-ban-0 | [62, 105) | exclus les critères de fin du lavage pour D |

## FT06 — negation_and_restriction_scope

**Decision: pending.**

**EN input**

> D: HiTrap Blue HP 5 mL. Do not exclude loading flow for D; give loading flow for D. Exclude operating elution for D.

**FR input**

> D : HiTrap Blue HP 5 mL. N’exclus pas le débit de chargement pour D ; donne le débit de chargement pour D. Exclus l’élution opératoire pour D.

**Proposed structured meaning**

- D: product {"state": "provided", "value": "HiTrap Blue HP 5 mL"}; separate column {"state": "not_supplied", "value": null}.
  - operating_phase/sample_application: flow_rate; buffer use not_applicable.
  - Active exclusions: [{"exclusion_id": "D-ban-1", "scope": {"task_id": "D"}, "selector": {"kind": "operating_phase", "code": "elution", "information": "all"}}].

**Expected answer / diagnostic (EN)**

D loading flow: 0.5–5 mL/min. The negated exclusion creates no conflict or extra positive request. No operating-elution instruction is requested.

**Réponse / diagnostic attendu (FR)**

Débit de chargement de D : 0,5 à 5 mL/min. L’exclusion niée ne crée ni conflit ni demande positive supplémentaire. Aucune instruction d’élution opératoire n’est demandée.

**Documentary units**

| Owner/item | Information | Expected state | Required admissible bundle |
|---|---|---|---|
| D/D-sample_application | flow_rate | supported | E120-H + E120-P + E120-W + E121-F + E121-L + E121-PH |

**Retained reservations / points to validate**

- Preserve full negation and owner spans; a negated ban is auditable but inactive.
- Do not transfer the washing range or turn the approximate syringe note into a universal conversion.

**Original manual passages to inspect**

[E120-H — PDF p. 120](#e120-h), [E120-P — PDF p. 120](#e120-p), [E120-W — PDF p. 120](#e120-w), [E121-F — PDF p. 121](#e121-f), [E121-L — PDF p. 121](#e121-l), [E121-PH — PDF p. 121](#e121-ph)

**Exact input origins (Unicode code points, half-open)**

| Language | Origin | Interval | Exact input quote |
|---|---|---|---|
| en | gold-D-scope | [0, 22) | D: HiTrap Blue HP 5 mL |
| en | gold-D-request-0 | [59, 82) | give loading flow for D |
| en | gold-D-ban-0 | [84, 115) | Exclude operating elution for D |
| en | gold-negated-ban | [24, 57) | Do not exclude loading flow for D |
| fr | gold-D-scope | [0, 23) | D : HiTrap Blue HP 5 mL |
| fr | gold-D-request-0 | [70, 105) | donne le débit de chargement pour D |
| fr | gold-D-ban-0 | [107, 141) | Exclus l’élution opératoire pour D |
| fr | gold-negated-ban | [25, 67) | N’exclus pas le débit de chargement pour D |

## FT07 — facts_and_uncertainty

**Decision: pending.**

**EN input**

> D: HiTrap Blue HP. Column size is unknown. Available sample volume is 7.5 mL. Loaded volume is unknown. Give washing flow for D. Independently, E asks for the general SEC principle.

**FR input**

> D : HiTrap Blue HP. Le volume de colonne est inconnu. L’échantillon contient 7,5 mL disponibles. Le volume chargé est inconnu. Donne le débit de lavage pour D. Indépendamment, E demande le principe général de la SEC.

**Proposed structured meaning**

- D: product {"state": "provided", "value": "HiTrap Blue HP"}; separate column {"state": "unknown", "value": null}.
  - operating_phase/washing: flow_rate; buffer use not_applicable.
  - Facts: [{"key": "sample_volume", "input_role": "user_observation", "value": {"state": "provided", "value": {"value": "7.5", "unit": "mL"}}}, {"key": "loaded_volume", "input_role": "user_observation", "value": {"state": "unknown", "value": null}}].
- E: product {"state": "not_applicable", "value": null, "reason": "Not required for the explicitly requested documentary information."}; separate column {"state": "not_applicable", "value": null, "reason": "Not required for the explicitly requested documentary information."}.
  - general_topic/method_selection: principle; buffer use not_applicable.

**Expected answer / diagnostic (EN)**

Ask for D column format before assigning its washing-flow range; 7.5 mL is available sample volume, not column bed volume or loaded volume. Independently explain that SEC separates by size.

**Réponse / diagnostic attendu (FR)**

Demander le format de colonne de D avant d’attribuer son débit de lavage ; 7,5 mL est le volume d’échantillon disponible, ni le volume de lit de colonne ni le volume chargé. Expliquer indépendamment que la SEC sépare selon la taille.

**Documentary units**

| Owner/item | Information | Expected state | Required admissible bundle |
|---|---|---|---|
| D/D-washing | flow_rate | needs_clarification | No assignment |
| E/E-method_selection | principle | supported | E118-M |

**Retained reservations / points to validate**

- First real context ambiguity: explicit unknown column, not an ambiguous preparation owner.
- Do not infer a format by elimination, invent loaded volume or suppress E.
- Only D flow is withheld; a nearby available source is not a D binding.

**Original manual passages to inspect**

[E118-M — PDF p. 118](#e118-m), [E121-W — PDF p. 121](#e121-w)

**Exact input origins (Unicode code points, half-open)**

| Language | Origin | Interval | Exact input quote |
|---|---|---|---|
| en | gold-D-scope | [0, 17) | D: HiTrap Blue HP |
| en | gold-D-column | [19, 41) | Column size is unknown |
| en | gold-D-fact-0 | [43, 76) | Available sample volume is 7.5 mL |
| en | gold-D-fact-1 | [78, 102) | Loaded volume is unknown |
| en | gold-D-request-0 | [104, 127) | Give washing flow for D |
| en | gold-E-scope | [144, 180) | E asks for the general SEC principle |
| en | gold-E-request-0 | [159, 180) | general SEC principle |
| fr | gold-D-scope | [0, 18) | D : HiTrap Blue HP |
| fr | gold-D-column | [20, 52) | Le volume de colonne est inconnu |
| fr | gold-D-fact-0 | [54, 95) | L’échantillon contient 7,5 mL disponibles |
| fr | gold-D-fact-1 | [97, 125) | Le volume chargé est inconnu |
| fr | gold-D-request-0 | [127, 158) | Donne le débit de lavage pour D |
| fr | gold-E-scope | [176, 215) | E demande le principe général de la SEC |
| fr | gold-E-request-0 | [189, 215) | principe général de la SEC |

## FT08 — facts_and_uncertainty

**Decision: pending.**

**EN input**

> D is named HiTrap Blue HP 1 mL, but its column field says 5 mL. Give washing flow for D. E: HiTrap Blue HP 5 mL. Give washing flow for E.

**FR input**

> D est nommé HiTrap Blue HP 1 mL, mais son volume de colonne est 5 mL. Donne le débit de lavage pour D. E : HiTrap Blue HP 5 mL. Donne le débit de lavage pour E.

**Proposed structured meaning**

- D: product {"state": "provided", "value": "HiTrap Blue HP 1 mL"}; separate column {"state": "provided", "value": {"bed_volume": {"value": "5", "unit": "mL"}}}.
  - operating_phase/washing: flow_rate; buffer use not_applicable.
- E: product {"state": "provided", "value": "HiTrap Blue HP 5 mL"}; separate column {"state": "not_supplied", "value": null}.
  - operating_phase/washing: flow_rate; buffer use not_applicable.

**Expected answer / diagnostic (EN)**

Clarify the conflicting 1 mL product label and 5 mL separate column field for D; neither assertion wins. E remains independent and has washing flow 5–10 mL/min.

**Réponse / diagnostic attendu (FR)**

Clarifier pour D le conflit entre l’étiquette produit 1 mL et le champ colonne séparé 5 mL ; aucune assertion ne prime. E reste indépendant, avec un débit de lavage de 5 à 10 mL/min.

**Documentary units**

| Owner/item | Information | Expected state | Required admissible bundle |
|---|---|---|---|
| D/D-washing | flow_rate | needs_clarification | No assignment |
| E/E-washing | flow_rate | supported | E120-H + E120-P + E120-W + E121-PH + E121-W |

**Retained reservations / points to validate**

- Second real context ambiguity: two conflicting assertions in one preparation, not two invented preparations.
- Preserve qualified-label provenance separately from the explicit column field.
- E may use a source shared with D without assigning that source to the blocked D unit.

**Original manual passages to inspect**

[E120-H — PDF p. 120](#e120-h), [E120-P — PDF p. 120](#e120-p), [E120-W — PDF p. 120](#e120-w), [E121-PH — PDF p. 121](#e121-ph), [E121-W — PDF p. 121](#e121-w)

**Exact input origins (Unicode code points, half-open)**

| Language | Origin | Interval | Exact input quote |
|---|---|---|---|
| en | gold-D-scope | [0, 30) | D is named HiTrap Blue HP 1 mL |
| en | gold-D-column | [40, 62) | column field says 5 mL |
| en | gold-D-request-0 | [64, 87) | Give washing flow for D |
| en | gold-E-scope | [89, 111) | E: HiTrap Blue HP 5 mL |
| en | gold-E-request-0 | [113, 136) | Give washing flow for E |
| fr | gold-D-scope | [0, 31) | D est nommé HiTrap Blue HP 1 mL |
| fr | gold-D-column | [42, 68) | volume de colonne est 5 mL |
| fr | gold-D-request-0 | [70, 101) | Donne le débit de lavage pour D |
| fr | gold-E-scope | [103, 126) | E : HiTrap Blue HP 5 mL |
| fr | gold-E-request-0 | [128, 159) | Donne le débit de lavage pour E |

## FT09 — numeric_roles

**Decision: pending.**

**EN input**

> D: HiTrap Blue HP 5 mL. My observed flow is 0.0 mL/min. Give washing flow for D. In documentary scenario E, minor contaminants do not interfere with the intended application. Explain the general HIC principle for E.

**FR input**

> D : HiTrap Blue HP 5 mL. Le débit observé est de 0,0 mL/min. Donne le débit de lavage pour D. Dans le scénario documentaire E, les contaminants mineurs n’interfèrent pas avec l’application prévue. Explique le principe général de la HIC pour E.

**Proposed structured meaning**

- D: product {"state": "provided", "value": "HiTrap Blue HP 5 mL"}; separate column {"state": "not_supplied", "value": null}.
  - operating_phase/washing: flow_rate; buffer use not_applicable.
  - Facts: [{"key": "observed_flow", "input_role": "user_observation", "value": {"state": "provided", "value": {"value": "0.0", "unit": "mL/min"}}}].
- E: product {"state": "not_applicable", "value": null, "reason": "Not required for the explicitly requested documentary information."}; separate column {"state": "not_applicable", "value": null, "reason": "Not required for the explicitly requested documentary information."}.
  - general_topic/method_selection: principle; buffer use not_applicable.
  - Facts: [{"key": "minor_contaminants_interfere", "input_role": "documentary_scenario", "value": {"state": "provided", "value": false}}].

**Expected answer / diagnostic (EN)**

D documentary washing flow is 5–10 mL/min. The zero observed flow is retained as an unverified observation, not an operating recommendation. HIC separates by differences in hydrophobicity. E supplied false remains conditional on the intended application, not a verified safety claim.

**Réponse / diagnostic attendu (FR)**

Le débit documentaire de lavage de D est de 5 à 10 mL/min. Le débit observé nul reste une observation non vérifiée, pas une recommandation opératoire. La HIC sépare selon les différences d’hydrophobicité. La valeur fausse fournie pour E reste conditionnée à l’application prévue, pas une garantie de sécurité vérifiée.

**Documentary units**

| Owner/item | Information | Expected state | Required admissible bundle |
|---|---|---|---|
| D/D-washing | flow_rate | supported | E120-H + E120-P + E120-W + E121-PH + E121-W |
| E/E-method_selection | principle | supported | E118-M |

**Retained reservations / points to validate**

- Zero and false are supplied values, not missing context.
- No inference of stopped-pump cause, target hydrophobicity, sample suitability, or additional purification is authorized.
- Decimal punctuation may normalize within mL/min; the original lexeme and full application condition remain.

**Original manual passages to inspect**

[E118-M — PDF p. 118](#e118-m), [E118-USE — PDF p. 118](#e118-use), [E120-H — PDF p. 120](#e120-h), [E120-P — PDF p. 120](#e120-p), [E120-W — PDF p. 120](#e120-w), [E121-PH — PDF p. 121](#e121-ph), [E121-W — PDF p. 121](#e121-w)

**Exact input origins (Unicode code points, half-open)**

| Language | Origin | Interval | Exact input quote |
|---|---|---|---|
| en | gold-D-scope | [0, 22) | D: HiTrap Blue HP 5 mL |
| en | gold-D-fact-0 | [24, 54) | My observed flow is 0.0 mL/min |
| en | gold-D-request-0 | [56, 79) | Give washing flow for D |
| en | gold-E-scope | [84, 106) | documentary scenario E |
| en | gold-E-fact-0 | [108, 173) | minor contaminants do not interfere with the intended application |
| en | gold-E-request-0 | [187, 214) | general HIC principle for E |
| fr | gold-D-scope | [0, 23) | D : HiTrap Blue HP 5 mL |
| fr | gold-D-fact-0 | [25, 59) | Le débit observé est de 0,0 mL/min |
| fr | gold-D-request-0 | [61, 92) | Donne le débit de lavage pour D |
| fr | gold-E-scope | [102, 125) | scénario documentaire E |
| fr | gold-E-fact-0 | [127, 195) | les contaminants mineurs n’interfèrent pas avec l’application prévue |
| fr | gold-E-request-0 | [209, 242) | principe général de la HIC pour E |

## FT10 — numeric_roles

**Decision: pending.**

**EN input**

> D: HiTrap Blue HP 1 mL. Available sample volume is 7.5 mL. Loaded volume is unknown. What loading flow does the manual give for D?

**FR input**

> D : HiTrap Blue HP 1 mL. L’échantillon contient 7,5 mL disponibles. Le volume chargé est inconnu. Quel débit de chargement le manuel indique-t-il pour D ?

**Proposed structured meaning**

- D: product {"state": "provided", "value": "HiTrap Blue HP 1 mL"}; separate column {"state": "not_supplied", "value": null}.
  - operating_phase/sample_application: flow_rate; buffer use not_applicable.
  - Facts: [{"key": "sample_volume", "input_role": "user_observation", "value": {"state": "provided", "value": {"value": "7.5", "unit": "mL"}}}, {"key": "loaded_volume", "input_role": "user_observation", "value": {"state": "unknown", "value": null}}].

**Expected answer / diagnostic (EN)**

Loading flow for the 1 mL column: 0.2–1 mL/min. The 7.5 mL sample is not a column-size assertion or loaded volume. Do not calculate loading duration; the syringe note stays approximate and reference-specific.

**Réponse / diagnostic attendu (FR)**

Débit de chargement de la colonne de 1 mL : 0,2 à 1 mL/min. Les 7,5 mL d’échantillon ne sont ni une taille de colonne ni le volume chargé. Ne pas calculer de durée ; la note sur la seringue reste approximative et limitée à sa référence.

**Documentary units**

| Owner/item | Information | Expected state | Required admissible bundle |
|---|---|---|---|
| D/D-sample_application | flow_rate | supported | E120-H + E120-P + E120-W + E121-F + E121-L + E121-PH |

**Retained reservations / points to validate**

- Preserve available, loaded and bed-volume roles separately.
- A qualified product label supplies its own size without filling a separate column field.
- Do not silently replace the natural question by a supported command after results.

**Original manual passages to inspect**

[E120-H — PDF p. 120](#e120-h), [E120-P — PDF p. 120](#e120-p), [E120-W — PDF p. 120](#e120-w), [E121-F — PDF p. 121](#e121-f), [E121-L — PDF p. 121](#e121-l), [E121-PH — PDF p. 121](#e121-ph)

**Exact input origins (Unicode code points, half-open)**

| Language | Origin | Interval | Exact input quote |
|---|---|---|---|
| en | gold-D-scope | [0, 22) | D: HiTrap Blue HP 1 mL |
| en | gold-D-fact-0 | [24, 57) | Available sample volume is 7.5 mL |
| en | gold-D-fact-1 | [59, 83) | Loaded volume is unknown |
| en | gold-D-request-0 | [85, 129) | What loading flow does the manual give for D |
| fr | gold-D-scope | [0, 23) | D : HiTrap Blue HP 1 mL |
| fr | gold-D-fact-0 | [25, 66) | L’échantillon contient 7,5 mL disponibles |
| fr | gold-D-fact-1 | [68, 96) | Le volume chargé est inconnu |
| fr | gold-D-request-0 | [98, 152) | Quel débit de chargement le manuel indique-t-il pour D |

## FT11 — partial_support_and_policy

**Decision: pending.**

**EN input**

> D: HiTrap Blue HP 1 mL. Give washing flow and maximum pressure for D. Independently, E asks for the general IEX principle.

**FR input**

> D : HiTrap Blue HP 1 mL. Donne le débit de lavage et la pression maximale pour D. Indépendamment, E demande le principe général de l’IEX.

**Proposed structured meaning**

- D: product {"state": "provided", "value": "HiTrap Blue HP 1 mL"}; separate column {"state": "not_supplied", "value": null}.
  - operating_phase/washing: flow_rate; buffer use not_applicable.
  - general_topic/operating_limits: maximum_pressure; buffer use not_applicable.
- E: product {"state": "not_applicable", "value": null, "reason": "Not required for the explicitly requested documentary information."}; separate column {"state": "not_applicable", "value": null, "reason": "Not required for the explicitly requested documentary information."}.
  - general_topic/method_selection: principle; buffer use not_applicable.

**Expected answer / diagnostic (EN)**

D washing flow: 1–2 mL/min. No maximum pressure is available in the exact 25 eligible excerpts; do not invent one or claim whole-manual absence. IEX separates by differences in charge; it is not a sample-specific choice.

**Réponse / diagnostic attendu (FR)**

Débit de lavage de D : 1 à 2 mL/min. Aucune pression maximale n’est disponible dans les 25 extraits admissibles précis ; ne pas en inventer ni étendre l’absence au manuel entier. L’IEX sépare selon les différences de charge ; ce n’est pas un choix pour cet échantillon.

**Documentary units**

| Owner/item | Information | Expected state | Required admissible bundle |
|---|---|---|---|
| D/D-washing | flow_rate | supported | E120-H + E120-P + E120-W + E121-PH + E121-W |
| D/D-operating_limits | maximum_pressure | missing_source | No assignment |
| E/E-method_selection | principle | supported | E118-M |

**Retained reservations / points to validate**

- First explicit mixed documentary-support request: supported siblings must remain served despite bounded pressure absence.
- Pressure is a general operating-limit selector, not a washing-flow parameter or a conversion.
- All 25 eligible excerpts support only the bounded absence audit, not an assigned pressure binding.

**Original manual passages to inspect**

[E118-C — PDF p. 118](#e118-c), [E118-M — PDF p. 118](#e118-m), [E118-USE — PDF p. 118](#e118-use), [E119-A — PDF p. 119](#e119-a), [E119-AH — PDF p. 119](#e119-ah), [E119-B — PDF p. 119](#e119-b), [E119-BH — PDF p. 119](#e119-bh), [E119-BI — PDF p. 119](#e119-bi), [E119-BL — PDF p. 119](#e119-bl), [E119-H — PDF p. 119](#e119-h), [E119-I — PDF p. 119](#e119-i), [E119-S — PDF p. 119](#e119-s), [E119-X — PDF p. 119](#e119-x), [E120-A — PDF p. 120](#e120-a), [E120-H — PDF p. 120](#e120-h), [E120-P — PDF p. 120](#e120-p), [E120-U — PDF p. 120](#e120-u), [E120-W — PDF p. 120](#e120-w), [E121-B — PDF p. 121](#e121-b), [E121-BH — PDF p. 121](#e121-bh), [E121-E — PDF p. 121](#e121-e), [E121-F — PDF p. 121](#e121-f), [E121-L — PDF p. 121](#e121-l), [E121-PH — PDF p. 121](#e121-ph), [E121-W — PDF p. 121](#e121-w)

**Exact input origins (Unicode code points, half-open)**

| Language | Origin | Interval | Exact input quote |
|---|---|---|---|
| en | gold-D-scope | [0, 22) | D: HiTrap Blue HP 1 mL |
| en | gold-D-request-0 | [29, 41) | washing flow |
| en | gold-D-request-1 | [46, 68) | maximum pressure for D |
| en | gold-E-scope | [85, 121) | E asks for the general IEX principle |
| en | gold-E-request-0 | [100, 121) | general IEX principle |
| fr | gold-D-scope | [0, 23) | D : HiTrap Blue HP 1 mL |
| fr | gold-D-request-0 | [34, 49) | débit de lavage |
| fr | gold-D-request-1 | [56, 80) | pression maximale pour D |
| fr | gold-E-scope | [98, 136) | E demande le principe général de l’IEX |
| fr | gold-E-request-0 | [111, 136) | principe général de l’IEX |

## FT12 — partial_support_and_policy

**Decision: pending.**

**EN input**

> D: HiTrap Blue HP 5 mL. Give equilibration flow and loading flow for D. E: HiTrap Blue HP 1 mL. Give the binding-buffer formulations for E.

**FR input**

> D : HiTrap Blue HP 5 mL. Donne le débit d’équilibrage et le débit de chargement pour D. E : HiTrap Blue HP 1 mL. Donne les formulations du tampon de fixation pour E.

**Proposed structured meaning**

- D: product {"state": "provided", "value": "HiTrap Blue HP 5 mL"}; separate column {"state": "not_supplied", "value": null}.
  - operating_phase/equilibration: flow_rate; buffer use not_applicable.
  - operating_phase/sample_application: flow_rate; buffer use not_applicable.
- E: product {"state": "provided", "value": "HiTrap Blue HP 1 mL"}; separate column {"state": "not_supplied", "value": null}.
  - preparation/buffer_preparation: buffer_formulation; buffer use provided=binding.

**Expected answer / diagnostic (EN)**

Do not assign equilibration flow: E121-EQ remains quarantined. D loading flow is 0.5–5 mL/min. E binding-buffer alternatives are 20 mM sodium phosphate, pH 7.0, OR 50 mM potassium hydrogen phosphate (KH 2PO4 as written), pH 7.0.

**Réponse / diagnostic attendu (FR)**

Ne pas attribuer de débit d’équilibrage : E121-EQ reste en quarantaine. Le débit de chargement de D est de 0,5 à 5 mL/min. Tampons de fixation alternatifs pour E : phosphate de sodium 20 mM, pH 7,0, OU hydrogénophosphate de potassium 50 mM (KH 2PO4 tel qu’écrit), pH 7,0.

**Documentary units**

| Owner/item | Information | Expected state | Required admissible bundle |
|---|---|---|---|
| D/D-equilibration | flow_rate | quarantined | No assignment |
| D/D-sample_application | flow_rate | supported | E120-H + E120-P + E120-W + E121-F + E121-L + E121-PH |
| E/E-buffer_preparation | buffer_formulation | supported | E120-H + E120-P + E120-W + E121-B + E121-BH |

**Retained reservations / points to validate**

- Second explicit mixed documentary-support request: withholding equilibration must not suppress loading or the independent E formulation.
- No transfer from loading or washing to equilibration, and no source-approval override.
- Preserve the manual nomenclature and alternatives without correcting formulas, pairing buffers or choosing a recipe.

**Original manual passages to inspect**

[E120-H — PDF p. 120](#e120-h), [E120-P — PDF p. 120](#e120-p), [E120-W — PDF p. 120](#e120-w), [E121-B — PDF p. 121](#e121-b), [E121-BH — PDF p. 121](#e121-bh), [E121-F — PDF p. 121](#e121-f), [E121-L — PDF p. 121](#e121-l), [E121-PH — PDF p. 121](#e121-ph)

**Exact input origins (Unicode code points, half-open)**

| Language | Origin | Interval | Exact input quote |
|---|---|---|---|
| en | gold-D-scope | [0, 22) | D: HiTrap Blue HP 5 mL |
| en | gold-E-scope | [72, 94) | E: HiTrap Blue HP 1 mL |
| en | gold-D-request-0 | [29, 47) | equilibration flow |
| en | gold-D-request-1 | [52, 70) | loading flow for D |
| en | gold-E-request-0 | [105, 138) | binding-buffer formulations for E |
| fr | gold-D-scope | [0, 23) | D : HiTrap Blue HP 5 mL |
| fr | gold-E-scope | [88, 111) | E : HiTrap Blue HP 1 mL |
| fr | gold-D-request-0 | [34, 53) | débit d’équilibrage |
| fr | gold-D-request-1 | [60, 86) | débit de chargement pour D |
| fr | gold-E-request-0 | [123, 164) | formulations du tampon de fixation pour E |

## Shared original manual quotations

Quotes are verbatim from the existing reviewed source registry. Their historical
registry status fields are not newly rewritten; eligibility derives from the
pinned review manifest/policy. No excluded passage is promoted by this packet.

### E118-USE

PDF page 118, printed page 118. Scope: Contaminants after initial antibody purification; laboratory-scale guidance.

> For many applications at laboratory scale, contaminant molecules are not always a significant problem. Affinity 
> chromatography (AC) will provide sufficient purity and, as long as the presence of any minor contaminants does not 
> interfere with the intended application, the purified sample can be used directly.

### E118-C

PDF page 118, printed page 118. Scope: Contaminants after initial antibody purification; laboratory-scale guidance.

> Common contaminants after initial purification are albumin, transferrin, antibody aggregates, leached protein A, DNA, 
> and host or bovine immunoglobulins that originate from ascites or cell culture serum. The problem of contaminants of 
> animal origin in, for example, bovine cell culture systems for monoclonal antibody (MAb) production, has been largely 
> circumvented by use of serum-free systems. The three main contaminants albumin, transferrin, and host or bovine 
> immunoglobulins pose three different purification problems: albumin because of its abundance; transferrin because of its 
> similarity to the charge characteristics of many antibodies; and host or bovine immunoglobulins because of the similarity 
> to that of the target immunoglobulin.

### E118-M

PDF page 118, printed page 118. Scope: Contaminants after initial antibody purification; laboratory-scale guidance.

>  Select chromatography techniques that utilize differences in the characteristics of the contaminant and target 
> molecule: ion exchange chromatography (IEX) for separation by differences in charge; hydrophobic interaction 
> chromatography (HIC) for separation by differences in hydrophobicity; and size exclusion chromatography (SEC) for 
> separation by size. See Appendix 9 for an overview of the principles of the chromatography techniques used  
> at laboratory scale.

### E119-BH

PDF page 119, printed page 119. Scope: Host or bovine immunoglobulin co-purification.

> Bovine immunoglobulins

### E119-B

PDF page 119, printed page 119. Scope: Host or bovine immunoglobulin co-purification.

> Co-purification of host or bovine immunoglobulins is a problem associated with any affinity purification of antibodies 
> from a native source or a source to which supplements such as calf serum or bovine serum albumin are added. This 
> contamination problem has been largely circumvented in the large-scale manufacture of MAbs for therapeutic use 
> through the widespread use of serum-free cell culture systems.

### E119-BI

PDF page 119, printed page 119. Scope: Host or bovine immunoglobulin co-purification.

> Difficulties have also been encountered when murine monoclonal antibodies are the target molecule. The similarities 
> between the physical characteristics of the target antibody and the contaminants require careful selection and 
> optimization to find the most suitable chromatography technique for purification. Both HIC and IEX can be used.

### E119-S

PDF page 119, printed page 119. Scope: Host or bovine immunoglobulin co-purification.

>  The hydrophobicity of proteins is difficult to predict. Screen several chromatography media with different 
> hydrophobicities (e.g., using HiTrap HIC Selection Kit) to find the medium that gives optimal results.

### E119-X

PDF page 119, printed page 119. Scope: Host or bovine immunoglobulin co-purification.

> HiTrap HIC Selection Kit includes seven HIC media with different hydrophobic properties for small-scale screening and 
> selection of optimal binding and elution conditions. Figure 4.1 shows an example of chromatography media screening 
> of a mouse monoclonal antibody on different HIC media prepacked in HiTrap 1 mL columns. In this case, the optimal 
> medium for purification was HiTrap Phenyl HP.

### E119-AH

PDF page 119, printed page 119. Scope: Albumin and transferrin after antibody purification.

> Albumin and transferrin

### E119-A

PDF page 119, printed page 119. Scope: Albumin and transferrin after antibody purification.

> Ion exchange and hydrophobic interaction chromatography are two methods used for removing albumin and transferrin, 
> separating the molecules on the basis of differences in their isoelectric points or hydrophobicities (see Appendix 9 for the 
> principles of these techniques).

### E119-I

PDF page 119, printed page 119. Scope: Albumin and transferrin after antibody purification.

>  After an IEX purification, albumin and transferrin can be present if their charge properties are similar to those of 
> the target antibody. In some cases, it might be possible to optimize pH and elution conditions in the IEX step to 
> improve the separation between the antibody and the contaminants (Appendix 9).

### E119-H

PDF page 119, printed page 119. Scope: Albumin and transferrin after antibody purification.

>  Since most monoclonal antibodies are more hydrophobic than albumin and transferrin, HIC can be used to bind the 
> antibody and allow these contaminants to wash through the column.

### E119-BL

PDF page 119, printed page 119. Scope: Albumin and transferrin after antibody purification.

> However, AC using Blue Sepharose 6 Fast Flow is a useful alternative to IEX and HIC for removing albumin.

### E120-H

PDF page 120, printed page 120. Scope: Albumin removal using Blue Sepharose / HiTrap Blue HP 1 mL and 5 mL.

> Removal of albumin using Blue Sepharose chromatography media

### E120-A

PDF page 120, printed page 120. Scope: Albumin removal using Blue Sepharose / HiTrap Blue HP 1 mL and 5 mL.

> Blue Sepharose 6 Fast Flow or prepacked HiTrap Blue HP 1 mL and 5 mL columns (Fig 4.2) can be used to remove albumin 
> either before or after other purification steps (see Table 4.1). The albumin binds in a nonspecific manner by electrostatic 
> and/or hydrophobic interactions with the aromatic anionic ligand, Cibacron Blue F3G-A, coupled to Sepharose.

### E120-U

PDF page 120, printed page 120. Scope: Albumin removal using Blue Sepharose / HiTrap Blue HP 1 mL and 5 mL.

>  Use HiTrap Blue HP 1 mL or 5 mL columns to remove host albumin from mammalian expression systems or when 
> the sample is known to contain high levels of albumin that might mask the UV absorption of other protein peaks.

### E120-W

PDF page 120, printed page 120. Scope: Albumin removal using Blue Sepharose / HiTrap Blue HP 1 mL and 5 mL.

>  Do not use Blue Sepharose chromatography media if the immunoglobulin or other target molecule has a 
> hydrophobicity similar to that of albumin.

### E120-P

PDF page 120, printed page 120. Scope: Albumin removal using Blue Sepharose / HiTrap Blue HP 1 mL and 5 mL.

> The protocol for removal of albumin using HiTrap Blue HP 1 mL and 5 mL columns is described below.

### E121-BH

PDF page 121, printed page 121. Scope: Albumin removal using Blue Sepharose / HiTrap Blue HP 1 mL and 5 mL.

> Buffer preparation

### E121-B

PDF page 121, printed page 121. Scope: Albumin removal using Blue Sepharose / HiTrap Blue HP 1 mL and 5 mL.

> Binding buffer: 20 mM sodium phosphate, pH 7.0, or 50 mM potassium hydrogen phosphate (KH 2PO4), pH 7.0
> Elution buffer: 0.02 M sodium phosphate, 2 M sodium chloride, pH 7.0, or 0.05 M potassium hydrogen phosphate, 
> 1.5 M potassium chloride, pH 7.0

### E121-PH

PDF page 121, printed page 121. Scope: Albumin removal using Blue Sepharose / HiTrap Blue HP 1 mL and 5 mL.

> Albumin removal

### E121-L

PDF page 121, printed page 121. Scope: Albumin removal using Blue Sepharose / HiTrap Blue HP 1 mL and 5 mL.

>  5. Apply the sample using a syringe fitted to the Luer connector or by pumping it onto the column. For optimal 
> results, use a flow rate of 0.2 to 1 mL/min (1 mL column) and 0.5 to 5 mL/min (5 mL column) during sample 
> application*.

### E121-W

PDF page 121, printed page 121. Scope: Albumin removal using Blue Sepharose / HiTrap Blue HP 1 mL and 5 mL.

>  6. Wash with binding buffer (generally at least 5 to 10 column volumes) until the absorbance reaches a steady 
> baseline or no material remains in the effluent. Maintain a flow rate of 1 to 2 mL/min (1 mL column) and  
> 5 to 10 mL/min (5 mL column) for washing.

### E121-E

PDF page 121, printed page 121. Scope: Albumin removal using Blue Sepharose / HiTrap Blue HP 1 mL and 5 mL.

>  7. Elute with elution buffer using a one-step or linear gradient. For step elution, 5 column volumes is usually 
> sufficient. For linear gradient elution, 10 to 20  column volumes are usually sufficient. Maintain a flow rate of  
> 1 to 2 mL/min (1 mL column) and 5 to 10 mL/min (5 mL column) for elution.

### E121-F

PDF page 121, printed page 121. Scope: Albumin removal using Blue Sepharose / HiTrap Blue HP 1 mL and 5 mL.

> *       1 mL/min corresponds to approximately 30 drops/min when using a syringe with a 1 mL HiTrap column; 5 mL/min corresponds to approximately 
> 120 drops/min when using a 5 mL HiTrap column

