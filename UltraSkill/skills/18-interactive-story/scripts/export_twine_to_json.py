#!/usr/bin/env python3
"""
Twee / Markdown Passage to UltraSkill `story_graph.json` Converter (`export_twine_to_json.py`).

Converts human-authored Twee 3 / Twine passage files (`:: node_id [cam=cam_wide speaker=CONSOLE]`)
with wiki-style links (`[[Choice Label->target_node]]`) into the strict JSON schema
validated by `validate_story_graph.py`.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


PASSAGE_HEADER_RE = re.compile(r"^::\s*([a-zA-Z0-9_-]+)(?:\s*\[([^\]]*)\])?\s*$")
LINK_RE = re.compile(r"\[\[([^\]]+?)(?:->|\|)([a-zA-Z0-9_-]+)\]\]")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="export_twine_to_json.py",
        description="Convert a Twee / Markdown passage script into UltraSkill story_graph.json format.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Input .twee or .md passage file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output path for story_graph.json.",
    )
    parser.add_argument(
        "--story-id",
        default="converted_story",
        help="Story identifier string (default: 'converted_story').",
    )
    return parser.parse_args(argv)


def parse_tags(tag_str: str | None) -> dict[str, str]:
    result: dict[str, str] = {}
    if not tag_str:
        return result
    for token in tag_str.split():
        if "=" in token:
            k, v = token.split("=", 1)
            result[k.strip()] = v.strip()
        else:
            result[token.strip()] = "true"
    return result


def convert_twee_text(source_text: str, story_id: str) -> dict:
    nodes: dict[str, dict] = {}
    start_node: str | None = None

    current_id: str | None = None
    current_tags: dict[str, str] = {}
    current_lines: list[str] = []

    def flush_passage() -> None:
        nonlocal start_node
        if current_id is None:
            return
        if start_node is None:
            start_node = current_id

        body_lines: list[str] = []
        choices: list[dict] = []
        for line in current_lines:
            matches = list(LINK_RE.finditer(line))
            if matches:
                for idx, m in enumerate(matches, start=1):
                    label, target = m.group(1).strip(), m.group(2).strip()
                    choices.append(
                        {
                            "id": f"c_{current_id}_{len(choices) + idx}",
                            "label": label,
                            "target": target,
                            "requires": {},
                            "effects": {},
                        }
                    )
            else:
                if line.strip():
                    body_lines.append(line.strip())

        is_terminal = len(choices) == 0 or current_tags.get("terminal") == "true"
        nodes[current_id] = {
            "id": current_id,
            "speaker": current_tags.get("speaker", "NARRATOR").replace("_", " "),
            "text": " ".join(body_lines) or "Scene observation.",
            "camera_mark": current_tags.get("cam", "cam_wide"),
            "scene_cue": current_tags.get("cue", "state_nominal"),
            "terminal": is_terminal,
            "choices": [] if is_terminal else choices,
        }

    for raw_line in source_text.splitlines():
        m = PASSAGE_HEADER_RE.match(raw_line.strip())
        if m:
            flush_passage()
            current_id = m.group(1)
            current_tags = parse_tags(m.group(2))
            current_lines = []
        elif current_id is not None:
            current_lines.append(raw_line)

    flush_passage()

    if not nodes or start_node is None:
        raise ValueError("No valid ':: passage_id' headers found in input file.")

    return {
        "schema_version": "1.0.0",
        "story_id": story_id,
        "title": story_id.replace("_", " ").title(),
        "start_node": start_node,
        "initial_variables": {},
        "camera_marks": {
            "cam_wide": {"position": [0.0, 1.7, 4.2], "target": [0.0, 1.0, 0.0], "fov": 45}
        },
        "nodes": nodes,
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    in_path = args.input.resolve()
    if not in_path.is_file():
        print(f"[ERROR] Input file not found: {in_path}", file=sys.stderr)
        return 1

    try:
        graph = convert_twee_text(in_path.read_text(encoding="utf-8"), args.story_id)
    except Exception as exc:
        print(f"[ERROR] Conversion failed: {exc}", file=sys.stderr)
        return 1

    out_path = args.output.resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(graph, indent=2), encoding="utf-8")
    print(f"[OK] Converted {len(graph['nodes'])} passages -> {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
