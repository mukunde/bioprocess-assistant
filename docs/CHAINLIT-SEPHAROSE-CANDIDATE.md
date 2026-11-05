# Rising backpressure: Protein A/G Sepharose candidate

This separate, model-free documentary adapter reuses the already reviewed Q01–Q04
and Q09 sources on Cytiva PDF pages 166–167. It is a **staged candidate awaiting
review**, not an activated release, scientific approval or operational procedure.
It does not modify the private MabSelect registry or either frozen runtime.

## Prepare a separate candidate

Use the existing development/verification environment at the repository root:

```powershell
.\.local-tools\verification-venv\Scripts\python.exe -m serving.sepharose_candidate --output .local-tools\sepharose-backpressure-candidate-v02 --release-id sepharose-backpressure-candidate-v02
```

The standard-library preparation command creates three files in a new directory:
`release.json`, `sources.json` and `mapping.json`. It never overwrites an existing
candidate, writes an active pointer, adds an approval or installs/downloads anything.
Known private authority roots and their ancestors/descendants are refused as
output locations. Source/review records and relevant code are pinned with LF-
normalized hashes. The reviewed cleaning package identity and its existing
verifier anchor the original evidence and literal human decisions. Candidate
source/mapping material is compared with that expected material on lookup; jointly
editing a quote and its local artifact digest cannot approve an invented quote.

Prepare only after code changes are complete. If pinned dependencies change,
prepare a new candidate directory/version explicitly; the service never repairs,
refreshes hashes, activates or silently regenerates an old candidate.

## Inspect in Chainlit, without activation

Configure the same local login and signing secret as the
[MabSelect Chainlit guide](CHAINLIT-MABSELECT.md), then select this **separate mode**:

```powershell
$env:BIOPROCESS_MODE = 'sepharose_candidate'
$env:SEPHAROSE_CANDIDATE_ROOT = (Resolve-Path .local-tools\sepharose-backpressure-candidate-v02).Path
.\.local-tools\verification-venv\Scripts\python.exe -m chainlit run app.py --host 127.0.0.1 --port 8788
```

Use [localhost:8788](http://127.0.0.1:8788/). Every candidate response/source view
displays **CANDIDATE ONLY — NOT ACTIVATED**. Missing/invalid candidate data refuses
support with a manual retry; there is no preview fallback to the active MabSelect
registry. `Candidate(root)` refuses delivery by default: only an explicit server-
selected `preview=True` workbench reads staged results. Browser settings cannot
select the root, enable preview, approve material or activate anything. The
application has no new activation API. The ordinary graph and MabSelect modes
remain available separately, with their existing behavior.

1. Leave product/context unknown: clarification, no selected recipe or diagnosis.
2. Choose Protein A or Protein G Sepharose and explore precipitated/denatured
   proteins: retain the original two-step quotation, immediate follow-up and
   reservations. No contact time or flow is added from the MabSelect page.
3. Explore hydrophobic proteins/lipoproteins/lipids: the detergent example and
   ethanol alternative stay separate. Ethanol cannot be supplied without its
   pressure precaution. A context selection is not a confirmed deposit diagnosis.
4. Ask for numerical maximum pressure: scoped abstention, no invented number or
   transfer from another product. This is a limitation of the selected candidate,
   not a declaration that the entire manual contains no pressure information.
5. Select MabSelect: outside this Protein A/G candidate, no Sepharose recipe
   transfer and no inferred incompatibility. Use its own reviewed route instead.
6. Open a source: original quote, PDF page, printed page label, page offsets/text
   digest, PDF identity and full scoped human decisions are retained. The PDF is
   not redistributed. Source actions recheck candidate integrity and dependencies.

On Windows, the preview checks the path Chainlit would use for a provenance
attachment. If it reaches the legacy Windows path limit, the source response
includes the same provenance as inline JSON. Short paths still use the Chainlit
attachment.

Text input only explains the guided controls; no model or free-text lookup runs.
Legacy extraction-level `pending` source flags remain verbatim in provenance;
the separate Q01–Q04/Q09 decisions establish only their specific documentary
review scopes. They do not turn the original source flags into universal approval.
Changes invalidate old actions. Late results are discarded; 15-second waits have
manual retry. Internal error details are not shown. Already displayed messages
are historical snapshots and cannot be recalled. The inherited Chainlit shell,
authentication and upload icon are not a public-deployment hardening claim.

## Withdrawal simulations and remaining gate

Preparation can build a *different* candidate using server-side
`withheld_sources`/`withheld_reviews` arguments. These conservative simulations
only remove support; they do not grant publication authority. Withholding E166-W
or Q04 removes the complete ethanol option and its quotation while retaining the
independent detergent option. Withholding the Q01 pressure indication blocks the
dependent pressure-journey options. Shared headings may remain available under
other complete review scopes; a procedural quote never survives a missing warning.

Each displayed summary belongs only to its eligible review scope. Q01 supplies
the cleaning indication; Q09 supplies clarification or product separation. A
withdrawn scope cannot survive inside another scope's combined summary. With
Q01 held and Q09 available, an unknown context still requires clarification;
the UI retains the supplied product and separately identifies held review scopes.
When Q09 itself is held, it supplies no clarification summary. Shared source
provenance remains available only under another complete eligible scope.

The corrected local preparation uses a new `v02` directory and release ID. The
previous `v01` artifacts are preserved; their old code pins now fail closed.
Neither directory is a frozen runtime or activated release. See the
[corrected review](validation/SEPHAROSE-CANDIDATE-CORRECTIONS.md).

Simulation lists are immutable candidate inputs, not a live approved withdrawal
feed. Modifying an already opened candidate invalidates it rather than partially
repairing it. There is **no durable cross-restart revocation authority or activation
workflow for this new scope yet**. Review the candidate, its mapping and tests
before designing/authorizing that transition. Do not insert synthetic approvals
or this candidate into the active private MabSelect root.

## Tests

```powershell
.\.local-tools\verification-venv\Scripts\python.exe scripts/run_tests.py --temp-root $env:TEMP tests.test_sepharose_candidate tests.test_chainlit_sepharose tests.test_chainlit_mabselect tests.test_app tests.test_registry_tracing
```

These known-source conformance/regression checks use temporary candidate folders,
real service lookups and captured Chainlit transport. They do not constitute a new
independent retrieval benchmark or scientific validation. See the
[implementation and verification report](validation/SEPHAROSE-CANDIDATE-IMPLEMENTATION.md).
The tracing test fixture waits for HTTP-handler completion before flushing the
exporter, so it cannot inspect a parent span that has not ended yet. This is test
synchronization; production tracing and request deadlines are unchanged.
