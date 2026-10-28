# Documentation index

| Question | Canonical document |
|---|---|
| What is the project and how do I run it? | [Project README](../README.md) |
| Where are contribution and Git-operation instructions? | [Repository instructions](../AGENTS.md) |
| What is next and what is already implemented? | [Active roadmap](ROADMAP.md) |
| How do I validate the demo on a second Windows PC? | [Pinned setup and five-minute protocol](validation/WINDOWS-SECOND-PC.md), [blank results](validation/windows-second-pc-results-template.md) |
| How are answers constrained and evaluated? | [Grounding ADR](ADR-001-knowledge-graph-grounding.md), [evaluation](../eval/README.md) |
| How does the existing PDF ingestion/review work? | [Ingestion](INGESTION.md) |
| How are Cytiva tables, captions, diagrams and chunking validated? | [Protocol and selected pages](experiments/cytiva-conversion-chunking-protocol.md), [first results on 77 and 88](experiments/cytiva-conversion-chunking-results-077-088.md) |
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
audits and full review journals remain in local ignored directories. A selected
[r2 review export](../experiments/cytiva/reviewed-r2/README.md) contains the corrected
candidate, 33 decisions with reservations and provenance hashes, without PDF or full
source text. A fresh clone has that curated evidence, not the local source bundle.
The experiment documentation distinguishes synthetic tests from checks requiring
that bundle. Decisions apply only to the candidate and individual claim hashes
recorded in the export; they do not authorize publication or approve modified claims.

All four lots are merged (PRs #3–#6), including the claim-contract command compatibility update. The README is merged through PR #7. That integrated revision passed 106 principal tests; seven historical checks also passed with the local evidence bundle and explicitly skip without it. The old pages 100–102 bundle uses the earlier prompt and remains unexecuted. The corrected-prompt r2 generation and human review are complete (19 validated, 14 with reservations, none pending). Migration into the review UI and publication remain pending. See the [experiment guide](../experiments/cytiva/README.md) for verification commands.
