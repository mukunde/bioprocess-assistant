# MabSelect registry presentation v02

An opt-in presentation variant addressing the three usability findings in
[UA01-UA08 trial v01](../experiments/cytiva/reviewed-registry-ui-acceptance-v01/README.md).
The baseline UI, acceptance inputs/results, selector, HTTP contract, local
registry, source routes and both runtime freezes remain unchanged.

## Start explicitly

From the project checkout, using its prepared verification environment:

```powershell
.\.local-tools\verification-venv\Scripts\python.exe -m demo.registry_ui_v02 --registry-root .local-tools\mabselect-registry-v02-runtime --port 8785
```

Open [the opt-in variant](http://127.0.0.1:8785/). This requires an already approved
local authority directory. It neither prepares nor activates a registry. The
existing `demo.registry_ui` entry point continues to serve the baseline page.
Source links retain the current-authority checks of the original server.

## Optional local tracing

The local tracing implementation is opt-in and outside both frozen runtimes.
The --trace-file option enables metadata-only JSONL in a new local file;
--trace-otlp-endpoint accepts a loopback OTLP/HTTP collector. Export queues are
bounded and asynchronous; SDK/sink failures do not select or block an answer.
Source HTML and response bodies remain unchanged; enabled replies add an
X-Trace-Id header. The baseline page remains separate.

See [tracing setup, privacy contract and regression commands](REGISTRY-TRACING.md).
Install its optional packages into a separate development environment, not the
frozen demo environment. No dependency installation, activation or download is
performed by the launcher or response path.

## Presentation changes

- Outside-release abstention names the product/release boundary and distinguishes
  cleaning procedures from numerical pressure. It does not claim incompatibility
  or whole-manual absence and does not suggest substitute products.
- Clarification retains each requested item's state, with one shared action that
  focuses the first missing field. Already provided controls remain untouched;
  uncertainty may remain unknown. The Q09 explanation, eight required sources and
  all original review reservations remain in a clearly labelled disclosure.
- A warning is folded into a complete-original-passage disclosure only when its
  whitespace-normalized full text exactly equals the displayed steps combined
  and every warning source is also attached to those steps. No fuzzy matching is
  used. Different-source or partially covered warnings remain expanded. The
  independent E167-W backpressure warning remains immediately visible; air-bubble
  and backpressure precautions are not merged. Full original text and citation
  links are retained in every case, including when folded.

The structured response and audit JSON are not transformed. No retrieval,
conditions, quantities, product scopes or source eligibility are changed.
This presentation variant is not a new runtime freeze or a rerun of the original
acceptance trial. Collapsing explanatory context changes default visibility,
not the documentary support required or delivered.

## Regression checks

```powershell
.\.local-tools\verification-venv\Scripts\python.exe -m unittest tests.test_registry_ui_v02 -v
```

Node and the development-only jsdom dependency from `tests/ui/package-lock.json`
are required. Tests use disposable authority roots and the real loopback API;
they never access or withdraw support from the user's private registry. They
exercise inherited withdrawal, missing-authority, stale-response and deadline
checks, as well as reason-specific messaging, grouped clarification, source and
reservation retention, complete warning disclosures and conservative deduplication.
Renderer-only synthetic warnings are explicitly confined to regression fixtures.
