# 60-Second Cinematic Trailer Architecture (1440 Frames @ 24 fps)

## 1. The Four-Act Micro-Trailer Blueprint

A 60-second teaser/trailer (`1440 frames` at `24.0 fps`) succeeds by accelerating editorial cut frequency while escalating stakes and audio density. Never cut at a constant metronomic duration (e.g., 12 shots of 5.0 seconds each—that puts the audience to sleep by second 20).

| Act | Timecode (`s`) | Frame Range (`24 fps`) | Average Shot Length | Narrative & Visual Goal | Audio Signature |
|---|---|---|---|---|---|
| **Act 1: Cold Hook & Atmosphere** | `00:00 – 00:12` | `0001 – 0288` (`288 f`) | `72 – 96 f` (`3.0 – 4.0 s`), `3–4` shots | Establish world scale, mood, and one intriguing anomaly. Wide `24–28 mm` lens + macro `100 mm` detail insert. | Low drone (`45–65 Hz`), isolated Foley (footstep, ticking gear, wind), sparse single piano/synth ping. |
| **Act 2: Premise & Escalation** | `00:12 – 00:38` | `0289 – 0912` (`624 f`) | `48 – 72 f` (`2.0 – 3.0 s`), `9–11` shots | Introduce protagonist/threat, show kinetic capability, shift camera from slow dolly to tracking medium (`35–50 mm`). | Ostinato pulse enters (`90–120 BPM`), sub-drop hit at frame `0289`, risingbraam/strings. |
| **Act 3: Rhythmic Montage & Hard Drop** | `00:38 – 00:52` | `0913 – 1248` (`336 f`) | `16 – 32 f` (`0.67 – 1.33 s`), `10–14` cuts + `12 f` hard blackout at `1237–1248` | High-energy action peaks synced to snare/taiko hits; end on a sudden **hard cut to black and silence** (`12–18 frames`) while a metallic reverb tail rings out. | Full percussion + riser crescendo cut off sharply at frame `1236`. |
| **Act 4: Title Card & Stinger** | `00:52 – 01:00` | `1249 – 1440` (`192 f`) | Title `108 f` (`4.5 s`) + Stinger `60 f` (`2.5 s`) + `24 f` tail | Boom title reveal (`1249–1356`), followed by one unexpected final visual/audio stinger twist (`1357–1416`). | Deep impact boom + signature melodic motif on title; dry close-mic Foley on stinger. |

## 2. Managing Colab T4 GPU Budgets for 1440-Frame Trailers

At `45 seconds` per 1080p frame on a Tesla T4, rendering all `1440` frames with heavy path tracing would take **`18.0 hours`**—exceeding the `3.0-hour` single-run gate by 6x. How veterans deliver a 60-second trailer inside a realistic Colab budget:

1. **Reuse Environment Sets Across Multiple Camera Markers**:
   Build 2–3 high-detail hero sets rather than 18 unrelated worlds. Binding 6 different physical camera rigs (`28mm wide`, `50mm OTS`, `85mm close`, `100mm macro`) to timeline markers in one `.blend` file eliminates redundant asset modeling and shader auditing.
2. **Use Hold/Ken-Burns High-Res Stills for Title Backdrops & Slow Inserts (`~25%` of screen time)**:
   Title cards (`108 frames`), black pauses (`24–36 frames`), and slow macro optical push-ins can be rendered as single `3840x2160` (`4K`) Cycles OptiX stills (`1 frame = 25 seconds` on T4) and animated with a subtle `1.00x -> 1.06x` 2D scale + real parallax dust layer in compositing—saving `250+` path-traced 3D frames.
3. **Chunk Sequences by Shot Priority**:
   Render each shot into its own Google Drive folder (`renders/SH-010/`, `renders/SH-020/`) with its own `render_manifest.json` so you can approve and assemble completed shots into the animatic timeline immediately.
