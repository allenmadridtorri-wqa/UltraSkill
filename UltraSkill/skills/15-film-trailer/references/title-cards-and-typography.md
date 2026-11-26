# Title Cards, Typography & Safe Margins

## 1. Title Card Ergonomics & Restraint

Amateur trailers ruin high-end 3D footage by slapping default Word-art gradients, heavy drop shadows, or unreadable cursive fonts over busy midtone backgrounds.

### Professional Cinema Title Card Rules (Starting Values)
1. **Dedicated Dark or Defocused Slate**:
   - Place mid-trailer copy cards ("IN A WORLD...", "CAPTURED IN CYCLES OPTIX") over a dedicated low-key backdrop (`luminance 0.02 – 0.08`) with slow drifting atmospheric dust motes or a heavily defocused (`f/1.4`) rim-lit silhouette.
2. **Letterspacing (Tracking) & Case**:
   - For cinematic all-caps serif or geometric sans-serif copy cards, set letter tracking to **`+180 to +350` thousandths of an em (`0.18em – 0.35em`)** and keep font height modest (`3.5% – 5.0%` of frame height for copy; `9% – 14%` for the main Act 4 Hero Title).
3. **Never Use Pure `#FFFFFF` White Text Over Dark Film Grain**:
   - Pure `1.0` white text pasted over a film-graded frame looks burned onto the monitor glass. Set title card text color to warm ivory/silver (`sRGB #E6E4DF`, linear `~0.78`) and apply the final compositor 35mm sensor grain **over** both the background and the typography so the letters sit inside the film emulsion.

## 2. Title Action & Broadcast Safe Margins (`1920 x 1080`)

| Margin Boundary | Inset Percentage | Pixel Bounds at `1920x1080` | Rule |
|---|---:|---|---|
| **Action Safe (`93%`)** | `3.5%` from each edge | `X: [67, 1853]`, `Y: [38, 1042]` | Keep all critical visual cues and HUD icons inside Action Safe. |
| **Title Safe (`90%`)** | `5.0%` from each edge (`10%` horizontal on ultrawide crops) | `X: [192, 1728]`, `Y: [108, 972]` | All typography, subtitles, studio credits, and call-to-action URLs must stay strictly inside Title Safe. |

## 3. Hold Timing Formula for Copy Slates

- **Minimum hold**: `48 frames` (`2.0 s`) for a single 1–3 word punch card.
- **Reading formula**: $\text{Frames} = \max\left(48,\; 24 + 10 \times N_{\text{words}}\right)$ at `24 fps` (e.g., a 6-word slate requires at least `84 frames = 3.5 seconds`, including a `10-frame` smooth opacity fade-in and `12-frame` fade-out).
