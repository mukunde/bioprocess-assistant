# Explore rising backpressure in the Cytiva demo

The local demo shows reviewed manual excerpts for **Protein A Sepharose** and
**Protein G Sepharose**. Use it to explore a product and deposit context and
inspect the supporting passages. A context selection is an assumption to
explore. The demo provides documentary evidence for review and does not
establish a diagnosis or an approved operating procedure.

## Run the local demo

Follow the [Windows setup guide](../DEMO-FIRST.md#install-from-a-fresh-windows-clone).
From the repository root, start the demo in PowerShell.

```powershell
.\Start-CytivaDemo.ps1
```

Open the [backpressure form on the default local port](http://127.0.0.1:8766/#troubleshooting-controls)
or select **Troubleshooting · rising backpressure** in **Input**. If you launched
on another port, use the address shown by the launcher.

1. Submit without choosing a product. The demo asks for the exact product.
2. Choose Protein A or Protein G Sepharose and leave the context unknown. The
   demo shows the manual's general cleaning indication and asks for context.
3. Choose a deposit context. Open the citations for the procedure, its scope
   and any precaution. The detergent example and ethanol alternative stay
   separate, and the ethanol route includes its backpressure warning.
4. Choose MabSelect to see the outside-scope response. Use the separate
   [MabSelect guide](../CHAINLIT-MABSELECT.md) for that product family.

Changing a selection marks the previous result as stale until you submit
again. For the separate Chainlit preview, see the
[staged candidate guide](../CHAINLIT-SEPHAROSE-CANDIDATE.md).

## Sources and scope

Source IDs below refer to the
[versioned excerpts](../../experiments/cytiva/retrieval-pilot-v01/evidence.json)
from PDF pages 166–167. The
[cleaning review](../../experiments/cytiva/reviewed-cleaning-retrieval/README.md)
records the review scope and reservations.

| Selection | Review | Citations and result |
| --- | --- | --- |
| Product unspecified | Q09 | E166-H/T/PH/LH and E167-H/PH/SH/LH. The source cards include the general Protein A/G cleaning indication in E166-T for context. The response asks for the product and selects no procedure. |
| Protein A/G, context unknown | Q01 + Q09 | Same citation set. The response shows the cleaning indication and asks for the missing context. |
| Precipitated or denatured proteins | Q01 + Q02 | E166-H/T/PH/P. The procedure retains its two steps and their order. |
| Strongly bound hydrophobic proteins, lipoproteins or lipids | Q01 + Q03 + Q04 | E166-H/T/LH/D/E/W. Separate options retain the example and the ethanol warning. |
| MabSelect | Q09 | E166-H/T/PH/LH and E167-H/PH/SH/LH. These context citations explain the scope boundary. The response selects no Sepharose procedure. |

The public GitHub repository contains the demo code, curated source excerpts
and documentary review records. Run the interactive demo locally. The cleaning
review's `publication_allowed: false` refers to publication in the knowledge
graph. It is separate from the visibility of the files in GitHub. This route
reads the reviewed evidence locally and performs no Neo4j writes.

See the [dated validation record](CYTIVA-TROUBLESHOOTING-2026-10-30.md) for the
original tests and browser observations.
