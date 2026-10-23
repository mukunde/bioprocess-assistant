# Cytiva section-context questions: compact human review

Completed on 23 October 2026: **eight questions validated with reservations; none
pending**. These are eight bilingual development intents (16 formulations), with
16 indispensable source passages on pages 166–167. Expected policies: three
answers, one clarification, four scoped refusals. These labels are not executed
assistant responses or independent test observations.

| File | Purpose |
|---|---|
| `events.json` | Original pending state, eight unchanged decision events and minimal metadata to replay intermediate states |
| `review.json` | Exact final human review, original French messages and all reservations |
| `provenance.json` | Original reference freeze, input identities and measured-run metadata, including the incomplete N05 outcome |
| `manifest.json` | Portable file/dependency hashes, original historical event/state hashes, counts and scope |

The [prepared questions](../cleaning_section_questions_v01.json) remain unchanged,
including historical pending flags. Source quotations are reused from the
[previous reviewed reference](../reviewed-cleaning-retrieval/README.md), not copied.
See the [completed review summary](../../../docs/experiments/cytiva-section-questions-human-review.md).

## Offline verification

From the repository root, Python 3.10+; standard library only:

```powershell
python -S -m experiments.cytiva.verify_section_questions_package
python -m unittest tests.test_section_questions_package -v
```

The verifier checks the previous source package, question/evidence bindings,
original human messages/reservations and all eight reconstructed review states.
File digests normalize CRLF to LF. Historical event/state bytes reconstruct UTF-8,
indent 2 and LF with a final newline. The historical source-evidence checkout used
CRLF, prepared questions used LF, and the original freeze used ASCII JSON with
CRLF and no final newline; those separate identities are preserved explicitly.

Optional replay of local text and experiment artifacts:

```powershell
python -S -m experiments.cytiva.verify_section_questions_package --source-text-dir data/experiments/cytiva/retrieval-pilot-v01/source-text --run-dir data/experiments/cytiva/retrieval-pilot-v01/runs/section-context-20261023-c
```

This additionally checks exact source spans, original measured artifact hashes and
the retained N05 projection. It does not rerun retrieval, tokenize context, render
or parse the PDF, approve benchmark results or authenticate reviewer identity.
The original result contexts and runtime are excluded; this is a review package,
not a self-contained reproduction of the experiment. The policy snapshot and code
hashes in provenance document historical inputs, not newly approved software.

**N05 remains incomplete in both measured variants**, missing E166-PH and E166-P.
Human reference approval does not erase that failure or demonstrate correct
answers/refusals. Source/decision hashes establish consistency, not scientific
truth, operational suitability or a cryptographic signature of human identity.

No PDF, full-page text, image, tokenizer/model weights, credentials or personal
absolute paths are included. Publication, scientific/operational use, production
retrieval and human approval of benchmark results remain false. Do not index the
questions, expected labels, human messages or review package as source evidence.
