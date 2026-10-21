# Bioprocess Troubleshooting Assistant

An AI assistant demonstrator for **troubleshooting Protein A capture chromatography**, a downstream bioprocess operation.

## How it works

Describe a symptom observed during capture. The assistant presents possible causes and corrective actions, **each with a public handbook citation**: Cytiva's *Affinity Chromatography Vol. 1: Antibodies Handbook* (CY13981-25Jan21-HB, 2021) and *MabSelect SuRe Data File* (CY12754-10Jul20-DF, 2020).

## Behavior and limitations

- **Constrained answers:** the model selects graph results. The application checks that selection and displays stored facts and citations. Relevance and scientific correctness require domain validation.
- **Traceability:** causes and actions carry references to specific source PDF pages. A citation alone does not establish documentary fidelity.
- **Current coverage:** six Protein A capture symptoms: reduced yield, high pressure, aggregates in the elution pool, Protein A leaching, residual HCP and bioburden.

## Questions to try

- *“My capture yield has dropped. What could cause it?”*
- *“My column pressure is unusually high.”*
- *“There are too many aggregates in my elution pool.”*
- *“How can I reduce Protein A leaching in the eluate?”*
- *“Residual HCP is above specification.”*
- *“I detected bioburden in my column.”*

Ask in French or English. Headings and refusals follow your language; technical descriptions remain in English, the graph's canonical language.

---

*Demonstrator POC: public sources only, not a GxP-qualified system. See the repository's `docs/ADR-001-knowledge-graph-grounding.md` for the architecture.*
