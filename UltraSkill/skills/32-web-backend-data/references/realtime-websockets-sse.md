# Realtime WebSockets and Server-Sent Events (SSE)

Choose the lightest protocol that fits your communication direction:

| Requirement | Best Protocol | Why |
|---|---|---|
| **Server -> Client One-Way Stream** (Render progress bars, live logs, notifications, ticker feeds) | **Server-Sent Events (`EventSource` / `text/event-stream`)** | Standard HTTP, built-in browser auto-reconnect with `Last-Event-ID`, works seamlessly through standard proxies |
| **Low-Latency Bidirectional Messaging** (Collaborative whiteboards, chat, live camera sync) | **WebSockets (`wss://`)** | Persistent full-duplex framing after HTTP `101 Switching Protocols` upgrade |

---

## 1. Server-Sent Events (SSE) Wire Format & Resume

1. **Response Headers**:
   - `Content-Type: text/event-stream`
   - `Cache-Control: no-cache`
   - `Connection: keep-alive`
   - `X-Accel-Buffering: no` (prevents Nginx from buffering small chunks!)
2. **Event Framing with Monotonic `id:`**:
   ```text
   id: 1042
   event: frame_completed
   data: {"frame": 48, "elapsed_sec": 3.42, "status": "OK"}

   ```
   - Send a comment keepalive line (`: heartbeat\n\n`) every **`20 seconds`** so idle load balancers never drop the connection.
   - When a client reconnects, read the `Last-Event-ID` request header to replay missed events since `1042`.

---

## 2. WebSocket Hardening (Heartbeats, Backpressure, Auth)

1. **Ping/Pong Dead-Peer Detection**:
   - TCP connections silently die when a laptop closes its lid or switches Wi-Fi networks.
   - Server sends a WebSocket `Ping` (or application `{"type": "ping"}`) every `25 seconds`. If no `Pong` arrives within `10 seconds`, terminate the socket and clean up subscriptions.
2. **Backpressure Protection (`bufferedAmount`)**:
   - Before broadcasting high-frequency updates to a client socket, check `ws.bufferedAmount`.
   - If `ws.bufferedAmount > 512 * 1024` (`512 KB`), drop non-critical telemetry frames for that slow client or disconnect abusive stalled readers so a single throttled connection cannot exhaust server RAM.
3. **Reconnect with Exponential Backoff + Jitter**:
   - On client `onclose`, never reconnect in an instant `setTimeout(connect, 0)` loop. Use `delay = min(15000, 500 * (2 ** attempt)) * (0.5 + Math.random() * 0.5)`.
