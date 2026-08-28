#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("evaluate_route_trace.py")
SPEC = importlib.util.spec_from_file_location("evaluate_route_trace", SCRIPT)
assert SPEC and SPEC.loader
EVALUATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EVALUATOR)


def action(
    action_id: str = "inspect-owner",
    action_type: str = "check",
    **fields: object,
) -> dict[str, object]:
    result: dict[str, object] = {
        "action_id": action_id,
        "type": action_type,
        "owner": "router",
        "scope": ["bounded:owner"],
        "observable_signal": "the owning boundary is identified",
    }
    result.update(fields)
    return result


def new_route() -> dict[str, object]:
    return {
        "route_envelope": {
            "current_decision": "identify the owning boundary",
            "minimum_skills": ["systematic-solving", "code-navigation"],
            "user_confirmation_required": "none",
            "unique_next": action(),
        },
        "events": [
            {"type": "skill_load", "skill": "systematic-solving"},
            {"type": "skill_load", "skill": "code-navigation"},
            {"type": "action", "action_id": "inspect-owner", "productive": True},
        ],
    }


class RouterTraceTest(unittest.TestCase):
    def test_accepts_exact_minimum_skill_route(self) -> None:
        result = EVALUATOR.evaluate_trace(new_route())
        self.assertTrue(result["passed"], result["errors"])

    def test_rejects_unadmitted_skill_load(self) -> None:
        trace = new_route()
        trace["events"].insert(2, {"type": "skill_load", "skill": "jetlinks-delivery"})
        result = EVALUATOR.evaluate_trace(trace)
        self.assertFalse(result["passed"])
        self.assertEqual(1, result["metrics"]["extra_loaded_skill_count"])

    def test_matching_compact_route_reuses_rules_and_hits_saved_next(self) -> None:
        trace = new_route()
        trace["recovery"] = {
            "type": "COMPACT_CONTINUATION",
            "identity_match": True,
            "instruction_changed": False,
            "loaded_rules_match": True,
            "saved_next_action_id": "inspect-owner",
        }
        trace["events"] = [
            {"type": "action", "action_id": "inspect-owner", "productive": True},
        ]
        result = EVALUATOR.evaluate_trace(trace)
        self.assertTrue(result["passed"], result["errors"])
        self.assertTrue(result["metrics"]["saved_next_action_hit"])

    def test_matching_compact_route_rejects_reload_and_reclassification(self) -> None:
        trace = new_route()
        trace["recovery"] = {
            "type": "COMPACT_CONTINUATION",
            "identity_match": True,
            "instruction_changed": False,
            "loaded_rules_match": True,
            "saved_next_action_id": "inspect-owner",
        }
        trace["events"] = [
            {"type": "skill_load", "skill": "systematic-solving"},
            {"type": "ordinary_classification"},
            {"type": "action", "action_id": "inspect-owner", "productive": True},
        ]
        result = EVALUATOR.evaluate_trace(trace)
        self.assertFalse(result["passed"])
        self.assertTrue(any("without skill reloads" in error for error in result["errors"]))
        self.assertTrue(any("ordinary classification" in error for error in result["errors"]))

    def test_open_semantic_fork_rejects_solution_route(self) -> None:
        trace = new_route()
        trace["route_envelope"]["unique_next"] = action(
            "implement", "mutation", purpose="solution"
        )
        trace["semantic_fork"] = {"status": "OPEN"}
        trace["evidence_budget"] = {
            "round": 1, "scout_count": 0, "status": "STOPPED", "stop_reason": "ASK_USER",
        }
        result = EVALUATOR.evaluate_trace(trace)
        self.assertFalse(result["passed"])
        self.assertTrue(any("cannot route authoritative" in error for error in result["errors"]))

    def test_accepts_dispatch_and_collect_actions(self) -> None:
        for unique_next in (
            action("dispatch-scout", "dispatch", work_class="evidence_scout"),
            action("collect-scout", "collect"),
        ):
            with self.subTest(action_type=unique_next["type"]):
                trace = new_route()
                trace["route_envelope"]["unique_next"] = unique_next
                trace["events"][-1]["action_id"] = unique_next["action_id"]
                result = EVALUATOR.evaluate_trace(trace)
                self.assertTrue(result["passed"], result["errors"])

    def test_open_semantic_fork_allows_observation_setup_and_scout_dispatch(self) -> None:
        for unique_next in (
            action("prepare-observation", "mutation", purpose="observation_setup"),
            action("dispatch-scout", "dispatch", work_class="evidence_scout"),
        ):
            with self.subTest(action_type=unique_next["type"]):
                trace = new_route()
                trace["route_envelope"]["unique_next"] = unique_next
                trace["events"][-1]["action_id"] = unique_next["action_id"]
                trace["semantic_fork"] = {"status": "OPEN"}
                trace["evidence_budget"] = {
                    "round": 1,
                    "scout_count": 0,
                    "status": "OPEN",
                }
                result = EVALUATOR.evaluate_trace(trace)
                self.assertTrue(result["passed"], result["errors"])

    def test_open_semantic_fork_rejects_implementation_dispatch(self) -> None:
        trace = new_route()
        trace["route_envelope"]["unique_next"] = action(
            "dispatch-implementation", "dispatch", work_class="implementation"
        )
        trace["events"][-1]["action_id"] = "dispatch-implementation"
        trace["semantic_fork"] = {"status": "OPEN"}
        trace["evidence_budget"] = {
            "round": 1,
            "scout_count": 0,
            "status": "OPEN",
        }
        result = EVALUATOR.evaluate_trace(trace)
        self.assertFalse(result["passed"])
        self.assertTrue(any("bounded evidence scout" in error for error in result["errors"]))

    def test_rejects_first_action_that_does_not_match_unique_next(self) -> None:
        trace = new_route()
        trace["events"][-1]["action_id"] = "adjacent-work"
        result = EVALUATOR.evaluate_trace(trace)
        self.assertFalse(result["passed"])
        self.assertTrue(any("first productive action" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
