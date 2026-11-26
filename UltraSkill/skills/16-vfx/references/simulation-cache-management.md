# OpenVDB & Alembic Simulation Cache Management on Google Colab

## 1. Never Bake Physics on the 4 GB Laptop

Mantaflow fluid/smoke solvers and cloth simulations allocate multi-gigabyte voxel and collision grids in system RAM. Running a 256-division bake on a 4 GB RAM laptop triggers swap thrashing and OS OOM kills.
- **Authoring rule**: On the laptop, set `Resolution Divisions = 32` or disable the Fluid/Cloth modifier (`show_viewport = False`) while scripting the scene.
- **Baking rule**: Execute the high-resolution bake headlessly on the **Google Colab instance (12.7 GB+ system RAM)**, writing `.vdb` or `.abc` caches directly to `/content/drive/MyDrive/<project>/caches/` before calling `render_sequence.py`.

## 2. OpenVDB Compression & Precision Settings

Before baking any Mantaflow domain, configure its cache settings in Python to cut Google Drive footprint by `65% – 80%`:

```python
import bpy

def configure_vdb_cache(domain_obj: bpy.types.Object, cache_dir: str, start: int, end: int) -> None:
    mod = next(m for m in domain_obj.modifiers if m.type == "FLUID")
    settings = mod.domain_settings
    settings.cache_directory = cache_dir
    settings.cache_frame_start = start
    settings.cache_frame_end = end
    settings.cache_type = "ALL"          # or "MODULAR"
    settings.cache_data_format = "OPENVDB"
    settings.openvdb_cache_compress_type = "ZIP"   # or "BLOSC"
    settings.openvdb_data_depth = "16"             # 16-bit Half Float (saves 50% vs 32-bit Float)
```

## 3. Voxel Budget Math (`sim_budget_estimator.py`)

For a domain of dimensions $(L_x, L_y, L_z)$ meters and base resolution $R_{\max}$ along the longest side $L_{\max} = \max(L_x, L_y, L_z)$:
$$N_x = \left\lceil R_{\max} \frac{L_x}{L_{\max}} \right\rceil, \quad N_y = \left\lceil R_{\max} \frac{L_y}{L_{\max}} \right\rceil, \quad N_z = \left\lceil R_{\max} \frac{L_z}{L_{\max}} \right\rceil$$
- If `Noise Upres = 2` is enabled, total wavelet voxels multiply by $2^3 = 8\times$.
- Always run [`../scripts/sim_budget_estimator.py`](../scripts/sim_budget_estimator.py) to confirm peak RAM `< 10.0 GB` and total sequence cache `< 8.0 GB` (starting value for free Google Drive accounts).
