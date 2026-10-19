# Documentation index

| Question | Canonical document |
|---|---|
| What is the project and how do I run it? | [Project README](../README.md) |
| What is next and what is already implemented? | [Active roadmap](ROADMAP.md) |
| How are answers constrained and evaluated? | [Grounding ADR](ADR-001-knowledge-graph-grounding.md), [evaluation](../eval/README.md) |
| How does the existing PDF ingestion/review work? | [Ingestion](INGESTION.md) |
| What do the troubleshooting concepts mean? | [Ontology draft](ontology/v0.1.md), [documentary examples](ontology/examples-v0.1.md) |
| What is the current extraction format and quarantine rule? | [Claim contract v0.2](CLAIM-CONTRACT-V02.md) |
| How will retrieval alternatives and LightRAG be evaluated? | [Three-arm comparison protocol](experiments/retrieval-comparison-protocol.md) |
| Where is the reproducible experiment code? | [Cytiva tooling](../experiments/cytiva/README.md) |
| What has been delivered and verified? | [Delivery history and verification](CONSOLIDATION.md), [machine-readable lists](commit-lots.json) |

## Historical evidence, not competing roadmaps

- [Local extraction diagnosis](experiments/cytiva-local-extraction-diagnostic.md):
  the slow first local extraction, missing relations and citation issues.
- [Subscription experiment](experiments/cytiva-v01-results.md): structural results.
- [Documentary fidelity comparison](experiments/cytiva-v01-fidelity.md): the source
  review and provisional model choice.
- [Methodology review](decisions/2026-10-roadmap-review.md): the reasoning behind
  revising the plan. Only ROADMAP.md is the active plan.

Manuals, raw conversions, source excerpts, full model responses, detailed generated
audits and review decisions remain in local ignored directories. A fresh clone
therefore has the code and curated findings, not the author's local evidence bundle.
The experiment documentation distinguishes synthetic tests from checks requiring
that bundle. No prior human approval is transferred by moving files.

All four lots are merged (PRs #3–#6), including the claim-contract command compatibility update. The README is merged through PR #7. The final integrated revision passed 106 principal tests; seven historical checks also passed with the local evidence bundle and explicitly skip without it. The old pages 100–102 bundle uses the earlier prompt. The local `pages-100-102-v02-r2` package is now prepared and verified with the corrected prompt; generation and human review remain pending. See the [experiment guide](../experiments/cytiva/README.md) for the workflow.
