# ADR-002 - Multilingual retrieval: bridge via the agent, not vector embeddings

**Status:** Accepted
**Date:** 2026-06
**Project context:** The source handbooks are in English; users ask in French (or English). The knowledge graph was migrated to an English canonical form (see seed). The open question: how to make retrieval work well across both languages.

---

## Context

I considered adding a **multilingual vector retrieval** layer: embed each symptom node with a multilingual model, store the vectors in a Neo4j vector index, and run a **hybrid** (BM25 + vector, fused with RRF). The appeal: a French question would match an English node directly in a shared embedding space, and semantic matching would also close the lexical recall gaps the evaluation had surfaced (e.g. "surpression", "HMW").

I did not decide on intuition: I prototyped it (Voyage `voyage-3.5`, 1024-dim, a Neo4j `symptom_vec` vector index, the new `SEARCH` clause) and **measured it against the evaluation suite**.

## What the measurements showed

**1. The vector arm cannot refuse near-domain misses.** Top-1 cosine of each evaluation question against the symptom index:

| Case category | Vector top-1 cosine |
|---|---|
| in-scope (19) | 0.70 - 0.85 |
| in-domain miss (endotoxins, residual DNA) | **0.72 - 0.77** (overlaps in-scope) |
| out of scope | 0.68 - 0.72 |
| off-topic (weather, recipe) | 0.63 - 0.64 |

The in-domain misses - exactly the cases the agent **must refuse** - sit squarely inside the in-scope cosine range. No similarity threshold separates "endotoxins" (refuse) from a legitimate in-scope paraphrase (answer). The vector arm is strong on cross-lingual recall but weak on refusal *precision* for semantically-near, out-of-graph cases. Refusal precision is the project's core anti-hallucination guarantee.

**2. The agent already provides multilingual coverage, with clean refusal.** The system never sends a raw question to retrieval: the agent (Claude tool-use) extracts an **English** search phrase from any-language question. So `query_graph` effectively receives English. Full agent-level evaluation of the English-canonical graph + agent bridge + BM25 (no vectors):

- in-scope: **19/19** answered with sources, **0 hallucinations** (French and English);
- refusals: **9/9** correct.

The agent's term extraction yields 100% in-scope recall, and BM25 keeps refusal clean: an out-of-graph English term ("endotoxin") has no lexical match, scores low, and is correctly refused.

## Decision

Keep the **English-canonical knowledge graph**, rely on the **agent to bridge any-language questions to an English search term**, and retrieve with **English BM25 full-text**. **Do not ship vector embeddings.**

Adding vectors would bring operational complexity (a hosted embedding API, a vector index, query-time latency and cost, rate limits) **and** a refusal-precision regression, for **zero recall gain** - the agent already achieves perfect in-scope recall. An addition that degrades the core guarantee for no measured benefit is the wrong trade.

## Consequences

**Positive**
- Simplest design that meets the bilingual goal; no embedding dependency, API key, cost, or rate limit.
- Refusal precision preserved (9/9), which the vector approach would have weakened.
- Multilingual handled where it is cheapest and most reliable: the agent's tool-use.

**Assumed**
- Retrieval is lexical (BM25 over name + description + curated keywords); it depends on the agent extracting a reasonable English term. At this scale (a few dozen nodes) this is reliable, and the agent-level eval measures it end to end.

**Revisit if**
- The graph grows large enough that lexical retrieval plus agent extraction starts to confuse near-synonym symptoms, or
- a use case needs `query_graph` itself to be cross-lingual without the agent in front.

The vector prototype, and the data above, are kept on record here so this can be revisited from evidence rather than re-litigated from scratch.
