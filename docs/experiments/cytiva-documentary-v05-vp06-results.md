# Cytiva v05 VP06 regression results

On 13 November 2026, both retrieval variants passed the targeted VP06
replay on all four repetitions. The frozen v04 prospective trial remains
at 1/8 per variant.

[Prospective v04 results](cytiva-documentary-v04-prospective-results.md) ·
[v04 regression replay](cytiva-documentary-v04-replay-results.md)

## VP06

Both variants rejected switching from HiTrap Blue HP to Blue Sepharose
6 Fast Flow when the target has similar hydrophobicity to albumin.
E120-W supplies the family-wide contraindication. E120-A identifies
the media listed for albumin removal, and E120-H supplies section context.
All three are on printed page 120. The answers supplied no operating
method. The assembled passage lists matched v04, where both variants
asked a generic clarification and omitted the warning.

| Variant | VP06 | Warm total latency, median (min–max) |
| --- | --- | ---: |
| Fixed 32 | 4/4 repetitions | 147.6 ms (123.6–152.5) |
| Product–procedure | 4/4 repetitions | 119.6 ms (117.1–144.9) |

Timing uses three warm requests per variant and excludes index setup.

## Regressions outside the score

- **PE01–PE08** Both variants preserved the earlier 8/8.
- **AD01** Product–procedure answered both branches with their own
  precautions. Fixed 32 answered Protein A Sepharose and abstained
  on MabSelect because E167-E and E167-W were missing.
- **XC06** Both variants separated the common wash from the stronger
  alkali rinse and preserved the SuRe/SuRe LX restriction.

All 80 regression requests reproduced their assembled passage lists,
proposals, decisions, citations, and rendered answers from the frozen
v04 prospective run. Neither E118-I nor E121-EQ entered the context.

## Provenance and limits

All 88 local requests completed with unique metadata-only traces and
zero generative or paid calls. Each case and variant had one correctness
request and three warm repetitions. Outputs and citations were stable
across repetitions, and citations and dependencies were checked against
the canonical assembled records.

| Record | SHA-256 of file bytes |
| --- | --- |
| v05 manifest `cytiva-documentary-v05-vp06-freeze.json` | `81bef27417b84b2c22c0f766c2ebf90127aac2f5bddee47ffd0c525e513f2e68` |
| Event journal in local run `documentary-v05-vp06-20261113-232856` | `ed9f46c95b939ddae9841c613ab7bd6a65beee64cfee52ee5863f9a7dbce16cf` |

The v05 freeze and its parent chain passed verification. This replay
measures recovery on a known warning omission. VP01–VP05 and VP07–VP08
were outside the v05 replay.
