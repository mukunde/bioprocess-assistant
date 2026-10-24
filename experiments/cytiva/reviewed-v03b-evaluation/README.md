# Reviewed V01-V12 and frozen v03b results

All twelve bilingual reference intents were validated with reservations. Original
French human decision quotations, UTC record times, canonical question/reference
bindings and the exact reservations are preserved in `review.json`. No synthetic
event history or new source approval was created.

The single frozen run has 24 contexts: 6/12 intents are evidence-complete in both
languages, but only V02/V05/V09 also respect explicit phase scope. The predeclared
gate is blocked. E118-I and E121-EQ remain excluded. No generated answers, scientific
correctness, refusal behavior or independent/new-section generalization was scored.

- `results.json`: all exact saved contexts, raw hits, navigation, seeds, missing
  sources, original timings, token counts and native measured metrics.
- `provenance.json`: review/freeze/run bindings, native artifact hashes and recorded
  preservation attestation. The private local inventory itself is not exported.
- `manifest.json`: portable LF/CRLF content and supporting-file hashes.

The original [preparation](../v03b-evaluation-v01/PROTOCOL.md), its pending flags,
manifest, historical test and runtime remain unchanged. This later export reports
review/execution status without rewriting historical preparation. Hashes establish
consistency, not reviewer authentication or scientific truth. Token bounds and
recorded timing summaries are checked without retokenization or rerunning search.

Standard-library verification from the repository root, with no local raw runs,
PDF, credentials, tokenizer cache or models required:

```powershell
python -S -m experiments.cytiva.verify_v03b_reviewed_package
python -S -m unittest tests.test_v03b_reviewed_package -v
```

This is lot A. It depends only on already merged code and its own selected files;
no v04 files are required. The old preparation-era test may still assume no local
run exists; its maintained fixture/discovery correction belongs to lot B. A fresh
checkout of lot A contains no ignored local locked-run directory.

See the [frozen outcome report](../../../docs/experiments/cytiva-v03b-prospective-results.md).
