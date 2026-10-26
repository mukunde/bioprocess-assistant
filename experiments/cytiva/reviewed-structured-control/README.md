# Reviewed structured-control challenge S01-S12

The twelve scenarios were approved individually with reservations before the
single frozen execution: **24/24 EN/FR inputs and 12/12 paired scenarios passed**.
No generated answer or free-text interpretation was evaluated. This is a
known-corpus diagnostic challenge, not independent scientific validation.

- `review.json`: twelve actual French human messages, original UTC record times,
  content hashes and retained reservations. Each message is preserved verbatim.
- `events.json`: consolidated decisions and the explicit S01 task-B washing-flow
  exclusion amendment. Original preparation inputs and hashes are embedded for
  that correction; no source, question, reference or method change is inferred.
- `results.json`: all 24 complete saved outputs, timings and original metrics.
  Adjacent source quantities can occur in the context without assignment to a
  blocked item; bindings and diagnostics are retained for inspection.
- `provenance.json`: original artifact hashes, reservation, preservation checks,
  source PDF identity, tokenizer identity and bounded result summary.
- `manifest.json`: LF/CRLF-portable hashes of the export and all required support.

The [frozen preparation](../structured-control-evaluation-v01/PROTOCOL.md) retains
its historical pending status. Completed decisions and execution live here;
neither the preparation nor the frozen method is rewritten after the run.
E118-I and E121-EQ remain excluded, not newly approved by this challenge.

From the repository root, with only the Python standard library:

```powershell
python -S -m experiments.cytiva.verify_structured_reviewed_package
python -S -m unittest tests.test_structured_reviewed_package -v
```

These commands require no private run directory, source PDF, tokenizer cache,
credentials, model or network. They verify saved evidence and never execute
StructuredControl. Token bounds are checked as recorded; exact retokenization
was performed during the original run, not by this portable verifier. Hashes
establish consistency, not reviewer authentication.

See the [result analysis](../../../docs/experiments/cytiva-structured-control-s-results.md)
and [exact proposed file list](../../../docs/experiments/cytiva-structured-control-s-package.md).
The tests reject altered sources, quarantine leakage, changed scores or review
bindings, an altered S01 amendment and token-budget violations, and verify a
CRLF checkout without private artifacts. No automatic production adoption follows.
