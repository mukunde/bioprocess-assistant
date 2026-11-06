# Chainlit Sepharose video verification

[Open the video](exports/sepharose-chainlit-continuous.mp4) · [Credits](ATTRIBUTION.md)

The clip records one new Chainlit conversation in the integrated browser. It uses
226 successive viewport captures, timed from the original session. The yellow
rings mark actual click positions. The longest interval between captures was
333 ms, so fast scrolling can appear stepped.

| Time | What to check |
| --- | --- |
| 0:04 | The product menu shows the click on **Protein G Sepharose**. |
| 0:06 | The context menu shows the click on **Precipitated or denatured proteins**. |
| 0:12–0:19 | The response repeats the product and context, then shows the conditional guidance. |
| 0:23–0:32 | The click opens **E166-P**. The final view shows the excerpt and PDF page 166. |

FFmpeg decoded the full 31.63-second export. It is a silent H.264 MP4 at
1440 × 810 (16:9). The export matches the reviewed file byte for byte.

- SHA-256: `b88535ec24223b57c1ca8cf6b3c97811c00d66a497c5470d41ac184d76e14c64`
- Preview: `sepharose-backpressure-candidate-v03` on project revision `c46215b`
- Status shown: **CANDIDATE ONLY — NOT ACTIVATED**

The preview demonstrates documentary lookup and citation inspection. See the
[candidate guide](../../docs/CHAINLIT-SEPHAROSE-CANDIDATE.md) for the limits of
the documentary review.
