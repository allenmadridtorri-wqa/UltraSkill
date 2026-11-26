# Matchmaking, Lobbies, and Reconnection

A multiplayer session needs a clean lifecycle from lobby discovery to seamless drop-in/reconnection without leaving zombie player slots or desynchronized scene loads.

---

## 1. Session & Lobby State Machine

```text
IDLE -> CREATING_OR_JOINING -> LOBBY_WAITING -> LOADING_BARRIER -> IN_PROGRESS -> POST_MATCH_SUMMARY
```

### The `LOADING_BARRIER` Handshake
Never start match timers or spawn enemy waves the instant the Host finishes loading the level (a client on a 4 GB RAM laptop with an HDD/eMMC drive may take 6 seconds longer to load than the host):
1. Server broadcasts `LoadScene(level_id, shared_rng_seed, match_config)`.
2. Each client loads the level asynchronously and sends `SceneLoadComplete(client_id, asset_hash)`.
3. Server waits until **all connected peers** report `SceneLoadComplete` (or a `25.0s` timeout expires), verifies `asset_hash` matches the server's build version, and then broadcasts `StartMatchCountdown(server_start_tick)`.

---

## 2. NAT Traversal & Relay First Design

Never require players to manually configure router port-forwarding (`UDP 7777`) for co-op games:
- **Always default to a Relay / STUN+TURN transport** (Steam Networking Sockets SDR, Epic EOS Relay, or WebRTC with TURN fallback).
- Use short 6-character alphanumeric invite codes (`"K7M-9P2"`) excluding ambiguous glyphs (`0/O`, `1/I/L`) mapped in a lightweight lobby directory service with a `15-minute` TTL heartbeat.

---

## 3. Graceful Reconnection (`30-Second` Reservation Window)

Wi-Fi blips and brief socket drops happen constantly. Do not instantly delete a player's character and inventory on the first timeout packet:

1. **Issue Session Reconnect Token on Join**:
   - On initial join, the server issues an HMAC-signed `reconnect_token` bound to `player_slot_id` and `match_id`.
2. **Zombie/AI Hold State (`30.0 s`)**:
   - When a peer times out (`> 5.0 s` without packets), mark their character `DISCONNECTED_PENDING`, zero their movement input, grant temporary invulnerability or AI follow behavior, and hold their slot for `30.0 seconds`.
3. **Full Baseline Snapshot on Rejoin**:
   - When the peer reconnects with a valid `reconnect_token`, reset their delta-compression baseline to `tick = 0` so the next packet sends a complete full-state snapshot of all active entities and world flags.
