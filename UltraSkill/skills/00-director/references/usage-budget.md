# Usage Budget: Context Tokens, GPU Hours & Regeneration Discipline

## 1. Context Window Budget (Agent Memory)

Loading unnecessary documentation degrades reasoning accuracy and wastes user quota.

| Budget Rule | Threshold (Starting Value) | Enforcement |
|---|---|---|
| **Max skills loaded at once** | `1` router + `00-director` + `1 to 3` domain `SKILL.md` files | Unload or stop reading unrelated pillars (e.g., never load `24-networking-backend` during a Cycles studio still task). |
| **Max reference files read per step** | `1 to 2` reference files from the active skill | Read a reference only when executing the step that cites it. |
| **Max `SKILL.md` file length** | `< 200` lines (`<= 199` lines hard validator gate) | Enforced automatically by `tools/validate.py`. |
| **Package file cap** | `288` target (`300` absolute maximum) | Enforced automatically by `tools/validate.py`. |

## 2. Google Colab GPU Budget (Cycles OptiX)

Google Colab sessions disconnect unpredictably and have daily GPU usage ceilings.

1. **Test stills before animation**:
   - Render single keyframe stills at `PREVIEW` (`960x540`) until composition and lighting values score `>= 4/5`.
   - Render 1 keyframe at `REVIEW` (`1920x1080`) plus a `2048-sample` small border crop (`256x256` px, starting value) to verify denoiser retention and run `FAKE_3D_CHECKLIST.md`.
   - Only after the `REVIEW` still passes may you render a 24-frame motion test or full sequence.
2. **Mandatory 3-Frame Benchmark Gate**:
   - Before rendering any sequence `> 5` frames, run `skills/14-blender-pipeline/scripts/benchmark_scene.py` on the first, middle, and heaviest frames.
   - Multiply average frame time by total frame count:
     $$\text{Estimated Hours} = \frac{\bar{t}_{\text{frame}} \times N_{\text{frames}}}{3600}$$
   - If $\text{Estimated Hours} > 3.0$, **STOP** and ask the user for explicit approval before starting the sequence.
3. **Never Re-Render Passed Frames**:
   - `skills/14-blender-pipeline/scripts/render_sequence.py` writes each frame directly to Google Drive and records its SHA-256 / byte size in `render_manifest.json`.
   - On session reconnect, skip every frame marked `COMPLETED` that passes `verify_frames.py`.

## 3. File Regeneration Discipline

- Never rewrite an entire file or project module that already passed its test and review gates just to make cosmetic edits elsewhere.
- When fixing the single weakest bar in a round, touch only the script, shader block, or function responsible for that bar.
