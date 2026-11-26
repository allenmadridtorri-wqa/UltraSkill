#!/usr/bin/env python3
"""Calculate multiplayer UDP packet sizes, per-client downstream/upstream bitrates, and MTU safety."""

import argparse
import json
import math
import sys
from typing import Any, Dict


UDP_IP_HEADER_BYTES = 28
PACKET_ENVELOPE_BYTES = 10  # sequence, ack, ack_bitfield, server_tick
MTU_SAFE_PAYLOAD_BYTES = 1200


def calculate_bandwidth(
    players: int,
    active_npcs: int,
    snapshot_hz: int,
    input_hz: int,
    avg_changed_ratio: float = 0.45,
    bytes_per_entity_delta: int = 14,
) -> Dict[str, Any]:
    total_entities = players + active_npcs
    changed_entities_per_tick = math.ceil(total_entities * avg_changed_ratio)

    snapshot_payload_bytes = PACKET_ENVELOPE_BYTES + (changed_entities_per_tick * bytes_per_entity_delta)
    packets_per_snapshot = math.ceil(snapshot_payload_bytes / MTU_SAFE_PAYLOAD_BYTES)
    wire_bytes_per_snapshot = snapshot_payload_bytes + (packets_per_snapshot * UDP_IP_HEADER_BYTES)

    client_downstream_bps = wire_bytes_per_snapshot * snapshot_hz
    client_downstream_kbps = round(client_downstream_bps / 1024.0, 2)

    # Client upstream sends 3 bundled inputs (8 bytes each) + header
    input_payload_bytes = PACKET_ENVELOPE_BYTES + (3 * 8)
    client_upstream_bps = (input_payload_bytes + UDP_IP_HEADER_BYTES) * input_hz
    client_upstream_kbps = round(client_upstream_bps / 1024.0, 2)

    server_total_egress_kbps = round(client_downstream_kbps * players, 2)
    server_total_ingress_kbps = round(client_upstream_kbps * players, 2)

    within_budget = (
        client_downstream_kbps <= 32.0
        and client_upstream_kbps <= 8.0
        and packets_per_snapshot == 1
    )

    return {
        "players": players,
        "active_npcs": active_npcs,
        "snapshot_hz": snapshot_hz,
        "changed_entities_per_tick": changed_entities_per_tick,
        "snapshot_payload_bytes": snapshot_payload_bytes,
        "packets_per_snapshot": packets_per_snapshot,
        "mtu_safe": snapshot_payload_bytes <= MTU_SAFE_PAYLOAD_BYTES,
        "client_downstream_KBps": client_downstream_kbps,
        "client_upstream_KBps": client_upstream_kbps,
        "server_total_egress_KBps": server_total_egress_kbps,
        "server_total_ingress_KBps": server_total_ingress_kbps,
        "within_32KBps_budget": within_budget,
    }


def run_self_test() -> int:
    # 4-player co-op with 24 active enemies at 20 Hz
    report = calculate_bandwidth(players=4, active_npcs=24, snapshot_hz=20, input_hz=30)
    if not report["within_32KBps_budget"]:
        print(f"Self-test failed: {report}", file=sys.stderr)
        return 1
    print(
        f"Self-test PASSED: 4P+24NPC @ 20Hz uses {report['client_downstream_KBps']} KB/s down "
        f"({report['snapshot_payload_bytes']} B/pkt <= {MTU_SAFE_PAYLOAD_BYTES} B MTU)."
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--players", type=int, default=4, help="Connected players")
    parser.add_argument("--npcs", type=int, default=24, help="Networked NPCs/projectiles")
    parser.add_argument("--snapshot-hz", type=int, default=20, help="Server snapshot send rate (Hz)")
    parser.add_argument("--input-hz", type=int, default=30, help="Client input send rate (Hz)")
    parser.add_argument("--self-test", action="store_true", help="Run built-in bandwidth self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    rep = calculate_bandwidth(args.players, args.npcs, args.snapshot_hz, args.input_hz)
    print(json.dumps(rep, indent=2))
    return 0 if rep["within_32KBps_budget"] else 1


if __name__ == "__main__":
    sys.exit(main())
