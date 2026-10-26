# Structured request review cards v0.1

Status: **R01-R08 approved collectively with the R08 correction**,
25 October 2026; not implemented or executed. The
[matrix/card decision](../decisions/2026-10-25-task-request-matrix-review.json)
records the actual collective message separately from the earlier
[D01-D08/C01-C04 decision](../decisions/2026-10-25-task-request-review.json). Companion:
[context matrix](../REQUEST-CONTEXT-MATRIX-V01.md) and
[request contract](../REQUEST-CONTRACT-V01.md).

These are illustrative design/development cases derived from known material,
not new frozen test questions, extracted facts, executable fixtures, submitted
user forms or measured outputs. The English case inputs below are authored
examples, not quotations from the manual or additional human decisions. No
free-text parser or retrieval was run. Source IDs are review-side references
only and must not enter the future submitted request.

The review approved task ownership, explicit/unknown/missing context, requested
information, exclusion scope, necessary clarification, retained source scope and
prohibited-inference handling. Input-origin paths will point to actual submitted form
fields; no artificial text offsets are claimed here. All applicability decisions
about real samples remain unestablished unless separately evidenced.

## R01 — Two column sizes and phases

**Case input:** “For A, look up sample-application flow on HiTrap Blue HP 1 mL.
For B, look up washing flow and stopping criteria on HiTrap Blue HP 5 mL.
Do not include operating elution information for either task.”

| Task | Supplied context | Requested items | Exclusions |
|---|---|---|---|
| A | Product HiTrap Blue HP, column 1 mL | A-load: sample application / flow_rate | Operating elution, A only |
| B | Product HiTrap Blue HP, column 5 mL | B-wash: washing / flow_rate and stopping_criteria | Operating elution, B only |

**Proposed interpretation:** ready; no conflict or missing required column binding.
M02/M03/M04 apply. Expected documentary associations are 0.2-1 mL/min for A
loading and 5-10 mL/min for B washing, with the source qualifications and endpoint
alternatives. These values are review references, not supplied request fields.

**Source references:** E121-L/F for A; E121-W for B; required protocol scope and
warning dependencies retained. Shared dependencies may be serialized once but
remain associated with both tasks. The six-seed/2,048-token budget is global.

**Review checks:** no size/phase crossover; no elution value; approximate footnote
not treated as universal conversion; source presence not called answer validation.

## R02 — Include for A, exclude for B

**Case input:** “For A, compare step and linear-gradient elution on HiTrap Blue HP
1 mL, with flow and column volumes. For B, tell me only whether HiTrap Blue HP
albumin removal can precede or follow other purification steps; exclude operating
elution information for B.”

| Task | Context | Requested items | Exclusions |
|---|---|---|---|
| A | Product provided, column 1 mL provided | A-elute: elution / flow_rate, column_volumes, elution_mode comparison | None |
| B | Product provided, column not_supplied | B-position: general workflow-position information | Operating elution, B only |

**Proposed interpretation:** ready; no global contradiction. M05/M06 apply to A;
M10 applies to B. Do not ask B's size for the before/after statement or borrow A's
size. Retain both elution alternatives separately and their usually-sufficient
qualification; B receives no operating elution assignment.

**Source references:** E121-E for A; E120-A for B, with eligible scope/warning
dependencies. E120-A also naming another medium does not merge product identities.

**Review checks:** task-local exclusions; no false clarification; no claim that
either actual sample is suitable; no attribution of A parameters to B. This is
the design counterpart of the known X11 failure, not a new held-out case.

## R03 — A real same-task conflict

**Case input:** “For task A on HiTrap Blue HP 1 mL, give washing flow and quantity
guidance, but exclude all operating washing parameters for that same task.”

**Structure:** one task, product and column provided; A-wash includes washing
flow/quantity and an overlapping same-task exclusion of all washing parameters.

**Proposed interpretation:** needs clarification for A-wash. Preserve both
assertions and their origins. Ask whether those parameters should be included
or withheld. Do not silently choose the later instruction or supply the values.
Only eligible non-operating scope/warning context may be retained pending that
clarification; this is not a contradiction in the manual.

**Source references:** E120-H/W/P and E121-PH can establish scope. Do not select
E121-W as an operating-value response to this unresolved item.

**Review checks:** same-task selector intersection; no operating values before
resolution; future user corrections would be actual new input, not invented events.

## R04 — Unknown size blocks flow, not washing endpoints

**Case input:** “The product is HiTrap Blue HP, but I do not know the column size.
Look up its washing flow and the criteria for stopping the wash.”

**Structure:** one task; product provided/resolvable; column explicitly `unknown`.
Two information items: A-flow and A-endpoints, both in washing.

**Proposed interpretation:** clarification needed for A-flow only under M03;
A-endpoints is ready under M04. Ask which of the documented 1 mL/5 mL formats
the user means before choosing a single flow. Do not demand that answer before
retaining the documented baseline-or-no-material endpoint alternatives.

**Source references:** E121-W and scope/warning dependencies. The atom contains
both flow ranges; keep it intact if needed for endpoints, but do not attribute
either range to the unknown column in the answer.

**Review checks:** explicitly unknown is not not-supplied; no column inferred from
flow/sample volume; no unsupported absorbance threshold or scientific authorization.
This card requires separating context retention from permitted answer fields.

## R05 — Buffer formulation is not an operating phase

**Case input:** “For HiTrap Blue HP, list the alternative elution-buffer
formulations. Do not give operating elution settings. I have not specified a
column size because I am asking about buffer preparation.”

**Structure:** product provided; column `not_supplied`; one buffer-preparation
item with `buffer_use=elution` and `information=buffer_formulation`. Exclude
operating-phase elution information for this task.

**Proposed interpretation:** ready under M08; no size clarification or phase
conflict. Retain the two printed formulations as alternatives without pairing
them with binding buffers, silently correcting nomenclature or selecting a recipe
for a real sample. Source text may include binding formulations in the same atom;
that does not request them in the answer.

**Source references:** E121-B/BH, with required product scope/warning dependencies.
Do not select E121-E merely because the buffer's name contains elution.

**Review checks:** topic versus operation; unknown size does not erase supported
formulations; no elution flow, volume, duration or gradient profile added.

## R06 — Supported washing and missing pressure

**Case input:** “For HiTrap Blue HP 1 mL, look up washing flow and maximum pressure
in bar. Keep the washing information even if the reviewed excerpts omit pressure.”

**Structure:** one resolved product/column task; A-wash-flow is an operating item;
A-pressure is an operating-limits topic item. No values are supplied as inputs.

**Proposed interpretation:** both items are understood. Washing can be supported
under M03; pressure is missing under M11 in the current 25-excerpt corpus.
Retain the 1-2 mL/min documentary washing association and qualifications. State
only the bounded source absence for pressure; do not compute it from flow.

**Source references:** E121-W with dependencies; eligible-excerpt registry for the
absence boundary. No numerical pressure source is introduced by this card.

**Review checks:** interpretation ready is not full documentary support; no
pointless extra field question that purports to unlock an absent pressure value;
absence is not extended to the whole manual or external documentation.

## R07 — Quarantine cannot be repaired by more user facts

**Case input:** “Keep these separate: the general IEX separation principle and
its specific cation-exchange pH-versus-pI condition; equilibration parameters
for HiTrap Blue HP 5 mL; washing flow for another HiTrap Blue HP 1 mL column.”

| Task | Context | Requested items |
|---|---|---|
| G | General IEX topic; no product/column needed for its general principle | G-principle and G-pH-condition, separately accounted |
| A | HiTrap Blue HP 5 mL | A-equilibrate: requested operating parameters |
| B | HiTrap Blue HP 1 mL | B-wash-flow |

**Proposed interpretation:** requests understood; G-principle and B-wash-flow may
be supported under M01/M03. G-pH-condition and A-equilibrate remain unavailable/
quarantined under M13/M12. No need to ask for pI or more equilibration details in
order to pretend the source-policy block can be removed.

**Source references:** E118-M and E121-W with dependencies are eligible. E118-I
and E121-EQ remain excluded, even if a user later supplies all missing facts or
asks the system to use them anyway. E119-I is a separate eligible excerpt and
must not be substituted as proof of the withheld pH/pI condition.

**Review checks:** partial documentary support without loss of independent items;
no reconstructed inequality or values borrowed from washing/loading; no source
approval from this card. Numerical/operating availability is not a catalog issue.

## R08 — Generic product and sample volume are not a column identity

**Case input:** “I have a HiTrap column and a 1 mL sample. What washing flow
should I use?”

**Structure:** stated product label provided as HiTrap, resolution ambiguous;
column bed volume `not_supplied`; **sample volume of 1 mL** is a separate supplied
fact, not the column's bed volume. **Volume actually loaded remains
`not_supplied`**: the input does not say that the entire sample will be loaded.
A-wash-flow has no resolved initial-scope product/column binding.

**Approved correction:** replace the former loaded-sample-volume assertion with
sample volume only. Neither a column size nor an applied volume may be inferred.

**Proposed interpretation:** clarify the exact product and relevant column format
under M14/M03 before a product-specific numerical response. Do not assume Blue HP
or a 1 mL column. Do not force another product into the initial catalog.

**Counter-control:** if the user explicitly names a different product, its identity
is no longer missing: report that it is outside the initial implementation scope,
rather than repeatedly asking for the same already supplied identity.

**Review checks:** input presence is separate from catalog resolution; sample/bed
volume distinction; no best-score product substitution or invented zero values.
No arbitrary Blue protocol source is assigned to this unresolved task.

## Shared approved checks and approval limits

All cards must preserve request origins separately from source evidence, enforce
task ownership, and keep qualifiers/alternatives/warnings intact. No artificial
offsets, user confirmations, response scores or successful retrieval are claimed.

The approved allocation modalities retain this **synthetic arithmetic illustration only**:
two non-overlapping complete bundles of 1,300 and 900 tokens cannot both fit a
2,048-token request. These numbers are not tokenizer measurements of any card.
Never split either bundle or give each task its own 2,048-token allowance. Record
the unserved item and budget reason; reusing a shared bundle in another example
does not serialize it twice. Exact within-item ranking still needs design review.

The actual collective approval covers R01-R08 with the correction above and the
allocation modalities. It validates design mappings and handling rules, not a
new source, an implemented form, a scientific procedure or measured generalization.
Exact within-item ranking, catalog mappings and the wire format still need
specification. Implementation is a subsequent task, not work performed by this
review record. The original X packet is unchanged.
