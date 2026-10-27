# Demo-first delivery: local Cytiva evidence explorer

## Priority and current slice

The user explicitly selected the local, free guided Cytiva route on 27 October
2026. The first product checkpoint is a usable request-to-citation path. Do not
gate it on another twelve-question review campaign, a new graph framework or a
broader corpus.

Corrected v03 is [frozen separately](../experiments/cytiva/free-text-v03-freeze-v01/README.md).
The first local UI is implemented in [demo/cytiva.py](../demo/cytiva.py). It calls
the frozen engine and renders complete source bundles without generated advice.
It does not change the existing Chainlit/Neo4j chat or publish new graph records.

The guided slice covers HiTrap Blue HP 1 mL/5 mL, or an unspecified format, and
the supported loading/washing/elution/buffer questions from the existing 25
reviewed excerpts. Pressure and equilibration demonstrate missing evidence and
quarantine. The optional EN/FR text input retains the bounded parser and its
clarification behavior. Source quotations remain in their original English.

## Launch on the prepared Windows workstation

No installation, Neo4j, model download, API key or paid call is required in the
existing verification environment. From the repository root:

```powershell
.\.local-tools\verification-venv\Scripts\python.exe -m experiments.cytiva.free_text_v03_freeze --environment
.\.local-tools\verification-venv\Scripts\python.exe -m demo.cytiva --port 8766
```

Open [the local demo](http://127.0.0.1:8766/). Stop the server with Ctrl+C. It binds
only to loopback, keeps no conversational state and writes no submitted text or
results to disk. This is a workstation demo, not a hosted deployment.

For a different machine, reproduce the versions in the runtime lock and supply
the offline tokenizer asset with its recorded hash before using the environment
check. The private verification environment/cache is not redistributed; a clean
installation/packaging path is the next delivery step, not already certified.

## Five-minute walkthrough

1. Keep the default 1 mL column and washing flow. Submit; inspect complete source
   context, the column-specific binding and the Blue Sepharose warning.
2. Add washing volume and stopping criteria. Show that the request uses several
   units while the complete shared source bundle is retained.
3. Add general maximum pressure and equilibration flow. Show partial service,
   missing selected-corpus evidence and quarantine without losing washing support.
4. Clear the column format. Show clarification rather than guessing a format.
5. Optionally use the French text example. Then try coordinated buffer purposes;
   the interpreter asks for clarification instead of silently dropping a purpose.

The corrected interface labels the request behind each result and flags it as
stale after input changes. Missing-format clarification has a direct correction
button; source/result navigation stays available. Highlighting marks a literal
format mention while preserving the complete original quotation. See the
[usability review and browser checks](experiments/cytiva-demo-ux-review.md).

The display reports whole-request support separately from eligible-context
coverage. A complete context ratio is not a fully answered request when other
units are missing. All admitted passages, required scope, conditions and warnings
remain visible. Each supported unit links to its bound source bundle. Absence is
limited to the selected excerpts, not the entire Cytiva manual.

## Next deliveries and stop rules

1. **Try the walkthrough with the user.** Fix only blockers to understanding,
   navigation or correct transmission. A scope or provenance defect remains a
   release blocker; cosmetic and broader language refinements can be iterative.
2. **Make launch reproducible.** One setup/launch command, packaged runtime
   dependencies, explicit tokenizer-cache preparation and a short demo recording.
3. **Extend one useful workflow.** Add a confirmed troubleshooting use case or
   connect the reviewed records to the existing chat, keeping serving provenance
   and rollback. Do not claim a procedural lookup is a causal diagnosis.
4. **Instrument the real path.** Start with operation/timing/context counts and
   OpenTelemetry; add call/cost accounting if model calls are introduced. Ragas
   and Promptfoo follow the actual answering/attack surface rather than delaying
   this deterministic demonstration.
5. **Evaluate and broaden incrementally.** Add a small fresh holdout appropriate
   to the next behavior change. Keep original freezes/results and use new versions
   for engine changes. LightRAG/KAG, fine-tuning, full-manual extraction and a
   generalized language grammar remain separate later decisions.

Passing implementation tests establishes behavior on their fixtures, not new
prospective performance, scientific validity, GxP readiness or whole-manual
coverage. The current UI exposes documentary evidence, not generated answers.
