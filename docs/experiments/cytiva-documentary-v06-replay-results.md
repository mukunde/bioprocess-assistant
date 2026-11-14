# Cytiva v06 documentary regression replay

On 14 November 2026, both frozen v06 variants passed **8/8** on
VP01–VP08. The v04 prospective result remains **1/8 per variant**.
The same questions informed the v06 corrections, so this replay measures
regression recovery on the 42-passage corpus.

[v04 prospective results](cytiva-documentary-v04-prospective-results.md) ·
[v05 VP06 replay](cytiva-documentary-v05-vp06-results.md)

## Scored cases

| Case | Observed outcome in both variants | Main citations |
| --- | --- | --- |
| VP01 | Kept the 1 min contact time with the detergent example. Returned 2 CV of 6 M guanidine and withheld a guanidine contact time. | E166-D, E166-P |
| VP02 | Returned the 3 CV prewash. Kept pH 7.0–8.0 with the post-reagent rinse and preserved the SuRe/SuRe LX restriction. | E167-S, E167-SH |
| VP03 | Returned the separate binding and elution formulations. The 2 M sodium chloride stayed with the sodium-phosphate elution formulation. | E121-B, E120-W |
| VP04 | Returned the usually sufficient volumes for both elution modes and the 1–2 mL/min range for the 1 mL column. | E121-E, E120-W |
| VP05 | Asked whether the column was 1 mL or 5 mL and withheld a flow range. | User input |
| VP06 | Applied the family-wide Blue Sepharose contraindication to the proposed switch. | E120-W, E120-A |
| VP07 | Gave conditional direct-use guidance and withheld a numerical contaminant cutoff. | E118-USE |
| VP08 | Returned the documented 5 mL HiTrap loading range and asked for the MabSelect variant on the other column. | E121-L, E120-W, E167-SH |

Both variants met the 7/8 threshold and passed all mandatory VP05–VP08
checks. Review found zero documentary safety violations in the recorded
outputs. Every expected reference was present in the scored contexts.
Citations and their dependencies matched the canonical assembled records.
E118-I and E121-EQ remained excluded.

## Regressions outside the score

- **PE01–PE08** Both variants retained their 8/8 regression result.
- **AD01** Product–procedure answered both branches. Fixed 32 answered
  Protein A Sepharose and explicitly abstained for MabSelect.
- **XC06** Both variants kept the common wash and stronger alkali rinse
  distinct and retained the SuRe/SuRe LX restriction.

All 80 regression requests matched v05 in assembled passages, proposals,
decisions, citations, and rendered answers. VP06 also matched v05.

## Timing and provenance

Median and range in milliseconds across 24 warm scored requests per
variant. Times exclude index setup and the separate regressions.

| Stage | Fixed 32 | Product–procedure |
| --- | ---: | ---: |
| Retrieval and assembly | 78.171 (64.584–105.434) | 80.679 (65.938–106.325) |
| Proposal | 0.314 (0.162–2.893) | 0.306 (0.162–3.416) |
| Validation | 0.200 (0.091–2.237) | 0.199 (0.108–3.418) |
| Rendering | 0.035 (0.008–0.074) | 0.037 (0.008–0.120) |
| Total | 79.506 (65.209–106.541) | 82.260 (66.344–107.654) |

The run completed 144 requests with unique metadata-only traces and
zero paid or generative calls. Decisions, citations, and answers were
stable across repetitions. The v06 freeze and its parents verified,
and the 75 protected files matched their pre-run hashes.

| Record | SHA-256 of file bytes |
| --- | --- |
| Local v06 replay manifest | `c5ed1c6abf1d6e6c7ea776871597ffeb245c488728e46650d9a680c580775a8d` |
| Event journal in local run `documentary-v06-replay-20261114-170643` | `f30604a6a29a77414e6d7a12726c9b7d9631cb183ed05eb19927effaa24c8abb` |

The replay supports the v06 corrections on the reviewed cases.
Performance on fresh questions remains to be measured.
