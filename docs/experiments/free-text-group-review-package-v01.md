# GR01-GR04 reviewed design package

Date: 26 October 2026. Local preparation on main at `7306478df374ca5f0cce2c6313599fda8e5481be` (PR #43). This checkpoint supersedes the pending-group status of the historical [design package](free-text-design-package-v01.md).

## Outcome and reservations

All four groups are human-validated with reservations: GR01 six examples, GR02 four, GR03 four, GR04 two plus three invalid caller inputs. The four original French approval messages remain verbatim in separate decision records bound to canonical example, condition and origin hashes.

- E08 retains the complete intended-application condition at [27,92); its normalized false value is unchanged.
- E03 explicitly supports washing with “Pour le lavage” at [64,78), linked to the stage assertion and fields. Ownership remains unresolved between A and B.
- Keep ambiguous ownership, conflicts, exclusions and partial/incomplete accounting explicit. Observations are not operating prescriptions; absence is limited to the admissible corpus.
- E04 starts from caller input. E05/E12/E13 are preclassified-ledger bridge fixtures, not language gold labels inferred from ordinary text.
- E11/E16 use external fault injection, not example-ID routing. Preserve rejected candidates, hashes and validation errors; never silently repair or submit them.
- N01-N03 reject blank text, source-approval fields and unsupported language before interpretation. E118-I/E121-EQ remain excluded.

The example file stays at revision 4. Its per-example pending markers are historical schema-required preparation fields; current approval status is recorded in the group decisions and comparison metadata.

## Exact proposed files (15)

- `docs/experiments/free-text-interface-examples-v01.json`
- `docs/experiments/free-text-interface-group-review-v01.md`
- `docs/experiments/structured-free-text-comparison-v01.json`
- `docs/technical/FREE-TEXT-MACHINE-DESIGN-V01.md`
- `docs/decisions/2026-10-26-free-text-GR01-review.json`
- `docs/decisions/2026-10-26-free-text-GR02-review.json`
- `docs/decisions/2026-10-26-free-text-GR03-review.json`
- `docs/decisions/2026-10-26-free-text-GR04-review.json`
- `docs/technical/free-text-machine-design-checks-v03.json`
- `docs/technical/free-text-machine-design-checks-v04.json`
- `docs/technical/free-text-machine-design-checks-v05.json`
- `docs/technical/free-text-machine-design-checks-v06.json`
- `docs/technical/free-text-machine-design-checks-v07.json`
- `docs/experiments/free-text-group-review-package-v01.md`
- `docs/experiments/free-text-group-review-package-v01.json`

## Controls and provenance

The [package manifest](free-text-group-review-package-v01.json) binds the other 14 files using SHA256 with CRLF normalized to LF; it deliberately does not hash itself. Historical v03-v06 reports and decisions remain unchanged. The current v07 report reruns offline checks against the final documentation and examples. Earlier reports describe their recorded snapshots, not the final document bytes.

Checks cover three new schemas plus the unchanged structured schema, 16 design examples, 16 external-condition checks, 970 focused field links, three rejected invalid inputs, an over-limit input and eight rejected semantic corruptions. All four decision bindings, all 16 example bindings and three invalid-input bindings verify. Local Markdown links resolve. Frozen baseline hashes and the 16 excluded older notes are unchanged. No complete runtime suite or S/F trial is rerun for this documentation package; prior 556-test results remain historical.

This package adds no runtime implementation, source approval or scientific validation. Parser, bridge and IF behavior remain unexecuted. Prior P/G text/form equivalence reviews and a prospective comparison dataset remain pending. README, roadmap, code, source PDFs, raw artifacts, credentials and the 16 old local notes are outside the lot.

## Proposed commit

Branch: `codex/free-text-group-reviewed`.

```text
docs(cytiva): record reviewed free-text interface fixtures

Record GR01-GR04 human decisions with retained reservations and content bindings.
Preserve the E08 application condition and E03 washing-stage provenance.
Package static checks and review status without changing runtime or frozen trials.
```

Next: separately requested minimal deterministic implementation and conformance tests, preserving the distinctions above before any frozen prospective comparison. Git-operation rules are in [AGENTS.md](../../AGENTS.md).
