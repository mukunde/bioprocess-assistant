# Scoped navigation v03b: selected development results

This is **lot B, dependent on lot A** and its
[reviewed H export](../reviewed-section-evaluation/README.md). It retains both
measured development iterations and the recorded C section-only control. No
original trial, source annotation or human decision is modified.

| Item | Original section-only | Development A | Development B |
|---|---:|---:|---:|
| H bilingual complete | 8/10 | 10/10 | 10/10 |
| H mean context tokens | 1578.65 | 643.40 | 593.40 |
| H contexts outside annotated acceptable IDs | 19/20 | 0/20 | 0/20 |
| C bilingual complete | 10/10 | 10/10 | 10/10 |
| C mean context tokens | 1725.70 | 733.20 | 733.20 |

These are known development questions used to design corrections. The results
are not independent generalization or answer-quality evidence. C context noise
is unannotated/unknown. H's proxy initially hid phase clutter in A's H10, prompting
B's explicit contrast rule; this history is preserved, not replaced by B's score.

`results.json` preserves all 80 scored measured contexts (40 per revision), both
metric objects and twenty selected C control rows. `provenance.json` preserves
original artifact digests, run configurations, the shared exact corpus and only
the three A code/config/test versions differing from current B. The remaining
input versions resolve against repository files and declared lot A dependencies.
The full native private path inventories are excluded; their counts/digests are
retained as historical preservation attestations. No PDF, full page render,
weights, credentials or personal absolute paths are included.

## Offline verification

Repository root, standard library only; no original local run or tokenizer needed:

```powershell
python -S -m experiments.cytiva.verify_section_navigation_package
python -S -m unittest tests.test_section_navigation_package -v
```

The verifier checks lot A first, all native selected result/context reconstructions,
A/B code versions, scope/provenance/dependency conservation, required-source
coverage, bilingual denominators and summary comparisons. Recorded token bounds
and statistics are checked without retokenizing or rerunning retrieval. It cannot
authenticate the reviewer, recover private inventories, or validate scientific
applicability. E118-I/E121-EQ remain excluded; H10's unavailable-role records are
retained. Neither source is approved by the completed question review.

The current [runtime](../../../ingestion/scoped_passage_context.py),
[configuration](../section_navigation_v03.json) and
[development launcher](../section_navigation_retrieval.py) implement revision B.
See the [development report](../../../docs/experiments/cytiva-scoped-context-results.md)
for regressions, resource limits and local commands. It records the 381-test
checkpoint before these packaging verifiers; packaging adds separate regressions.
A clone contains selected evidence for offline verification; the original
launcher still expects ignored historical runs/review records for a new paired
measurement. Do not manufacture a new review or rerun the frozen trial to fill
that gap.

No default change, graph publication or scientific qualification is granted.
A newly frozen candidate needs separately prepared questions before adoption.
