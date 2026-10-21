# Subscription-based trial — 19 October 2026

Historical v0.1 trial report. Raw artifacts remain local under `data/experiments/cytiva/pages-097-099-v01/`; tools are in [experiments/cytiva](../../experiments/cytiva/README.md). The current contract is v0.2.

One generation per model, in two new Chrome conversations, using the same prompt containing the converted text of pages 97–99. Sonnet 5.5 and GPT‑6.1 Sol were selected with the effort setting labelled « Moyen » in the original interface (medium). No API calls or purchases were made. Neither response was repaired through a second generation.

| Local check | Sonnet 5.5 | GPT‑6.1 Sol |
|---|---:|---:|
| JSON conforms to the schema | Yes | Yes |
| Entities | 29 | 29 |
| Total proposals | 20 | 29 |
| Non-PROCEDURE relations | 14 | 10 |
| PROCEDURE | 6 | 19 |
| Nonexistent references detected | 0 | 0 |
| Type/direction errors detected | 1 | 0 |

Sonnet c20 uses RECOMMENDED_FOR with a Cause as its object; the ontology requires a Symptom. The model acknowledges this choice in its uncertainties. This proposal must not be accepted automatically. Converting it to a PROCEDURE with an explicit purpose requires review rather than silently correcting the trial output.

GPT‑6.1 Sol passes these structural checks. Its higher proposal count mainly comes from procedures; it demonstrates neither better precision nor better troubleshooting coverage. All references being resolvable means that the cited items can be found in the input, not that they support every assertion.

## Files and preservation

- `resultat-sonnet-original.json`: response copied from Claude and saved through Notepad, unchanged.
- `archive/resultat-sonnet-alias.json`: an older, identical copy retained for traceability; the verifier now reads the original directly.
- `resultat-sol.json`: response copied from ChatGPT Work and saved through Notepad, unchanged.
- `verification-sonnet.json`, `verification-sol.json`: checks and resolved evidence text.
- `comparaison-structurelle.json`: the computed table above.
- `execution-abonnements.json`: models, settings, prompt fingerprint, conversation links and measurement limitations.
- `archive/resultat-sonnet-accessibility.txt`: the first accessibility-text capture, with typographic quotation marks; this is not the original to evaluate.

At this historical checkpoint, the eight reference cards were drafts awaiting validation. No result had been manually approved or promoted into the graph. Semantic review needed to check quantities, conditions, modality, product boundaries and omissions, with candidate names concealed during scoring where possible.

The trial used subscription quotas. No additional API cost was incurred. Billable tokens are unavailable, and observed completion times include automation: neither API cost nor relative speed can be inferred. The 8192-token output cap planned for API requests could not be enforced in these interfaces. Internal instructions and account personalization were uncontrolled.

## Subsequent documentary review

The assistant's review of all 49 proposals is available in the [fidelity report](cytiva-v01-fidelity.md). Detailed `AUDIT-DETAILLE.md` and `audit-fidelite.json` files remain in the local trial directory. That review provisionally recommends GPT‑6.1 Sol, with corrections and documentary quarantine. It does not replace human decisions: no claim was approved in the database through this trial. This document preserves the initial structural findings.
