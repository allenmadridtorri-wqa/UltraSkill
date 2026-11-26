# Game Accessibility Standards

Accessibility features are not niche add-ons—subtitles, clear contrast, remappable controls, and camera-shake sliders improve playability for the majority of players.

---

## 1. Visual Accessibility Checklist

1. **Zero Color-Only Information**:
   - Never distinguish enemy rarity, faction, puzzle wires, or status effects by Red vs Green alone (`~8%` of male players have deuteranopia/protanopia).
   - Pair every color cue with a **distinct silhouette/icon** (`Circle`, `Triangle`, `Diamond`, `Skull`) or pattern hatching.
   - Default to a colorblind-safe palette (e.g., **Blue `#2B8CBE` / Orange `#F07818`** instead of Green / Red for friendly vs hostile indicators).
2. **Contrast & Background Plates**:
   - Any text rendered over the 3D scene must pass **`>= 7.0:1` contrast** against bright backgrounds by using a dark semi-opaque backing box (`rgba(8, 10, 14, 0.78)`) plus a `2 px` dark outline.
3. **Motion Sickness & Photosensitivity Controls**:
   - **Camera Shake Intensity Slider**: `0%` to `100%` (default `100%`, multiplies trauma rotation).
   - **Head Bob Toggle**: `On / Off` for first-person movement.
   - **FOV Slider**: `60°` to `105°` horizontal.
   - **Persistent Center Dot**: Optional `4 px` high-contrast center dot to anchor vision and prevent simulator sickness.
   - **Screen Flash Cap**: Never flash more than `25%` of the screen to pure white, and never exceed `3 flashes per second`.

---

## 2. Audio & Subtitle Standards

1. **Subtitles On by Default**:
   - Speaker name prefixed with distinct color/brackets: `[Vera]: The beacon battery is dead.`
   - Configurable font sizes: `Small (20 px)`, `Medium (24 px - Default)`, `Large (32 px)` at 1080p.
   - Maximum `42 characters per line`, `2 lines max` on screen at once.
2. **Closed Captions for Gameplay-Critical Audio**:
   - Provide optional directional visual captions (`[Sniper Laser Charging - Left]`, `[Grenade Beeping - Behind]`) so deaf/hard-of-hearing players or laptop users playing muted receive critical combat telegraphs.

---

## 3. Motor & Input Accessibility

- **Full Action Remapping**: Persist user bindings to `user://input_bindings.json` with conflict detection and a one-click `"Restore Defaults"` button.
- **Hold-to-Toggle Alternatives**: Allow switching continuous holds (`Hold to Sprint`, `Hold to Aim`, `Hold to Crouch`) to single-press toggles.
- **No Mandatory Rapid Button Mashing (QTEs)**: Allow holding the button instead of mashing `10 times/second`.
