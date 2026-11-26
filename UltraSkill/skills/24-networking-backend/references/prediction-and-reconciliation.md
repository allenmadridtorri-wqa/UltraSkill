# Prediction, Reconciliation, and Interpolation

In an authoritative server game with `100 ms` round-trip latency (RTT), waiting for the server to echo your movement before moving your character on screen feels unplayably sluggish. To make multiplayer feel instant while remaining cheat-proof, every client runs **two different timelines simultaneously**:
- **Local Player**: Runs in the **Present (`T_server + RTT/2`)** via Client-Side Prediction.
- **Remote Entities**: Render in the **Past (`T_server - 100 ms`)** via Snapshot Interpolation.

---

## 1. Client-Side Prediction & Server Reconciliation

### Data Structures on the Client
Keep a 128-slot ring buffer indexed by `tick % 128`:
- `input_buffer[tick % 128]`: `{tick, move_dir, buttons, yaw, pitch}`
- `state_buffer[tick % 128]`: `{tick, position, velocity, movement_flags}`

### Step-by-Step Reconciliation Loop
1. **Local Prediction (`60 Hz`)**:
   - On local tick `T`, sample input `I_T`, store it in `input_buffer[T % 128]`, run the exact shared movement function `S_T = step_movement(S_{T-1}, I_T, dt)`, and store `S_T` in `state_buffer[T % 128]`.
   - Send a UDP packet containing `[I_{T-2}, I_{T-1}, I_T]` (bundling the last 3 inputs eliminates single-packet loss hiccups).
2. **Server Authoritative Verification**:
   - The server steps the player using `I_k` and includes `last_processed_input_tick = k` plus authoritative `{pos_k, vel_k}` in its next snapshot.
3. **Client Reconciliation Check**:
   - When the snapshot for tick `k` arrives, look up the client's historical prediction `pred = state_buffer[k % 128]`.
   - Compute position discrepancy: `err = (server_pos_k - pred.position).length()`.
   - If `err <= 0.04 m`: **Do nothing** (prediction matched within floating-point tolerance).
   - If `err > 0.04 m`:
     1. Overwrite `state_buffer[k % 128]` with `{server_pos_k, server_vel_k}`.
     2. Loop `replay_tick` from `k + 1` to `current_client_tick`:
        - Re-run `step_movement` using `input_buffer[replay_tick % 128]` and update `state_buffer[replay_tick % 128]`.
     3. Smooth visual correction offset (`visual_error_offset *= exp(-18.0 * dt)`) so small `0.15 m` corrections glide smoothly over `100 ms` instead of popping the camera.

---

## 2. Remote Entity Snapshot Interpolation

Never extrapolate remote players unless the interpolation buffer completely runs dry for `> 150 ms`.

1. Maintain a sorted buffer of the last `8` received snapshots per remote entity, each stamped with `server_tick_time`.
2. Compute `interp_time = estimated_server_time - interp_delay` (where `interp_delay = 0.100 s` for a `20 Hz` snapshot rate = 2 full snapshot intervals).
3. Find the two snapshots $A$ and $B$ bracketing `interp_time` ($t_A \le \text{interp\_time} \le t_B$).
4. Compute blend factor $\alpha = \frac{\text{interp\_time} - t_A}{t_B - t_A}$ and interpolate:
   - Position: `lerp(A.pos, B.pos, alpha)` (unless a `teleported` bit flag is set on snapshot $B$, in which case snap immediately).
   - Rotation: `A.quat.slerp(B.quat, alpha)`.
