# Sepharose replay on long Windows paths

The corrected Chainlit preview passed all seven cases from the
[original acceptance plan](sepharose-chainlit-acceptance-v01/plan.json).
The replay used the working changes based on `6981322`, with a separate
disposable candidate and synthetic login for each case.

## Replay results

| Case | Observed outcome | Result |
| --- | --- | --- |
| S01 | Unknown product prompted clarification and a separate pressure refusal. The response returned the expected context citations. | Pass |
| S02 | Protein G kept the Q02 sequence and refused a numerical pressure limit. E166-P opened with Q02 provenance. | Pass |
| S03 | Protein G kept the detergent and ethanol options separate. E166-W opened with the lower-flow warning and Q04 provenance. | Pass |
| S04 | MabSelect remained outside scope. The response refused a numerical pressure limit and supplied no transferred procedure. | Pass |
| S05 | Withholding E166-W blocked the ethanol option. The detergent option remained available and E166-D opened with Q03 provenance. | Pass |
| S06 | Withholding Q01 preserved context clarification and pressure refusal. The old citation action expired after the settings changed. | Pass |
| S07 | Withholding Q03 blocked the detergent option. The ethanol option retained its warning and E166-W opened with Q04 provenance. | Pass |

## Provenance delivery

Chainlit would have written the four opened provenance attachments to paths
of 292 UTF-16 code units. The preview returned the same provenance JSON in
each source message. The checks covered the quotation hash, page number,
extracted text offsets, PDF identity, and scoped review. Each response retained
the non-activation notice, and all candidate file hashes matched their
pre-run values.

A separate replay of S02 on a short Windows path downloaded E166-P through
Chainlit's authenticated attachment endpoint. The 66 targeted regression
tests passed, including the path boundary and the inline provenance response.

The replay exercised authenticated Chainlit server events and actions on
loopback. The [original acceptance record](sepharose-chainlit-acceptance-v01/README.md)
covers the earlier Windows failure. See the
[candidate guide](../CHAINLIT-SEPHAROSE-CANDIDATE.md) for preview setup.
