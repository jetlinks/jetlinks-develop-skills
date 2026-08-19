#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("evaluate_orchestration_trace.py")
SPEC = importlib.util.spec_from_file_location("evaluate_orchestration_trace", SCRIPT)
assert SPEC and SPEC.loader
EVALUATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EVALUATOR)


def capsule(scope: str) -> dict[str, object]:
    return {
        "objective": f"Map {scope}",
        "decision": "Identify the owning boundary",
        "allowed_scope": [scope],
        "excluded_scope": ["production edits"],
        "inputs": ["source:abc"],
        "acceptance": ["owner cited"],
        "output_contract": ["findings", "evidence"],
        "stop_conditions": ["source drift"],
        "escalation_triggers": ["shared contract decision"],
        "permissions": {"read": [scope], "write": []},
    }


class EvaluateOrchestrationTraceTest(unittest.TestCase):
    def test_accepts_bounded_parallel_scouts(self) -> None:
        trace = {
            "budget": {"max_active": 2, "max_depth": 1},
            "events": [
                {"type": "route", "mode": "PARALLEL_SCOUTS", "rationale": "independent owners"},
                {"type": "delegate", "agent": "a", "assignment_id": "back", "tier": "economy", "depth": 1,
                 "write_set": [], "capsule": capsule("backend")},
                {"type": "delegate", "agent": "b", "assignment_id": "front", "tier": "economy", "depth": 1,
                 "write_set": [], "capsule": capsule("frontend")},
                {"type": "result", "agent": "a", "assignment_id": "back", "status": "success",
                 "evidence": ["Backend.java:20"], "source_fingerprint": "abc"},
                {"type": "result", "agent": "b", "assignment_id": "front", "status": "success",
                 "evidence": ["Page.vue:10"], "source_fingerprint": "abc"},
                {"type": "integrate", "acceptance": ["both owners mapped"],
                 "evidence": ["Backend.java:20", "Page.vue:10"]},
            ],
        }
        result = EVALUATOR.evaluate_trace(trace)
        self.assertTrue(result["passed"], result["errors"])
        self.assertEqual(2, result["metrics"]["max_observed_active"])

    def test_accepts_single_owner_without_delegation(self) -> None:
        result = EVALUATOR.evaluate_trace({
            "events": [{"type": "route", "mode": "SINGLE_OWNER", "rationale": "short coupled task"}]
        })
        self.assertTrue(result["passed"], result["errors"])

    def test_rejects_overlapping_active_writes(self) -> None:
        result = EVALUATOR.evaluate_trace({
            "events": [
                {"type": "route", "mode": "BOUNDED_WORKER", "rationale": "two adapters"},
                {"type": "delegate", "agent": "a", "assignment_id": "a", "tier": "balanced", "write_set": ["api.yaml"],
                 "capsule": capsule("adapter-a")},
                {"type": "delegate", "agent": "b", "assignment_id": "b", "tier": "balanced", "write_set": ["api.yaml"],
                 "capsule": capsule("adapter-b")},
            ]
        })
        self.assertFalse(result["passed"])
        self.assertTrue(any("overlapping active writes" in error for error in result["errors"]))

    def test_rejects_same_slice_retry_without_escalation(self) -> None:
        result = EVALUATOR.evaluate_trace({
            "events": [
                {"type": "route", "mode": "BOUNDED_WORKER", "rationale": "stable contract"},
                {"type": "delegate", "agent": "a", "assignment_id": "slice", "tier": "economy", "write_set": [],
                 "capsule": capsule("slice")},
                {"type": "result", "agent": "a", "assignment_id": "slice", "status": "failed"},
                {"type": "delegate", "agent": "b", "assignment_id": "slice", "tier": "economy", "write_set": [],
                 "capsule": capsule("slice")},
            ]
        })
        self.assertFalse(result["passed"])
        self.assertEqual(1, result["metrics"]["weak_retry_count"])

    def test_rejects_evidence_free_success(self) -> None:
        result = EVALUATOR.evaluate_trace({
            "events": [
                {"type": "route", "mode": "PARALLEL_SCOUTS", "rationale": "bounded scan"},
                {"type": "delegate", "agent": "a", "assignment_id": "scan", "tier": "economy", "write_set": [],
                 "capsule": capsule("scan")},
                {"type": "result", "agent": "a", "assignment_id": "scan", "status": "success",
                 "evidence": [], "source_fingerprint": ""},
                {"type": "integrate", "acceptance": ["scan complete"], "evidence": []},
            ]
        })
        self.assertFalse(result["passed"])
        self.assertTrue(any("successful result lacks evidence" in error for error in result["errors"]))

    def test_rejects_fake_escalation_followed_by_lower_tier(self) -> None:
        result = EVALUATOR.evaluate_trace({
            "events": [
                {"type": "route", "mode": "BOUNDED_WORKER", "rationale": "stable slice"},
                {"type": "delegate", "agent": "a", "assignment_id": "slice", "tier": "economy",
                 "write_set": [], "capsule": capsule("slice")},
                {"type": "result", "agent": "a", "assignment_id": "slice", "status": "failed"},
                {"type": "escalate", "assignment_id": "slice", "from_tier": "economy", "to_tier": "strong",
                 "facts": ["failure moved"], "evidence": ["test.log:20"]},
                {"type": "delegate", "agent": "b", "assignment_id": "slice", "tier": "economy",
                 "write_set": [], "capsule": capsule("slice")},
                {"type": "result", "agent": "b", "assignment_id": "slice", "status": "blocked"},
                {"type": "integrate", "acceptance": ["blocker reported"], "evidence": ["test.log:20"]},
            ]
        })
        self.assertFalse(result["passed"])
        self.assertTrue(any("below escalated tier" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
