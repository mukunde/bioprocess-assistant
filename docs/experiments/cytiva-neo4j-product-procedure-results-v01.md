# Cytiva product and procedure retrieval results

On 12 November 2026, fixed-depth 32 and product–procedure retrieval both
covered all eight reviewed SP questions. The candidate also recovered
the missing MabSelect solvent evidence in the separate AD01 regression.
[Reviewed protocol and questions](cytiva-neo4j-product-procedure-protocol-v01.md)
· [Passage map and aliases](cytiva-neo4j-product-procedure-scope-map-v01.md)

## SP01–SP08 comparison

| Measure | Fixed 32 | Product–procedure |
| --- | ---: | ---: |
| Complete evidence | 8/8 | 8/8 |
| Mean recall in the ranking | 96.43% | 96.43% |
| Mean recall with dependencies before assembly | 100% | 100% |
| Median warm total latency | 125.07 ms | 129.83 ms |
| Warm latency range | 90.19–194.98 ms | 91.58–229.64 ms |
| Median evidence tokens | 2,661.5 | 2,661.5 |

Complete evidence requires every reference passage in the final context.
Each variant had eight coverage requests and 24 warm timing requests.
Total latency includes scope resolution where applicable, retrieval,
ranking, and assembly. Both variants use the same 42 reviewed passages,
a cap of 32 final passages, and a 4,096-token context limit.

## Acceptance criteria

- **Coverage** The candidate exceeded the 7/8 threshold and preserved all
  eight cases covered by fixed 32.
- **Scope integrity** The candidate retained evidence for the reviewed
  product and procedure scopes, with their source dependencies.
- **Latency** The candidate took 1.038 times the fixed-32 warm median,
  within the 1.25 limit. The median increased by about 4.8 ms.
- **Separate regressions** The candidate recovered AD01 and preserved XC06.

The new questions show equal coverage and median context size. The observed
coverage gain is on the previously diagnosed AD01 case. This experiment
evaluates retrieval on this corpus. Answer generation and the correctness
of clarification and abstention are outside its scope.

## AD01 and XC06 regressions

| Case | Fixed 32 | Product–procedure |
| --- | --- | --- |
| AD01 | `E167-E` fell outside the ranking and the assembly cap excluded `E167-W`. | Both passages were retained. Protein A Sepharose and MabSelect solvent guidance kept their own warnings and dependencies. |
| XC06 | All five reference passages were retained. | All five were retained. The common MabSelect wash and the stronger alkali option remained distinct, and the latter kept the SuRe/SuRe LX restriction. |

[Reviewed AD01](cytiva-neo4j-adaptive-depth-protocol-v01.md#ad01)
· [Reviewed XC06](cytiva-expanded-heldout-questions-v01.md#xc06)

## Run provenance

The comparison and regressions completed 80 local requests. Each has an
OpenTelemetry trace linked by the event journal. Both variants used zero
embedding tokens, zero generative calls, and zero paid calls.

Local run `product-procedure-scored-v01-20261112-212335` under
`data/experiments/retrieval/cytiva-feasibility-v01/`.

| Record | SHA-256 |
| --- | --- |
| Product–procedure freeze | `11d978be671aa56f1852c2eec9126c0d9ea9de688f24b181360d8f010eb2503e` |
| Original expanded retrieval freeze | `03a14ba1417dea530beb3e16530b5f2db1a26d60a95f78041955276c80c89e54` |
| Event journal | `9494be4e3a4931621bfbf86e5700916cf67ce7c425e3ebee91457e4f5a2e5693` |
| Result summary | `e7ad84902d911d674532a195e3f74ed3104044e042acc40ad1f0508c7ee26012` |
