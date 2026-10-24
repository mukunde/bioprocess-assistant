# Selected v05 development attempts A and B

This is lot B and depends on lot A's
[reviewed v04 package](../reviewed-v04-evaluation/README.md). It contains all
176 saved contexts from the two known-question development attempts, not a new
prospective evaluation. Neither v04 nor any previous result is overwritten.

Attempt A covers W 12/12, V 12/12, H 10/10 and C 9/10 in both languages.
Its C02 failure is retained. Attempt B restores C 10/10 while preserving the
other coverage; its W scope and diagnostic failures are zero. Missing scope
annotations for H/C remain unavailable, never fabricated as zero-error results.

`results.json` preserves contexts and original metrics. `provenance.json` binds
native artifact hashes, run reservations and exact archived code/test inputs
where earlier attempts differ from the final implementation. Archived input
text is verified as data, never executed. `manifest.json` binds all selected
and supporting files and the exact lot A export manifest.

Standard-library verification needs no private raw run directory, PDF, model,
tokenizer, retrieval or network:

```powershell
python -S -m experiments.cytiva.verify_polarity_navigation_package
python -S -m unittest tests.test_polarity_navigation_package -v
```

E118-I and E121-EQ remain excluded. Recorded token bounds are checked without
retokenizing. Answer quality and generalization are not evaluated; no automatic
adoption occurs. The next step is a new reviewed challenge after freezing v05.
See the [development report](../../../docs/experiments/cytiva-polarity-context-results.md).
