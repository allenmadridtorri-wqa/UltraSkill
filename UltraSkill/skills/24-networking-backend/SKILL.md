---
name: ultraskill-networking-backend
description: Multiplayer topology selection, client-side prediction and server reconciliation, entity snapshot interpolation, bit-packed delta serialization, matchmaking lobbies, and server-authoritative anti-cheat.
---

# 24 — Networking & Backend

This skill designs and validates low-latency, cheat-resistant multiplayer architectures—from co-op WebRTC/Steam relay hosts to dedicated authoritative UDP/WebSocket servers—staying inside strict per-client bandwidth budgets (`<= 32 KB/s` downstream, `<= 8 KB/s` upstream).

## When to use

- Choosing between Client-Server Authoritative, Listen-Server Host + Relay, or Deterministic Lockstep / Rollback topologies.
- Implementing Client-Side Prediction, Server Reconciliation, and Remote Entity Snapshot Interpolation.
- Calculating packet budgets, quantizing transforms, and designing delta-compressed binary protocols.
- Building lobby state machines, NAT traversal / relay integration, and reconnection handshakes.
- Enforcing server-authoritative movement speed clamps, fire-rate cool-downs, and lag-compensated hit validation.

## Inputs

- Target player count per match (`2–4` co-op, `8–16` arena, `64+` large scale).
- Core gameplay tick rate (`60 Hz` simulation, `20–30 Hz` network snapshot send rate).
- Dynamic networked entity counts (players, enemies, projectiles, destructibles).

## Steps

1. **Select Network Topology & Authority Model**:
   - Choose the topology matching your genre and budget using [references/authority-and-topology.md](references/authority-and-topology.md). Never trust client-reported damage, currency, or teleport coordinates.
2. **Implement Prediction, Reconciliation & Interpolation**:
   - Simulate the local player's inputs immediately on the client (`0 ms` input delay), buffer unacknowledged input commands by `tick_id`, and render remote entities `100 ms` (`2–3 snapshots`) in the past using [references/prediction-and-reconciliation.md](references/prediction-and-reconciliation.md).
3. **Quantize & Budget Bandwidth**:
   - Bit-pack positions, smallest-three quaternion rotations, and dirty-flagged state masks using [references/bandwidth-and-serialization.md](references/bandwidth-and-serialization.md).
   - Verify packet sizes and per-client bitrates with [scripts/bandwidth_calculator.py](scripts/bandwidth_calculator.py).
4. **Build Matchmaking, Lobbies & Reconnection**:
   - Manage join tokens, ready barriers, deterministic random seeds, and `30s` drop-in grace windows using [references/matchmaking-and-lobbies.md](references/matchmaking-and-lobbies.md).
5. **Harden Server Validation & Anti-Cheat**:
   - Enforce per-tick movement distance envelopes, server-side cooldown clocks, rewind lag compensation capped at `200 ms`, and fog-of-war interest filtering using [references/anti-cheat-and-validation.md](references/anti-cheat-and-validation.md).

## Numbers and defaults

| Parameter | Default Value | Tolerance / Notes |
|---|---|---|
| Simulation Tick Rate | `60 Hz` (`16.67 ms`) | Fixed deterministic physics step |
| Server Snapshot Send Rate | `20 Hz` (`50 ms`) or `30 Hz` (`33.3 ms`) | Co-op: `20 Hz`; competitive shooters: `30–60 Hz` |
| Client Input Send Rate | `30–60 Hz` | Each packet bundles the last `3` unacked inputs for packet-loss resilience |
| Remote Entity Interpolation Buffer | `100 ms` (`2` snapshots @ 20 Hz, `3` @ 30 Hz) | Absorbs `±25 ms` network jitter smoothly |
| Max Lag-Compensation Rewind | `200 ms` | Prevents high-ping players from shooting victims `500 ms` behind cover |
| Max UDP Payload Size (MTU Safe) | `<= 1,200 bytes` | Avoids IP-layer packet fragmentation (`MTU = 1500` minus headers) |
| Per-Client Downstream Budget | `<= 32 KB/s` (`256 kbps`) | Comfortably playable on mobile hotspots and budget broadband |

## Failure modes and fixes

- **Symptom**: Local player movement stutters or rubber-bands every time a server snapshot arrives (`150 ms` RTT).
  - **Fix**: Never snap the local player directly to the server's `T - RTT` snapshot position. Compare the server's authoritative state at `ack_tick` against the client's historical predicted state at `ack_tick`; only replay buffered inputs `(ack_tick + 1 .. current_tick)` if the error exceeds `0.05 m`.
- **Symptom**: Remote players jitter and teleport back and forth even on a low-ping connection.
  - **Fix**: Do not extrapolate or render remote players at the latest received packet timestamp. Buffer incoming snapshots and interpolate linearly (`lerp` / `slerp`) at `render_time = server_clock - 100 ms`.
- **Symptom**: A single `2,400 byte` world-state UDP packet drops constantly on home routers.
  - **Fix**: Packets exceeding `~1,400 bytes` trigger IP fragmentation; if any fragment drops, the entire packet is discarded. Split snapshots into `<= 1,200 byte` chunks and use priority accumulator scheduling.

## Done check

- [ ] Authority table explicitly assigns every gameplay variable (position, HP, inventory, cooldowns) to a single authoritative peer.
- [ ] Local client input prediction includes historical ring-buffer reconciliation (`128` ticks).
- [ ] Server validates movement deltas, fire rates, and line-of-sight before applying any client command.
- [ ] `python3 skills/24-networking-backend/scripts/bandwidth_calculator.py --self-test` exits with code `0`.

## Related files

- [references/authority-and-topology.md](references/authority-and-topology.md)
- [references/prediction-and-reconciliation.md](references/prediction-and-reconciliation.md)
- [references/bandwidth-and-serialization.md](references/bandwidth-and-serialization.md)
- [references/matchmaking-and-lobbies.md](references/matchmaking-and-lobbies.md)
- [references/anti-cheat-and-validation.md](references/anti-cheat-and-validation.md)
- [scripts/bandwidth_calculator.py](scripts/bandwidth_calculator.py)
