# ADR-001 - Grounding my troubleshooting agent on a knowledge graph

**Status:** Accepted
**Date:** 2026-05
**Project context:** Prototype AI assistant for troubleshooting Protein A capture chromatography (a *downstream* bioprocess unit operation).

---

## Context

I want to build an assistant demonstrator that helps a process engineer diagnose a Protein A capture problem: from an observed symptom ("my capture yield dropped"), the agent proposes the probable causes and associated corrective actions.

The usage context I'm targeting is biopharma, a regulated environment. I draw three constraints from it that dominate all others:

- **Auditability.** Every answer must be traceable back to its source. A claim without provenance is unusable.
- **Zero tolerated hallucination.** An agent that invents a plausible-but-wrong cause is worse than useless: it is dangerous.
- **Extensibility by domain experts.** The knowledge must be enrichable through contact with bioprocess engineers, without rewriting the system.

**My riskiest assumption (RAT):** can an agent produce an answer a bioprocess engineer would judge credible and non-hallucinated, with its sources? That is the hypothesis this prototype exists to validate. To me, everything else (UI, graph volume) is secondary.

## Options considered

1. **LLM alone (parametric knowledge).** The agent answers from what it learned during training.
   *Rejected:* no traceability, unbounded hallucination, frozen and non-auditable knowledge. Disqualifying in a regulated context.

2. **Vector RAG over documents.** We index application notes; the agent retrieves the chunks semantically close to the question.
   *Rejected as the foundation:* vector RAG returns text fragments with no explicit causal structure. Yet troubleshooting knowledge is intrinsically relational - a symptom has *several* causes, a cause has *several* actions. Chunking breaks these relations and can mix sources without the agent being aware of it.

3. **Structured knowledge graph (chosen).** I model the knowledge explicitly as `Symptom → Cause → Action`, store it in Neo4j, and the agent queries it through a dedicated tool.

## Decision

I ground the agent on a **Neo4j knowledge graph** as the single source of truth.

- **Hosting: Neo4j AuraDB Free.** A free tier with no time limit, amply sized for the POC's target volume (~6 symptoms / ~12 causes / ~12 actions, vs. 200k nodes allowed). It saves me a local install and makes the database reachable from any machine. I note that AuraDB Free pauses the instance after ~3 days of inactivity - wakeable in one click, but worth accounting for on the demo side (the planned backup video covers this risk).
- **A single tool exposed to the agent**, `query_graph(symptom)`, which translates the question into a Cypher query and returns the ranked causes and their corrective actions.
- **Strict system prompt.** I enforce the following rule: **answer only from the graph, cite the source of every node, and explicitly state "I don't have this information" when out of scope.** My anti-hallucination grounding lives in this constraint.
- **Every node carries a `source` field** (the originating application note), which I surface in the answer.

The relational model matches the causal nature of the domain: it is the graph, not the agent, that holds the knowledge. My agent is merely a natural-language interface over a structured, auditable truth.

## Consequences

**Positive**
- Native auditability: every answer traces back to an identified source.
- Anti-hallucination by construction: the agent can only assert what the graph contains.
- Extensible: domain experts enrich the graph (nodes, relations, sources) without touching the code.
- Causal relations - the heart of troubleshooting reasoning - are explicit and queryable.

**Assumed limitations**
- Answer quality depends entirely on graph curation: *garbage in, garbage out*.
- I deliberately restrict the initial scope to a single unit operation (Protein A capture).
- I rely only on **public sources** (handbooks and application notes), not internal data. This is a proof of concept, **not a GxP-grade system**.
- Dependency on AuraDB Free: if Neo4j changes the free-tier terms, I switch to Neo4j Community locally (only the URI changes; the rest of the agent code stays identical).

**Debt / future evolutions**
- Extending to other unit operations will raise the question of **entity alignment** across representations (cf. the ChatP&ID pattern for plant topology + a Fabric IQ-style ontology layer for operational state). This is real architecture work, not to be underestimated - and precisely why I leave it out of scope here.
- A vector RAG layer could *complement* the graph for open questions not covered by the relational model - as a complement, never a replacement for the structured truth.
