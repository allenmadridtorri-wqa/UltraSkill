# Bandwidth Budgeting and Bit-Packed Serialization

Never serialize high-frequency `20–30 Hz` world snapshots as verbose JSON strings (`{"entity_id": 42, "position_x": 124.5529102, ...}`). JSON wastes `5x–10x` bandwidth and CPU parse time compared to quantized binary packets.

---

## 1. Transform & State Quantization Table

| Field | Naive Raw Size | Quantized Representation | Quantized Size | Savings |
|---|---|---|---|---|
| **3D Position (`x, y, z`)** within `±512 m` arena (`1 mm` precision) | `3 x float32 = 12 bytes` (`96 bits`) | Fixed-point integers (`20 bits` per axis) or `3 x int16` (`1.5 cm` precision = `48 bits`) | **`6 bytes`** (`48 bits`) | **50%** |
| **3D Rotation (`Quaternion`)** | `4 x float32 = 16 bytes` (`128 bits`) | **Smallest-Three**: `2 bits` index of largest component + `3 x 10-bit` signed components in $[-0.707, +0.707]$ | **`4 bytes`** (`32 bits`) | **75%** |
| **Yaw-Only Character Facing** | `1 x float32 = 4 bytes` (`32 bits`) | `uint8` (`0..255` -> `1.4°` step) or `uint16` (`0.005°` step) | **`1–2 bytes`** | **50–75%** |
| **Player Input Buttons** | `8 x bool = 8 bytes` | Single bitfield `uint16` (`bit 0 = jump`, `bit 1 = fire`, etc.) | **`2 bytes`** (`16 bits`) | **75%** |
| **Entity Health (`0..1000`)** | `int32 = 4 bytes` | `uint10` or `uint16` | **`2 bytes`** | **50%** |

---

## 2. Delta Compression & Dirty Bitmasks

In a room with 40 entities, typically only 8–12 move or change health on any given tick.
1. Prefix each entity snapshot entry with an `entity_id (uint16)` and a **`change_mask (uint8)`**:
   - `Bit 0 (0x01)`: Position changed (`+6 bytes`)
   - `Bit 1 (0x02)`: Rotation changed (`+2 or 4 bytes`)
   - `Bit 2 (0x04)`: Velocity present (`+4 bytes`)
   - `Bit 3 (0x08)`: Animation / Action state changed (`+2 bytes`)
   - `Bit 4 (0x10)`: Health / Shield changed (`+2 bytes`)
2. If `change_mask == 0` relative to the last snapshot **acknowledged by that specific client**, omit the entity from the packet altogether.

---

## 3. Priority Accumulator & Interest Management

When total changed entities exceed the single-packet MTU budget (`1,200 bytes`):
1. Score each entity for each client:
   $$\text{Priority} = \frac{\text{base\_importance} \times \text{ticks\_since\_last\_sent}}{1.0 + \text{distance\_to\_client}^2}$$
   - Bosses and nearby players get updated at the full `20–30 Hz`.
   - Distant props or enemies `45 m` away outside the view cone step down to `5–10 Hz`.
2. Pack highest-priority entities until reaching `1,150 bytes`; deferred entities automatically gain `ticks_since_last_sent` priority for the very next tick.
