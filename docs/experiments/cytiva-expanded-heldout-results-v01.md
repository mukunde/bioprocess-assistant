# Cytiva XC01–XC12 retrieval results

On 12 November 2026, expanded Neo4j covered 11 of 12 questions at depth
16 and all 12 at depth 32. The median total latency rose from 26.8 to
71.3 ms, and the median evidence context grew from 1,295 to 2,720.5
tokens. [Reviewed questions and evidence](cytiva-expanded-heldout-questions-v01.md)

## Results

| Depth | Method | Complete evidence | Recall before assembly | Search median (ms) | Total median (ms) | Embedding tokens median | Evidence tokens median |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 8 | Expanded Neo4j | 10/12 | 77.36% | 7.88 | 14.77 | 0 | 592.5 |
| 8 | Vector passage search | 8/12 | 71.39% | 8.07 | 14.16 | 45.5 | 638.5 |
| 8 | LightRAG | 9/12 | 73.75% | 36.72 | 43.61 | 136.5 | 629.5 |
| 16 | Expanded Neo4j | 11/12 | 92.08% | 6.86 | 26.75 | 0 | 1295 |
| 16 | Vector passage search | 10/12 | 83.19% | 8.03 | 28.32 | 45.5 | 1242 |
| 16 | LightRAG | 9/12 | 76.25% | 58.70 | 77.81 | 136.5 | 1183.5 |
| 32 | Expanded Neo4j | 12/12 | 100.00% | 6.82 | 71.28 | 0 | 2720.5 |
| 32 | Vector passage search | 12/12 | 94.44% | 7.98 | 75.89 | 45.5 | 2597.5 |
| 32 | LightRAG | 11/12 | 97.22% | 69.40 | 137.17 | 136.5 | 2579 |

Complete coverage requires every reference passage in the final context.
Recall measures the fraction present before assembly, averaged across the
12 cases. Search and total latencies use 36 warm measurements per method
and depth. Total latency includes retrieval, assembly, and metric
calculation. Index construction is outside both latency measures.
Token medians use the 12 scored requests. Embedding tokens measure
query inference. Evidence tokens include the assembled passages and
their source metadata. Neo4j uses full-text ranking and consumes zero
embedding tokens.

## Depth 16 versus 32

| Method | Additional complete cases | Added median total latency | Added median evidence tokens |
| --- | --- | ---: | ---: |
| Expanded Neo4j | XC06 | 44.53 ms | 1425.5 |
| Vector passage search | XC06 and XC10 | 47.57 ms | 1355.5 |
| LightRAG | XC02 and XC10 | 59.36 ms | 1395.5 |

Depth 16 gives the smaller and faster context in all three methods.
Depth 32 gives full coverage for Neo4j and vector passage search on this
set. For Neo4j, XC06 already had a complete evidence bundle before the
depth-16 assembly cap. At depth 32, LightRAG still excluded the XC06
passage `E167-P` at the passage cap. The 4,096-token cap excluded zero
bundles across the three depths.

## Run provenance and scope

- Freeze ID `cytiva-expanded-corpus-v01`. Manifest SHA-256
  `03a14ba1417dea530beb3e16530b5f2db1a26d60a95f78041955276c80c89e54`.
- The three methods passed the same 42-passage corpus check at each depth.
  Corpus SHA-256
  `028133038b3054fbe392d47b4f302ee5187f1bfa3b03f305defde4da5a5cb5a6`.
- Reviewed question document SHA-256 with LF endings
  `fdcbe395bd66f736ca62627310e49db3fc3e8e9dd967c1756827fa02d2c65c7b`.
- Local run folders `xc-scored-depth8-20261112-143711`,
  `xc-scored-depth16-20261112-143711`, and
  `xc-scored-depth32-20261112-143711` under
  `data/experiments/retrieval/cytiva-feasibility-v01/`.
  The run journals map all 432 completed requests to their OpenTelemetry
  trace IDs. The frozen span filter omits XC case IDs from the spans.
- The experiment measures evidence retrieval on 12 reviewed English
  questions over a curated corpus. Answer generation and the correctness
  of clarification and abstention behavior are outside its scope.
