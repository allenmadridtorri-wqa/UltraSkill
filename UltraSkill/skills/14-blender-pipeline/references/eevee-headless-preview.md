# Optional Headless EEVEE Previews (EGL & Xvfb)

## 1. Strict Rule: EEVEE Is Only for Fast Playblasts

Per Section 4 Render Standard:
- **Final renderer**: Always **Blender Cycles with OptiX on Google Colab GPU**.
- **Cycles headless**: Runs directly via `blender -b` with zero virtual display.
- **EEVEE (`BLENDER_EEVEE_NEXT` / `BLENDER_EEVEE`)**: Rasterized OpenGL/Vulkan preview engine. Use EEVEE **only** when generating a rapid timing animatic or camera blocking playblast (e.g., 1440 frames in 3 minutes to verify editorial cuts in `15-film-trailer` before committing Colab hours to Cycles). Never pass an EEVEE render off as a Cycles review or final frame.

## 2. How to Run EEVEE Headlessly on Linux / Colab

Unlike Cycles, Blender's EEVEE rasterizer requires an OpenGL context. On headless Linux (Colab or CI):

### Option A: Headless EGL (Preferred on NVIDIA GPUs in Blender 3.6 / 4.x)
Modern Linux Blender builds compiled with `WITH_GL_EGL` automatically initialize an off-screen hardware EGL context on the NVIDIA driver without X11:

```bash
blender -b animatic.blend -E BLENDER_EEVEE_NEXT -o /tmp/animatic_####.png -a
```

### Option B: Virtual Framebuffer (`xvfb-run`) Fallback
If a Linux container returns `Unable to open a display` when `-E BLENDER_EEVEE_NEXT` is requested, wrap the invocation in `xvfb-run`:

```bash
xvfb-run -a -s "-screen 0 1920x1080x24" \
  blender -b animatic.blend -E BLENDER_EEVEE_NEXT -o /tmp/animatic_####.png -a
```

## 3. Labeling Playblasts Clearly

Whenever an EEVEE animatic is rendered for timing checks:
1. Enable Stamp Output (`scene.render.use_stamp = True`, `scene.render.stamp_note_text = "EEVEE TIMING PREVIZ - NOT CYCLES"`).
2. Store output in a separate `previz_animatic/` directory, never inside the `frames/` directory tracked by `render_manifest.json`.
