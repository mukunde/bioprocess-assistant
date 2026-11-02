# Local activation review — MabSelect registry v02

Prepared on 2 November 2026 against merged `main` at `ef58f0f` (PR75).
**Awaiting human review. No activation or withdrawal approval is recorded.**
This document and its [machine-readable inventory](MABSELECT-REGISTRY-V02-ACTIVATION-REVIEW.json)
are review material, not registry authority. No activation decision file is
created. Reviewing this proposal and executing activation are separate actions.

## Exact candidate

- Release: `mabselect-local-v02`, currently `staged`, mode `local_opt_in_no_model`.
- Staged authority digest: `3aa0d8c42e4ba61d3964979196bc7d5d593db6392624c743e2205e3b4a1c87e5`.
- Six release artifacts: release, catalog, mapping, source index, withdrawals and
  proposed withdrawal decision. Their exact LF SHA-256 hashes are in the inventory.
- 56 bound dependencies: 52 original handoff-freeze files, its lock, the two
  registry Python files and catalog. Five original scoped reviews: Q05, Q06,
  N06, N07 and Q09. Their original wording and reservations remain authoritative
  for documentary fidelity only.
- Request limits: 32,768 bytes, eight tasks; context limit: 65,536 bytes. Byte
  limits are not token budgets and do not authorize dosage calculations.
- Both freezes remain unchanged: v03 (36 pins) and MabSelect (52 pins).

The [versioned release](../../serving-data/releases/mabselect-local-v02/release.json)
and [source index](../../serving-data/releases/mabselect-local-v02/source-index.json)
remain staged. Their sources are selected excerpts from printed pages 166–167;
PDF page identities and source-object/quote hashes are retained in the inventory.
The original v01 remains historical, not a fallback release.

## Authorized documentary scope proposed for review

| Scoped review | Product/context | Allowed role and limits |
|---|---|---|
| Q05 | Plain MabSelect, SuRe, SuRe LX; precipitated substances | General block: four separate alternatives and immediate follow-up buffer wash. Preserve conditions and quantities verbatim; no automatic alternative choice. |
| Q06 | SuRe and SuRe LX only; precipitated substances | Separate restricted three-step sequence. Do not transfer it to plain MabSelect or imply guaranteed reuse. |
| N06 | Plain MabSelect, SuRe, SuRe LX; hydrophobic deposits | Nonionic-detergent alternative; 0.1% is an example. Follow-up pH belongs to the subsequent buffer wash. |
| N07 | Same products/context as N06 | Separate organic-solvent alternatives, their holding condition and pressure warning. Do not invent a solvent volume, flow or numerical pressure. |
| Q09 | Unknown, mixed, contradictory or otherwise insufficient product/context | Context for clarification only. Its broader product/context list does not authorize a cleaning recipe or extend applicability. |

The thirteen exact IDs are `E166-H`, `E166-LH`, `E166-PH`, `E166-T`,
`E167-D`, `E167-E`, `E167-H`, `E167-LH`, `E167-P`, `E167-PH`, `E167-S`,
`E167-SH`, `E167-W`. Required groups stay atomic; withdrawn required support
holds its dependent scopes. Independently valid tasks and essential warnings
must remain intact. Current withdrawal authority also governs old source views.
No quotation should be returned from a source view with no eligible scope.

No new source approval, numerical inference, operational suitability, scientific
validation, whole-manual coverage or generated-answer quality is established.
E118-I and E121-EQ remain excluded; their absence from this inventory is not a
withdrawal/reinstatement event. All original reservations remain in effect.

## Decisions to review together

All choices below are **proposals**. No original human approval message is filled.

| ID | Choice | Proposed boundary |
|---|---|---|
| LA01 | Exact candidate | Review mabselect-local-v02 with the recorded staged authority digest, six release artifacts and 56 dependency bindings; preserve v01 as historical. |
| LA02 | Local scope | One configured private local authority root, one cooperating writer process, no model, paid API, HTTP exposure, UI dispatch or legacy-chat change. |
| LA03 | Allowed support | Only the five registered bundle purposes and thirteen exact source objects; Q09 provides clarification context, not a cleaning procedure. Preserve conditions, warnings, alternatives, quotations and reservations. |
| LA04 | Initial withdrawals | Explicitly approve version 1 with zero events if still appropriate. This is no additional withdrawal within this bounded release, not approval of all manual content or release of E118-I/E121-EQ. |
| LA05 | Failure and revocation policy | Unavailable on invalid global authority; hold scopes dependent on withdrawn support, preserve independent tasks and essential warnings. Source views use current withdrawal authority; drift discards results without fallback. |
| LA06 | Storage and recovery limits | Accept trusted local storage and pointer-only rollback detection. Whole-store rollback, multiple writers and malicious tampering need stronger external controls. Interrupted commit requires reviewed manual recovery; no automatic rollback. |
| LA07 | Post-approval execution | A later explicitly requested action may prepare approved decision records in the private runtime copy, preserve the exact human approval text, recompute consequential bindings and activate only the approved semantic scope. Keep staged versioned files and both freezes unchanged. |
| LA08 | Acceptance and stop conditions | After later activation, replay accepted cases and verify normal reads/citations, both freezes, head/pointer equality and unchanged protections. Lifecycle fault/withdrawal tests run in disposable copies; fail closed on any mismatch, never change the live register merely to test it. |

## Initial withdrawals and later changes

Proposed initial inventory: `mabselect-local-v02-withdrawals-v01`, version 1,
**zero events**, decision status `proposed`. An empty register is explicit; a
missing/unreadable one is invalid authority. Approving it means no additional
withdrawal recorded for this bounded release at activation time, not a guarantee
that the sources can never require withdrawal.

Each later event must name the exact target release, bundle/review/source and
canonical object hash, with a reviewed reason and decision. Earlier events stay
in order; reinstatement needs a prior withdrawal and a new reviewed version.
An old-edition withdrawal is not automatically promoted to every newer edition.
Do not edit an active inventory in place or drop history to clear a withdrawal.

## Proposed execution boundary after review

Use a separate ignored root, `.local-tools/mabselect-registry-v02-runtime`, with
an explicit server-side configuration. It does not exist yet. Preserve the
versioned staged directory, old replays and both freezes; do not silently change
`serving-data` or any existing preview/launcher to point at it. No HTTP route,
public host, UI dispatch, legacy chat connection or automatic startup is included.

After a later explicit activation instruction, copy the reviewed release into
that private root; record literal human approvals for the empty inventory and
activation, then recompute affected inventory/decision/manifest bindings in the
required order. The final activated manifest/digest will differ from the staged
digest above because approval references and stage change. Preserve an exact
before/after record; these metadata changes must not change sources, mapping,
limits, code or reservations. Any substantive drift requires renewed review.
The current internal activation method requires already approved artifacts;
there is no CLI activation or approval writer. Do not bypass its validation.

Activation appends the durable head before replacing the active pointer. Verify
both identities and replay SX01–SX06 through active evaluation and citation views.
Use disposable copies for withdrawal, drift and crash simulations; no synthetic
withdrawal should be introduced into the real register to demonstrate a test.
The existing complete suite on PR74 passed 895 tests with one optional skip;
PR75's documentation checks passed 20 tests. These are historical checkpoints.

## Recovery limits and stop conditions

| Observed situation | Required behavior / operator action |
|---|---|
| Before any durable head is committed, no active pointer exists | Remain inactive. Keep any partial attempt for diagnosis; retry only after validating the approved artifacts and unchanged inputs. |
| New valid head exists but pointer is absent or older after interruption | Requests remain unavailable. Stop writers; preserve the full directory and logs. Verify the entire chain, latest approved release and withdrawal history. Prepare a separately reviewed recovery to that latest authorized head; no old-pointer rollback or blind second activation. No recovery command is supplied. |
| Head/pointer/artifacts missing, corrupt or inconsistent | Fail closed; preserve evidence and stop serving. Reconstruct only from independently trusted complete evidence with explicit operator review, never infer an empty register or delete the journal to restart. |
| Old pointer restored while newer valid head remains | Refuse the old authority, including after restart; retain withdrawals. Restore only via the reviewed recovery process above. |
| Entire trusted directory and journal replaced by an older backup | Current code cannot reliably detect this. An independent external anchor is required; an old backup is not automatically safe to serve. If rollback cannot be ruled out, keep the service unavailable. |
| Multiple independent writers or malicious edits | Outside the supported trust model. Do not activate in that setting without a stronger design. Hashes detect drift; they do not prove who approved. |

The initial scope is one trusted local machine/directory with cooperating
single-process writers. No automatic rollback, data loss recovery guarantee,
cryptographic signatures or protection against a privileged local attacker is
claimed. A later UI connection must preserve these failure outcomes and never
fall back to unsourced prose.

## Readiness observed during preparation

A fresh candidate-only replay passed SX01–SX06 and matched the preserved v02
output exactly, with zero socket attempts, LLM calls or paid API calls. Both
freeze/environment verifiers passed unchanged. The register remains inactive:
no real `active.json`, authority journal, approved withdrawal decision or
activation decision was created. Notes and pilots remain untouched.

See [the registry guide](../../serving/README.md) and
[review corrections and limitations](../validation/MABSELECT-LOCAL-REGISTRY-REVIEW-FIXES.md).
