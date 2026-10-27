# v03 review fixes and second pre-freeze review

This record follows the [original review](FREE-TEXT-CANDIDATE-V03-REVIEW.md).
The original implementation and review reports remain historical snapshots;
their old candidate fingerprints and open-findings status are not rewritten.
This corrected candidate is still opt-in and is not a new frozen method or
prospective result.

## VR03-01: keep coordinated buffer purposes unresolved

The interpreter now detects adjacent coordinated purposes even when the second
purpose repeats the buffer noun rather than the formulation selector. The text
below is no longer reduced to a successful binding-only request:

> B : HiTrap Blue HP 1 mL. Donne les formulations du tampon de fixation et du tampon d’élution pour B.

The phrase remains an explicit unresolved fragment. `inventory_complete` and
`full_service` are false, no buffer purpose is arbitrarily chosen, and the
fragment retains its original text provenance. The same guard covers English
coordination, reversed French purposes and alternatives. It deliberately requests
clarification instead of adding automatic ellipsis expansion to the grammar.

The existing conservative policy for an unresolved substantive clause still
applies: possible dependent sibling requests can also be preblocked. Their
owners, positive units and explicit outcomes remain present. This correction
does not introduce localized partial interpretation of an unknown clause.

Explicitly repeated formulation selectors still yield distinct binding/elution
item IDs; repeating the same purpose still retains occurrence identity. A
different operating phase on a neighboring flow selector is not treated as a
second buffer purpose.

## VR03-02: retain the origin of every accepted inherited phase

When a unit falls back to the previously established phase, its prior phase
origin and a `stage` assertion are now attached regardless of phase words owned
by sibling selectors. For the original counterexample, the inherited loading
unit and both projected stage leaves refer to `Pour le chargement`; the washing
sibling retains its own local phase.

The regression checks the actual original source phrase, not a manufactured
shorter quote. It also checks decomposed Unicode input. Local phase precedence,
explicit French apostrophe phases, general pressure routing and scoped owner
handling remain covered by the compatibility tests. This provenance fix does
not invent a rule for resolving linguistically ambiguous phase ownership.

## VR03-03: reject inconsistent support and context counts

When eligible/covered sets are known, the producer now requires supported keys
to equal valid covered keys, with covered keys belonging to the eligible set.
An inconsistent producer input raises `ValueError`; it is not silently repaired
into a success claim. Public boundaries already convert assessment exceptions
into explicit error outcomes.

The numerical summary validator likewise requires equal supported/covered
counts whenever those context counts are known. It rejects the original 2/2
support with 1/1 eligible-context example, even when the full-service flag is
false. Set-level checks also catch equal-cardinality mismatched keys.

Unknown denominators remain null. Reliable sibling support can remain counted
in an error summary with unknown eligibility, and all 12 approved design
boundaries retain their specified output. FV06 still reports eligible context
1/1, whole-request support 1/3 and no full service. The legacy flag and original
frozen result retain their original meanings.

## Second review conclusion

The three original findings are addressed within the bounded grammar and the
approved coverage contract. The implementation, regression tests and source
origins were rechecked. No additional blocking issue was found within this
review's scope. The [verification record](../experiments/free-text-v03-review-fixes-checks.json)
contains the completed full-suite result, current fingerprints and preservation
checks.

The regression suite includes the original counterexamples and neighboring
cases. It exercises actual engine/bridge behavior for the language changes and
producer/validator behavior for contradictory counts, while keeping the existing
context-integrity, budget and FV development checks. These tests are development
evidence, not unseen-question performance or scientific validation.

The next checkpoint is review of this corrected candidate before a new freeze.
After a freeze, prepare new human-reviewed questions before the next prospective
comparison. The default serving interface remains unchanged. No model or paid
API is involved.
