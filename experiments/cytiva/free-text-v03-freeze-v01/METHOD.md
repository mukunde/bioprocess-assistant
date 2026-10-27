# Corrected v03 runtime freeze

This checkpoint freezes the corrected v03 engine merged in PR50 at main
`173497fb5d8b1e66a551c923a7604aba4db83151`, following the user's explicit request.
It is a runtime/configuration freeze, not a new paired trial, acceptance score,
source approval or scientific validation. It does not activate the legacy chat.

The lock pins the four v03 modules, their shared runtime and identity dependencies,
input/output/coverage schemas, approved source catalog/adapter/policy, the exact
25 eligible passages, relevant decisions, this protocol and the read-only verifier.
Python, installed dependency versions and the existing offline tokenizer asset
are recorded separately and checked with `--environment`. Hashes normalize
LF/CRLF; the binary tokenizer hash does not. No PDF or model weight is copied.

Keep E118-I/E121-EQ excluded, one core call per request, six selected roots and
2,048 serialized context tokens. Preserve conditions, warnings, reservations,
source/unit bindings and exact input origins. Coverage uses the versioned v03
contract, including FV06's distinction between context 1/1 and request support
1/3. Legacy fields and historical scores retain their original meanings.

Coordinated buffer purposes that the bounded grammar cannot represent remain
explicit unresolved fragments; the conservative policy may block siblings.
An accepted inherited phase retains its prior text origin and assertion.

Active regression tests and a future demo renderer are outside the method lock.
The demo may present outputs from the frozen engine but may not rewrite intent,
choose a buffer purpose, invent missing values, override quarantine or weaken
coverage checks. If the pinned engine, schemas or source policy change, create a
new candidate/checkpoint; do not refresh this lock in place.

Do not require another question-review campaign before demonstrating existing
capabilities. Examples drawn from previously inspected FV cases are development
demonstrations and must not be reported as new validation. A later prospective
comparison needs its own frozen comparator, fresh questions/expected answers,
human review and explicit execution authorization. This runtime lock contains
no dataset, acceptance gate, runner or adjudicated new results.

The maintained suite passed 757 tests on merged main before this freeze.
Freeze-verifier and any demo tests added later are separate implementation checks.
Prior freezes, questions, references, reviews, raw runs and 16 older local notes
remain unchanged.
