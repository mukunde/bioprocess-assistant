# EN/FR runtime: corrected implementation review v02

This local review addresses the five findings against the initial implementation.
The GR01-GR04 approvals, schemas, common structured core, prior experiment results
and all 16 older local notes remain unchanged. No freeze or prospective S/F run
is performed by this review. See the [runtime guide](FREE-TEXT-RUNTIME-V01.md) and
[current verification report](free-text-runtime-v02-checks.json).

| Finding | Correction | Regression evidence |
|---|---|---|
| R01: positive requests disappear in a mixed request/exclusion sentence | Offset-preserving instruction segmentation processes positive requests and restrictions separately, including reverse order. Facet lookup uses the positive instruction rather than a later exclusion. | Mixed flow/endpoint restriction retains A plus C; binding formulation keeps binding use despite a later elution ban; French negated ban keeps exact code-point origins. |
| R02: restrictions widen selectors or reach unrelated preparations | Explicit selectors remain typed lists; phase-only coordinations become typed bans on the same owner. Unrepresentable restrictions retain known-owner boundaries when preblocking. | Excluding endpoints does not ban flow; A's phase bans and unrepresentable pairings leave C independently evaluable. |
| R03: incoherent ledger/projection values pass validation | Check units against request/stage assertions; check scoped facts, literal product identity and same-unit quantity lexemes. Copy assertion values to avoid shared mutable aliases. Compare projection context, ordered items, stages/selectors and active restrictions with the ledger. | Reused real origins cannot validate forged quantities/products; selector/stage mutation and projection context/exclusion mutation are rejected before the core. Invalid candidates retain their rejection audit. |
| R04: explicitly unknown column becomes absent | Parse an unknown slot, retain a column assertion with null normalized value and exact text-span origins; copy that state unchanged into the submission. | EN/FR variants distinguish `unknown` from `not_supplied`; provenance is a real citation, not a fabricated absence record. |
| R05: explicit owners applied globally across a sentence | Prefix/suffix owner associations attach to individual selectors and retain their own text spans. A conjunction separates a next-selector prefix from the previous selector's suffix. | EN/FR flow-for-A/endpoints-for-B requests dispatch separately; prefix variant works; unsupported bare coordinated owner is retained as incomplete inventory. |

## Review outcome and practical bounds

The five reproduced findings are covered by 14 new regression methods, in addition
to the original 33 IF01-IF14/conformance regression methods. These are development
controls, not held-out accuracy measurements. Each positive unit remains in
whole-request accounting; preblocking or a failed projection does not remove it.
Core attempts remain zero or one, with shared root/token limits and unchanged
E118-I/E121-EQ exclusions. Core output and projection-only flags are not rewritten.

Local verification passed **603/603 maintained tests**, including all 47 targeted
interface/review tests, with no failure, error, skip or external connection attempt.
Existing loopback socket tests account for the 33 local network operations. The
portable structured-package verifier passed without repeating its trial. Original
33-test source, all previously tracked artifacts and the 16 old notes are unchanged.

No remaining blocker was reproduced within these five reviewed boundaries.
The candidate is suitable to submit for a separately requested freeze after human
review of this correction. This is not a claim of universal EN/FR understanding,
scientific suitability or unrestricted support for arbitrary constructions.

Remaining planned work is unchanged: P/G text/form equivalence review, a new
human-reviewed prospective paired dataset after freeze, and a separately reviewed
serving integration. The internal preclassified-ledger and fault-injection tests
remain distinct from caller-input interpretation. Historical v01 checks retain
their recorded hashes and results; the current v02 report binds the corrected
source files. No old experiment or human decision is overwritten.
