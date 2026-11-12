# Neo4j adaptive depth results

On 12 November 2026, the 16→32 trigger expanded on all 10 reviewed AD
questions. It preserved the evidence coverage of fixed depth 32, but
increased median total latency from 87.37 to 118.58 ms and returned the
same median context size. The rule failed the three efficiency criteria.
[Reviewed protocol and questions](cytiva-neo4j-adaptive-depth-protocol-v01.md)

## AD01–AD10 results

| Variant | Complete evidence | Mean recall before assembly | Median search (ms) | Median assembly (ms) | Median total (ms) | Total range (ms) | Median evidence tokens | Expansions |
| --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| Fixed 16 | 8/10 | 87.40% | 8.14 | 22.62 | 29.75 | 19.61–56.45 | 1313.5 | — |
| Fixed 32 | 9/10 | 97.08% | 8.08 | 78.43 | 87.37 | 67.51–200.57 | 2705.5 | — |
| Adaptive 16→32 | 9/10 | 97.08% | 17.25 | 100.87 | 118.58 | 88.88–190.55 | 2705.5 | 10/10 |

Coverage requires every reference passage in the final context.
Recall measures reference IDs in the final ranking before assembly.
Each variant has 10 coverage requests and 30 warm timing requests.
Adaptive time includes both attempts and the trigger decision. Stage
medians and total medians are calculated independently. All variants
used zero embedding tokens. Median tokenizer work during assembly was
16,607.5 tokens at fixed 16, 59,941 at fixed 32, and 76,892.5 with the
adaptive rule. This counts repeated tokenization of candidate contexts.

## Trigger outcome

| Reviewed criterion | Result |
| --- | --- |
| Preserve each case covered by either fixed depth | Pass |
| Expand on at most 5 of 10 questions | Fail. The rule expanded on all 10. |
| Reduce median total latency relative to fixed 32 | Fail. The median rose by 31.21 ms. |
| Reduce median evidence tokens relative to fixed 32 | Fail. Both returned a median of 2,705.5 tokens. |

AD02–AD09 already had complete evidence at 16. All eight still
expanded. AD10 gained complete coverage at 32 after the depth-16 cap
excluded `E118-C` and `E118-M`. AD01 remained incomplete. At 32,
`E167-E` was absent from the ranking and the passage cap excluded
`E167-W`. The qualifying exclusion identifies pressure on the passage
budget. On this set it triggered for all questions, including the
eight whose references already fit.

## XC06 regression

XC06 was scored separately. Fixed 16 omitted `E167-P` and `E167-S`
because of the passage cap. Fixed 32 retained both. The adaptive
variant expanded and recovered the complete five-passage reference set.
[Reviewed XC06](cytiva-expanded-heldout-questions-v01.md#xc06)

## Provenance

The 132 requests completed on the 42-passage corpus with no errors.
Each request has a local OpenTelemetry trace. The journal maps cases
and variants to trace IDs and records each attempt separately.
This experiment measures retrieval coverage on reviewed English
questions. It uses zero generative or paid calls.

Local run `adaptive-neo4j-v01-20261112-182939` under
`data/experiments/retrieval/cytiva-feasibility-v01/`.

| Record | SHA-256 |
| --- | --- |
| Reviewed protocol | `24c86f80209f6adb043ed1f3cce6a08b3fa04a4875db4257a5e9be4cef3b82d9` |
| Expanded retrieval freeze | `03a14ba1417dea530beb3e16530b5f2db1a26d60a95f78041955276c80c89e54` |
| Adaptive launcher | `60ad788e507959210e0dea2c05c22fd06e312663afd0124d3c5e3b29a2dc22b8` |
| Local event journal | `f7726eaf9652ffb48de2aacc21c6c8381f6a8ff44bd33d1d9019b5745aac51cb` |
| Local result summary | `ec193074655e56b009ac85abf1e2c2e5a784743fe9468c2e7b8ff770ad54d76c` |
