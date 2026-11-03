# Reviewed MabSelect UI acceptance UA01-UA08

Eight human-validated references were exercised once each through the baseline UI
on 3 November 2026. **Eight functional outcomes passed; no critical failure was
detected in this bounded set.** Three noncritical display findings remain in this
historical trial; the opt-in UI v02 is a separate dependent lot, not a retuned rerun.

[Questions and initial proposal](../registry-ui-acceptance-v01/README.md),
[current human decisions](../registry-ui-acceptance-v01/review.json) and
[completed review status](../registry-ui-acceptance-v01/REVIEW-STATUS.md) are preserved.
The proposal README and reference status strings intentionally describe preparation;
review.json and REVIEW-STATUS.md are authoritative for completed human decisions.

[Observations](observations.json) contain the eight actual requests/responses and
visible outcomes, plus thirteen opened source quotations, provenance and original
scoped review records. The compact export is parsed from unchanged local HTTP
captures, not a new run or synthetic expected-answer output. [Results](results.json)
retain 216 per-case checks and 91 source checks. [Provenance](provenance.json) binds
the raw local captures by hash without publishing them or private path inventories.

[Assessment history](assessment-history.json) preserves the initial checker and
corrected result objects. An initial checker wrongly required procedural keys for
Q09 clarification refs. Its correction follows the unchanged baseline contract:
clarification context can have refs while procedural keys remain empty. No input,
reference, response or case execution was replaced or repeated.

## Historical findings

- UA08 has the correct outside-release structured reason but generic visible
  absence/numerical wording, including for cleaning.
- UA05-UA07 repeat clarification text; UA05 repeats the same action for two items.
- UA04 repeats the full solvent passage already present in its steps. Both distinct
  precautions, quantities and original source wording remain intact.

## Offline verification

```powershell
python experiments/cytiva/reviewed-registry-ui-acceptance-v01/verify.py
python scripts/run_tests.py --temp-root "$env:LOCALAPPDATA\Temp" tests.test_registry_ui_acceptance_package
```

The verifier uses the standard library and preserved artifacts, with no browser,
network, registry access, API or model. [Verification](verification.json) records
its result. This checks export integrity and documentary response invariants;
it does not repeat the original browser test or establish new acceptance metrics.

No withdrawal was introduced into the private authority. Withdrawal/deadline
regressions remain separate development evidence. Known evidence and guided input
combinations are not a blinded retrieval benchmark or scientific validation.
No numerical latency claim, operational permission, suitability judgment or
whole-manual absence follows. E118-I/E121-EQ remain excluded. Original runtime,
registry, two freezes, sixteen old notes and pilots remain unchanged.
