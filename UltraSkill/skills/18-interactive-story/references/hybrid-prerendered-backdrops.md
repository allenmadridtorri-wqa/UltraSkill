# Hybrid Cycles-Prerendered Backdrops + Realtime 3D Hotspots

## 1. Achieving Offline Cycles Photorealism on a 4 GB Laptop

When a story scene requires photorealistic caustics, heavy volumetric fog, wet reflections, or intricate machinery that exceeds a 1 GB Intel UHD laptop's realtime triangle budget, use the **2.5D Hybrid Camera-Projection Technique** (pioneered by classic prerendered adventure games and modernized with Three.js depth/parallax):

1. **Render 3–4 Camera Mark Stills (or Seamless 4-Second Video Loops) in Cycles OptiX on Google Colab**:
   - Match the exact camera positions, sensor size (`36 mm`), and vertical FOV (`45 deg`, `34 deg`, `28 deg`) of your `story_graph.json` camera marks (`cam_wide`, `cam_desk_macro`, `cam_console`).
   - Also export the low-poly proxy collision geometry (`.glb`, `< 2,500` triangles) from the exact same `.blend` scene.
2. **Project or Backdrop the Cycles Render in Three.js**:
   - Display the Cycles OptiX render as the camera-locked background or project it onto the simple proxy room geometry via camera-space UV projection (`gl_Position.xy / gl_Position.w * 0.5 + 0.5`).
   - Enable the `0.06 m` damped pointer parallax (`camera-choreography.md`).
3. **Render Interactive Props & Hotspots in Realtime Three.js On Top**:
   - Render the interactive hero prop (the ticking chronometer hand, the glowing hologram, the rotating valve wheel, and floating dust particles) as live 3D meshes lit by a matching `PMREM` environment and shadow catcher (`THREE.ShadowMaterial`).

## 2. Budget & Fidelity Comparison

| Metric | Pure Realtime WebGL (`LOW`) | Hybrid Cycles Backdrop + Realtime Props (`LOW`) |
|---|---|---|
| **Visual Fidelity** | Baked diffuse lightmap + simple PBR | **Full Cycles OptiX path-traced caustics, SSS, and volumetrics** |
| **Scene Draw Calls** | `15 – 45` | **`4 – 12`** (backdrop + 3–5 interactive 3D hero props) |
| **Laptop GPU Frame Time** | `14 – 28 ms` (`35–60 FPS`) | **`4 – 9 ms` (`60 FPS` locked on 1 GB Intel UHD!)** |
| **VRAM Footprint** | `60 – 120 MB` | **`25 – 45 MB`** (`3` compressed 1080p backdrop textures + low-poly proxies) |
