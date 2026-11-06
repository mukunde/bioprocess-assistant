# Sepharose local activation review

Decision pending. The Protein A/G Sepharose candidate is staged for local
preview. This review proposes the scope and safeguards for a future local
documentary release. The current implementation has no activation API or
durable withdrawal authority for Sepharose.

## Candidate and evidence

| Check | Evidence |
| --- | --- |
| Exact candidate | `sepharose-backpressure-candidate-v03` uses the runtime from merge `c46215b`. The read-only check at `a6a9844` verified all 16 dependency pins, the source and mapping artifacts, and 12 source excerpts. Canonical snapshot SHA-256: `96fcbdadb78aa03d1e6749627b6f19a151b3fb99ddc560faa3fa02dbfe21a61d`. |
| Current gate | The release declares `staged`, `not_authorized`, and `awaiting_user_review`. The initial simulation lists are empty. Without explicit preview, both a valid Protein G request and the E166-P lookup returned unavailable. |
| Documentary review | Q01–Q04 and Q09 bind the original quotations, scope, conditions, and reservations on Cytiva PDF pages 166–167. [Cleaning review](../../experiments/cytiva/reviewed-cleaning-retrieval/README.md) |
| Known-case acceptance | All seven cases passed the corrected Chainlit replay on disposable data. This covers exact product scope, clarification, numerical pressure abstention, citation provenance, and simulated withdrawals. Long Windows paths returned inline provenance and the short-path E166-P check used an attachment. [Replay results](SEPHAROSE-CHAINLIT-WINDOWS-PATH-REPLAY.md) |
| Browser evidence | The continuous recording shows one fresh Protein G path and opening E166-P with inline provenance. Public playback from the README reached the end. [Recording review](../../media/chainlit-sepharose-continuous/REVIEW.md) · [Publication record](../CYTIVA-VIDEO-HOSTING.md#published-chainlit-sepharose-video) |

The replay tested known cases against the corrected implementation. The browser
recording covers one route. A future release needs a targeted check of the
actual activation, durable withdrawal, and rollback paths once those exist.

## Decisions for review

| ID | Proposed decision |
| --- | --- |
| SA01 | Authorize design for one separate local documentary release, bound to the exact reviewed snapshot. Keep the current candidate staged while implementing and testing the release gate. Require a separate decision before enabling service. |
| SA02 | Limit serving to guided Chainlit on loopback and to Protein A Sepharose and Protein G Sepharose for rising backpressure. Preserve Q01 cleaning indication, Q02 for precipitated or denatured proteins, Q03 detergent example, Q04 ethanol alternative with its warning, and Q09 clarification or product separation. Keep the alternatives separate. |
| SA03 | Ask for the missing product or context before selecting an option. Abstain on numerical pressure limits within the reviewed excerpts. Preserve conditions, reservations, and source provenance. The document does not establish the cause or authorize laboratory use. |
| SA04 | Keep the release authority separate from the private MabSelect registry. Start with an explicitly reviewed empty withdrawal inventory only if no actual withdrawal is outstanding. Bind the inventory and the approval to the exact release, and record changes durably across restart. |
| SA05 | Withdraw by source or reviewed scope. A missing required source blocks its dependent bundle and citation actions. E166-W or Q04 blocks the ethanol option and its quote. Q01 blocks dependent pressure-journey options. Independent Q09 clarification can remain when its own sources and review are eligible. |
| SA06 | Recheck authority and withdrawals when answering and when opening a citation. Invalidate stale actions and discard late results after authority changes. Already displayed messages, downloaded attachments, and public recordings remain historical copies. |
| SA07 | Roll back to disabled serving if the authority is missing, inconsistent, or no longer approved. Record the disable decision in the separate local authority, stop serving, and verify that new requests and old citation actions cannot retrieve the release. Re-enable a prior version only after verifying it against current withdrawals and obtaining explicit approval. |

## Evidence required before enabling service

1. Exercise activation refusal for missing approval, a mismatched snapshot, and
   a missing or invalid inventory.
2. Exercise an approved disposable release, then withdraw E166-W and Q01 in
   separate cases. Verify blocked output and stale citation refusal after restart,
   with independent clarification and detergent guidance retained where eligible.
3. Disable the disposable release, restart, and verify refusal without fallback
   to another registry or an older release. Confirm the existing MabSelect route
   is unaffected.
4. Bring the results and exact release inventory back for the activation
   decision. [Candidate guide](../CHAINLIT-SEPHAROSE-CANDIDATE.md)

## Recorded design decision

The project user approved SA01–SA07 and their clarifications on 6 November
2026, with the project user as initial validator. This decision authorizes
implementation and disposable testing. A separate explicit serving decision
and an approved inventory are required for the real release.

> Je valide SA01–SA07 et tes clarifications, avec moi comme valideur initial. Enregistre mes décisions, puis implémente le mécanisme local et teste les retraits et le retour arrière sur données jetables. Aucune activation, aucun commit ni push.

## Local mechanism

The separate Chainlit entry point, `demo/chainlit_sepharose_local.py`, requires
a loopback listener, local sign-in, an explicit candidate path, and a separate
`SEPHAROSE_LOCAL_AUTHORITY` database path. A missing or disabled authority
returns unavailable. The original preview and MabSelect entry points keep
their existing configuration.

A trusted local operator uses `Authority.initialize()` to create an empty
database and `Authority.record()` to append a decision. Every decision binds
the exact candidate snapshot, the designated validator, and the verbatim
approval. An enable or inventory change requires both lists explicitly,
including empty lists. Disable preserves the latest inventory. Re-enabling
the same snapshot requires a new approval and retains outstanding withdrawals.
A different snapshot needs a separate authority and review.

SQLite stores the history and its current head in the same transaction. The
serving process reads it without write access. Keep the database in an
operator-controlled directory, away from public or shared storage. The
validator field records the source of the decision. It is not a cryptographic
signature. Replacing the database and its head with an older backup is outside
this trust boundary and must never be used as rollback.

Citations carry the authority generation that issued them. A subsequent
withdrawal, disable, or re-enable invalidates older actions. Chainlit returns
provenance inline, under the same authority check. For rollback, record a
disable decision and stop the dedicated listener. After restart, verify that a
new request and any prior citation reference return unavailable.

To inspect the separate UI with a disposable database, set
`SEPHAROSE_CANDIDATE_ROOT` to a disposable candidate and
`SEPHAROSE_LOCAL_AUTHORITY` to its separate authority database. Configure
local login as described in the [MabSelect Chainlit guide](../CHAINLIT-MABSELECT.md).
Then run this from the repository root:

```powershell
.\.local-tools\verification-venv\Scripts\python.exe -m chainlit run demo/chainlit_sepharose_local.py --host 127.0.0.1 --port 8789 --headless
```

This command starts the listener. Serving requires a separate recorded enable
decision. The real candidate and the private MabSelect registry were outside
the write scope of the disposable tests.

## Disposable browser replay

On 6 November 2026, a dedicated loopback Chainlit instance used a disposable
candidate, SQLite authority, and synthetic sign-in. The browser exercised the
actual settings, request, and citation actions.

| Step | Observed result |
| --- | --- |
| Open citations before withdrawal | E166-P and E166-W opened on PDF page 166 with the passage and inline provenance. E166-P retained Q02; E166-W retained Q04 and the pressure precaution. |
| Withdraw E166-W | The previous E166-W button returned unavailable. A new response held Q04 and issued neither E166-W nor E166-E. E166-D still opened for the detergent option. |
| Disable serving | The previous E166-D button and a new request both returned unavailable. |
| Restart Chainlit | A new server process reopened the same disposable authority. A fresh browser session returned unavailable with no procedure or citation buttons. |

The browser exercised the old buttons before restart. The fresh session after
restart had no old buttons to click. Earlier responses remain historical
snapshots. The server was stopped and the disposable database was removed.
The three files of the real staged candidate retained their original bytes.

The automated tests also cover approval and snapshot mismatch, invalid
inventory, a withdrawal during evaluation, damaged authority history,
and refusal to re-enable while dropping outstanding withdrawals.
See [test cases](../../tests/test_sepharose_local.py).
