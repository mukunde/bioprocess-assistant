# v03 pre-freeze implementation review

Status: **changes required before freeze**. Review performed on 27 October 2026.
No implementation, schema, freeze, reference or historical result was edited.
The review uses deterministic local execution only.

## Findings

### VR03-01 — P1: a coordinated buffer purpose can disappear with full service

Location: `ingestion/free_text_interpreter_v03.py:124` (purpose selection and
coordination check), and the phase-consumption check at line 419.

Reproduction:

> B : HiTrap Blue HP 1 mL. Donne les formulations du tampon de fixation et du tampon d’élution pour B.

Actual: one positive unit, `B-buffer_preparation-binding-1`,
`inventory_complete=true`, `full_service=true`. The elution formulation is not
requested from the core. The coordination guard only catches a short conjunction
between use tokens; it misses `et du tampon d’`. The final phase check consumes
the elution word as a buffer-purpose phrase, so it does not mark an incomplete
inventory either.

The fully repeated wording (`les formulations du tampon de fixation et les
formulations du tampon d’élution`) correctly yields two distinct items. Existing
tests cover this fully repeated spelling and a shorter ambiguous coordination,
but not the omitted repeated noun phrase above.

Required: either represent both explicit purposes as distinct positive
occurrences with focused origins, or retain an explicit unresolved fragment and
prevent a complete-service claim. Do not select one purpose silently. Add EN/FR
coordination and mixed-task regressions, preserving distinct/repeated item IDs.

### VR03-02 — P2: an inherited French phase loses its supporting origin

Location: `ingestion/free_text_interpreter_v03.py:380`.

Reproduction:

> B : HiTrap Blue HP 1 mL. Pour le chargement. Donne le débit et les critères de fin du lavage pour B.

Actual: the first unit inherits `sample_application` from the earlier context;
the second explicitly uses `washing`. Both are supported and full service is
true. However, the first unit's origins contain only `B :` and `débit`, its
assertions contain no `stage`, and both projected stage leaves link only to
those same origins. The source span `chargement` exists but is not attached.

The fallback assignment at line 375 can use `current_phase`; its provenance is
only copied when the entire clause has no phase tokens. A different selector's
explicit `lavage` makes that condition false. This finding concerns the missing
provenance, independent of whether a reviewer accepts the inherited reading or
prefers clarification of the coordinated wording.

Required: whenever an inherited phase is accepted, attach its actual prior
phase origin and stage assertion regardless of phases belonging to siblings.
If ownership remains ambiguous, clarify instead. Assert the selected phase's
origin and projected field origins, not merely valid substring offsets.

### VR03-03 — P2: coverage validation accepts support outside eligible context

Location: `ingestion/coverage_v03.py:31` and `:58`.

Deterministic reproduction:

```python
summary = summarize(
    ['a', 'b'], ['a', 'b'],
    supported_keys=['a', 'b'],
    eligible_keys=['a'], covered_keys=['a'],
)
validate_summary(summary)  # currently accepts
```

Actual: eligible coverage is 1/1, whole-request support is 2/2 and full service
is true. Unit `b` is counted as supported without belonging to the eligible set
or having covered context. The producer checks `covered <= eligible` and
`covered <= supported`, but not the support-to-eligibility/context relationship;
the numeric validator has the corresponding gap.

The normal core/bridge currently supply `covered_keys=supported_keys`, so this
is a contract-validation hole exposed by a synthetic inconsistent input, not an
observed ordinary engine output. It still weakens the claimed defensive boundary.

Required: reject impossible known-set relationships and contradictory summaries,
including any complete-service claim with known uncovered/noneligible supported
units. Preserve null denominators and valid sibling counts in error cases;
do not repair contradictions by silently filtering requested units. Add positive
and negative boundary tests to both the producer and summary validator.

## Checks that passed and limits

- The 70 v03 targeted tests were rerun: zero failures, errors, skips or external
  connection attempts. The earlier full-suite result of 751 passing tests is
  preserved; the full suite was not rerun for this review.
- FV06 separates eligible context 1/1 from whole-request support 1/3 and keeps
  full service false. Budget rejection stays in the pre-assembly denominator.
- Explicit/repeated buffer occurrences have distinct IDs; focused formulation
  facets work for the currently tested repeated-selector grammar.
- The tested local French apostrophe phases, washing stopping criteria and
  unqualified pressure cases pass. Some additional constructions fail closed
  with incomplete inventory; this is a bounded grammar, not arbitrary French.
- The preservation audit checks all 608 baseline files, both historical method
  locks and run fingerprints, the 16 older notes and the implementation hashes.
  See the [review verification record](../experiments/free-text-v03-review-checks.json).

The counterexamples are development material. They do not replace frozen scores
or create a new prospective evaluation. After fixes, rerun regressions and the
complete suite, review the candidate again, then consider a new freeze and fresh
human-reviewed questions.
