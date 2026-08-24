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
        "acceptance_owner": "primary",
        "output_contract": ["findings", "evidence"],
        "stop_conditions": ["source drift"],
        "escalation_triggers": ["shared contract decision"],
        "permissions": {"read": [scope], "write": []},
    }


def authority_capsule(scope: str, *, parent: str = "primary", depth: int = 1,
                      delegation: str = "denied") -> dict[str, object]:
    value = capsule(scope)
    value.update({
        "parent_assignment_id": parent,
        "depth": depth,
        "budget": {"token_budget": 1000, "max_children": 0 if delegation == "denied" else 1},
        "delegation": delegation,
    })
    return value


def acceptance(assignment: str, *, artifacts_checked: bool = False,
               status: str = "accepted", signals: dict[str, object] | None = None,
               stage_id: str | None = None) -> dict[str, object]:
    event: dict[str, object] = {
        "type": "accept",
        "assignment_id": assignment,
        "owner": "primary",
        "status": status,
        "scope_checked": True,
        "artifacts_checked": artifacts_checked,
        "source_fingerprint": "abc",
        "acceptance_matrix": signals or {"owner cited": ["evidence:1"]},
    }
    if stage_id is not None:
        event["stage_id"] = stage_id
    return event


def with_write_permission(value: dict[str, object], *paths: str) -> dict[str, object]:
    value["permissions"] = {"read": list(paths), "write": list(paths)}
    return value


def program(*, contract_state: str = "frozen", dependency_status: str = "completed") -> dict[str, object]:
    return {
        "program_id": "full-stack-feature",
        "primary_role": "ORCHESTRATOR_INTEGRATOR",
        "current_stage": "implementation",
        "stages": [
            {
                "stage_id": "design",
                "objective": "Freeze API contract",
                "depends_on": [],
                "entry_gate": "requirements mapped",
                "route_mode": "SINGLE_OWNER",
                "exit_gate": "contract revision recorded",
                "status": dependency_status,
            },
            {
                "stage_id": "implementation",
                "objective": "Implement disjoint frontend and backend slices",
                "depends_on": ["design"],
                "entry_gate": "API contract frozen",
                "route_mode": "BOUNDED_WORKER",
                "exit_gate": "accepted artifacts integrated",
                "status": "active",
            },
        ],
        "shared_contracts": [
            {"contract_id": "feature-api", "revision": "r1", "state": contract_state, "owner": "primary"},
        ],
    }


def program_capsule(scope: str, *paths: str, revision: str = "r1") -> dict[str, object]:
    value = with_write_permission(capsule(scope), *paths)
    value.update({"depends_on": ["design"], "contract_revisions": {"feature-api": revision}})
    return value


class EvaluateOrchestrationTraceTest(unittest.TestCase):
    def test_accepts_legacy_single_stage_trace_without_v2_receipts(self) -> None:
        legacy_capsule = capsule("backend")
        legacy_capsule.pop("acceptance_owner")
        result = EVALUATOR.evaluate_trace({
            "events": [
                {"type": "route", "mode": "PARALLEL_SCOUTS", "rationale": "legacy bounded scan"},
                {"type": "delegate", "agent": "a", "assignment_id": "scan", "tier": "economy",
                 "write_set": [], "capsule": legacy_capsule},
                {"type": "result", "agent": "a", "assignment_id": "scan", "status": "success",
                 "evidence": ["Owner.java:10"], "source_fingerprint": "abc"},
                {"type": "integrate", "acceptance": ["scan complete"], "evidence": ["Owner.java:10"]},
            ],
        })
        self.assertTrue(result["passed"], result["errors"])

    def test_accepts_bounded_parallel_scouts(self) -> None:
        trace = {
            "budget": {"max_active": 2, "max_depth": 1},
            "events": [
                {"type": "route", "mode": "PARALLEL_SCOUTS", "rationale": "independent owners"},
                {"type": "delegate", "agent": "a", "assignment_id": "back", "tier": "economy", "depth": 1,
                 "dispatch_receipt": "host:back", "write_set": [], "capsule": capsule("backend")},
                {"type": "delegate", "agent": "b", "assignment_id": "front", "tier": "economy", "depth": 1,
                 "dispatch_receipt": "host:front", "write_set": [], "capsule": capsule("frontend")},
                {"type": "result", "agent": "a", "assignment_id": "back", "status": "success",
                 "evidence": ["Backend.java:20"], "source_fingerprint": "abc"},
                {"type": "result", "agent": "b", "assignment_id": "front", "status": "success",
                 "evidence": ["Page.vue:10"], "source_fingerprint": "abc"},
                acceptance("back"),
                acceptance("front"),
                {"type": "integrate", "acceptance": ["both owners mapped"],
                 "evidence": ["Backend.java:20", "Page.vue:10"]},
            ],
        }
        result = EVALUATOR.evaluate_trace(trace)
        self.assertTrue(result["passed"], result["errors"])
        self.assertEqual(2, result["metrics"]["max_observed_active"])
        self.assertEqual(2, result["metrics"]["dispatch_receipts"])

    def test_accepts_single_owner_without_delegation(self) -> None:
        result = EVALUATOR.evaluate_trace({
            "events": [{"type": "route", "mode": "SINGLE_OWNER", "rationale": "short coupled task"}]
        })
        self.assertTrue(result["passed"], result["errors"])

    def test_accepts_v3_leaf_with_denied_delegation(self) -> None:
        result = EVALUATOR.evaluate_trace({
            "schema_version": 3,
            "budget": {"max_active": 1, "max_depth": 1},
            "events": [
                {"type": "route", "mode": "PARALLEL_SCOUTS", "rationale": "bounded evidence"},
                {"type": "delegate", "agent": "leaf", "assignment_id": "scan", "tier": "economy",
                 "depth": 1, "dispatch_receipt": "host:scan", "write_set": [],
                 "capsule": authority_capsule("backend")},
                {"type": "result", "agent": "leaf", "assignment_id": "scan", "status": "success",
                 "evidence": ["Owner.java:10"], "source_fingerprint": "abc"},
                acceptance("scan"),
                {"type": "integrate", "acceptance": ["scan accepted"], "evidence": ["Owner.java:10"]},
            ],
        })
        self.assertTrue(result["passed"], result["errors"])

    def test_rejects_v3_brokered_delegation_without_enforced_broker(self) -> None:
        result = EVALUATOR.evaluate_trace({
            "schema_version": 3,
            "budget": {"max_active": 1, "max_depth": 1},
            "events": [
                {"type": "route", "mode": "BOUNDED_WORKER", "rationale": "claimed manager"},
                {"type": "delegate", "agent": "manager", "assignment_id": "stage", "tier": "strong",
                 "depth": 1, "dispatch_receipt": "host:stage", "write_set": [],
                 "capsule": authority_capsule("modules", delegation="brokered")},
            ],
        })
        self.assertFalse(result["passed"])
        self.assertTrue(any("requires spawn_broker_enforced=true" in error for error in result["errors"]))

    def test_rejects_v3_nested_scope_expansion(self) -> None:
        result = EVALUATOR.evaluate_trace({
            "schema_version": 3,
            "budget": {"max_active": 2, "max_depth": 2, "spawn_broker_enforced": True},
            "events": [
                {"type": "route", "mode": "BOUNDED_WORKER", "rationale": "brokered nested slice"},
                {"type": "delegate", "agent": "manager", "assignment_id": "stage", "tier": "strong",
                 "depth": 1, "dispatch_receipt": "host:stage", "write_set": [],
                 "capsule": authority_capsule("module-a", delegation="brokered")},
                {"type": "delegate", "agent": "leaf", "assignment_id": "child", "tier": "balanced",
                 "depth": 2, "dispatch_receipt": "host:child", "write_set": [],
                 "capsule": authority_capsule("module-b", parent="stage", depth=2)},
            ],
        })
        self.assertFalse(result["passed"])
        self.assertTrue(any("child allowed_scope exceeds parent authority" in error for error in result["errors"]))

    def test_rejects_v3_nested_permission_and_budget_expansion(self) -> None:
        parent = authority_capsule("module-a", delegation="brokered")
        parent["permissions"] = {
            "read": ["module-a"], "write": ["module-a.py"],
            "external_side_effects": [], "secrets": [],
        }
        child = authority_capsule("module-a", parent="stage", depth=2)
        child["permissions"] = {
            "read": ["module-a"], "write": ["module-a.py", "module-b.py"],
            "external_side_effects": [], "secrets": [],
        }
        child["budget"] = {"token_budget": 2000, "max_children": 2}
        result = EVALUATOR.evaluate_trace({
            "schema_version": 3,
            "budget": {"max_active": 2, "max_depth": 2, "spawn_broker_enforced": True},
            "events": [
                {"type": "route", "mode": "BOUNDED_WORKER", "rationale": "brokered nested slice"},
                {"type": "delegate", "agent": "manager", "assignment_id": "stage", "tier": "strong",
                 "depth": 1, "dispatch_receipt": "host:stage", "write_set": ["module-a.py"],
                 "capsule": parent},
                {"type": "delegate", "agent": "leaf", "assignment_id": "child", "tier": "balanced",
                 "depth": 2, "dispatch_receipt": "host:child", "write_set": ["module-a.py", "module-b.py"],
                 "capsule": child},
            ],
        })
        self.assertFalse(result["passed"])
        self.assertTrue(any("child permissions.write exceeds parent authority" in error for error in result["errors"]))
        self.assertTrue(any("child budget.token_budget exceeds parent authority" in error for error in result["errors"]))

    def test_rejects_overlapping_active_writes(self) -> None:
        first_capsule = with_write_permission(capsule("adapter-a"), "api.yaml")
        second_capsule = with_write_permission(capsule("adapter-b"), "api.yaml")
        result = EVALUATOR.evaluate_trace({
            "events": [
                {"type": "route", "mode": "BOUNDED_WORKER", "rationale": "two adapters"},
                {"type": "delegate", "agent": "a", "assignment_id": "a", "tier": "balanced", "write_set": ["api.yaml"],
                 "dispatch_receipt": "host:a", "capsule": first_capsule},
                {"type": "delegate", "agent": "b", "assignment_id": "b", "tier": "balanced", "write_set": ["api.yaml"],
                 "dispatch_receipt": "host:b", "capsule": second_capsule},
            ]
        })
        self.assertFalse(result["passed"])
        self.assertTrue(any("overlapping active writes" in error for error in result["errors"]))

    def test_rejects_same_slice_retry_without_escalation(self) -> None:
        result = EVALUATOR.evaluate_trace({
            "events": [
                {"type": "route", "mode": "BOUNDED_WORKER", "rationale": "stable contract"},
                {"type": "delegate", "agent": "a", "assignment_id": "slice", "tier": "economy", "write_set": [],
                 "dispatch_receipt": "host:a", "capsule": capsule("slice")},
                {"type": "result", "agent": "a", "assignment_id": "slice", "status": "failed"},
                {"type": "delegate", "agent": "b", "assignment_id": "slice", "tier": "economy", "write_set": [],
                 "dispatch_receipt": "host:b", "capsule": capsule("slice")},
            ]
        })
        self.assertFalse(result["passed"])
        self.assertEqual(1, result["metrics"]["weak_retry_count"])

    def test_rejects_evidence_free_success(self) -> None:
        result = EVALUATOR.evaluate_trace({
            "events": [
                {"type": "route", "mode": "PARALLEL_SCOUTS", "rationale": "bounded scan"},
                {"type": "delegate", "agent": "a", "assignment_id": "scan", "tier": "economy", "write_set": [],
                 "dispatch_receipt": "host:scan", "capsule": capsule("scan")},
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
                 "dispatch_receipt": "host:a", "write_set": [], "capsule": capsule("slice")},
                {"type": "result", "agent": "a", "assignment_id": "slice", "status": "failed"},
                {"type": "escalate", "assignment_id": "slice", "from_tier": "economy", "to_tier": "strong",
                 "facts": ["failure moved"], "evidence": ["test.log:20"]},
                {"type": "delegate", "agent": "b", "assignment_id": "slice", "tier": "economy",
                 "dispatch_receipt": "host:b", "write_set": [], "capsule": capsule("slice")},
                {"type": "result", "agent": "b", "assignment_id": "slice", "status": "blocked"},
                {"type": "integrate", "acceptance": ["blocker reported"], "evidence": ["test.log:20"]},
            ]
        })
        self.assertFalse(result["passed"])
        self.assertTrue(any("below escalated tier" in error for error in result["errors"]))

    def test_rejects_delegated_route_without_real_dispatch(self) -> None:
        result = EVALUATOR.evaluate_trace({
            "events": [
                {"type": "route", "mode": "PARALLEL_SCOUTS", "rationale": "independent review scopes"},
            ]
        })
        self.assertFalse(result["passed"])
        self.assertTrue(any("requires at least one accepted dispatch" in error for error in result["errors"]))

    def test_rejects_delegate_without_dispatch_receipt(self) -> None:
        result = EVALUATOR.evaluate_trace({
            "schema_version": 2,
            "events": [
                {"type": "route", "mode": "BOUNDED_WORKER", "rationale": "stable disjoint slice"},
                {"type": "delegate", "agent": "a", "assignment_id": "slice", "tier": "balanced",
                 "write_set": [], "capsule": capsule("slice")},
            ]
        })
        self.assertFalse(result["passed"])
        self.assertTrue(any("lacks accepted dispatch_receipt" in error for error in result["errors"]))

    def test_rejects_delegate_under_single_owner_route(self) -> None:
        result = EVALUATOR.evaluate_trace({
            "events": [
                {"type": "route", "mode": "SINGLE_OWNER", "rationale": "short coupled task"},
                {"type": "delegate", "agent": "a", "assignment_id": "slice", "tier": "economy",
                 "dispatch_receipt": "host:a", "write_set": [], "capsule": capsule("slice")},
            ]
        })
        self.assertFalse(result["passed"])
        self.assertTrue(any("must not contain delegate events" in error for error in result["errors"]))

    def test_accepts_economy_mechanical_write_after_primary_acceptance(self) -> None:
        write_capsule = with_write_permission(capsule("adapter.py"), "adapter.py")
        write_capsule.update({
            "execution_class": "mechanical",
            "contract_state": "frozen",
            "oracle": "deterministic",
            "risk_flags": [],
            "reversible": True,
        })
        result = EVALUATOR.evaluate_trace({
            "events": [
                {"type": "route", "mode": "BOUNDED_WORKER", "rationale": "large frozen rewrite"},
                {"type": "delegate", "agent": "luna", "assignment_id": "slice", "tier": "economy",
                 "dispatch_receipt": "host:luna", "write_set": ["adapter.py"], "capsule": write_capsule},
                {"type": "result", "agent": "luna", "assignment_id": "slice", "status": "success",
                 "evidence": ["adapter.py", "test:pass"], "source_fingerprint": "abc"},
                acceptance("slice", artifacts_checked=True),
                {"type": "integrate", "acceptance": ["owner cited"], "evidence": ["adapter.py", "test:pass"]},
            ]
        })
        self.assertTrue(result["passed"], result["errors"])
        self.assertEqual(1, result["metrics"]["acceptances"])

    def test_rejects_economy_write_without_admission_fields(self) -> None:
        write_capsule = with_write_permission(capsule("adapter.py"), "adapter.py")
        result = EVALUATOR.evaluate_trace({
            "events": [
                {"type": "route", "mode": "BOUNDED_WORKER", "rationale": "claimed mechanical rewrite"},
                {"type": "delegate", "agent": "luna", "assignment_id": "slice", "tier": "economy",
                 "dispatch_receipt": "host:luna", "write_set": ["adapter.py"], "capsule": write_capsule},
            ]
        })
        self.assertFalse(result["passed"])
        self.assertTrue(any("economy write requires" in error for error in result["errors"]))

    def test_rejects_worker_success_without_primary_acceptance(self) -> None:
        result = EVALUATOR.evaluate_trace({
            "events": [
                {"type": "route", "mode": "PARALLEL_SCOUTS", "rationale": "bounded scan"},
                {"type": "delegate", "agent": "a", "assignment_id": "scan", "tier": "economy",
                 "dispatch_receipt": "host:scan", "write_set": [], "capsule": capsule("scan")},
                {"type": "result", "agent": "a", "assignment_id": "scan", "status": "success",
                 "evidence": ["Owner.java:10"], "source_fingerprint": "abc"},
                {"type": "integrate", "acceptance": ["scan complete"], "evidence": ["Owner.java:10"]},
            ]
        })
        self.assertFalse(result["passed"])
        self.assertTrue(any("without acceptance" in error for error in result["errors"]))

    def test_rejects_incomplete_acceptance_matrix(self) -> None:
        two_signal_capsule = capsule("scan")
        two_signal_capsule["acceptance"] = ["owner cited", "consumer cited"]
        result = EVALUATOR.evaluate_trace({
            "events": [
                {"type": "route", "mode": "PARALLEL_SCOUTS", "rationale": "bounded scan"},
                {"type": "delegate", "agent": "a", "assignment_id": "scan", "tier": "economy",
                 "dispatch_receipt": "host:scan", "write_set": [], "capsule": two_signal_capsule},
                {"type": "result", "agent": "a", "assignment_id": "scan", "status": "success",
                 "evidence": ["Owner.java:10"], "source_fingerprint": "abc"},
                acceptance("scan"),
                {"type": "integrate", "acceptance": ["scan complete"], "evidence": ["Owner.java:10"]},
            ]
        })
        self.assertFalse(result["passed"])
        self.assertTrue(any("consumer cited" in error for error in result["errors"]))

    def test_accepts_primary_rejection_then_balanced_escalation(self) -> None:
        write_capsule = with_write_permission(capsule("adapter.py"), "adapter.py")
        write_capsule.update({
            "execution_class": "mechanical",
            "contract_state": "frozen",
            "oracle": "deterministic",
            "risk_flags": [],
            "reversible": True,
        })
        result = EVALUATOR.evaluate_trace({
            "events": [
                {"type": "route", "mode": "BOUNDED_WORKER", "rationale": "frozen adapter rewrite"},
                {"type": "delegate", "agent": "luna", "assignment_id": "slice", "tier": "economy",
                 "dispatch_receipt": "host:luna", "write_set": ["adapter.py"], "capsule": write_capsule},
                {"type": "result", "agent": "luna", "assignment_id": "slice", "status": "success",
                 "evidence": ["adapter.py:scope-drift"], "source_fingerprint": "abc"},
                acceptance("slice", artifacts_checked=True, status="rejected"),
                {"type": "escalate", "assignment_id": "slice", "from_tier": "economy", "to_tier": "balanced",
                 "facts": ["scope drift found"], "evidence": ["adapter.py:scope-drift"]},
                {"type": "delegate", "agent": "terra", "assignment_id": "slice", "tier": "balanced",
                 "dispatch_receipt": "host:terra", "write_set": ["adapter.py"],
                 "capsule": with_write_permission(capsule("adapter.py"), "adapter.py")},
                {"type": "result", "agent": "terra", "assignment_id": "slice", "status": "success",
                 "evidence": ["adapter.py", "test:pass"], "source_fingerprint": "abc"},
                acceptance("slice", artifacts_checked=True),
                {"type": "integrate", "acceptance": ["owner cited"], "evidence": ["adapter.py", "test:pass"]},
            ]
        })
        self.assertTrue(result["passed"], result["errors"])
        self.assertEqual(1, result["metrics"]["rejections"])
        self.assertEqual(1, result["metrics"]["escalations"])

    def test_rejects_same_tier_retry_after_primary_rejection(self) -> None:
        result = EVALUATOR.evaluate_trace({
            "events": [
                {"type": "route", "mode": "PARALLEL_SCOUTS", "rationale": "bounded scan"},
                {"type": "delegate", "agent": "a", "assignment_id": "scan", "tier": "economy",
                 "dispatch_receipt": "host:a", "write_set": [], "capsule": capsule("scan")},
                {"type": "result", "agent": "a", "assignment_id": "scan", "status": "success",
                 "evidence": ["Owner.java:10"], "source_fingerprint": "abc"},
                acceptance("scan", status="rejected"),
                {"type": "delegate", "agent": "b", "assignment_id": "scan", "tier": "economy",
                 "dispatch_receipt": "host:b", "write_set": [], "capsule": capsule("scan")},
            ]
        })
        self.assertFalse(result["passed"])
        self.assertEqual(1, result["metrics"]["weak_retry_count"])

    def test_rejects_write_set_that_differs_from_capsule_permissions(self) -> None:
        result = EVALUATOR.evaluate_trace({
            "events": [
                {"type": "route", "mode": "BOUNDED_WORKER", "rationale": "bounded write"},
                {"type": "delegate", "agent": "terra", "assignment_id": "slice", "tier": "balanced",
                 "dispatch_receipt": "host:terra", "write_set": ["actual.py"],
                 "capsule": with_write_permission(capsule("declared.py"), "declared.py")},
            ]
        })
        self.assertFalse(result["passed"])
        self.assertTrue(any("write_set does not match" in error for error in result["errors"]))

    def test_rejects_escalation_that_lies_about_failed_tier(self) -> None:
        result = EVALUATOR.evaluate_trace({
            "events": [
                {"type": "route", "mode": "BOUNDED_WORKER", "rationale": "stable slice"},
                {"type": "delegate", "agent": "strong", "assignment_id": "slice", "tier": "strong",
                 "dispatch_receipt": "host:strong", "write_set": [], "capsule": capsule("slice")},
                {"type": "result", "agent": "strong", "assignment_id": "slice", "status": "failed"},
                {"type": "escalate", "assignment_id": "slice", "from_tier": "economy", "to_tier": "balanced",
                 "facts": ["failed"], "evidence": ["test.log:1"]},
                {"type": "delegate", "agent": "terra", "assignment_id": "slice", "tier": "balanced",
                 "dispatch_receipt": "host:terra", "write_set": [], "capsule": capsule("slice")},
            ]
        })
        self.assertFalse(result["passed"])
        self.assertTrue(any("does not match failed tier" in error for error in result["errors"]))

    def test_accepts_program_with_frozen_contract_and_manager_actions(self) -> None:
        trace = {
            "program": program(),
            "events": [
                {"type": "route", "stage_id": "implementation", "mode": "BOUNDED_WORKER",
                 "rationale": "frozen API allows disjoint frontend and backend writes"},
                {"type": "delegate", "stage_id": "implementation", "agent": "backend",
                 "assignment_id": "backend", "tier": "balanced", "dispatch_receipt": "host:backend",
                 "write_set": ["service.py"], "capsule": program_capsule("backend", "service.py")},
                {"type": "primary_action", "stage_id": "implementation", "action_class": "coordination",
                 "write_set": []},
                {"type": "delegate", "stage_id": "implementation", "agent": "frontend",
                 "assignment_id": "frontend", "tier": "balanced", "dispatch_receipt": "host:frontend",
                 "write_set": ["page.ts"], "capsule": program_capsule("frontend", "page.ts")},
                {"type": "result", "stage_id": "implementation", "agent": "backend",
                 "assignment_id": "backend", "status": "success", "evidence": ["service.py:test"],
                 "source_fingerprint": "abc"},
                {"type": "result", "stage_id": "implementation", "agent": "frontend",
                 "assignment_id": "frontend", "status": "success", "evidence": ["page.ts:test"],
                 "source_fingerprint": "abc"},
                acceptance("backend", artifacts_checked=True, stage_id="implementation"),
                acceptance("frontend", artifacts_checked=True, stage_id="implementation"),
                {"type": "primary_action", "stage_id": "implementation", "action_class": "integration",
                 "write_set": []},
                {"type": "integrate", "stage_id": "implementation", "acceptance": ["both accepted"],
                 "evidence": ["service.py:test", "page.ts:test"]},
            ],
        }
        result = EVALUATOR.evaluate_trace(trace)
        self.assertTrue(result["passed"], result["errors"])
        self.assertEqual(1, result["metrics"]["programs"])
        self.assertEqual(2, result["metrics"]["program_stages"])
        self.assertEqual(2, result["metrics"]["primary_actions"])
        self.assertEqual(0, result["metrics"]["contract_gate_violations"])

    def test_rejects_program_with_unfinished_stage_dependency(self) -> None:
        result = EVALUATOR.evaluate_trace({
            "program": program(dependency_status="active"),
            "events": [
                {"type": "route", "stage_id": "implementation", "mode": "BOUNDED_WORKER",
                 "rationale": "claimed ready"},
            ],
        })
        self.assertFalse(result["passed"])
        self.assertTrue(any("dependency 'design' must be completed" in error for error in result["errors"]))

    def test_rejects_unresolved_or_mismatched_program_contract(self) -> None:
        unresolved = EVALUATOR.evaluate_trace({
            "program": program(contract_state="proposed"),
            "events": [
                {"type": "route", "stage_id": "implementation", "mode": "BOUNDED_WORKER",
                 "rationale": "claimed ready"},
                {"type": "delegate", "stage_id": "implementation", "agent": "backend",
                 "assignment_id": "backend", "tier": "balanced", "dispatch_receipt": "host:backend",
                 "write_set": ["service.py"], "capsule": program_capsule("backend", "service.py")},
            ],
        })
        mismatch = EVALUATOR.evaluate_trace({
            "program": program(),
            "events": [
                {"type": "route", "stage_id": "implementation", "mode": "BOUNDED_WORKER",
                 "rationale": "claimed ready"},
                {"type": "delegate", "stage_id": "implementation", "agent": "backend",
                 "assignment_id": "backend", "tier": "balanced", "dispatch_receipt": "host:backend",
                 "write_set": ["service.py"],
                 "capsule": program_capsule("backend", "service.py", revision="r0")},
            ],
        })
        self.assertFalse(unresolved["passed"])
        self.assertFalse(mismatch["passed"])
        self.assertEqual(1, unresolved["metrics"]["contract_gate_violations"])
        self.assertEqual(1, mismatch["metrics"]["contract_gate_violations"])

    def test_rejects_program_worker_that_omits_shared_contract_revision(self) -> None:
        worker_capsule = program_capsule("backend", "service.py")
        worker_capsule["contract_revisions"] = {}
        result = EVALUATOR.evaluate_trace({
            "program": program(),
            "events": [
                {"type": "route", "stage_id": "implementation", "mode": "BOUNDED_WORKER",
                 "rationale": "claimed ready"},
                {"type": "delegate", "stage_id": "implementation", "agent": "backend",
                 "assignment_id": "backend", "tier": "balanced", "dispatch_receipt": "host:backend",
                 "write_set": ["service.py"], "capsule": worker_capsule},
            ],
        })
        self.assertFalse(result["passed"])
        self.assertTrue(any("must cover program shared contracts" in error for error in result["errors"]))

    def test_rejects_primary_leaf_implementation_or_overlapping_write_while_worker_active(self) -> None:
        trace = {
            "program": program(),
            "events": [
                {"type": "route", "stage_id": "implementation", "mode": "BOUNDED_WORKER",
                 "rationale": "frozen API"},
                {"type": "delegate", "stage_id": "implementation", "agent": "backend",
                 "assignment_id": "backend", "tier": "balanced", "dispatch_receipt": "host:backend",
                 "write_set": ["service.py"], "capsule": program_capsule("backend", "service.py")},
                {"type": "primary_action", "stage_id": "implementation",
                 "action_class": "leaf_implementation", "write_set": []},
                {"type": "primary_action", "stage_id": "implementation", "action_class": "coordination",
                 "write_set": ["service.py"]},
            ],
        }
        result = EVALUATOR.evaluate_trace(trace)
        self.assertFalse(result["passed"])
        self.assertEqual(1, result["metrics"]["primary_leaf_violations"])
        self.assertTrue(any("leaf_implementation is forbidden" in error for error in result["errors"]))
        self.assertTrue(any("overlaps active worker" in error for error in result["errors"]))

    def test_rejects_program_event_with_wrong_stage_id(self) -> None:
        result = EVALUATOR.evaluate_trace({
            "program": program(),
            "events": [
                {"type": "route", "stage_id": "design", "mode": "BOUNDED_WORKER",
                 "rationale": "wrong stage"},
            ],
        })
        self.assertFalse(result["passed"])
        self.assertTrue(any("route.stage_id must match" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
