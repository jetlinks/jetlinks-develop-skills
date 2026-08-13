#!/usr/bin/env python3

from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path


SCRIPT_ROOT = Path(__file__).parent


def load_script(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_ROOT / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


STATE = load_script("validate_continuity_state")
TRACE = load_script("evaluate_continuity_trace")


def valid_state() -> dict:
    action = {
        "action_id": "implement-validator",
        "type": "mutation",
        "owner": "task-continuity/scripts/validate_continuity_state.py",
        "scope": ["validator"],
        "observable_signal": "state fixtures return the expected gate",
    }
    return {
        "recovery_capsule": {
            "contract": {
                "boundary_id": "b7",
                "task_id": "continuity-tools",
                "revision": "contract-r3",
                "objective": "make continuation state executable",
                "acceptance": ["matching state reaches READY"],
            },
            "checkpoint": {"boundary_id": "b7", "phase": "implementation", "validated": [], "in_flight": {}},
            "decision_state": {
                "boundary_id": "b7",
                "active_hypothesis": "missing deterministic execution layer",
                "acceptance_status": "in_progress",
            },
            "resume": {
                "boundary_id": "b7",
                "gate": "RESUME_AUDIT",
                "anchors": ["task-continuity/scripts"],
                "next": copy.deepcopy(action),
                "first_allowed_action": copy.deepcopy(action),
            },
        },
        "continuity_metadata": {
            "boundary_id": "b7",
            "audit_fingerprint": "audit-3",
            "consecutive_matching_audits": 1,
            "referenced_sources": [{"id": "trellis-docs", "revision": "0.6.14"}],
            "loaded_rules": [{"id": "task-continuity", "revision": "sha256:rules"}],
        },
        "source_snapshot": {
            "boundary_id": "b7",
            "source_id": "workspace",
            "source_fingerprint": "sha256:tree",
            "strength": "full",
            "locator": "workspace-state",
            "expected_changed_items": ["task-continuity/scripts"],
            "missing_layers": [],
        },
        "observed": {
            "boundary_id": "b7",
            "source_fingerprint": "sha256:tree",
            "contract_revision": "contract-r3",
            "referenced_sources": {"trellis-docs": "0.6.14"},
            "loaded_rules": {"task-continuity": "sha256:rules"},
        },
    }


class ContinuityStateTest(unittest.TestCase):
    def test_matching_observations_transition_to_ready(self) -> None:
        result = STATE.validate_state(valid_state())
        self.assertTrue(result["valid"])
        self.assertTrue(result["ready"])
        self.assertEqual("READY", result["suggested_gate"])

    def test_vague_next_requires_snapshot(self) -> None:
        document = valid_state()
        for field in ("next", "first_allowed_action"):
            action = document["recovery_capsule"]["resume"][field]
            action.pop("action_id")
            action["owner"] = "continue analysis"
        result = STATE.validate_state(document)
        self.assertFalse(result["valid"])
        self.assertEqual("SNAPSHOT_REQUIRED", result["suggested_gate"])
        self.assertIn("action.vague", {item["code"] for item in result["errors"]})

    def test_reference_revision_change_invalidates_saved_next(self) -> None:
        document = valid_state()
        document["observed"]["referenced_sources"]["trellis-docs"] = "0.7.0"
        result = STATE.validate_state(document)
        self.assertTrue(result["valid"])
        self.assertFalse(result["ready"])
        self.assertEqual("SNAPSHOT_REQUIRED", result["suggested_gate"])
        self.assertEqual("mismatch", result["comparisons"]["references"])

    def test_user_contract_revision_change_invalidates_saved_next(self) -> None:
        document = valid_state()
        document["observed"]["contract_revision"] = "contract-r4"
        result = STATE.validate_state(document)
        self.assertTrue(result["valid"])
        self.assertEqual("SNAPSHOT_REQUIRED", result["suggested_gate"])
        self.assertEqual("mismatch", result["comparisons"]["contract"])

    def test_validated_stage_requires_evidence_and_checkpoint(self) -> None:
        document = valid_state()
        document["recovery_capsule"]["checkpoint"]["validated"] = [{"stage": "scripts"}]
        result = STATE.validate_state(document)
        codes = {item["code"] for item in result["errors"]}
        self.assertIn("checkpoint.missing_evidence", codes)
        self.assertIn("checkpoint.missing_identity", codes)

    def test_partial_fingerprint_must_declare_risk(self) -> None:
        document = valid_state()
        document["source_snapshot"]["strength"] = "partial(untracked)"
        document["source_snapshot"]["missing_layers"] = ["untracked"]
        result = STATE.validate_state(document)
        self.assertIn("snapshot.partial_risk_missing", {item["code"] for item in result["errors"]})


class ContinuityTraceTest(unittest.TestCase):
    def test_detects_idle_reads_duplicate_check_and_prd_leak(self) -> None:
        metrics = TRACE.evaluate_trace(
            {
                "expected_action_id": "patch",
                "events": [
                    {"type": "read", "target": "PRD", "revision": "r1", "scope": "full_prd", "recovery_id": "r1"},
                    {"type": "read", "target": "PRD", "revision": "r1", "scope": "full_prd", "recovery_id": "r1"},
                    {"type": "mutation", "action_id": "patch", "turn": 2, "recovery_id": "r2"},
                    {"type": "check", "check_id": "unit", "source_fingerprint": "s1", "input_revision": "i1", "environment": "e1"},
                    {"type": "check", "check_id": "unit", "source_fingerprint": "s1", "input_revision": "i1", "environment": "e1"},
                    {"type": "prd_write", "content_classes": ["test_counts", "stage_progress"]},
                ],
            }
        )
        self.assertEqual(1, metrics["repeated_read_count"])
        self.assertEqual(1, metrics["repeated_verification_count"])
        self.assertEqual(["r1"], metrics["idle_recovery_ids"])
        self.assertEqual(1, metrics["authoritative_runtime_leak_count"])
        self.assertTrue(metrics["next_action_hit"])

    def test_rejects_python_graph_for_java_task(self) -> None:
        metrics = TRACE.evaluate_trace(
            {
                "source_fingerprint": "java-tree",
                "events": [
                    {
                        "type": "graph_injection",
                        "decision_question": "who calls AgentService",
                        "task_anchor": "AgentService",
                        "task_source_fingerprint": "java-tree",
                        "graph_source_fingerprint": "python-tree",
                        "task_languages": ["java"],
                        "graph_languages": ["python"],
                    }
                ],
            }
        )
        reasons = metrics["irrelevant_graph_injections"][0]["reasons"]
        self.assertIn("source_fingerprint_mismatch", reasons)
        self.assertIn("target_language_mismatch", reasons)

    def test_compares_full_capsule_and_ablation_context(self) -> None:
        document = {
            "expected_action_id": "patch",
            "required_constraint_ids": ["no-special-case"],
            "required_evidence_ids": ["failure-signature"],
            "runs": {
                "full_context": {
                    "events": [
                        {"type": "read", "target": "history", "scope": "full_history"},
                        {"type": "decision", "constraint_ids": ["no-special-case"], "evidence_ids": ["failure-signature"]},
                        {"type": "mutation", "action_id": "patch", "turn": 3},
                    ]
                },
                "capsule": {
                    "events": [
                        {"type": "capsule_read", "target": "capsule"},
                        {"type": "decision", "constraint_ids": ["no-special-case"], "evidence_ids": ["failure-signature"]},
                        {"type": "mutation", "action_id": "patch", "turn": 2},
                    ]
                },
                "ablation": {"events": [{"type": "mutation", "action_id": "patch", "turn": 1}]},
            },
        }
        result = TRACE.evaluate_document(document)
        self.assertTrue(result["assessment"]["capsule_preserves_required_context"])
        self.assertTrue(result["assessment"]["capsule_not_slower_to_first_action"])
        self.assertTrue(result["assessment"]["ablation_exposes_context_loss"])


if __name__ == "__main__":
    unittest.main()
