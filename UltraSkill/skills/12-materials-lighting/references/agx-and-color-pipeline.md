# AgX Color Management & False Color Exposure Verification

## 1. Configuring AgX in Every Scene

Under Section 4 Render Standard, every Cycles scene must use the **AgX** view transform:

```python
scene = bpy.context.scene
scene.display_settings.display_device = "sRGB"
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "AgX - Medium High Contrast"  # starting value
scene.view_settings.exposure = 0.0
scene.view_settings.gamma = 1.0
```

### Selecting the Right AgX Look
- **`None` (Base AgX)**: Neutral log-like shoulder and toe; use when exporting 16-bit PNGs intended for external DaVinci Resolve / FFmpeg LUT grading.
- **`AgX - Medium High Contrast`** (Starting Default): Balanced cinema contrast curve with rich shadow toe and natural highlight roll-off ready for direct delivery.
- **`AgX - Punchy`**: Higher contrast and saturation recovery for product macro stills and sunny exteriors.

## 2. Using `False Color` to Nail Physical Exposure

Human eyes adapt to monitor brightness, making it easy to underexpose or clip a render by 3 stops without noticing. Before running a `REVIEW` or `FINAL` pass, temporarily switch `scene.view_settings.view_transform = 'False Color'` on a `PREVIEW` still and check the heatmap:

| False Color Readout | Scene-Linear EV / Reflectance Meaning | Target Scene Elements |
|---|---|---|
| **Purple / Black** | Clipping black floor (`< -10 EV`) | Deepest zero-bounce pinholes and negative-fill crevices only (`< 3%` of frame). |
| **Blue / Cyan** | Shadow zones (`-4 EV to -1.5 EV`) | Shadow side of hero subject and background corners. |
| **Grey** | **Middle Grey (`0.18` linear reflectance, `0.0 EV`)** | Lit 18% grey card, asphalt in sun, or shadowed side of Caucasian/medium skin. |
| **Green / Yellow** | Lit midtones and bright diffuse (`+0.7 EV to +2.5 EV`) | Key-lit side of human skin (`+1.0 EV` green-yellow), concrete, sunlit foliage, white drywall (`+2.0 EV` yellow). |
| **Orange** | Bright speculars (`+3.0 EV to +5.5 EV`) | Bevel catchlights on metal, bright sky clouds, rim light highlights. |
| **Red / White** | Highlight peak (`> +6.5 EV`) | **Permitted only on bare light filaments, sun disc, sparks, and tiny mirror glints.** Never allow a diffuse wall, shirt, or skin forehead to read Red in False Color! |

Remember to switch `view_transform` back to `'AgX'` immediately after inspecting the False Color check.
