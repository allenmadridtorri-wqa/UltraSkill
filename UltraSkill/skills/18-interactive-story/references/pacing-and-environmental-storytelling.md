# Pacing & Environmental Storytelling in 3D Spaces

## 1. Show Through Physical Prop Changes, Don't Explain in Paragraphs

If a writer puts 250 words of backstory into a modal box over a static 3D canvas, the 3D scene is wasted. Every narrative beat in `18-interactive-story` must couple concise copy (`<= 45 words`) with a visible change in the 3D space:

| Narrative Goal | Bad (Text-Only Exposition) | Veteran 3D Environmental Storytelling |
|---|---|---|
| **Establish Danger / Urgency** | A paragraph stating that reactor pressure is rising dangerously. | Camera dollies to the pressure gauge (`cam_gauge`), the needle trembles past the red line, and the room's key light shifts from `5400 K` white to a pulsing `2800 K` amber warning beacon. |
| **Reveal Past History** | A long journal entry describing a struggle in the room. | An overturned chair rotated `37 deg` off-grid, scratch marks across the brass lockplate, and a cracked watch crystal stopped at `03:14` on the floor under a table lamp. |
| **Confirm Player Choice Impact** | A toast message saying `"You stabilized the coolant."` | The volumetric steam hiss subsides, the red strobe turns off, cool `6500 K` work lights fade up, and the flywheel rotation smooths out to a steady hum. |

## 2. The Rule of Three Interactive Clues Per Room

In an interactive story room:
- Place **`3 to 5` distinct spatial hotspots** visible from the `cam_wide` hub view.
- Make **1 hotspot the primary progression gate** (e.g., the containment lever or exit hatch) and **2–3 hotspots optional forensic clues** (e.g., the chronometer, the schematic terminal, the coolant valve).
- Inspecting the optional forensic clues sets state flags (`inspected_chronometer = true`) that unlock a smarter, safer third choice at the primary progression gate—rewarding observant players who explore the 3D environment.
