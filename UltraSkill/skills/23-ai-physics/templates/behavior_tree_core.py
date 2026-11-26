#!/usr/bin/env python3
"""Minimal, deterministic Behavior Tree and Squad Attack Token coordinator with self-test."""

import argparse
import enum
import sys
from typing import Any, Callable, Dict, List


class Status(enum.Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RUNNING = "RUNNING"


class Blackboard:
    """Shared or per-agent key-value memory store with squad attack token management."""

    def __init__(self, initial: Dict[str, Any] | None = None) -> None:
        self.data: Dict[str, Any] = dict(initial or {})

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value


class SquadCoordinator:
    """Prevents enemy dogpiling by limiting concurrent melee attack tokens."""

    def __init__(self, max_tokens: int = 2) -> None:
        self.max_tokens = max_tokens
        self.holders: set[str] = set()

    def request_token(self, agent_id: str) -> bool:
        if agent_id in self.holders:
            return True
        if len(self.holders) < self.max_tokens:
            self.holders.add(agent_id)
            return True
        return False

    def release_token(self, agent_id: str) -> None:
        self.holders.discard(agent_id)


class BTNode:
    def tick(self, agent_bb: Blackboard, squad: SquadCoordinator) -> Status:
        raise NotImplementedError


class Sequence(BTNode):
    def __init__(self, children: List[BTNode]) -> None:
        self.children = children

    def tick(self, agent_bb: Blackboard, squad: SquadCoordinator) -> Status:
        for child in self.children:
            res = child.tick(agent_bb, squad)
            if res != Status.SUCCESS:
                return res
        return Status.SUCCESS


class Selector(BTNode):
    def __init__(self, children: List[BTNode]) -> None:
        self.children = children

    def tick(self, agent_bb: Blackboard, squad: SquadCoordinator) -> Status:
        for child in self.children:
            res = child.tick(agent_bb, squad)
            if res != Status.FAILURE:
                return res
        return Status.FAILURE


class Condition(BTNode):
    def __init__(self, fn: Callable[[Blackboard, SquadCoordinator], bool]) -> None:
        self.fn = fn

    def tick(self, agent_bb: Blackboard, squad: SquadCoordinator) -> Status:
        return Status.SUCCESS if self.fn(agent_bb, squad) else Status.FAILURE


class Action(BTNode):
    def __init__(self, fn: Callable[[Blackboard, SquadCoordinator], Status]) -> None:
        self.fn = fn

    def tick(self, agent_bb: Blackboard, squad: SquadCoordinator) -> Status:
        return self.fn(agent_bb, squad)


def build_tactical_melee_tree() -> BTNode:
    """Build a canonical 3-branch melee AI tree: Flee -> MeleeStrike (token-gated) -> FlankStrafe."""
    flee_branch = Sequence([
        Condition(lambda bb, _: bb.get("hp_ratio", 1.0) < 0.20),
        Action(lambda bb, sq: (sq.release_token(bb.get("id")), bb.set("action", "RETREAT_TO_COVER"), Status.SUCCESS)[2]),
    ])

    attack_branch = Sequence([
        Condition(lambda bb, _: bb.get("target_visible", False) and bb.get("target_dist", 99.0) <= 3.0),
        Condition(lambda bb, sq: sq.request_token(bb.get("id"))),
        Action(lambda bb, _: (bb.set("action", "MELEE_COMBO"), Status.RUNNING)[1]),
    ])

    strafe_branch = Action(
        lambda bb, _: (bb.set("action", "FLANK_STRAFE_OUTER_RING"), Status.RUNNING)[1]
    )

    return Selector([flee_branch, attack_branch, strafe_branch])


def run_self_test() -> int:
    squad = SquadCoordinator(max_tokens=2)
    tree = build_tactical_melee_tree()

    agents = [
        Blackboard({"id": f"enemy_{i}", "hp_ratio": 1.0, "target_visible": True, "target_dist": 2.2})
        for i in range(4)
    ]

    for a in agents:
        tree.tick(a, squad)

    attackers = [a.get("id") for a in agents if a.get("action") == "MELEE_COMBO"]
    strafers = [a.get("id") for a in agents if a.get("action") == "FLANK_STRAFE_OUTER_RING"]

    assert len(attackers) == 2, f"Expected exactly 2 attackers, got {attackers}"
    assert len(strafers) == 2, f"Expected 2 outer-ring strafers, got {strafers}"

    # Wounded attacker retreats and releases token to waiting strafer
    agents[0].set("hp_ratio", 0.10)
    tree.tick(agents[0], squad)
    tree.tick(agents[2], squad)
    assert agents[0].get("action") == "RETREAT_TO_COVER"
    assert agents[2].get("action") == "MELEE_COMBO"

    print("Self-test PASSED: Squad Attack Token gating and BT fallback verified.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="Run tactical BT self-test")
    parser.parse_args()
    return run_self_test()


if __name__ == "__main__":
    sys.exit(main())
