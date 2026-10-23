# Cytiva cleaning: reviewed retrieval-reference pilot

Completed on 23 October 2026: **10 questions validated with reservations; none
pending**. Ten FR/EN intents have 20 formulations and refer to 17 source passages
on pages 166–167. Expected outcomes: seven answers, one clarification, two scoped
refusals. These are development references, not observed system scores.

| File | Contents |
|---|---|
| `events.json` | Original pending review, ten unchanged decision events with original French messages and reservations, and minimal intermediate state metadata |
| `review.json` | Exact final cumulative human review |
| `manifest.json` | Portable file/support digests, original local event/state hashes, counts and scope |

The unchanged [prepared references](../retrieval-pilot-v01/) are dependencies,
not duplicated here. The [review summary](../../../docs/experiments/cytiva-cleaning-retrieval-human-review.md)
is the readable current status; frozen preparation flags remain historical.
Per-question approval does not approve every excerpt for every use.

## Offline verification

From the repository root, Python 3.10+; standard library only:

```powershell
python -S -m experiments.cytiva.verify_cleaning_retrieval_package
python -m unittest tests.test_cleaning_retrieval_package -v
```

The verifier checks exact question/evidence bindings, original quotations and
reservations, source page mappings and selected text offsets, and reconstructs
all ten original review states from the original events. Portable file digests
normalize CRLF to LF. Historical JSON digests reconstruct the original UTF-8,
indent-2, LF, final-newline representation with insertion order preserved.

Optional replay against the exact local pypdf page-text artifacts:

```powershell
python -S -m experiments.cytiva.verify_cleaning_retrieval_package --source-text-dir data/experiments/cytiva/retrieval-pilot-v01/source-text
```

This verifies page-text hashes and all 17 exact quote spans. It does not parse or
render the PDF, independently validate visual associations, authenticate the
reviewer, retokenize context or run retrieval. Source hashes establish consistency,
not scientific truth or a cryptographic signature of human identity.

No PDF, complete page text, image, model weight, credential or personal absolute
path is included. Original raw sources and review snapshots remain local.
Scientific validation, operational suitability, graph publication and production
retrieval remain unapproved. The benchmark has not run. Question/answer/reference
files, this package and human review labels must never enter a retrieval index;
only an explicitly assembled source-passage corpus is eligible for a future test.
