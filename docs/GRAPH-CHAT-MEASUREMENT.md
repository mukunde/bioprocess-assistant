# Graph chat measurement protocol

The original measurement used a USD 1.00 ceiling. The structured-output
replay used a separately approved USD 1.01 ceiling. A new live run requires
separate approval.

## Question set

Compare the displayed claims and citations with the frozen snapshot of the
[graph seed](../graph/seed.cypher). The expected answers describe graph
behavior. Clinical or process recommendations and independent source
verification are outside this measurement.

| ID | Exact question | Expected result |
| --- | --- | --- |
| G01 | My Protein A capture yield has dropped and antibody is appearing in the flow-through. What should I check? | Sourced answer for Capture step yield drop. Expect both paths, degraded resin with a binding capacity check and conditional replacement, and excessive loading flow with a reduction in flow. Cytiva MabSelect SuRe data file CY12754, pp. 1–3, with the handbook p. 58 where cited in the seed. |
| G02 | La pression de ma colonne augmente pendant la capture Protein A. Quelles causes dois-je vérifier ? | Sourced answer for High column pressure, with French headings. Expect fouling with cleaning suited to the resin and packing or flow with an efficiency check. Cytiva handbook CY13981, pp. 162–167, and MabSelect SuRe data file CY12754 where cited in the seed. Preserve resin-specific conditions. |
| G03 | Protein A capture yield and column pressure are normal. I only see a slow decline in cell viability in the upstream bioreactor. What should I change? | Intentional abstention. No capture troubleshooting advice, citation, or treatment for the bioreactor. Record any retrieval attempt. |
| G04 | My capture elution pool has elevated endotoxin. What endotoxin-removal procedure does the graph support? | Intentional abstention. No substitution with host cell protein contamination or aggregation and no invented procedure or citations. Record any retrieval attempt. |
| G05 | Same prompt as G01, with an injected retrieval failure. | Offline. Stub the model's first tool request and raise a Neo4j availability error at the retrieval boundary. Expect a safe service error in the chat and error spans for the request and search. No source-backed answer, intentional abstention, or further model call. |

## Procedure

1. Record the commit, seed hash, model and SDK versions, Neo4j configuration,
   retrieval threshold (default 2.5), and the measurement limits. Verify that
   the graph contains the seed fixture and the full-text index is ready. Use
   a fixture database when the local graph contains unrelated additions.
2. Run G05 and confirm the request and search error spans using the existing
   [offline tests](../tests/test_graph_chat_tracing.py) and
   [chat error checks](../tests/test_app.py). Initialize the trace sink and
   verify export with a stubbed warm-up in the benchmark process.
3. After approval and budget preflight, submit G01–G04 twice in that order,
   one at a time, with a fresh conversation per submission. Keep the process
   and graph warm. Record failures and excluded measurements. Avoid replacing
   them with reruns.
4. Match each case to its exported trace ID. Record client elapsed time and
   request, Anthropic, and Neo4j span durations, plus the counts of calls,
   reported token categories, and estimated USD cost. Record missing traces
   and usage explicitly. Keep raw traces and answers local.

Report individual outcomes, a median and range for each measured stage, and
the number of observations. Separate offline fault timing from live timing.
Mark quality as passing only if every live outcome matches the reference,
each displayed claim keeps the corresponding graph citation, and G05 returns
the expected service error. Report trace coverage separately. The sample is
too small to establish a tail-latency target.

## Original spend ceiling

The original run had a USD 1.00 ceiling, including failed calls. The live preflight
must enforce eight submissions total, at most three Anthropic calls per
submission, zero SDK retries, a verified input limit of 5,000 tokens per call,
and a maximum of 512 output tokens per call. The input limit includes system
instructions, tool schema, conversation, and retrieval results. Confirm
standard API billing and use the benchmark path, which sends no cache controls.
The benchmark guard is opt-in and scoped to one sequential run.

Before each generation the guard checks the full payload with Anthropic's
[token-counting endpoint](https://platform.claude.com/docs/en/build-with-claude/token-counting).
The endpoint is free but remote, and its count can differ from actual usage.
The guard admits estimated counts up to 4,500, reserves for 5,000, and halts
if reported input exceeds 5,000 or the reported usage cannot be verified.
The counting call is outside the generation span and inside request timing.
Verify the first-party endpoint and billing configuration before any live run.

With standard Sonnet 4.6 pricing of USD 3 per million input tokens and USD 15
per million output tokens, the worst case under these limits is approximately
USD 0.60 including the 10% US-only surcharge. Reserve the worst-case cost
before each call and retain the full reserve even if the call fails or uses
fewer tokens. Halt if a limit cannot be verified or enforced. Record any budget-induced abort as
its own outcome. The smaller turn and output limits are part of the baseline
and may affect the answers. [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing)


Run the offline guard checks with
`python -m unittest tests.test_graph_chat_budget -v` from the repository root.
They exercise the agent with simulated model and graph responses. The
benchmark runner shares one guard across all eight submissions and writes
a local report with case IDs, outcomes, reserves, and verified trace links.
It requires an explicitly supplied client. Generate an offline preview with
the simulated client and graph fixture.

```powershell
.\.local-tools\graph-chat-venv\Scripts\python.exe -c "from tests.test_graph_chat_benchmark import simulate; print(simulate()[0])"
```

The preview writes an ignored report and trace file under
`tmp/graph-chat-traces/`. It exercises the runner and trace links. Review
answer quality separately against the seed. G05 remains an independent
offline fault test.

## Targeted follow-up

The first run reserved USD 0.399168. Repeat G01 and G02 twice with
`run_targeted_retry` after approval. Raise the output limit from 512 to
1,536 tokens. Keep the 4,500-token input preflight, 5,000-token input
reserve, three-generation limit per submission, and zero SDK retries.

The follow-up reserves at most USD 0.502128 for 12 generations, including
the possible US routing surcharge. The cumulative maximum reserve is
USD 0.901296, leaving USD 0.098704 of the original ceiling. Use the same
verified first-party client with standard-only billing. Check the new
stop reason on each Anthropic span and compare the displayed citations
with the seed. Earlier traces lack this field.

## G01 with structured output

A single G01 submission on 6 November 2026 used the structured JSON schema,
a 1,536-token output limit per generation, and a two-generation limit. The
Cytiva seed contained 30 expected nodes and 24 expected links. Its full-text
index was online.

The chat returned both expected paths. It suggested measuring the resin's
dynamic binding capacity and considering replacement if it had degraded. It
also suggested checking whether the loading flow allowed sufficient residence
time. All five displayed citations matched the seed. They referenced the
Cytiva MabSelect SuRe data file CY12754, pp. 1–3, figures 2–3, and table 2,
and the Cytiva antibodies handbook CY13981, p. 58.

Anthropic returned `tool_use` followed by `end_turn`. The final generation
used 19 output tokens. Neo4j returned one match and one miss. The request
took 9.01 seconds and used 3,515 input tokens and 124 output tokens. The
estimated cost was USD 0.012405. Across the four live runs, estimated costs
totaled USD 0.233286 and reserves totaled USD 0.984984 against the USD 1.00
ceiling.

The preceding G01 diagnostic run recorded an `invalid_json` rejection. This
follow-up confirms one successful G01 result with the schema. It does not
measure repeatability or assess the full question set with structured output.
The report and trace remain local. The trace ID is
`9293edd91fee2af830263c1f856cf83f`.

## Structured-output replay

On 6 November 2026, two passes of G01–G04 used Claude Sonnet 4.6, Anthropic
SDK 2.6.0, standard billing, and the structured JSON schema. The local Neo4j
fixture matched the 30 expected nodes and 24 expected links. The full-text
index was online, and the retrieval threshold was 2.5. The LF-normalized
SHA-256 of the seed was
`9d95f426fb92cc718712bca99694c886201a32c124838f4a2351bf75b942d6ed`.

The `run_structured_replay` entry point uses the separate USD 1.01 ceiling.
It allows up to three generations per request, 1,536 output tokens per
generation, and zero SDK retries. The input preflight and reserve remain at
4,500 and 5,000 tokens respectively. The planned reserve was USD 1.004256
for up to 24 generations.

| Pass | Case | Result | Citations | Request (s) | Input tokens | Output tokens | Estimated USD |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | G01 | Sourced answer | 5 | 4.70 | 4,248 | 128 | 0.014664 |
| 1 | G02 | Sourced answer | 5 | 3.98 | 3,448 | 85 | 0.011619 |
| 1 | G03 | Abstention | 0 | 4.30 | 2,671 | 85 | 0.009288 |
| 1 | G04 | Abstention | 0 | 2.90 | 2,655 | 85 | 0.009240 |
| 2 | G01 | Sourced answer | 5 | 3.88 | 4,248 | 128 | 0.014664 |
| 2 | G02 | Sourced answer | 5 | 4.12 | 3,448 | 85 | 0.011619 |
| 2 | G03 | Abstention | 0 | 3.96 | 2,671 | 85 | 0.009288 |
| 2 | G04 | Abstention | 0 | 3.03 | 2,655 | 85 | 0.009240 |

All eight requests exported a trace and matched their expected outcomes.
Each used two generations with `tool_use` followed by `end_turn`. The final
JSON selection passed validation each time. The 16 generations used
26,044 input and 766 output tokens. Estimated model cost was USD 0.089622,
and the guard reserved USD 0.669504.

| Stage | Observations | Median (ms) | Range (ms) |
| --- | --- | --- | --- |
| Request | 8 | 3,970 | 2,897–4,699 |
| Anthropic generation | 16 | 1,585 | 1,168–2,502 |
| Neo4j search | 10 | 32 | 18–223 |

G01 returned both the degraded-resin and loading-flow paths in each pass.
Its citations point to Cytiva CY12754, pp. 1–3, figures 2–3 and table 2, and
CY13981, p. 58. G02 returned the bed-efficiency and resin-specific cleaning
paths in each pass. Its citations point to CY13981, pp. 162–164 and 166–167,
and CY12754, pp. 4–5 and figure 11. All 20 displayed citation entries
matched the seed. G03 and G04 had no eligible match and abstained without
citations in both passes.

The separate G05 offline check injected a Neo4j availability error. Chainlit
returned the generic service error, and the request and search spans recorded
the failure. The agent stopped after one simulated model call.

These results measure repeatability on four known questions and citation
fidelity to the seed. Independent source review and performance on unseen
questions are separate checks.
