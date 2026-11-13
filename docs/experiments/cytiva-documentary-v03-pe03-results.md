# Cytiva v03 PE03 regression results

Both retrieval variants passed the targeted PE03 replay on 13 November
2026. Each returned the stronger MabSelect SuRe LX procedure on all
four repetitions. AD01 and XC06 met their separate regression criteria.

[Prospective v02 results](cytiva-documentary-v02-prospective-results.md)

## PE03

The stronger sodium hydroxide wash specifies 100–500 mM, at least 2 CV,
and 10–15 min of contact time. The response lists the 3 CV binding-buffer
prewash separately and attaches the contact time to the reagent step.
E167-S supports the procedure and E167-SH restricts it to MabSelect SuRe
and SuRe LX. Both passages are on printed page 167.

Both variants retrieved E167-P, the common procedure. Neither used it to
answer PE03. All citations and their dependencies matched the canonical
records and were present in the assembled context.

| Variant | PE03 | Warm total latency, median (min–max) |
| --- | --- | ---: |
| Fixed 32 | 4/4 repetitions | 179.4 ms (150.3–184.1) |
| Product–procedure | 4/4 repetitions | 192.6 ms (165.3–194.7) |

Timing uses three warm requests per variant and excludes index setup.

## Regressions outside the score

- **AD01** Product–procedure answered both branches with their own
  solvent precautions. Fixed 32 lacked E167-E and E167-W, answered the
  Protein A Sepharose branch, and explicitly abstained on MabSelect.
- **XC06** Both variants separated the common wash from the stronger
  alkali rinse and preserved the SuRe/SuRe LX restriction without
  inferring column eligibility.

## Provenance and limits

The approved protocol is retained locally as
`cytiva-documentary-v02-prospective-protocol.md`. The local run used
`cytiva-documentary-v03-pe03-freeze.json` (SHA-256 of file bytes
`0ca0763eeaae7263cbecf20b25e8a2951366286bdf382e7f3da1fad4e1ddf16e`).

The replay used 42 admissible passages and completed 24 local requests
with unique traces. Decisions, citations, and rendered outputs were stable
across the four repetitions of each case and variant. The run made zero
generative or paid calls.

Local run `documentary-v03-pe03-20261113-205338`. Event journal SHA-256
`17207176544be7397e5d3acd491101fbbe5d3931f3f1e067973fac98d3becd1a`.
The v03 manifest and its parent chain passed verification. The earlier
journals and freeze files were preserved.

This replay measures one known procedure-scope regression. The prospective
v02 score remains 1/8 per variant. The other prospective cases were outside
the v03 replay.
