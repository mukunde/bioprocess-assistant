# Sepharose acceptance in Chainlit

On 5 November 2026, all seven cases passed on revision `85bf82e`.
The [plan](plan.json) records the expectations fixed before execution.
The [results](results.json) record the exact citation sets and checked
attachments. The candidate remains staged and non-activated.

## Cases and outcomes

| Case | Request or simulated withdrawal | Observed outcome |
| --- | --- | --- |
| S01 | Unknown product, hydrophobic context, and a pressure request | Asked for the exact product, declined to give a numerical pressure limit, and returned context citations. |
| S02 | Protein G, precipitated proteins, and a pressure request | Preserved the Q02 sequence, declined to give a numerical pressure limit, and opened E166-P with Q02 provenance. |
| S03 | Protein G and hydrophobic deposits | Kept the detergent and ethanol options separate and opened E166-W with the lower-flow warning and Q04 provenance. |
| S04 | MabSelect, precipitated proteins, and a pressure request | Reported the product outside scope and declined to give a numerical pressure limit. No procedure transferred. |
| S05 | Protein A with E166-W withheld | Held the ethanol option and its citations. Kept the detergent option and opened E166-D with Q03 provenance. |
| S06 | Protein A with Q01 withheld and context unknown | Kept clarification and pressure abstention. Rejected an old citation action after a settings change. |
| S07 | Protein A with Q03 withheld | Held the detergent option. Kept the ethanol option with its warning and opened E166-W with Q04 provenance. |

Each case used a separate disposable candidate and synthetic login.
The client exercised the authenticated Chainlit Socket.IO and HTTP actions
over loopback. It checked all citation sets and opened four provenance
attachments. Each opened attachment retained the page, quotation hash,
extracted text offsets, PDF identity, and scoped review. All seven candidate
directories retained their file bytes. A service call without preview
returned an unavailable status.

## Windows attachment failure

The first run returned the source message but could not attach the provenance
file under a deeply nested Chainlit root. A direct write to the disposable
session directory reproduced `FileNotFoundError` at a path length of 282
characters. A short temporary Chainlit root restored attachment delivery.

The intermediate run reached the attachment event but used the wrong download
route in the test client. The final run fetched the attachment through the
authenticated session endpoint. Both retries used the original case plan and
application code. The earlier case statuses and evidence digests are retained
in the results.

Use a short Chainlit root for Windows validation while this issue is open.
Treat the result as acceptance of the tested server behavior. Browser layout,
accessibility, scientific suitability, and an activation decision have their
own checks. See the [candidate guide](../../CHAINLIT-SEPHAROSE-CANDIDATE.md).
