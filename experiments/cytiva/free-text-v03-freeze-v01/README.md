# Corrected v03: frozen runtime baseline

The user requested this freeze after the corrected runtime and coverage contract
were merged in PR49/PR50. It is prepared locally; no new Git operation is implied.

- [Scope and preservation rules](METHOD.md)
- [Exact dependency and environment lock](method-lock.json)
- [Actual freeze request](freeze-decision.json)
- [Original correction review](../../../docs/technical/FREE-TEXT-CANDIDATE-V03-REVIEW-FIXES.md)

From the repository root, verify without constructing an engine or using a model:

```powershell
python -m experiments.cytiva.free_text_v03_freeze
python -m experiments.cytiva.free_text_v03_freeze --environment
```

The first command uses only Python's standard library. The second requires the
recorded runtime environment and pre-existing private tokenizer cache. Neither
command downloads assets or runs questions. A changed pinned component fails
verification. The lock is versioned separately from v01/v02 and their trials.

The next product delivery is a small local source-backed demonstrator using this
baseline. Runtime freeze integrity, documentary request handling, generated-answer
quality and scientific suitability are different claims. No new trial or complete
manual coverage is established by this checkpoint.
