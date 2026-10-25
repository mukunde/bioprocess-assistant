# Reviewed X01-X12 and frozen v05 results

All twelve bilingual reference intents were validated with reservations before
the single reserved run. Original French decision quotations, UTC record times,
canonical question/reference bindings and reservations remain in `review.json`.
X01/X02 were reviewed individually. X03-X12 share one actual collective approval;
their common message and recording time are explicitly identified in provenance.
No artificial ten-message approval history or new source approval was created.

The frozen gate remains **blocked**: 7/12 intents have complete evidence in both
languages (EN 8/12, FR 7/12), with 9/24 explicit scope violations and 6/24
diagnostic failures. Only X02/X05/X09 meet completeness, explicit scope and
diagnostic criteria in both languages. All 24 contexts and 72 timing measurements
are retained. E118-I and E121-EQ remain excluded; E119-I is separately eligible.

- `results.json`: all saved contexts, exact source serialization, raw hits,
  navigation/negation traces, original timings, recorded tokens and native metrics.
- `provenance.json`: native artifact and review/freeze bindings, tokenizer identity,
  collective-approval scope and the historical 1,588-file preservation attestation.
  Private file inventories and local absolute user paths are omitted.
- `manifest.json`: LF/CRLF-portable hashes for selected files and supporting code,
  documentation and the original preparation packet.

The [preparation](../v05-evaluation-v01/PROTOCOL.md), its pending flags and method
lock remain unchanged. This export supplies the later completed review/run state
without rewriting historical preparation. Hashes establish consistency, not
reviewer authentication or scientific correctness. This is a known-corpus,
known-code drafting challenge, not independent validation. No generated answer,
actual clarification wording or sample-specific answer attribution was scored.

From the repository root, verify using only the standard library:

```powershell
python -S -m experiments.cytiva.verify_v05_reviewed_package
python -S -m unittest tests.test_v05_reviewed_package -v
```

These commands need no private run directory, PDF, credentials, models, tokenizer
cache or network, and never execute retrieval or planning. Token bounds are
verified as recorded, without retokenization. Source/dependency integrity,
reference and diagnostic scores, timing summaries and original artifact hashes
are checked. The five export tests also exercise source/score/diagnostic tampering
and collective-approval scope changes.

The latest [outcome report](../../../docs/experiments/cytiva-v05-prospective-results.md)
analyzes the frozen failures without modifying the method. v05's earlier
[development attempts](../polarity-navigation-v05-results/README.md) remain intact.
Next: design explicit task-scoped request interpretation and a structured-input
control before another development variant; reserve a new reviewed challenge
before testing generalization. No automatic adoption or chat-default change.
