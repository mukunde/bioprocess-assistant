# Reviewed W01-W12 and frozen v04 results

All twelve bilingual reference intents were validated with reservations before
the single reserved run. Original French decision quotations, UTC record times,
question/reference hashes and reservations are preserved in `review.json`.
No new source approval or reconstructed event history was created.

The frozen outcome remains blocked: evidence is complete for 8/12 intents in both
languages, with 13/24 explicit scope failures and 2/24 diagnostic failures.
Only W10/W11 meet completeness, scope and diagnostic criteria in both languages.
E118-I and E121-EQ remain excluded. No generated answer was evaluated.

- `results.json`: the exact 24 saved contexts, rankings, navigation diagnostics,
  timings, token counts and original metrics.
- `provenance.json`: native run/review/freeze hashes, tokenizer identity and the
  historical preservation attestation for 1,488 files. Private inventories and
  local absolute paths are intentionally omitted.
- `manifest.json`: LF/CRLF-portable hashes for the selected and supporting files.

The [preparation](../v04-evaluation-v01/PROTOCOL.md) and its original pending
flags remain unchanged. This later export supplies completed review and execution
status without modifying the original lock. Hashes establish consistency, not
reviewer authentication, scientific validation or independent generalization.

Standard-library checks from the repository root, without raw local artifacts,
PDF, credentials, tokenizer, retrieval, model calls or network access:

```powershell
python -S -m experiments.cytiva.verify_v04_reviewed_package
python -S -m unittest tests.test_v04_reviewed_package -v
```

This is lot A. It needs the already merged project and its own sixteen files;
no v05 file is required. Recorded token bounds are checked without retokenizing.
See the [frozen report](../../../docs/experiments/cytiva-v04-prospective-results.md).
