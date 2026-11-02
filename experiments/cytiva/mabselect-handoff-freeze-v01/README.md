# Corrected MabSelect documentary handoff — local freeze v01

Frozen on 2 November 2026 from merged `main` at `776dc12` (handoff PR70,
status documentation PR71). This is a separate, model-free runtime candidate;
the old v03 freeze and all previous results remain unchanged. It is not an
activated serving release, new source approval or independent answer benchmark.

## Verify and replay

From the repository root with CPython 3.13.0 (the recorded environment):

```powershell
python -S -m experiments.cytiva.mabselect_handoff_freeze
python -S -m experiments.cytiva.mabselect_handoff_freeze --environment
python -S -m experiments.cytiva.mabselect_handoff_freeze --replay
```

Static verification hashes the complete declared closure before importing the
runtime. Replay additionally checks the exact Python environment, explicitly
constructs staging preview mode, executes accepted SX01–SX06 and resolves every
delivered citation against the reviewed excerpt snapshot. All socket operations
are blocked. No activation, LLM, paid API, graph write, download, tokenizer cache,
source PDF or hidden audit directory is required. There are no third-party
runtime dependencies; `-S` disables site-package loading.

To retain a separate new replay (parent directory must already exist):

```powershell
python -S -m experiments.cytiva.mabselect_handoff_freeze --replay --output new-replay.json
```

An existing output is refused without overwriting it. The shipped
[replay-results.json](replay-results.json) contains the first executed replay:
complete requests/responses, response digests, lookup counts and resolved citation
identities. It is an output of the frozen method, not an input to selection or a
new human approval. No result is used to retune the runtime.

## Scope and evidence

The [method](METHOD.md), [user decision](freeze-decision.json) and
[method lock](method-lock.json) identify the immutable code, schema and original
source/review closure. Hashes use CRLF-to-LF normalization for artifact files;
exact quote strings keep their original UTF-8 identity. Python implementation and
version are checked separately; OS/hardware portability is not certified.

SX01–SX06 are already accepted examples on known reviewed material. Their replay
checks documentary support, clarification, partial pressure abstention, independent
tasks, exclusions and unauthorized authority fields. It does not measure unseen
questions, generated answers, recall, scientific validity or process suitability.
The existing 24 handoff regressions separately cover quarantines, missing warnings,
authority changes, budgets and the three corrected implementation gaps. The new
freeze tests cover integrity, environment mismatch, line endings and replay guards.

Production active-release/withdrawal authority and legacy-chat integration remain
separate gates. The CLI creates no active pointer or serving inventory. A trusted
reviewed checkout is the authority for this local freeze; hashes detect drift,
not a malicious replacement of both verifier and lock. Deliberate changes require
a new freeze/version, never refreshed hashes to bless the old version.
