# Shot-to-Shot Color Continuity & Contact Sheet Audits

## 1. Why Individually Pretty Shots Fail When Cut Together

When 15 trailer shots are lit or graded in isolation, cutting them together reveals jarring discontinuities: Shot 1 has crushed pure-black shadows (`0.000`), Shot 2 has lifted blue milky shadows (`0.045`), and Shot 3 shifts the hero character's skin or brass casing from `4800 K` warm amber to `6500 K` green-cyan within the same room.

## 2. Three Quantitative Continuity Anchors

Before rendering full shot sequences on Colab, render 1 hero frame per shot at `REVIEW` (`1920x1080`, AgX), build a tiled grid with [`../scripts/contact_sheet.py`](../scripts/contact_sheet.py), and verify three continuity anchors across every shot inside the same scene/location:

| Continuity Anchor | Target Tolerance Across Same-Scene Shots (Starting Values) | How to Measure & Fix |
|---|---|---|
| **1. Shadow Black Floor (`1st Percentile Luminance`)** | Deepest non-specular shadow valley matches within `+-0.008` sRGB (`~2/255` 8-bit steps) across adjacent shots. | Sample shadow corner RGB values on the contact sheet; adjust bounded volumetric density or compositor `ASC-CDL Offset` (`Lift`). |
| **2. Key-to-Fill Color Temperature (`Kelvin`)** | Identical light source Kelvin (`+-150 K`) for the primary key and sky fill within the same location. | Share a single linked World/Light setup or Python lighting function (`setup_studio_lighting.py`) across all shots in that location. |
| **3. Hero Albedo & Highlight Peak (`99th Percentile`)** | Hero prop/skin key-lit midtone stays in the same AgX False Color band (`Green-Yellow`, `+0.7 to +2.0 EV`). | Adjust camera exposure (`scene.view_settings.exposure`) or key light distance so cutting from Wide to Close-Up does not jump `+1.5 stops` brighter. |

## 3. Intentional Act-Level Color Arcs

While shots *inside* the same scene must match tightly, a 60-second trailer benefits from a deliberate macro color arc across the four acts:
- **Act 1 (Cold Hook)**: Cooler desaturated slate/cyan palette (`5800 K – 7500 K`, higher shadow ratio `6:1`).
- **Act 2 (Escalation)**: Neutral-warm balanced contrast (`5000 K – 5600 K`, `4:1` ratio).
- **Act 3 (Climax)**: High-contrast complementary split (warm `2800 K – 4200 K` fire/practical sparks against deep `7500 K` cold negative fill, `8:1+` ratio).
