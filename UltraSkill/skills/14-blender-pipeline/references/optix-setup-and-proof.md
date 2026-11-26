# Cycles OptiX Setup, Device Enumeration & Hardware Proof

## 1. Exact Python Initialization Sequence

Blender does not automatically enable OptiX GPU devices in a fresh headless container even when a `.blend` file was saved with `scene.cycles.device = 'GPU'`. Every headless render invocation on Google Colab must explicitly configure user preferences in Python before calling `bpy.ops.render.render()`:

```python
import bpy

prefs = bpy.context.preferences
cprefs = prefs.addons["cycles"].preferences
cprefs.compute_device_type = "OPTIX"
cprefs.get_devices()

enabled_gpus = []
for dev in cprefs.devices:
    if dev.type == "OPTIX":
        dev.use = True
        enabled_gpus.append(dev.name)
    else:
        # Disable CPU device so hybrid CPU+GPU tile contention never slows T4 RT cores
        dev.use = False

if not enabled_gpus:
    raise RuntimeError("Zero OPTIX devices found. Refusing silent CPU fallback.")

bpy.context.scene.cycles.device = "GPU"
```

## 2. Why CPU Must Be Disabled alongside Tesla T4

On Google Colab, a Tesla T4 GPU is paired with 2 virtual Xeon CPU cores. If the CPU device is left enabled (`dev.use = True`) in hybrid OptiX mode, the slow CPU cores claim a render tile or work slice and stall frame completion while the T4 sits idle at 98% completion. Always set `dev.use = False` on `dev.type == 'CPU'`.

## 3. Verifying Hardware Engagement

Run [`../scripts/optix_verify.py`](../scripts/optix_verify.py) before any multi-frame job. It verifies four things:

| Check | Expected Value | Failure Diagnosis |
|---|---|---|
| `nvidia-smi` exit code | `0`, reports `Tesla T4` (or `L4` / `A100`) and driver `>= 525.x` (starting value) | Colab runtime is set to `None` (CPU) or TPU. Switch Runtime -> Change runtime type -> T4 GPU. |
| `cprefs.compute_device_type` | `'OPTIX'` | NVIDIA OptiX library missing or older non-RTX architecture (e.g., K80/P100). Stop and ask user before using `--allow-cuda-fallback`. |
| First frame kernel load time | `5 s – 45 s` on first run, `< 3 s` cached (starting value) | Normal on first frame while OptiX compiles PTX shaders. Cache `/root/.cache/cycles` to Drive if restarting frequently. |
| Post-render `nvidia-smi` VRAM | `memory.used >= 400 MiB` (starting value) | Confirms Cycles allocated buffers on the GPU rather than system RAM. |

## 4. Headless Cycles Needs No X11 Display

Cycles path tracing is purely compute-driven and runs via `blender -b` without `DISPLAY`, Xorg, `xvfb`, or Wayland. Never install or launch `xvfb` for Cycles renders.
