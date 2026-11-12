# Cytiva offline answer-layer replay results

The reviewed offline replay passed all 50 checks. The two retrieval
variants produced the same outcomes on AR01–AR06. They differed on AD01,
where product–procedure retrieval supplied the two passages needed to
answer the MabSelect branch. [Protocol and reviewed cases](cytiva-answer-layer-offline-protocol-v01.md)

## AR01–AR06 and fault controls

| Check | Fixed 32 | Product–procedure |
| --- | ---: | ---: |
| Full-evidence controls | 6/6 | 6/6 |
| Paired retrieval snapshots | 6/6 | 6/6 |
| F01–F07 fault groups | 7/7 | 7/7 |
| Fault subcases | 11/11 | 11/11 |

Each variant produced three answers, one clarification, and two abstentions
on the paired snapshots. AR03 asked for column size. AR02 applied the
Blue Sepharose warning, and AR05 abstained on the unsupported pressure
quantity. No invalid citation or unsupported actionable claim appeared
in the recorded outputs.

| Control | Observed behavior for both variants |
| --- | --- |
| F01 | Rejected an absent citation, abstained on the unsupported branch, and preserved the supported branch. |
| F02 | Abstained when the required warning or heading was removed. |
| F03 | Rejected the cross-product citation and preserved the independent branch. |
| F04 | Rejected the loading-to-elution transfer and the wrong-format syringe conversion. |
| F05 | Rejected an altered page, an altered quotation, and an excluded passage. |
| F06 | Asked for column size and withheld the format-specific answer. |
| F07 | Rejected the invented maximum pressure and stated the source limit. |

The validator checked controlled proposals against an approved fact
catalog. These results establish how the validator and renderer handle
the reviewed proposals and mutations. Answer generation and
generalization to unseen proposals are outside the evaluation scope.

## Separate regressions

| Case | Fixed 32 | Product–procedure |
| --- | --- | --- |
| AD01 | Answered the Protein A Sepharose branch and abstained on MabSelect because `E167-E` and `E167-W` were absent. | Answered both branches with their own scope, citations, and warnings. |
| XC06 | Rendered the common rinse and stronger alkali option separately, with the SuRe/SuRe LX restriction. | Rendered both branches with the same restriction. |

The four regression replays are counted separately from AR01–AR06 and
the fault controls.
[Reviewed AD01](cytiva-neo4j-adaptive-depth-protocol-v01.md#ad01) ·
[Reviewed XC06](cytiva-expanded-heldout-questions-v01.md#xc06)

## Provenance

The local replay is `answer-layer-replay-v01-20261112-234930` under
`data/experiments/retrieval/cytiva-feasibility-v01/`. It used
`answer-layer-fixtures-v01-20261112-234608`. Each of the 50 outputs has a
metadata-only OpenTelemetry trace. The replay made zero retrieval,
generative, and paid calls.

| Record | SHA-256 |
| --- | --- |
| Fixture manifest | `032884d8b44c40ffbe7d27c1fcba8542f89e0aa291a6dc7b3a2f618228d8c681` |
| Replay launcher | `14a02950716b930c09debc6e1a653616a80ff7d6a423b8de15743f6bc2e788b0` |
| Summary | `7f216b8877b7bb2b8472dfadc1f2bcc3258445acdffebc0b1929fbdf1d14fe8a` |
| Per-case outputs | `2d25c16159c951c3cc8ceedca65cc06e4ea594646d76de58358e2003c19ab358` |
| Trace export | `b5ab83b2aadb3af78be9905844b1fbf46adb3f456e89906a4535e9d02e820f34` |
