# FV01-FV12: paired human-review cards

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

## FV01 — ownership_and_order

**Decision: pending.**

**EN input**

> P: HiTrap Blue HP 1 mL. Q: HiTrap Blue HP 5 mL. Independently, R asks for the general HIC principle. For Q, I need the loading flow; for P, give washing flow.

**FR input**

> P : HiTrap Blue HP 1 mL. Q : HiTrap Blue HP 5 mL. Indépendamment, R demande le principe général de la HIC. Pour Q, il me faut le débit de chargement ; pour P, donne le débit de lavage.

**Proposed structured meaning**

- P: product {"state": "provided", "value": "HiTrap Blue HP 1 mL"}; separate column {"state": "not_supplied", "value": null}.
  - operating_phase/washing: flow_rate; buffer use not_applicable.
- Q: product {"state": "provided", "value": "HiTrap Blue HP 5 mL"}; separate column {"state": "not_supplied", "value": null}.
  - operating_phase/sample_application: flow_rate; buffer use not_applicable.
- R: product {"state": "not_applicable", "value": null, "reason": "Not required for the explicitly requested documentary information."}; separate column {"state": "not_applicable", "value": null, "reason": "Not required for the explicitly requested documentary information."}.
  - general_topic/method_selection: principle; buffer use not_applicable.

**Expected answer / diagnostic (EN)**

P washing: 1–2 mL/min. Q loading: 0.5–5 mL/min. R: HIC separates by differences in hydrophobicity. Preserve declaration order P/Q/R although R is requested first.

**Expected answer / diagnostic (FR)**

Lavage de P : 1 à 2 mL/min. Chargement de Q : 0,5 à 5 mL/min. R : la HIC sépare selon les différences d’hydrophobicité. Conserver l’ordre de déclaration P/Q/R même si R est demandé en premier.

**Documentary units**

| Owner/item | Information | Expected state | Required admissible bundle |
|---|---|---|---|
| P/P-washing | flow_rate | supported | E120-H + E120-P + E120-W + E121-PH + E121-W |
| Q/Q-sample_application | flow_rate | supported | E120-H + E120-P + E120-W + E121-F + E121-L + E121-PH |
| R/R-method_selection | principle | supported | E118-M |

**Retained reservations / points to validate**

- Three independent tasks and three requested units; no flow range or scientific suitability transfers between them.
- The syringe correspondence is inherited approximate context, not a requested conversion or an extra unit.

**Original manual passages to inspect**

[E118-M — PDF p. 118](#e118-m), [E120-H — PDF p. 120](#e120-h), [E120-P — PDF p. 120](#e120-p), [E120-W — PDF p. 120](#e120-w), [E121-F — PDF p. 121](#e121-f), [E121-L — PDF p. 121](#e121-l), [E121-PH — PDF p. 121](#e121-ph), [E121-W — PDF p. 121](#e121-w)

**Exact input origins (Unicode code points, half-open)**

| Language | Origin | Interval | Exact input quote |
|---|---|---|---|
| en | gold-P-scope | [0, 22) | P: HiTrap Blue HP 1 mL |
| en | gold-Q-scope | [24, 46) | Q: HiTrap Blue HP 5 mL |
| en | gold-R-scope | [63, 99) | R asks for the general HIC principle |
| en | gold-P-request-0 | [133, 157) | for P, give washing flow |
| en | gold-Q-request-0 | [101, 131) | For Q, I need the loading flow |
| en | gold-R-request-0 | [78, 99) | general HIC principle |
| fr | gold-P-scope | [0, 23) | P : HiTrap Blue HP 1 mL |
| fr | gold-Q-scope | [25, 48) | Q : HiTrap Blue HP 5 mL |
| fr | gold-R-scope | [66, 105) | R demande le principe général de la HIC |
| fr | gold-P-request-0 | [151, 183) | pour P, donne le débit de lavage |
| fr | gold-Q-request-0 | [107, 148) | Pour Q, il me faut le débit de chargement |
| fr | gold-R-request-0 | [79, 105) | principe général de la HIC |

## FV02 — ownership_and_order

**Decision: pending.**

**EN input**

> Q: HiTrap Blue HP 1 mL. P: HiTrap Blue HP 5 mL. What washing flow does the manual give for P? For Q, give loading flow and washing flow.

**FR input**

> Q : HiTrap Blue HP 1 mL. P : HiTrap Blue HP 5 mL. Quel débit de lavage le manuel indique-t-il pour P ? Pour Q, donne le débit de chargement et le débit de lavage.

**Proposed structured meaning**

- Q: product {"state": "provided", "value": "HiTrap Blue HP 1 mL"}; separate column {"state": "not_supplied", "value": null}.
  - operating_phase/sample_application: flow_rate; buffer use not_applicable.
  - operating_phase/washing: flow_rate; buffer use not_applicable.
- P: product {"state": "provided", "value": "HiTrap Blue HP 5 mL"}; separate column {"state": "not_supplied", "value": null}.
  - operating_phase/washing: flow_rate; buffer use not_applicable.

**Expected answer / diagnostic (EN)**

Q loading: 0.2–1 mL/min; Q washing: 1–2 mL/min. P washing: 5–10 mL/min. Retain Q before P in the structured task inventory, despite the request for P preceding the requests for Q.

**Expected answer / diagnostic (FR)**

Chargement de Q : 0,2 à 1 mL/min ; lavage de Q : 1 à 2 mL/min. Lavage de P : 5 à 10 mL/min. Garder Q avant P dans les tâches structurées, malgré la demande pour P placée avant celles pour Q.

**Documentary units**

| Owner/item | Information | Expected state | Required admissible bundle |
|---|---|---|---|
| Q/Q-sample_application | flow_rate | supported | E120-H + E120-P + E120-W + E121-F + E121-L + E121-PH |
| Q/Q-washing | flow_rate | supported | E120-H + E120-P + E120-W + E121-PH + E121-W |
| P/P-washing | flow_rate | supported | E120-H + E120-P + E120-W + E121-PH + E121-W |

**Retained reservations / points to validate**

- Two distinct stages for Q, not a merged flow selector; P and Q remain separate.
- No duration or universal drops/min conversion is derived. Natural question wording is not repaired after results.

**Original manual passages to inspect**

[E120-H — PDF p. 120](#e120-h), [E120-P — PDF p. 120](#e120-p), [E120-W — PDF p. 120](#e120-w), [E121-F — PDF p. 121](#e121-f), [E121-L — PDF p. 121](#e121-l), [E121-PH — PDF p. 121](#e121-ph), [E121-W — PDF p. 121](#e121-w)

**Exact input origins (Unicode code points, half-open)**

| Language | Origin | Interval | Exact input quote |
|---|---|---|---|
| en | gold-Q-scope | [0, 22) | Q: HiTrap Blue HP 1 mL |
| en | gold-P-scope | [24, 46) | P: HiTrap Blue HP 5 mL |
| en | gold-Q-request-0 | [94, 118) | For Q, give loading flow |
| en | gold-Q-request-1 | [123, 136) | washing flow. |
| en | gold-P-request-0 | [48, 92) | What washing flow does the manual give for P |
| fr | gold-Q-scope | [0, 23) | Q : HiTrap Blue HP 1 mL |
| fr | gold-P-scope | [25, 48) | P : HiTrap Blue HP 5 mL |
| fr | gold-Q-request-0 | [103, 139) | Pour Q, donne le débit de chargement |
| fr | gold-Q-request-1 | [146, 162) | débit de lavage. |
| fr | gold-P-request-0 | [50, 100) | Quel débit de lavage le manuel indique-t-il pour P |

## FV03 — buffer_and_operating_scope

**Decision: pending.**

**EN input**

> P: HiTrap Blue HP 1 mL. Q: HiTrap Blue HP 5 mL. List elution-buffer formulations for P and give elution flow for Q. Exclude operating elution for P.

**FR input**

> P : HiTrap Blue HP 1 mL. Q : HiTrap Blue HP 5 mL. Liste les formulations du tampon d’élution pour P et donne le débit d’élution pour Q. Exclus l’élution opératoire pour P.

**Proposed structured meaning**

- P: product {"state": "provided", "value": "HiTrap Blue HP 1 mL"}; separate column {"state": "not_supplied", "value": null}.
  - preparation/buffer_preparation: buffer_formulation; buffer use provided=elution.
  - Active exclusions: [{"exclusion_id": "P-ban-1", "scope": {"task_id": "P"}, "selector": {"kind": "operating_phase", "code": "elution", "information": "all"}}].
- Q: product {"state": "provided", "value": "HiTrap Blue HP 5 mL"}; separate column {"state": "not_supplied", "value": null}.
  - operating_phase/elution: flow_rate; buffer use not_applicable.

**Expected answer / diagnostic (EN)**

P elution-buffer alternatives: 0.02 M sodium phosphate with 2 M sodium chloride, pH 7.0, OR 0.05 M potassium hydrogen phosphate with 1.5 M potassium chloride, pH 7.0. Q elution flow: 5–10 mL/min. The operating-elution exclusion is limited to P.

**Expected answer / diagnostic (FR)**

Tampons d’élution alternatifs de P : phosphate de sodium 0,02 M avec chlorure de sodium 2 M, pH 7,0, OU hydrogénophosphate de potassium 0,05 M avec chlorure de potassium 1,5 M, pH 7,0. Débit d’élution de Q : 5 à 10 mL/min. L’exclusion de l’élution opératoire est limitée à P.

**Documentary units**

| Owner/item | Information | Expected state | Required admissible bundle |
|---|---|---|---|
| P/P-buffer_preparation | buffer_formulation | supported | E120-H + E120-P + E120-W + E121-B + E121-BH |
| Q/Q-elution | flow_rate | supported | E120-H + E120-P + E120-W + E121-E + E121-PH |

**Retained reservations / points to validate**

- Formulating an elution buffer is not requesting operating elution. The exclusion for P cannot suppress Q.
- Do not select an elution mode or duration, pair buffers, or silently correct the manual nomenclature.

**Original manual passages to inspect**

[E120-H — PDF p. 120](#e120-h), [E120-P — PDF p. 120](#e120-p), [E120-W — PDF p. 120](#e120-w), [E121-B — PDF p. 121](#e121-b), [E121-BH — PDF p. 121](#e121-bh), [E121-E — PDF p. 121](#e121-e), [E121-PH — PDF p. 121](#e121-ph)

**Exact input origins (Unicode code points, half-open)**

| Language | Origin | Interval | Exact input quote |
|---|---|---|---|
| en | gold-P-scope | [0, 22) | P: HiTrap Blue HP 1 mL |
| en | gold-Q-scope | [24, 46) | Q: HiTrap Blue HP 5 mL |
| en | gold-P-request-0 | [53, 86) | elution-buffer formulations for P |
| en | gold-Q-request-0 | [91, 114) | give elution flow for Q |
| en | gold-P-ban-0 | [116, 147) | Exclude operating elution for P |
| fr | gold-P-scope | [0, 23) | P : HiTrap Blue HP 1 mL |
| fr | gold-Q-scope | [25, 48) | Q : HiTrap Blue HP 5 mL |
| fr | gold-P-request-0 | [60, 99) | formulations du tampon d’élution pour P |
| fr | gold-Q-request-0 | [103, 134) | donne le débit d’élution pour Q |
| fr | gold-P-ban-0 | [136, 170) | Exclus l’élution opératoire pour P |

## FV04 — buffer_and_operating_scope

**Decision: pending.**

**EN input**

> P: HiTrap Blue HP 5 mL. List binding-buffer formulations for P. Separately, list elution-buffer formulations for P. Do not exclude washing flow for P; give washing flow for P.

**FR input**

> P : HiTrap Blue HP 5 mL. Liste les formulations du tampon de fixation pour P. Séparément, liste les formulations du tampon d’élution pour P. N’exclus pas le débit de lavage pour P ; donne le débit de lavage pour P.

**Proposed structured meaning**

- P: product {"state": "provided", "value": "HiTrap Blue HP 5 mL"}; separate column {"state": "not_supplied", "value": null}.
  - preparation/buffer_preparation: buffer_formulation; buffer use provided=binding.
  - preparation/buffer_preparation: buffer_formulation; buffer use provided=elution.
  - operating_phase/washing: flow_rate; buffer use not_applicable.

**Expected answer / diagnostic (EN)**

Binding alternatives: 20 mM sodium phosphate, pH 7.0, OR 50 mM potassium hydrogen phosphate (KH 2PO4 as written), pH 7.0. Keep separate elution alternatives: 0.02 M sodium phosphate with 2 M sodium chloride, pH 7.0, OR 0.05 M potassium hydrogen phosphate with 1.5 M potassium chloride, pH 7.0. Washing flow: 5–10 mL/min.

**Expected answer / diagnostic (FR)**

Alternatives de fixation : phosphate de sodium 20 mM, pH 7,0, OU hydrogénophosphate de potassium 50 mM (KH 2PO4 tel qu’écrit), pH 7,0. Alternatives d’élution séparées : phosphate de sodium 0,02 M avec chlorure de sodium 2 M, pH 7,0, OU hydrogénophosphate de potassium 0,05 M avec chlorure de potassium 1,5 M, pH 7,0. Débit de lavage : 5 à 10 mL/min.

**Documentary units**

| Owner/item | Information | Expected state | Required admissible bundle |
|---|---|---|---|
| P/P-binding-formulation | buffer_formulation | supported | E120-H + E120-P + E120-W + E121-B + E121-BH |
| P/P-elution-formulation | buffer_formulation | supported | E120-H + E120-P + E120-W + E121-B + E121-BH |
| P/P-washing | flow_rate | supported | E120-H + E120-P + E120-W + E121-PH + E121-W |

**Retained reservations / points to validate**

- Binding and elution require two separate preparation items despite sharing the same source and stage code; their identities must not collapse.
- Retain all four alternative formulations without pairing, correction or recipe selection. The negated exclusion is inactive and does not add a positive request.

**Original manual passages to inspect**

[E120-H — PDF p. 120](#e120-h), [E120-P — PDF p. 120](#e120-p), [E120-W — PDF p. 120](#e120-w), [E121-B — PDF p. 121](#e121-b), [E121-BH — PDF p. 121](#e121-bh), [E121-PH — PDF p. 121](#e121-ph), [E121-W — PDF p. 121](#e121-w)

**Exact input origins (Unicode code points, half-open)**

| Language | Origin | Interval | Exact input quote |
|---|---|---|---|
| en | gold-P-scope | [0, 22) | P: HiTrap Blue HP 5 mL |
| en | gold-P-request-0 | [24, 62) | List binding-buffer formulations for P |
| en | gold-P-request-1 | [76, 114) | list elution-buffer formulations for P |
| en | gold-P-request-2 | [151, 174) | give washing flow for P |
| en | gold-negated-ban | [116, 149) | Do not exclude washing flow for P |
| fr | gold-P-scope | [0, 23) | P : HiTrap Blue HP 5 mL |
| fr | gold-P-request-0 | [25, 76) | Liste les formulations du tampon de fixation pour P |
| fr | gold-P-request-1 | [90, 139) | liste les formulations du tampon d’élution pour P |
| fr | gold-P-request-2 | [182, 213) | donne le débit de lavage pour P |
| fr | gold-negated-ban | [141, 179) | N’exclus pas le débit de lavage pour P |

## FV05 — pressure_routing

**Decision: pending.**

**EN input**

> P: HiTrap Blue HP 5 mL. Q: HiTrap Blue HP 1 mL. For P, give maximum pressure and loading flow. For Q, give washing stopping criteria.

**FR input**

> P : HiTrap Blue HP 5 mL. Q : HiTrap Blue HP 1 mL. Pour P, donne la pression maximale et le débit de chargement. Pour Q, donne les critères de fin du lavage.

**Proposed structured meaning**

- P: product {"state": "provided", "value": "HiTrap Blue HP 5 mL"}; separate column {"state": "not_supplied", "value": null}.
  - general_topic/operating_limits: maximum_pressure; buffer use not_applicable.
  - operating_phase/sample_application: flow_rate; buffer use not_applicable.
- Q: product {"state": "provided", "value": "HiTrap Blue HP 1 mL"}; separate column {"state": "not_supplied", "value": null}.
  - operating_phase/washing: stopping_criteria; buffer use not_applicable.

**Expected answer / diagnostic (EN)**

No maximum pressure is documented in the exact 25 eligible excerpts. P loading flow is 0.5–5 mL/min. Q washing ends at a steady absorbance baseline OR no material remaining in the effluent.

**Expected answer / diagnostic (FR)**

Aucune pression maximale n’est documentée dans les 25 extraits admissibles précis. Le débit de chargement de P est de 0,5 à 5 mL/min. Le lavage de Q finit à une ligne de base d’absorbance stable OU à l’absence de matière dans l’effluent.

**Documentary units**

| Owner/item | Information | Expected state | Required admissible bundle |
|---|---|---|---|
| P/P-operating_limits | maximum_pressure | missing_source | No assignment |
| P/P-sample_application | flow_rate | supported | E120-H + E120-P + E120-W + E121-F + E121-L + E121-PH |
| Q/Q-washing | stopping_criteria | supported | E120-H + E120-P + E120-W + E121-PH + E121-W |

**Retained reservations / points to validate**

- General pressure precedes the loading selector and must not acquire its phase. No pressure is invented or inferred from flow.
- Keep pressure absence bounded to the eligible excerpt set; both independently supported units remain counted and served.

**Original manual passages to inspect**

[E118-C — PDF p. 118](#e118-c), [E118-M — PDF p. 118](#e118-m), [E118-USE — PDF p. 118](#e118-use), [E119-A — PDF p. 119](#e119-a), [E119-AH — PDF p. 119](#e119-ah), [E119-B — PDF p. 119](#e119-b), [E119-BH — PDF p. 119](#e119-bh), [E119-BI — PDF p. 119](#e119-bi), [E119-BL — PDF p. 119](#e119-bl), [E119-H — PDF p. 119](#e119-h), [E119-I — PDF p. 119](#e119-i), [E119-S — PDF p. 119](#e119-s), [E119-X — PDF p. 119](#e119-x), [E120-A — PDF p. 120](#e120-a), [E120-H — PDF p. 120](#e120-h), [E120-P — PDF p. 120](#e120-p), [E120-U — PDF p. 120](#e120-u), [E120-W — PDF p. 120](#e120-w), [E121-B — PDF p. 121](#e121-b), [E121-BH — PDF p. 121](#e121-bh), [E121-E — PDF p. 121](#e121-e), [E121-F — PDF p. 121](#e121-f), [E121-L — PDF p. 121](#e121-l), [E121-PH — PDF p. 121](#e121-ph), [E121-W — PDF p. 121](#e121-w)

**Exact input origins (Unicode code points, half-open)**

| Language | Origin | Interval | Exact input quote |
|---|---|---|---|
| en | gold-P-scope | [0, 22) | P: HiTrap Blue HP 5 mL |
| en | gold-Q-scope | [24, 46) | Q: HiTrap Blue HP 1 mL |
| en | gold-P-request-0 | [48, 76) | For P, give maximum pressure |
| en | gold-P-request-1 | [81, 93) | loading flow |
| en | gold-Q-request-0 | [95, 132) | For Q, give washing stopping criteria |
| fr | gold-P-scope | [0, 23) | P : HiTrap Blue HP 5 mL |
| fr | gold-Q-scope | [25, 48) | Q : HiTrap Blue HP 1 mL |
| fr | gold-P-request-0 | [50, 84) | Pour P, donne la pression maximale |
| fr | gold-P-request-1 | [91, 110) | débit de chargement |
| fr | gold-Q-request-0 | [112, 155) | Pour Q, donne les critères de fin du lavage |

## FV06 — pressure_routing

**Decision: pending.**

**EN input**

> P: HiTrap Blue HP 1 mL. Q: HiTrap Blue HP 5 mL. Give maximum pressure for washing for P. Independently, give maximum pressure for Q and loading flow for Q.

**FR input**

> P : HiTrap Blue HP 1 mL. Q : HiTrap Blue HP 5 mL. Donne pour P la pression maximale du lavage. Indépendamment, donne la pression maximale pour Q et le débit de chargement pour Q.

**Proposed structured meaning**

- P: product {"state": "provided", "value": "HiTrap Blue HP 1 mL"}; separate column {"state": "not_supplied", "value": null}.
  - operating_phase/washing: maximum_pressure; buffer use not_applicable.
- Q: product {"state": "provided", "value": "HiTrap Blue HP 5 mL"}; separate column {"state": "not_supplied", "value": null}.
  - general_topic/operating_limits: maximum_pressure; buffer use not_applicable.
  - operating_phase/sample_application: flow_rate; buffer use not_applicable.

**Expected answer / diagnostic (EN)**

P explicitly requests washing-specific maximum pressure: no reviewed adapter role supports that stage/selector combination, so retain it as unsupported_selector rather than generalize it. Q general maximum pressure is missing from the exact 25 eligible excerpts; Q loading flow is 0.5–5 mL/min.

**Expected answer / diagnostic (FR)**

P demande explicitement la pression maximale du lavage : aucun rôle revu de l’adaptateur ne couvre cette combinaison étape/information ; la conserver en unsupported_selector sans la généraliser. La pression maximale générale de Q manque dans les 25 extraits admissibles précis ; son débit de chargement est de 0,5 à 5 mL/min.

**Documentary units**

| Owner/item | Information | Expected state | Required admissible bundle |
|---|---|---|---|
| P/P-washing | maximum_pressure | unsupported_selector | No assignment |
| Q/Q-operating_limits | maximum_pressure | missing_source | No assignment |
| Q/Q-sample_application | flow_rate | supported | E120-H + E120-P + E120-W + E121-F + E121-L + E121-PH |

**Retained reservations / points to validate**

- Distinguish unsupported representation from bounded missing documentary evidence; neither authorizes inventing pressure.
- The phase-specific P request must not be silently changed into a general operating-limit question or suppress Q loading.

**Original manual passages to inspect**

[E118-C — PDF p. 118](#e118-c), [E118-M — PDF p. 118](#e118-m), [E118-USE — PDF p. 118](#e118-use), [E119-A — PDF p. 119](#e119-a), [E119-AH — PDF p. 119](#e119-ah), [E119-B — PDF p. 119](#e119-b), [E119-BH — PDF p. 119](#e119-bh), [E119-BI — PDF p. 119](#e119-bi), [E119-BL — PDF p. 119](#e119-bl), [E119-H — PDF p. 119](#e119-h), [E119-I — PDF p. 119](#e119-i), [E119-S — PDF p. 119](#e119-s), [E119-X — PDF p. 119](#e119-x), [E120-A — PDF p. 120](#e120-a), [E120-H — PDF p. 120](#e120-h), [E120-P — PDF p. 120](#e120-p), [E120-U — PDF p. 120](#e120-u), [E120-W — PDF p. 120](#e120-w), [E121-B — PDF p. 121](#e121-b), [E121-BH — PDF p. 121](#e121-bh), [E121-E — PDF p. 121](#e121-e), [E121-F — PDF p. 121](#e121-f), [E121-L — PDF p. 121](#e121-l), [E121-PH — PDF p. 121](#e121-ph), [E121-W — PDF p. 121](#e121-w)

**Exact input origins (Unicode code points, half-open)**

| Language | Origin | Interval | Exact input quote |
|---|---|---|---|
| en | gold-P-scope | [0, 22) | P: HiTrap Blue HP 1 mL |
| en | gold-Q-scope | [24, 46) | Q: HiTrap Blue HP 5 mL |
| en | gold-P-request-0 | [53, 87) | maximum pressure for washing for P |
| en | gold-Q-request-0 | [104, 131) | give maximum pressure for Q |
| en | gold-Q-request-1 | [136, 154) | loading flow for Q |
| fr | gold-P-scope | [0, 23) | P : HiTrap Blue HP 1 mL |
| fr | gold-Q-scope | [25, 48) | Q : HiTrap Blue HP 5 mL |
| fr | gold-P-request-0 | [56, 93) | pour P la pression maximale du lavage |
| fr | gold-Q-request-0 | [111, 144) | donne la pression maximale pour Q |
| fr | gold-Q-request-1 | [151, 177) | débit de chargement pour Q |

## FV07 — context_uncertainty

**Decision: pending.**

**EN input**

> P: HiTrap Blue HP. Column size is unknown. Give loading flow and washing stopping criteria for P. Independently, Q asks for the general HIC principle.

**FR input**

> P : HiTrap Blue HP. Le volume de colonne est inconnu. Donne le débit de chargement et les critères de fin du lavage pour P. Indépendamment, Q demande le principe général de la HIC.

**Proposed structured meaning**

- P: product {"state": "provided", "value": "HiTrap Blue HP"}; separate column {"state": "unknown", "value": null}.
  - operating_phase/sample_application: flow_rate; buffer use not_applicable.
  - operating_phase/washing: stopping_criteria; buffer use not_applicable.
- Q: product {"state": "not_applicable", "value": null, "reason": "Not required for the explicitly requested documentary information."}; separate column {"state": "not_applicable", "value": null, "reason": "Not required for the explicitly requested documentary information."}.
  - general_topic/method_selection: principle; buffer use not_applicable.

**Expected answer / diagnostic (EN)**

Ask for P column format before assigning loading flow. The missing size does not prevent the qualitative washing endpoints: steady absorbance baseline OR no material remaining in effluent. Independently, HIC separates by differences in hydrophobicity.

**Expected answer / diagnostic (FR)**

Demander le format de colonne de P avant d’attribuer son débit de chargement. L’absence de taille n’empêche pas les critères qualitatifs de fin du lavage : ligne de base stable OU absence de matière dans l’effluent. Indépendamment, la HIC sépare selon les différences d’hydrophobicité.

**Documentary units**

| Owner/item | Information | Expected state | Required admissible bundle |
|---|---|---|---|
| P/P-sample_application | flow_rate | needs_clarification | No assignment |
| P/P-washing | stopping_criteria | supported | E120-H + E120-P + E120-W + E121-PH + E121-W |
| Q/Q-method_selection | principle | supported | E118-M |

**Retained reservations / points to validate**

- Real context ambiguity: the size is explicitly unknown; do not select 1 mL or 5 mL by elimination.
- Only the size-dependent flow needs clarification; qualitative endpoints and the independent principle remain served. No scientific suitability is inferred.

**Original manual passages to inspect**

[E118-M — PDF p. 118](#e118-m), [E120-H — PDF p. 120](#e120-h), [E120-P — PDF p. 120](#e120-p), [E120-W — PDF p. 120](#e120-w), [E121-L — PDF p. 121](#e121-l), [E121-PH — PDF p. 121](#e121-ph), [E121-W — PDF p. 121](#e121-w)

**Exact input origins (Unicode code points, half-open)**

| Language | Origin | Interval | Exact input quote |
|---|---|---|---|
| en | gold-P-scope | [0, 17) | P: HiTrap Blue HP |
| en | gold-P-column | [19, 41) | Column size is unknown |
| en | gold-P-request-0 | [48, 60) | loading flow |
| en | gold-P-request-1 | [65, 96) | washing stopping criteria for P |
| en | gold-Q-scope | [113, 149) | Q asks for the general HIC principle |
| en | gold-Q-request-0 | [128, 149) | general HIC principle |
| fr | gold-P-scope | [0, 18) | P : HiTrap Blue HP |
| fr | gold-P-column | [20, 52) | Le volume de colonne est inconnu |
| fr | gold-P-request-0 | [63, 82) | débit de chargement |
| fr | gold-P-request-1 | [90, 122) | critères de fin du lavage pour P |
| fr | gold-Q-scope | [140, 179) | Q demande le principe général de la HIC |
| fr | gold-Q-request-0 | [153, 179) | principe général de la HIC |

## FV08 — context_uncertainty

**Decision: pending.**

**EN input**

> P is named HiTrap Blue HP 5 mL, but its column field says 1 mL. Give washing flow and washing column volumes for P. Q: HiTrap Blue HP 1 mL. Give loading flow for Q.

**FR input**

> P est nommé HiTrap Blue HP 5 mL, mais son volume de colonne est 1 mL. Donne le débit de lavage et le volume de lavage en volumes de colonne pour P. Q : HiTrap Blue HP 1 mL. Donne le débit de chargement pour Q.

**Proposed structured meaning**

- P: product {"state": "provided", "value": "HiTrap Blue HP 5 mL"}; separate column {"state": "provided", "value": {"bed_volume": {"value": "1", "unit": "mL"}}}.
  - operating_phase/washing: flow_rate, column_volumes; buffer use not_applicable.
- Q: product {"state": "provided", "value": "HiTrap Blue HP 1 mL"}; separate column {"state": "not_supplied", "value": null}.
  - operating_phase/sample_application: flow_rate; buffer use not_applicable.

**Expected answer / diagnostic (EN)**

Clarify the contradictory 5 mL product label and separate 1 mL column assertion for P. Under the frozen structured policy both P procedural units are held pending clarification, even though washing volumes alone normally do not require size. Q loading flow remains 0.2–1 mL/min.

**Expected answer / diagnostic (FR)**

Clarifier pour P le conflit entre l’étiquette produit 5 mL et le champ colonne séparé 1 mL. Selon la politique structurée figée, les deux unités procédurales de P attendent une clarification, même si les volumes de lavage seuls ne nécessitent normalement pas la taille. Le débit de chargement de Q reste de 0,2 à 1 mL/min.

**Documentary units**

| Owner/item | Information | Expected state | Required admissible bundle |
|---|---|---|---|
| P/P-washing | flow_rate | needs_clarification | No assignment |
| P/P-washing | column_volumes | needs_clarification | No assignment |
| Q/Q-sample_application | flow_rate | supported | E120-H + E120-P + E120-W + E121-F + E121-L + E121-PH |

**Retained reservations / points to validate**

- Real contradiction differs from an unknown optional column field. Do not select one assertion, split P into invented preparations, or create task S from son.
- This expected block reflects the current conservative policy, not a scientific claim that qualitative washing information depends on column size. Q remains independent.

**Original manual passages to inspect**

[E120-H — PDF p. 120](#e120-h), [E120-P — PDF p. 120](#e120-p), [E120-W — PDF p. 120](#e120-w), [E121-F — PDF p. 121](#e121-f), [E121-L — PDF p. 121](#e121-l), [E121-PH — PDF p. 121](#e121-ph), [E121-W — PDF p. 121](#e121-w)

**Exact input origins (Unicode code points, half-open)**

| Language | Origin | Interval | Exact input quote |
|---|---|---|---|
| en | gold-P-scope | [0, 30) | P is named HiTrap Blue HP 5 mL |
| en | gold-P-column | [40, 62) | column field says 1 mL |
| en | gold-P-request-0 | [64, 114) | Give washing flow and washing column volumes for P |
| en | gold-Q-scope | [116, 138) | Q: HiTrap Blue HP 1 mL |
| en | gold-Q-request-0 | [140, 163) | Give loading flow for Q |
| fr | gold-P-scope | [0, 31) | P est nommé HiTrap Blue HP 5 mL |
| fr | gold-P-column | [42, 68) | volume de colonne est 1 mL |
| fr | gold-P-request-0 | [70, 146) | Donne le débit de lavage et le volume de lavage en volumes de colonne pour P |
| fr | gold-Q-scope | [148, 171) | Q : HiTrap Blue HP 1 mL |
| fr | gold-Q-request-0 | [173, 208) | Donne le débit de chargement pour Q |

## FV09 — numeric_roles

**Decision: pending.**

**EN input**

> P: HiTrap Blue HP 1 mL. My observed flow is 0.0 mL/min. Available sample volume is 2.5 mL. Loaded volume is unknown. What loading flow does the manual give for P? Separately, give elution flow for P.

**FR input**

> P : HiTrap Blue HP 1 mL. Le débit observé est de 0,0 mL/min. L’échantillon contient 2,5 mL disponibles. Le volume chargé est inconnu. Quel débit de chargement le manuel indique-t-il pour P ? Séparément, donne le débit d’élution pour P.

**Proposed structured meaning**

- P: product {"state": "provided", "value": "HiTrap Blue HP 1 mL"}; separate column {"state": "not_supplied", "value": null}.
  - operating_phase/sample_application: flow_rate; buffer use not_applicable.
  - operating_phase/elution: flow_rate; buffer use not_applicable.
  - Facts: [{"key": "observed_flow", "input_role": "user_observation", "value": {"state": "provided", "value": {"value": "0.0", "unit": "mL/min"}}}, {"key": "sample_volume", "input_role": "user_observation", "value": {"state": "provided", "value": {"value": "2.5", "unit": "mL"}}}, {"key": "loaded_volume", "input_role": "user_observation", "value": {"state": "unknown", "value": null}}].

**Expected answer / diagnostic (EN)**

P loading flow: 0.2–1 mL/min; elution flow: 1–2 mL/min. The observed zero is supplied but its operating stage is unstated. Available 2.5 mL is not a bed volume or a confirmed loaded volume. No duration can be derived.

**Expected answer / diagnostic (FR)**

Débit de chargement de P : 0,2 à 1 mL/min ; débit d’élution : 1 à 2 mL/min. Le zéro observé est fourni, mais son étape opératoire n’est pas précisée. Les 2,5 mL disponibles ne sont ni un volume de lit ni un volume chargé confirmé. Aucune durée ne peut être déduite.

**Documentary units**

| Owner/item | Information | Expected state | Required admissible bundle |
|---|---|---|---|
| P/P-sample_application | flow_rate | supported | E120-H + E120-P + E120-W + E121-F + E121-L + E121-PH |
| P/P-elution | flow_rate | supported | E120-H + E120-P + E120-W + E121-E + E121-PH |

**Retained reservations / points to validate**

- Retain all three numerical/unknown fact roles and the original zero lexeme; do not turn zero into missing input or infer a pump fault.
- The two documentary ranges belong to different stages. Do not choose an elution mode or interpolate the approximate syringe note.

**Original manual passages to inspect**

[E120-H — PDF p. 120](#e120-h), [E120-P — PDF p. 120](#e120-p), [E120-W — PDF p. 120](#e120-w), [E121-E — PDF p. 121](#e121-e), [E121-F — PDF p. 121](#e121-f), [E121-L — PDF p. 121](#e121-l), [E121-PH — PDF p. 121](#e121-ph)

**Exact input origins (Unicode code points, half-open)**

| Language | Origin | Interval | Exact input quote |
|---|---|---|---|
| en | gold-P-scope | [0, 22) | P: HiTrap Blue HP 1 mL |
| en | gold-P-fact-0 | [24, 54) | My observed flow is 0.0 mL/min |
| en | gold-P-fact-1 | [56, 89) | Available sample volume is 2.5 mL |
| en | gold-P-fact-2 | [91, 115) | Loaded volume is unknown |
| en | gold-P-request-0 | [117, 161) | What loading flow does the manual give for P |
| en | gold-P-request-1 | [175, 198) | give elution flow for P |
| fr | gold-P-scope | [0, 23) | P : HiTrap Blue HP 1 mL |
| fr | gold-P-fact-0 | [25, 59) | Le débit observé est de 0,0 mL/min |
| fr | gold-P-fact-1 | [61, 102) | L’échantillon contient 2,5 mL disponibles |
| fr | gold-P-fact-2 | [104, 132) | Le volume chargé est inconnu |
| fr | gold-P-request-0 | [134, 188) | Quel débit de chargement le manuel indique-t-il pour P |
| fr | gold-P-request-1 | [203, 234) | donne le débit d’élution pour P |

## FV10 — numeric_roles

**Decision: pending.**

**EN input**

> P: HiTrap Blue HP. Column size is 5 mL. Give washing column volumes and washing flow for P. In documentary scenario Q, minor contaminants do not interfere with the intended application. Explain the general IEX principle for Q.

**FR input**

> P : HiTrap Blue HP. Le volume de colonne est 5 mL. Donne le volume de lavage en volumes de colonne et le débit de lavage pour P. Dans le scénario documentaire Q, les contaminants mineurs n’interfèrent pas avec l’application prévue. Explique le principe général de l’IEX pour Q.

**Proposed structured meaning**

- P: product {"state": "provided", "value": "HiTrap Blue HP"}; separate column {"state": "provided", "value": {"bed_volume": {"value": "5", "unit": "mL"}}}.
  - operating_phase/washing: column_volumes, flow_rate; buffer use not_applicable.
- Q: product {"state": "not_applicable", "value": null, "reason": "Not required for the explicitly requested documentary information."}; separate column {"state": "not_applicable", "value": null, "reason": "Not required for the explicitly requested documentary information."}.
  - general_topic/method_selection: principle; buffer use not_applicable.
  - Facts: [{"key": "minor_contaminants_interfere", "input_role": "documentary_scenario", "value": {"state": "provided", "value": false}}].

**Expected answer / diagnostic (EN)**

P washing: generally at least 5–10 column volumes; flow 5–10 mL/min. Keep volume in CV without conversion to mL. Q: IEX separates by differences in charge. The supplied false condition remains limited to the intended application, without a scientific suitability conclusion.

**Expected answer / diagnostic (FR)**

Lavage de P : généralement au moins 5 à 10 volumes de colonne ; débit de 5 à 10 mL/min. Conserver le volume en CV, sans conversion en mL. Q : l’IEX sépare selon les différences de charge. La condition fausse fournie reste limitée à l’application prévue, sans conclusion d’adéquation scientifique.

**Documentary units**

| Owner/item | Information | Expected state | Required admissible bundle |
|---|---|---|---|
| P/P-washing | column_volumes | supported | E120-H + E120-P + E120-W + E121-PH + E121-W |
| P/P-washing | flow_rate | supported | E120-H + E120-P + E120-W + E121-PH + E121-W |
| Q/Q-method_selection | principle | supported | E118-M |

**Retained reservations / points to validate**

- The 5 mL bed volume is a separate supplied column field, not an inferred product-label suffix or available sample volume.
- Keep generally/at least, do not compute duration, and do not turn false into missing context or authorization to use an actual sample.

**Original manual passages to inspect**

[E118-M — PDF p. 118](#e118-m), [E118-USE — PDF p. 118](#e118-use), [E120-H — PDF p. 120](#e120-h), [E120-P — PDF p. 120](#e120-p), [E120-W — PDF p. 120](#e120-w), [E121-PH — PDF p. 121](#e121-ph), [E121-W — PDF p. 121](#e121-w)

**Exact input origins (Unicode code points, half-open)**

| Language | Origin | Interval | Exact input quote |
|---|---|---|---|
| en | gold-P-scope | [0, 17) | P: HiTrap Blue HP |
| en | gold-P-column | [19, 38) | Column size is 5 mL |
| en | gold-P-request-0 | [40, 90) | Give washing column volumes and washing flow for P |
| en | gold-Q-scope | [95, 117) | documentary scenario Q |
| en | gold-Q-fact-0 | [119, 184) | minor contaminants do not interfere with the intended application |
| en | gold-Q-request-0 | [198, 225) | general IEX principle for Q |
| fr | gold-P-scope | [0, 18) | P : HiTrap Blue HP |
| fr | gold-P-column | [20, 49) | Le volume de colonne est 5 mL |
| fr | gold-P-request-0 | [51, 127) | Donne le volume de lavage en volumes de colonne et le débit de lavage pour P |
| fr | gold-Q-scope | [137, 160) | scénario documentaire Q |
| fr | gold-Q-fact-0 | [162, 230) | les contaminants mineurs n’interfèrent pas avec l’application prévue |
| fr | gold-Q-request-0 | [244, 276) | principe général de l’IEX pour Q |

## FV11 — partial_support_and_quarantine

**Decision: pending.**

**EN input**

> P: HiTrap Blue HP 1 mL. Give equilibration flow and elution flow for P. Q: HiTrap Blue HP 5 mL. For Q, I need the loading flow.

**FR input**

> P : HiTrap Blue HP 1 mL. Donne le débit d’équilibrage et le débit d’élution pour P. Q : HiTrap Blue HP 5 mL. Pour Q, il me faut le débit de chargement.

**Proposed structured meaning**

- P: product {"state": "provided", "value": "HiTrap Blue HP 1 mL"}; separate column {"state": "not_supplied", "value": null}.
  - operating_phase/equilibration: flow_rate; buffer use not_applicable.
  - operating_phase/elution: flow_rate; buffer use not_applicable.
- Q: product {"state": "provided", "value": "HiTrap Blue HP 5 mL"}; separate column {"state": "not_supplied", "value": null}.
  - operating_phase/sample_application: flow_rate; buffer use not_applicable.

**Expected answer / diagnostic (EN)**

Keep P equilibration flow quarantined because E121-EQ is excluded. P elution flow remains 1–2 mL/min and Q loading flow 0.5–5 mL/min. Do not substitute either range for equilibration.

**Expected answer / diagnostic (FR)**

Garder le débit d’équilibrage de P en quarantaine, car E121-EQ est exclu. Le débit d’élution de P reste de 1 à 2 mL/min et le débit de chargement de Q de 0,5 à 5 mL/min. Ne substituer aucun de ces débits à celui de l’équilibrage.

**Documentary units**

| Owner/item | Information | Expected state | Required admissible bundle |
|---|---|---|---|
| P/P-equilibration | flow_rate | quarantined | No assignment |
| P/P-elution | flow_rate | supported | E120-H + E120-P + E120-W + E121-E + E121-PH |
| Q/Q-sample_application | flow_rate | supported | E120-H + E120-P + E120-W + E121-F + E121-L + E121-PH |

**Retained reservations / points to validate**

- One quarantined unit and two supported units remain in the denominator; same-task and independent siblings both remain served.
- No source approval, elution mode, duration or inferred equivalence between steps is introduced.

**Original manual passages to inspect**

[E120-H — PDF p. 120](#e120-h), [E120-P — PDF p. 120](#e120-p), [E120-W — PDF p. 120](#e120-w), [E121-E — PDF p. 121](#e121-e), [E121-F — PDF p. 121](#e121-f), [E121-L — PDF p. 121](#e121-l), [E121-PH — PDF p. 121](#e121-ph)

**Exact input origins (Unicode code points, half-open)**

| Language | Origin | Interval | Exact input quote |
|---|---|---|---|
| en | gold-P-scope | [0, 22) | P: HiTrap Blue HP 1 mL |
| en | gold-Q-scope | [72, 94) | Q: HiTrap Blue HP 5 mL |
| en | gold-P-request-0 | [29, 47) | equilibration flow |
| en | gold-P-request-1 | [52, 70) | elution flow for P |
| en | gold-Q-request-0 | [96, 126) | For Q, I need the loading flow |
| fr | gold-P-scope | [0, 23) | P : HiTrap Blue HP 1 mL |
| fr | gold-Q-scope | [84, 107) | Q : HiTrap Blue HP 5 mL |
| fr | gold-P-request-0 | [34, 53) | débit d’équilibrage |
| fr | gold-P-request-1 | [60, 82) | débit d’élution pour P |
| fr | gold-Q-request-0 | [109, 150) | Pour Q, il me faut le débit de chargement |

## FV12 — partial_support_and_quarantine

**Decision: pending.**

**EN input**

> P: HiTrap Blue HP 5 mL. Give equilibration flow, maximum pressure and washing flow for P. Independently, Q asks for the general SEC principle.

**FR input**

> P : HiTrap Blue HP 5 mL. Donne le débit d’équilibrage, la pression maximale et le débit de lavage pour P. Indépendamment, Q demande le principe général de la SEC.

**Proposed structured meaning**

- P: product {"state": "provided", "value": "HiTrap Blue HP 5 mL"}; separate column {"state": "not_supplied", "value": null}.
  - operating_phase/equilibration: flow_rate; buffer use not_applicable.
  - general_topic/operating_limits: maximum_pressure; buffer use not_applicable.
  - operating_phase/washing: flow_rate; buffer use not_applicable.
- Q: product {"state": "not_applicable", "value": null, "reason": "Not required for the explicitly requested documentary information."}; separate column {"state": "not_applicable", "value": null, "reason": "Not required for the explicitly requested documentary information."}.
  - general_topic/method_selection: principle; buffer use not_applicable.

**Expected answer / diagnostic (EN)**

P equilibration is quarantined; general maximum pressure is missing from the exact 25 eligible excerpts. P washing flow is 5–10 mL/min. Independently, SEC separates by size. Preserve all four units and the distinction between quarantine and bounded absence.

**Expected answer / diagnostic (FR)**

L’équilibrage de P est en quarantaine ; la pression maximale générale manque dans les 25 extraits admissibles précis. Le débit de lavage de P est de 5 à 10 mL/min. Indépendamment, la SEC sépare selon la taille. Conserver les quatre unités et distinguer quarantaine et absence bornée.

**Documentary units**

| Owner/item | Information | Expected state | Required admissible bundle |
|---|---|---|---|
| P/P-equilibration | flow_rate | quarantined | No assignment |
| P/P-operating_limits | maximum_pressure | missing_source | No assignment |
| P/P-washing | flow_rate | supported | E120-H + E120-P + E120-W + E121-PH + E121-W |
| Q/Q-method_selection | principle | supported | E118-M |

**Retained reservations / points to validate**

- Do not inherit equilibration or washing for unqualified maximum pressure; no pressure number or whole-manual absence claim.
- Both withheld units remain counted without suppressing washing or SEC; E118-I and E121-EQ remain excluded.

**Original manual passages to inspect**

[E118-C — PDF p. 118](#e118-c), [E118-M — PDF p. 118](#e118-m), [E118-USE — PDF p. 118](#e118-use), [E119-A — PDF p. 119](#e119-a), [E119-AH — PDF p. 119](#e119-ah), [E119-B — PDF p. 119](#e119-b), [E119-BH — PDF p. 119](#e119-bh), [E119-BI — PDF p. 119](#e119-bi), [E119-BL — PDF p. 119](#e119-bl), [E119-H — PDF p. 119](#e119-h), [E119-I — PDF p. 119](#e119-i), [E119-S — PDF p. 119](#e119-s), [E119-X — PDF p. 119](#e119-x), [E120-A — PDF p. 120](#e120-a), [E120-H — PDF p. 120](#e120-h), [E120-P — PDF p. 120](#e120-p), [E120-U — PDF p. 120](#e120-u), [E120-W — PDF p. 120](#e120-w), [E121-B — PDF p. 121](#e121-b), [E121-BH — PDF p. 121](#e121-bh), [E121-E — PDF p. 121](#e121-e), [E121-F — PDF p. 121](#e121-f), [E121-L — PDF p. 121](#e121-l), [E121-PH — PDF p. 121](#e121-ph), [E121-W — PDF p. 121](#e121-w)

**Exact input origins (Unicode code points, half-open)**

| Language | Origin | Interval | Exact input quote |
|---|---|---|---|
| en | gold-P-scope | [0, 22) | P: HiTrap Blue HP 5 mL |
| en | gold-P-request-0 | [29, 47) | equilibration flow |
| en | gold-P-request-1 | [49, 65) | maximum pressure |
| en | gold-P-request-2 | [70, 88) | washing flow for P |
| en | gold-Q-scope | [105, 141) | Q asks for the general SEC principle |
| en | gold-Q-request-0 | [120, 141) | general SEC principle |
| fr | gold-P-scope | [0, 23) | P : HiTrap Blue HP 5 mL |
| fr | gold-P-request-0 | [34, 53) | débit d’équilibrage |
| fr | gold-P-request-1 | [58, 75) | pression maximale |
| fr | gold-P-request-2 | [82, 104) | débit de lavage pour P |
| fr | gold-Q-scope | [122, 161) | Q demande le principe général de la SEC |
| fr | gold-Q-request-0 | [135, 161) | principe général de la SEC |

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

