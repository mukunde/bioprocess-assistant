# Cytiva C01-C10: compact documentary reference review

Completed on 24 October 2026: **ten questions validated with reservations, none
pending**. The ten bilingual intents have 20 formulations and refer to pages
118–121. Expected behaviours: seven answers, one clarification and two scoped
refusals. These are reference expectations; retrieval and answer generation have
not been executed on this set.

| File | Purpose |
|---|---|
| `events.json` | Exact initial review and ten original events, sufficient to reconstruct every intermediate state |
| `review.json` | Exact final review, original French user messages and all reservations |
| `provenance.json` | Original preparation, source-page identities, preparation/final-review audit records and scope |
| `manifest.json` | LF/CRLF-portable file hashes, original historical event/state hashes, counts and dependencies |

The [questions](../contaminants-pilot-v01/questions.json),
[source excerpts](../contaminants-pilot-v01/evidence.json),
[source topology](../contaminants-pilot-v01/source_context.json) and
[preparation manifest](../contaminants-pilot-v01/manifest.json) remain unchanged.
Their pending labels record the frozen preparation, while the current decisions
are separate. See the [completed review](../../../docs/experiments/cytiva-contaminants-human-review.md)
and [original review cards/source catalogue](../../../docs/experiments/cytiva-contaminants-retrieval-pilot.md).

The required reference sets cover 25 of the 27 candidate source records.
**E118-I and E121-EQ were not individually covered by these question reviews.**
Keep this distinction when preparing a retrieval adapter; completion does not
approve all source annotations or a production source-selection policy.

## Offline verification

From the repository root, Python 3.10+; standard library only:

```powershell
python -S -m experiments.cytiva.verify_contaminant_questions_package
python -m unittest tests.test_contaminant_questions_package -v
```

Optional comparison with the local full-page native text:

```powershell
python -S -m experiments.cytiva.verify_contaminant_questions_package --source-text-dir data/experiments/cytiva/contaminants-pilot-v01/source-text
```

The verifier checks source spans/hashes, dependencies, question/evidence bindings,
all original events and the ten reconstructed review states. It validates with
LF or CRLF checkouts and without the original local artifact directories. The
historical serialization is UTF-8, `ensure_ascii=False`, indent 2, LF and final
newline; canonical event/state links use sorted compact JSON.

Source PDF, complete pages, renders, model/tokenizer assets, credentials and
personal absolute paths are excluded. Original local events and repeated state
snapshots remain intact outside this compact package. No previous experiment is
replaced. Earlier top-six results concern a different source section and are not
claimed as results for C01-C10.

Publication, scientific/operational validation, production retrieval and human
approval of benchmark results remain ungranted. Hashes establish consistency,
not independent scientific truth or authentication of reviewer identity. Do not
index questions, answers, review messages or decision metadata as source evidence.
