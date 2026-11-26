#!/usr/bin/env python3
"""
Interactive Story Graph Invariant Validator (`validate_story_graph.py`).

Audits a `story_graph.json` file against all `18-interactive-story` gates:
  1. `start_node` exists in `nodes`.
  2. Every choice `target` resolves to an existing node ID in `nodes`.
  3. Every node in `nodes` is reachable from `start_node` via Breadth-First Search.
  4. At least one valid `terminal: true` ending node is reachable from every node
     (zero inescapable infinite loops).
  5. Every non-terminal node (`terminal: false`) has at least one choice with an
     empty `"requires": {}` guard so the player can never get soft-locked.
  6. All variable keys referenced in `requires` and `effects` are declared in
     `initial_variables`.
  7. Every node's `camera_mark` exists in `camera_marks`, and `text` is <= `--max-words`.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import deque
from pathlib import Path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="validate_story_graph.py",
        description="Validate a story_graph.json file for unreachable nodes, dead ends, and undeclared flags.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to the story_graph.json file to validate.",
    )
    parser.add_argument(
        "--max-words",
        type=int,
        default=45,
        help="Maximum allowed words per dialogue node text (default: 45 starting value).",
    )
    return parser.parse_args(argv)


def validate_graph(data: dict, max_words: int) -> list[str]:
    errors: list[str] = []
    nodes: dict = data.get("nodes", {})
    start_node: str = data.get("start_node", "")
    init_vars: dict = data.get("initial_variables", {})
    camera_marks: dict = data.get("camera_marks", {})

    if not nodes:
        return ["story_graph.json contains zero nodes."]
    if start_node not in nodes:
        errors.append(f"start_node '{start_node}' does not exist in nodes.")
        return errors

    for node_id, node in nodes.items():
        text = str(node.get("text", "")).strip()
        word_count = len(text.split())
        if word_count == 0:
            errors.append(f"Node '{node_id}': empty text.")
        elif word_count > max_words:
            errors.append(f"Node '{node_id}': text has {word_count} words (max allowed is {max_words}).")

        cam_mark = node.get("camera_mark")
        if camera_marks and cam_mark not in camera_marks:
            errors.append(f"Node '{node_id}': camera_mark '{cam_mark}' not found in camera_marks.")

        is_terminal = bool(node.get("terminal", False))
        choices = node.get("choices", [])

        if is_terminal and choices:
            errors.append(f"Node '{node_id}': marked terminal=true but defines {len(choices)} outgoing choices.")
        if not is_terminal:
            if not choices:
                errors.append(f"Node '{node_id}': marked terminal=false but has zero outgoing choices (dead end).")
            else:
                has_unconditional = any(not c.get("requires") for c in choices)
                if not has_unconditional:
                    errors.append(
                        f"Node '{node_id}': every choice has precondition guards ('requires'); "
                        "at least 1 unconditional fallback choice is required to prevent soft-locks."
                    )

        for choice in choices:
            cid = choice.get("id", "<unnamed>")
            target = choice.get("target", "")
            if target not in nodes:
                errors.append(f"Node '{node_id}' choice '{cid}': target '{target}' does not exist in nodes.")
            for var_key in choice.get("requires", {}):
                if var_key not in init_vars:
                    errors.append(
                        f"Node '{node_id}' choice '{cid}': requires undeclared variable '{var_key}'."
                    )
            for var_key in choice.get("effects", {}):
                if var_key not in init_vars:
                    errors.append(
                        f"Node '{node_id}' choice '{cid}': mutates undeclared variable '{var_key}'."
                    )

    # Forward BFS reachability from start_node
    reachable: set[str] = set()
    queue: deque[str] = deque([start_node])
    while queue:
        curr = queue.popleft()
        if curr in reachable or curr not in nodes:
            continue
        reachable.add(curr)
        for ch in nodes[curr].get("choices", []):
            tgt = ch.get("target")
            if tgt in nodes and tgt not in reachable:
                queue.append(tgt)

    unreachable = sorted(set(nodes.keys()) - reachable)
    for u in unreachable:
        errors.append(f"Node '{u}' is unreachable from start_node '{start_node}'.")

    # Reverse BFS from all terminal nodes to verify every node can reach an ending
    terminals = [nid for nid, n in nodes.items() if n.get("terminal", False)]
    if not terminals:
        errors.append("Graph contains zero terminal=true ending nodes.")
    else:
        can_reach_terminal: set[str] = set(terminals)
        changed = True
        while changed:
            changed = False
            for nid, n in nodes.items():
                if nid in can_reach_terminal:
                    continue
                for ch in n.get("choices", []):
                    if ch.get("target") in can_reach_terminal:
                        can_reach_terminal.add(nid)
                        changed = True
                        break
        trapped = sorted(set(nodes.keys()) - can_reach_terminal)
        for t in trapped:
            errors.append(f"Node '{t}' has no path to any terminal ending node (infinite loop trap).")

    return errors


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    in_path = args.input.resolve()
    if not in_path.is_file():
        print(f"[ERROR] File not found: {in_path}", file=sys.stderr)
        return 1

    try:
        data = json.loads(in_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"[ERROR] Invalid JSON in {in_path}: {exc}", file=sys.stderr)
        return 1

    errors = validate_graph(data, args.max_words)
    if errors:
        print(f"[FAIL] Story graph validation failed for {in_path}:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print(
        f"[OK] Story graph '{data.get('story_id')}' ({len(data.get('nodes', {}))} nodes) "
        "passed reachability, soft-lock, and schema validation."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
