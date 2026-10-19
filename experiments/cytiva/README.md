# Cytiva experiments

Code and curated reports are versioned. Manuals, conversions, model responses,
review data and machine-specific settings are local under `data/experiments/`
and excluded from Git and the chatbot image. They must not be staged wholesale.

| Role | Location |
|---|---|
| Current plan | `docs/ROADMAP.md` |
| Current extraction contract | `docs/CLAIM-CONTRACT-V02.md`, `ingestion/claim_contract.py` |
| Ontology draft and documentary cards | `docs/ontology/` |
| Curated experiment reports | `docs/experiments/` |
| Historical v0.1 tooling | `experiments/cytiva/v01/` |
| v0.1 frozen local data | `data/experiments/cytiva/pages-097-099-v01/` |
| Reference cards, machine-readable | `data/experiments/cytiva/reference-v01/` |
| Archived v0.2 package (earlier prompt) | `data/experiments/cytiva/pages-100-102-v02/` |

## Next test: pages 100–102 with the corrected prompt

GPT-6.1 Sol, medium effort, one subscription-interface generation planned.
The old `pages-100-102-v02` package is an immutable archive made with the earlier
prompt. Generation has not been launched. It is not the corrected-prompt test.
Prepare a new package such as `pages-100-102-v02-r2`; do not overwrite the old one. No API purchase or execution is
authorized by these scripts. The preparation defaults to cached local Docling
weights and creates a new output directory. Example from the repository root:

```powershell
& '.\.venv-ingestion\Scripts\python.exe' -m ingestion.prepare_claim_test 'references/manual.pdf' --output 'data/experiments/cytiva/pages-100-102-v02-r2' --pages 100 101 102 --document-reference 'CY13981-25Jan21-HB' --document-version '25Jan21' --selection-reason 'Next complete product section; scope, conditions, negation and quantities'
```

Read the reference and edition from the PDF before supplying them; the command
records operator-supplied metadata and does not authenticate it automatically.
`--selection-reason` records the actual rationale for the chosen pages.
The preparation date is generated in UTC. Resuming an incomplete preparation
requires identical source, pages and metadata.

After the one response has been saved in the new package, validate against that
same frozen corpus:

```powershell
& '.\.venv-ingestion\Scripts\python.exe' -m ingestion.claim_validation 'data/experiments/cytiva/pages-100-102-v02-r2/resultat-sol.json' --corpus 'data/experiments/cytiva/pages-100-102-v02-r2/input.json' --output 'data/experiments/cytiva/pages-100-102-v02-r2/validation-sol.json'
```

## Historical v0.1 comparison: pages 97–99

The original responses remain frozen and human approval remains pending. The
authoritative Sonnet file is `resultat-sonnet-original.json`. The byte-identical
old alias and the typographic accessibility capture are archived under the local
`archive/` directory. Neither is used to grade the extraction.

The v0.1 `prepare` command refuses a bundle with execution metadata. Do not
regenerate or repair the model responses. Offline summaries may be reproduced
from the repository root using:

```powershell
& '.\.venv-ingestion\Scripts\python.exe' -m experiments.cytiva.v01.compare_saved
& '.\.venv-ingestion\Scripts\python.exe' -m experiments.cytiva.v01.build_fidelity_audit
& '.\.venv-ingestion\Scripts\python.exe' -m unittest discover -s experiments/cytiva/v01 -p 'test_*.py' -v
```

The seven archived comparison checks require the ignored local bundle and
`experiments/cytiva/requirements.txt`. They skip when the bundle is absent in a
fresh clone. The main tests under `tests/` use synthetic fixtures and do not
require the private experiment results. The reference-card builder requires a new directory and never updates the
repository ontology or existing human annotations:

```powershell
& '.\.venv-ingestion\Scripts\python.exe' -m experiments.cytiva.build_reference_cards --output 'data/experiments/cytiva/reference-v01-r2'
```

It writes `exemples.json`, `examples-v0.1.md` and `verification.json` into that
new directory. Review and promote a draft separately; keep human decisions
separate from generation. The conversion and local PDF artifacts are required.

The fidelity audit contains authored judgments, not an automatic judge. It is
bound to the exact reviewed response, corpus, prompt, excerpt and source-map
bytes. A changed input is rejected before writing any audit output. New results
require a new documentary review and versioned judgments; changing only the
expected hashes does not make the old judgments applicable.
