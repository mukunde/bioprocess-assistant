# Reviewed serving v1 — machine schema preparation

Prepared on 2 November 2026 against `main` at `6c8bfe0`. The user accepted TS01–TS06, SX01–SX06 and six technical clarifications in the [technical decision record](../../technical/reviewed-dossier-serving-technical-decisions-v01.json). The earlier [design record](../../technical/reviewed-dossier-serving-decisions-v01.json), [technical specification](../../technical/REVIEWED-DOSSIER-SERVING-TECHNICAL-V01.md) and [original shape examples](../../technical/reviewed-dossier-serving-interface-examples-v01.json) remain unchanged. Their proposed labels are historical, superseded for accepted design by the new decision record.

**These files are schemas and synthetic fixtures, not an adapter, API, serving release, activation or new scientific/source approval.** No application or dependency file was changed. All nine schemas use JSON Schema Draft 2020-12 and local URN references; validation uses an explicit offline registry without retrieving remote schemas.

## Inventory

| Schema | Responsibility |
|---|---|
| [common](common.schema.json) | Shared identifiers, exact quote provenance, original scoped reviews, conditions, steps, quantities, options, bundles and item outcomes |
| [request](request.schema.json) | Strict structured input; eight-task maximum, finite selectors, no authority/source/budget override |
| [response](response.schema.json) | Documentary envelope, item outcomes, complete context fields, citations, counts, measurement and non-authorization limits |
| [validation error](validation-error.schema.json) | Malformed/unauthorized input error without technical context; distinct from a documentary response |
| [mapping](mapping.schema.json) | Exactly the five registered keys, original Q/N source-ID sets, exact products and documentary categories |
| [source index](source-index.schema.json) | Versioned excerpt/review inventory and artifact bindings; PDF availability is explicit |
| [source view](source-view.schema.json) | Available excerpt vs quarantine/unavailable display; no held quote returned as ordinary usable support |
| [release](release.schema.json) | Explicit staged vs activated release, dependency bindings, initial limits, activation decision requirement |
| [authority](authority.schema.json) | Active pointer or explicit versioned withdrawal inventory; missing entries is not an empty inventory |

[Shape fixtures](shape-fixtures.json) contain 32 positive/negative structural checks. All SYNTHETIC IDs, zero digests and placeholder versions are intentionally nonauthoritative; no actual release or withdrawal register was created. The inactive/staged fixtures cannot be treated as an activation decision.

## Accepted decisions encoded

- Initial context default: 65,536 UTF-8 bytes, configurable on the service side. Request limit: 32,768 bytes; maximum eight tasks. Request JSON has no field for overriding these limits. JSON Schema `default` is an annotation, not automatic insertion or validation of missing data.
- Product absent → structural rejection; explicit `unknown`/`family_unknown` → valid request shape for later clarification. False/zero selectors are rejected rather than coerced. Procedure scope is fixed to MabSelect cleaning documentation in this first registry.
- Requested/excluded overlap remains structurally valid and exclusions win during future evaluation. SX05 therefore validates as a request; its all-excluded result remains a semantic outcome, not a source-absence assertion.
- Exact registered source-ID sets are encoded in mapping and bundle shapes. The SuRe/SuRe LX-only block cannot structurally expand its product set to plain MabSelect. The clarification mapping covers all input categories but is labelled context-only; product `other` must still abstain under the eligibility policy rather than acquire a recipe.
- Quantities preserve original text and owned-step provenance. Per-quantity spans include source ID, page-text offsets, exact text and quote hash; there is no automatic parsed-number conversion.
- Context-only options have no procedure steps. Supported procedure bundles require exact supported products and true documentary applicability; operational suitability remains unestablished.
- Structural validity never establishes that a release's hashes match actual files or that a cited human decision authorized activation. The configured trusted authority and original approvals remain separate checks.

## SX01–SX06 compatibility

The exact original requests were copied into the fixtures: SX01–SX05 validate structurally, including SX05's exclusion overlap. SX06 is rejected for its extra `approved_sources` field. The corresponding validation-error shape uses `unknown_authority_field`.

The original `expected` objects are deliberately partial assertion projections, not full response envelopes; they have not been relabelled as schema-valid complete answers. No adapter has generated the expected SX responses. Their behavioral checks remain required in the implementation stage.

The earlier unbound empty-withdrawal illustration has a null activation reference and incomplete authority fields. It is deliberately rejected by the complete authority schema. This does not contradict acceptance of an explicitly empty first inventory: that inventory must still have its version and actual reviewed authority binding, created only for a later approved release.

## Required semantic checks before serving

Schema validation is the first gate only. Future code must additionally verify:

1. Unique task/source/review IDs across different objects, reference closure and exact registered task-to-bundle ownership. The duplicate-task-ID fixture intentionally passes structural validation to expose this JSON Schema limitation and must fail `duplicate_task_id` before lookup.
2. Hashes against actual approved files, exact quote/span text, offset arithmetic and PDF page-index correspondence. A hash-shaped string or valid interval type is not a verified quote.
3. Original review scope, complete evidence-record bindings, unchanged reservations and full required warnings/follow-up steps. A complete source-ID list does not prove that the correctly bound source objects or semantic instructions were actually delivered.
4. Three-valued condition evaluation, no product/phase/task transfer, preserved alternatives, no invented quantities and no rewriting of user intent. Conditions are data; they are never evaluated as code.
5. Current trusted activation/withdrawal authority, request-start and pre-delivery checks, atomic pointer changes, no stale-release fallback and no hidden retry. An empty register with a fake digest cannot pass these gates.
6. Canonical UTF-8 context byte count, equality/one-byte-overflow boundaries, shared-object identity/deduplication and atomic alternatives. `maxLength` counts Unicode characters, not HTTP body bytes; enforce the 32,768-byte limit before parsing. No reservations may be dropped to fit.
7. Derived item/aggregate states and counts, exclusions first, all-excluded handling, absolute task order, global vs isolated integrity failure, and citation URL resolution on the exact release.
8. Escaping, localization boundaries, versioned excerpt access and zero model/API/Neo4j calls in the initial staging path. No held source or private filesystem path becomes ordinary answer support.

An empty `context` object still serializes its three empty arrays and keys; the synthetic unavailable response records that byte size rather than claiming zero serialized bytes. Its technical content is empty. Budget measurement itself and transport framing remain outside the counted context, as specified.

## Schema-level refinements for the next review

Safe ASCII IDs are limited to 96 characters and optional input labels to 2,048 characters. These are concrete schema refinements of the accepted bounded-field design, not new scientific facts. Other refinements include `allowed_contexts` arrays for mappings, explicit validation-error/source-view shapes and reason-code enums. Cross-field behavioral constraints remain in ST01–ST12 and SC01–SC14; the schemas do not silently approve new rendering summaries or new graph mappings.

## Verification performed

- All nine schema documents pass the local Draft 2020-12 meta-schema check.
- All local `$ref` targets resolve in the offline registry.
- All 32 labelled structural cases match their declared validity, including the six original SX request shapes, missing/wrong-type product, unknown selectors, task/item limits, source-ID omission, restricted-product expansion, missing activation decision and authority-injection rejection.
- Original decision messages, bound proposals, source facts, v03, sixteen old notes and the pilots remain unchanged. This is schema preparation validation, not an executed release or adapter-conformance result.

Reproduce structural checks with the already prepared environment's `jsonschema` and `referencing` development tools (no runtime dependency or automatic installation is introduced):

```python
import json
from pathlib import Path
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
root = Path('docs/schemas/reviewed-serving-v1')
schemas = {p.name.removesuffix('.schema.json'): json.loads(p.read_text(encoding='utf-8'))
           for p in root.glob('*.schema.json')}
for schema in schemas.values():
    Draft202012Validator.check_schema(schema)
registry = Registry().with_resources((s['$id'], Resource.from_contents(s)) for s in schemas.values())
fixtures = json.loads((root / 'shape-fixtures.json').read_text(encoding='utf-8'))
for case in fixtures['cases']:
    validator = Draft202012Validator(schemas[case['schema']], registry=registry)
    assert validator.is_valid(case['value']) == case['expected_structural_validity'], case['id']
```

No serving-data directory, active pointer or local release has been created. An implementation and its concrete staged release inventory must be reviewed separately before activation.

## Minimal handoff correction — task-bound references

The corrected development handoff emits `items[].bundle_refs`: JSON pointers
such as `/context/bundles/0`, resolved only within that same response. These
identify the exact product/category-bound object for the requesting task/item.
Consumers must use these references rather than resolve a `bundle_key` alone:
the same registered key may occur for different product-bound objects.

Clarification items reference their Q09 context with `bundle_refs`, while their
`bundle_keys` remain empty because no procedure is supported. Excluded,
quarantined, failed or budget-withheld items have no delivered references.
Identical objects may be shared by multiple tasks; their exact source/review
objects remain deduplicated and the context budget still counts delivered data.
References are response-local, not source URLs or persistent identifiers.

The additive field is structurally optional to preserve the original synthetic
fixtures; the corrected runtime always emits it. Its resolution, task/product
ownership and consistency with item state are semantic runtime/regression checks,
not guarantees provided by the pointer-pattern schema alone. Product/context
origins and applicable exclusion origins are also preserved as request pointers.
The original decision records and shape fixtures are unchanged. See the
[implementation review](../../validation/MABSELECT-DOCUMENTARY-HANDOFF.md)
for the correction checks and current scope.
