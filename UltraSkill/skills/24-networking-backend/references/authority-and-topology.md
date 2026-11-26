# Authority and Network Topology

Before writing a single network RPC, choose the topology that matches your game's competitive integrity, budget, and simulation scale.

---

## 1. Topology Selection Matrix

| Topology | How It Works | Best For | Fatal Weakness if Misused |
|---|---|---|---|
| **Dedicated Authoritative Server** | Headless cloud server runs simulation; clients send **inputs only** and receive **state snapshots** | Competitive PvP, persistent survival/MMO (`8–64+` players) | Requires server hosting infrastructure |
| **Listen-Server (Host + Relay)** | Player 1 runs both client and server in one process; peers connect via Steam Datagram Relay / WebRTC TURN | 2–4 Player Co-Op, party games | Host has `0 ms` ping advantage; host disconnect requires migration or ends session |
| **Rollback Netcode (Deterministic Lockstep)** | Peers exchange 2-byte inputs per frame; local state rolls back and re-simulates on late remote input | 1v1 Fighting games, 2–4p deterministic arcade | Requires 100% bit-deterministic fixed-point physics across CPUs and low state size |

---

## 2. Single Source of Truth Authority Rules

Even in a friendly 4-player co-op game, allowing two peers to both mutate an enemy's HP causes **split-brain desynchronization** (the enemy dies on Client B's screen while remaining alive at 10 HP on the Host's screen).

| State Domain | Authoritative Owner | Client Behavior |
|---|---|---|
| **Player Input Commands** | Owning Client | Sampled at `60 Hz`, transmitted to Server with monotonic `tick_id` |
| **Player Transform & Velocity** | Server | Client predicts locally; Server validates and reconciles |
| **Weapon Fire & Hit Registration** | Server | Client spawns instant visual muzzle flash/tracer; Server rewinds hurtboxes and confirms damage |
| **AI Pathfinding & Combat Decisions** | Server | Clients receive enemy transform, animation state ID, and target ID only |
| **Inventory, Currency, Loot Drops** | Server / Backend DB | Client sends `RequestEquip(slot)`; UI updates optimistically with rollback on rejection |

---

## 3. Transport Channel Discipline (UDP / ENet / WebRTC DataChannels)

Never send high-frequency player positions over a single head-of-line blocking TCP or reliable-ordered stream:
- **Channel 0 — Unreliable Unordered (or Sequenced)**:
  - High-frequency world snapshots (`20–30 Hz`) and client input frames (`60 Hz`). If snapshot `#104` drops, you never want the socket to stall snapshot `#105` waiting for a retransmit of stale data.
- **Channel 1 — Reliable Ordered**:
  - Match lifecycle transitions, chat messages, inventory transactions, quest state changes.
- **Channel 2 — Reliable Unordered (or Event Piggybacking)**:
  - Discrete combat events (spawn explosion VFX, damage numbers, audio triggers).
