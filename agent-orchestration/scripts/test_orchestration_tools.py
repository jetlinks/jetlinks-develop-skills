#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import copy
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
        "directive_revision": "directive-r1",
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


def semantic_fork(status: str = "RESOLVED", *, source: str = "EVIDENCE",
                  evidence_can_decide: object | None = None) -> dict[str, object]:
    if evidence_can_decide is None:
        evidence_can_decide = source == "EVIDENCE"
    value: dict[str, object] = {
        "decision_question": "Which boundary owns the behavior?",
        "status": status,
        "evidence_can_decide": evidence_can_decide,
        "options": [
            {"id": "boundary-a", "contract": "Boundary A owns the behavior"},
            {"id": "boundary-b", "contract": "Boundary B owns the behavior"},
        ] if status != "NOT_APPLICABLE" else [],
        "architectural_consequences": {
            "ownership": "The selected boundary becomes the behavior owner",
            "public_contract": "Consumers bind to the selected boundary",
        } if status != "NOT_APPLICABLE" else {},
    }
    if status == "RESOLVED":
        value["resolution"] = {
            "source": source,
            "decision": "boundary-a",
            "locator": "decision:1",
        }
    return value


def v4_capsule(scope: str, work_class: str) -> dict[str, object]:
    value = authority_capsule(scope)
    value["work_class"] = work_class
    return value


def compact_capsule(
    scope: str,
    work_class: str,
    *,
    write_set: list[str] | None = None,
) -> dict[str, object]:
    writes = list(write_set or [])
    return {
        "profile": "compact",
        "objective": f"Complete the bounded {scope} slice",
        "decision": f"Whether the {scope} slice satisfies its acceptance signal",
        "allowed_scope": [scope],
        "acceptance": ["slice behavior verified"],
        "permissions": {"read": [scope], "write": writes},
        "directive_revision": "directive-r1",
        "work_class": work_class,
        "source_fingerprint": "abc",
    }


def scout_capsule(scope: str, axis: str, *, round_number: int = 1,
                  expansion_reason: str | None = None) -> dict[str, object]:
    value = v4_capsule(scope, "evidence_scout")
    value.update({
        "decision": "Which boundary owns the behavior?",
        "hypothesis": f"{scope} owns the behavior",
        "discriminator": f"Find direct ownership evidence in {scope}",
        "evidence_axis": axis,
        "scout_round": round_number,
    })
    if expansion_reason is not None:
        value["expansion_reason"] = expansion_reason
    return value


def v4_program(*, stage_kind: str = "implementation",
               contract_state: str = "frozen") -> dict[str, object]:
    stages: list[dict[str, object]] = [
        {
            "stage_id": "decision",
            "stage_kind": "semantic_decision_contract_freeze",
            "objective": "Resolve semantics and freeze contract",
            "depends_on": [],
            "required_contracts": [],
            "entry_gate": "decision question known",
            "route_mode": "SINGLE_OWNER",
            "exit_gate": "semantic decision and contract revision recorded",
            "status": "completed" if stage_kind != "semantic_decision_contract_freeze" else "active",
        }
    ]
    if stage_kind == "implementation":
        stages.append({
            "stage_id": "implementation",
            "stage_kind": "implementation",
            "objective": "Implement accepted slices",
            "depends_on": ["decision"],
            "required_contracts": ["feature-api"],
            "entry_gate": "semantic fork resolved and contract frozen",
            "route_mode": "BOUNDED_WORKER",
            "exit_gate": "accepted artifacts integrated",
            "status": "active",
        })
    return {
        "program_id": "admission-program",
        "primary_role": "ORCHESTRATOR_INTEGRATOR",
        "current_stage": "implementation" if stage_kind == "implementation" else "decision",
        "stages": stages,
        "shared_contracts": [
            {"contract_id": "feature-api", "revision": "r1", "state": contract_state,
             "owner": "primary"},
        ],
    }


def compact_cross_module_trace() -> dict[str, object]:
    backend = compact_capsule(
        "backend", "implementation", write_set=["backend/service.py"]
    )
    frontend = compact_capsule(
        "frontend", "implementation", write_set=["frontend/page.ts"]
    )
    for value in (backend, frontend):
        value.update({"depends_on": ["decision"], "contract_revisions": {"feature-api": "r1"}})
    return {
        "schema_version": 5,
        "semantic_fork": semantic_fork(),
        "program": v4_program(),
        "budget": {"max_active": 2, "max_depth": 1},
        "events": [
            {"type": "route", "stage_id": "implementation", "mode": "BOUNDED_WORKER",
             "decision_question": "Which boundary owns the behavior?",
             "rationale": "two disjoint slices consume one frozen contract"},
            {"type": "delegate", "stage_id": "implementation", "agent": "backend-worker",
             "assignment_id": "backend-r1", "tier": "balanced", "depth": 1,
             "dispatch_receipt": "host:backend-r1", "write_set": ["backend/service.py"],
             "capsule": backend},
            {"type": "delegate", "stage_id": "implementation", "agent": "frontend-worker",
             "assignment_id": "frontend-r1", "tier": "balanced", "depth": 1,
             "dispatch_receipt": "host:frontend-r1", "write_set": ["frontend/page.ts"],
             "capsule": frontend},
            {"type": "result", "stage_id": "implementation", "agent": "backend-worker",
             "assignment_id": "backend-r1", "status": "success",
             "directive_revision": "directive-r1", "contract_revisions": {"feature-api": "r1"},
             "changed_artifacts": ["backend/service.py"], "evidence": ["backend:test"],
             "unverified_items": [], "scope_or_contract_conflicts": [],
             "source_fingerprint": "abc"},
            {"type": "result", "stage_id": "implementation", "agent": "frontend-worker",
             "assignment_id": "frontend-r1", "status": "success",
             "directive_revision": "directive-r1", "contract_revisions": {"feature-api": "r1"},
             "changed_artifacts": ["frontend/page.ts"], "evidence": ["frontend:typecheck"],
             "unverified_items": [], "scope_or_contract_conflicts": [],
             "source_fingerprint": "abc"},
            acceptance("backend-r1", artifacts_checked=True,
                       signals={"slice behavior verified": ["backend:test"]},
                       stage_id="implementation"),
            acceptance("frontend-r1", artifacts_checked=True,
                       signals={"slice behavior verified": ["frontend:typecheck"]},
                       stage_id="implementation"),
            {"type": "integrate", "stage_id": "implementation",
             "acceptance": ["both slices accepted against feature-api:r1"],
             "evidence": ["backend:test", "frontend:typecheck"]},
        ],
    }


def review_disposition_trace(reason: str) -> dict[str, object]:
    review_program = {
        "program_id": "review-program",
        "primary_role": "ORCHESTRATOR_INTEGRATOR",
        "current_stage": "review",
        "stages": [
            {"stage_id": "integration", "stage_kind": "integration",
             "objective": "Integrate accepted work", "depends_on": [],
             "required_contracts": [], "entry_gate": "accepted work", "route_mode": "SINGLE_OWNER",
             "exit_gate": "candidate retained", "status": "completed"},
            {"stage_id": "review", "stage_kind": "review", "objective": "Review material risk",
             "depends_on": ["integration"], "required_contracts": [],
             "entry_gate": "retained candidate", "route_mode": "INDEPENDENT_REVIEW",
             "exit_gate": "findings integrated", "status": "active",
             "review_targets": ["artifact-r1"], "material_risks": ["security"]},
        ],
        "shared_contracts": [],
    }
    reviewer = v4_capsule("artifact-r1", "review")
    reviewer.update({
        "review_targets": ["artifact-r1"],
        "material_risks": ["security"],
        "depends_on": ["integration"],
        "contract_revisions": {},
    })
    return {
        "schema_version": 4,
        "semantic_fork": semantic_fork(),
        "artifacts": [{"artifact_id": "artifact-r1", "status": "retained"}],
        "program": review_program,
        "events": [
            {"type": "route", "stage_id": "review", "mode": "INDEPENDENT_REVIEW",
             "decision_question": "Which boundary owns the behavior?",
             "rationale": "retained artifact has material security risk"},
            {"type": "delegate", "stage_id": "review", "agent": "reviewer",
             "assignment_id": "review", "tier": "strong", "depth": 1,
             "dispatch_receipt": "host:review", "write_set": [], "capsule": reviewer},
            {"type": "result", "stage_id": "review", "agent": "reviewer",
             "assignment_id": "review", "status": "success", "evidence": ["finding:1"],
             "source_fingerprint": "abc"},
            acceptance("review", stage_id="review"),
            {"type": "artifact_disposition", "artifact_id": "artifact-r1",
             "status": "discarded", "reason": reason, "evidence": ["decision:2"]},
            {"type": "integrate", "stage_id": "review", "acceptance": ["finding recorded"],
             "evidence": ["finding:1"]},
        ],
    }


class EvaluateOrchestrationTraceTest(unittest.TestCase):
    def test_dependency_must_be_accepted_before_consumer_dispatch(self) -> None:
        for dependency in ("backend-r1", "unknown-artifact"):
            with self.subTest(dependency=dependency):
                trace = compact_cross_module_trace()
                trace["events"][2]["capsule"]["depends_on"] = [dependency]
                result = EVALUATOR.evaluate_trace(trace)
                self.assertFalse(result["passed"])
                self.assertTrue(any("already accepted assignment" in error for error in result["errors"]))
        trace = compact_cross_module_trace()
        events = trace["events"]
        events[2]["capsule"]["depends_on"] = ["backend-r1"]
        trace["events"] = [events[index] for index in (0, 1, 3, 5, 2, 4, 6, 7)]
        result = EVALUATOR.evaluate_trace(trace)
        self.assertTrue(result["passed"], result["errors"])

    def test_integration_cannot_precede_dispatch_or_terminal_collection(self) -> None:
        for index in (1, 3):
            with self.subTest(index=index):
                trace = compact_cross_module_trace()
                trace["events"].insert(index, trace["events"].pop())
                result = EVALUATOR.evaluate_trace(trace)
                self.assertFalse(result["passed"])
                self.assertTrue(any("integration" in error for error in result["errors"]))

    def test_each_accepted_result_requires_later_integration(self) -> None:
        trace = compact_cross_module_trace()
        trace["events"][-1]["assignment_ids"] = ["backend-r1"]
        result = EVALUATOR.evaluate_trace(trace)
        self.assertFalse(result["passed"])
        self.assertTrue(any("frontend-r1" in error and "subsequent integration" in error for error in result["errors"]))

    def test_required_evidence_rejects_booleans_and_malformed_locators(self) -> None:
        for value in (False, True, 1, [False], {"agreed": True}, [""]):
            for event_type in ("result", "accept"):
                with self.subTest(value=value, event_type=event_type):
                    trace = compact_cross_module_trace()
                    for event in trace["events"]:
                        if event["type"] == event_type:
                            if event_type == "result":
                                event["evidence"] = value
                            else:
                                event["acceptance_matrix"] = {"slice behavior verified": value}
                    result = EVALUATOR.evaluate_trace(trace)
                    self.assertFalse(result["passed"])
                    self.assertTrue(any("evidence" in error for error in result["errors"]))

    def test_passive_user_messages_preserve_running_assignments(self) -> None:
        trace = compact_cross_module_trace()
        trace["events"][3:3] = [
            {"type": "user_message", "message_class": "QUERY"},
            {"type": "user_message", "message_class": "REMINDER"},
        ]
        result = EVALUATOR.evaluate_trace(trace)
        self.assertTrue(result["passed"], result["errors"])
        self.assertEqual(2, result["metrics"]["delegations"])
        self.assertEqual(2, result["metrics"]["accepted_assignments"])
        trace["events"][3]["directive_changed"] = True
        self.assertFalse(EVALUATOR.evaluate_trace(trace)["passed"])

    def test_scoped_directive_change_preserves_unaffected_work_and_requires_fresh_assignment(self) -> None:
        trace = compact_cross_module_trace()
        events = trace["events"]
        new_delegate = copy.deepcopy(events[1])
        new_delegate.update(agent="backend-new", assignment_id="backend-r2", dispatch_receipt="host:backend-r2", supersedes="backend-r1")
        new_delegate["capsule"]["directive_revision"] = "directive-r2"
        new_result = copy.deepcopy(events[3])
        new_result.update(agent="backend-new", assignment_id="backend-r2", directive_revision="directive-r2")
        new_acceptance = copy.deepcopy(events[5])
        new_acceptance["assignment_id"] = "backend-r2"
        update = {
            "type": "directive_update", "owner": "primary", "directive_revision": "directive-r2",
            "affected_assignment_ids": ["backend-r1"], "stopped_assignment_ids": ["backend-r1"],
            "evidence": ["user:scoped-constraint"],
        }
        trace["events"] = events[:3] + [update, events[4], events[6], new_delegate, new_result, new_acceptance, events[7]]
        result = EVALUATOR.evaluate_trace(trace)
        self.assertTrue(result["passed"], result["errors"])
        self.assertEqual(2, result["metrics"]["accepted_assignments"])
        stale = copy.deepcopy(trace)
        stale["events"].insert(4, events[3])
        result = EVALUATOR.evaluate_trace(stale)
        self.assertFalse(result["passed"])
        self.assertTrue(any("superseded directive" in error for error in result["errors"]))
        stale = copy.deepcopy(trace)
        stale["events"][6]["capsule"]["directive_revision"] = "directive-r1"
        self.assertFalse(EVALUATOR.evaluate_trace(stale)["passed"])

    def test_contract_change_invalidates_previously_accepted_results(self) -> None:
        trace = compact_cross_module_trace()
        trace["events"].insert(-1, {
            "type": "contract_update", "owner": "primary", "contract_revisions": {"feature-api": "r2"},
            "stopped_assignment_ids": [], "evidence": ["user:new-shared-contract"],
        })
        result = EVALUATOR.evaluate_trace(trace)
        self.assertFalse(result["passed"])
        self.assertTrue(any("no current accepted result" in error for error in result["errors"]))

    def test_contract_change_accepts_fresh_results_after_invalidating_old_acceptance(self) -> None:
        trace = compact_cross_module_trace()
        initial = trace["events"]
        fresh = copy.deepcopy(initial[1:7])
        for event in fresh:
            event["assignment_id"] = event["assignment_id"].replace("-r1", "-r2")
            if "agent" in event:
                event["agent"] += "-new"
            if event["type"] == "delegate":
                event["supersedes"] = event["assignment_id"].replace("-r2", "-r1")
                event["dispatch_receipt"] += "-new"
                event["capsule"]["contract_revisions"] = {"feature-api": "r2"}
            elif event["type"] == "result":
                event["contract_revisions"] = {"feature-api": "r2"}
        trace["events"] = initial[:-1] + [{
            "type": "contract_update", "owner": "primary", "contract_revisions": {"feature-api": "r2"},
            "stopped_assignment_ids": [], "evidence": ["user:new-shared-contract"],
        }] + fresh + [initial[-1]]
        result = EVALUATOR.evaluate_trace(trace)
        self.assertTrue(result["passed"], result["errors"])
        self.assertEqual(2, result["metrics"]["accepted_assignments"])

        partial = copy.deepcopy(trace)
        partial["events"] = [event for event in partial["events"]
                             if event.get("assignment_id") != "frontend-r2"]
        result = EVALUATOR.evaluate_trace(partial)
        self.assertFalse(result["passed"])
        self.assertTrue(any("uncovered invalidated assignments: frontend-r1" in error
                            for error in result["errors"]))

        # A useful intermediate integration is legal while the remaining obligation is later replaced.
        intermediate = copy.deepcopy(trace)
        first = intermediate["events"][:8]
        by_id = {assignment: [event for event in intermediate["events"][8:-1]
                             if event.get("assignment_id") == assignment]
                 for assignment in ("backend-r2", "frontend-r2")}
        integration = intermediate["events"][-1]
        intermediate["events"] = (first + by_id["backend-r2"] + [copy.deepcopy(integration)]
                                  + by_id["frontend-r2"] + [integration])
        result = EVALUATOR.evaluate_trace(intermediate)
        self.assertTrue(result["passed"], result["errors"])

        cancelled = copy.deepcopy(partial)
        update = next(event for event in cancelled["events"] if event["type"] == "contract_update")
        update["cancelled_assignment_ids"] = ["frontend-r1"]
        result = EVALUATOR.evaluate_trace(cancelled)
        self.assertTrue(result["passed"], result["errors"])

        unbound = copy.deepcopy(trace)
        for event in unbound["events"]:
            event.pop("supersedes", None)
        result = EVALUATOR.evaluate_trace(unbound)
        self.assertFalse(result["passed"])
        self.assertTrue(any("uncovered invalidated assignments" in error for error in result["errors"]))

    def test_declared_task_binding_cannot_be_reused_for_another_task(self) -> None:
        trace = compact_cross_module_trace()
        binding = {"task_id": "task-a", "run_id": "run-1", "workspace_id": "workspace-1"}
        trace.update(binding)
        for event in trace["events"]:
            if event["type"] in {"delegate", "result", "accept", "integrate"}:
                event.update(binding)
        result = EVALUATOR.evaluate_trace(trace)
        self.assertTrue(result["passed"], result["errors"])
        for field in binding:
            stale = copy.deepcopy(trace)
            stale["events"][5][field] = "other"
            result = EVALUATOR.evaluate_trace(stale)
            self.assertFalse(result["passed"])
            self.assertTrue(any(f".{field} does not match trace identity" in error for error in result["errors"]))

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

    def test_accepts_v5_low_risk_single_owner_without_control_plane_ceremony(self) -> None:
        result = EVALUATOR.evaluate_trace({
            "schema_version": 5,
            "events": [
                {"type": "route", "mode": "SINGLE_OWNER",
                 "rationale": "one private-symbol rename with an existing deterministic test"},
                {"type": "primary_action", "action_class": "leaf_implementation",
                 "write_set": ["module/private_symbol.py"]},
                {"type": "primary_action", "action_class": "validation", "write_set": []},
            ],
        })
        self.assertTrue(result["passed"], result["errors"])
        self.assertEqual(0, result["metrics"]["delegations"])
        self.assertEqual(0, result["metrics"]["compact_assignments"])

    def test_accepts_v5_compact_cross_module_simulation(self) -> None:
        result = EVALUATOR.evaluate_trace(compact_cross_module_trace())
        self.assertTrue(result["passed"], result["errors"])
        self.assertEqual(2, result["metrics"]["compact_assignments"])
        self.assertEqual(2, result["metrics"]["accepted_assignments"])
        self.assertEqual(0, result["metrics"]["contract_gate_violations"])

    def test_rejects_v5_compact_result_without_disclosure_fields(self) -> None:
        trace = compact_cross_module_trace()
        events = trace["events"]
        assert isinstance(events, list)
        backend_result = events[3]
        assert isinstance(backend_result, dict)
        backend_result.pop("unverified_items")
        result = EVALUATOR.evaluate_trace(trace)
        self.assertFalse(result["passed"])
        self.assertTrue(any(
            "compact result unverified_items must be a list" in error
            for error in result["errors"]
        ))

    def test_rejects_v5_read_only_role_with_write_scope(self) -> None:
        read_only = compact_capsule(
            "validation", "validation", write_set=["module/service.py"]
        )
        result = EVALUATOR.evaluate_trace({
            "schema_version": 5,
            "semantic_fork": semantic_fork(),
            "events": [
                {"type": "route", "mode": "BOUNDED_WORKER",
                 "decision_question": "Which boundary owns the behavior?",
                 "rationale": "invalid validation worker write"},
                {"type": "delegate", "agent": "validator", "assignment_id": "validation-r1",
                 "tier": "balanced", "depth": 1, "dispatch_receipt": "host:validation-r1",
                 "write_set": ["module/service.py"], "capsule": read_only},
            ],
        })
        self.assertFalse(result["passed"])
        self.assertTrue(any(
            "work_class 'validation' must be read-only" in error
            for error in result["errors"]
        ))

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

    def test_capability_floor_rejects_underpowered_tier(self) -> None:
        bounded = capsule("design")
        bounded["capability_floor"] = {
            "judgment": "architectural",
            "impact": "shared",
            "oracle": "judgment",
            "minimum_tier": "strong",
        }
        result = EVALUATOR.evaluate_trace({
            "events": [
                {"type": "route", "mode": "BOUNDED_WORKER", "rationale": "shared design"},
                {"type": "delegate", "agent": "worker", "assignment_id": "slice", "tier": "balanced",
                 "dispatch_receipt": "host:worker", "write_set": [], "capsule": bounded},
            ]
        })
        self.assertFalse(result["passed"])
        self.assertTrue(any("below capsule capability floor" in error for error in result["errors"]))

    def test_capability_floor_rejects_internally_weak_declaration(self) -> None:
        bounded = capsule("design")
        bounded["capability_floor"] = {
            "judgment": "architectural",
            "impact": "local",
            "oracle": "evidence_backed",
            "minimum_tier": "balanced",
        }
        result = EVALUATOR.evaluate_trace({
            "events": [
                {"type": "route", "mode": "BOUNDED_WORKER", "rationale": "architecture judgment"},
                {"type": "delegate", "agent": "worker", "assignment_id": "slice", "tier": "strong",
                 "dispatch_receipt": "host:worker", "write_set": [], "capsule": bounded},
            ]
        })
        self.assertFalse(result["passed"])
        self.assertTrue(any("below derived floor" in error for error in result["errors"]))

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

    def test_contract_update_stops_old_workers_and_rejects_stale_results(self) -> None:
        stale = EVALUATOR.evaluate_trace({
            "program": program(),
            "events": [
                {"type": "route", "stage_id": "implementation", "mode": "BOUNDED_WORKER",
                 "rationale": "frozen API"},
                {"type": "delegate", "stage_id": "implementation", "agent": "backend",
                 "assignment_id": "backend-r1", "tier": "balanced", "dispatch_receipt": "host:backend-r1",
                 "write_set": ["service.py"], "capsule": program_capsule("backend", "service.py")},
                {"type": "contract_update", "owner": "primary",
                 "contract_revisions": {"feature-api": "r2"}, "stopped_assignment_ids": [],
                 "evidence": ["user-decision:r2"]},
                {"type": "result", "stage_id": "implementation", "agent": "backend",
                 "assignment_id": "backend-r1", "status": "success", "evidence": ["service.py:test"],
                 "source_fingerprint": "abc"},
                acceptance("backend-r1", artifacts_checked=True, stage_id="implementation"),
                {"type": "integrate", "stage_id": "implementation", "acceptance": ["accepted"],
                 "evidence": ["service.py:test"]},
            ],
        })
        self.assertFalse(stale["passed"])
        self.assertEqual(1, stale["metrics"]["stale_contract_results"])
        self.assertTrue(any("did not stop affected active assignments" in error for error in stale["errors"]))
        self.assertTrue(any("superseded contracts" in error for error in stale["errors"]))

    def test_contract_update_allows_new_assignment_at_current_revision(self) -> None:
        trace = {
            "program": program(),
            "events": [
                {"type": "route", "stage_id": "implementation", "mode": "BOUNDED_WORKER",
                 "rationale": "frozen API"},
                {"type": "delegate", "stage_id": "implementation", "agent": "backend-old",
                 "assignment_id": "backend-r1", "tier": "balanced", "dispatch_receipt": "host:backend-r1",
                 "write_set": ["service.py"], "capsule": program_capsule("backend", "service.py")},
                {"type": "contract_update", "owner": "primary",
                 "contract_revisions": {"feature-api": "r2"},
                 "stopped_assignment_ids": ["backend-r1"], "evidence": ["user-decision:r2"]},
                {"type": "delegate", "stage_id": "implementation", "agent": "backend-new",
                 "assignment_id": "backend-r2", "tier": "balanced", "dispatch_receipt": "host:backend-r2",
                 "write_set": ["service.py"],
                 "capsule": program_capsule("backend", "service.py", revision="r2")},
                {"type": "result", "stage_id": "implementation", "agent": "backend-new",
                 "assignment_id": "backend-r2", "status": "success", "evidence": ["service.py:test"],
                 "source_fingerprint": "abc"},
                acceptance("backend-r2", artifacts_checked=True, stage_id="implementation"),
                {"type": "integrate", "stage_id": "implementation", "acceptance": ["accepted"],
                 "evidence": ["service.py:test"]},
            ],
        }
        result = EVALUATOR.evaluate_trace(trace)
        self.assertTrue(result["passed"], result["errors"])

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
                {"type": "primary_action", "stage_id": "implementation", "action_class": "validation",
                 "write_set": []},
            ],
        }
        result = EVALUATOR.evaluate_trace(trace)
        self.assertFalse(result["passed"])
        self.assertEqual(1, result["metrics"]["primary_leaf_violations"])
        self.assertEqual(3, result["metrics"]["primary_work_violations"])
        self.assertTrue(any("leaf_implementation is forbidden" in error for error in result["errors"]))
        self.assertTrue(any("overlaps active worker" in error for error in result["errors"]))

    def test_rejects_primary_source_write_in_delegated_program(self) -> None:
        trace = {
            "schema_version": 5,
            "semantic_fork": semantic_fork(),
            "program": v4_program(),
            "events": [
                {"type": "route", "stage_id": "implementation", "mode": "BOUNDED_WORKER",
                 "decision_question": "Which boundary owns the behavior?",
                 "rationale": "delegated implementation stage"},
                {"type": "primary_action", "stage_id": "implementation",
                 "action_class": "coordination", "write_set": ["service.py"]},
            ],
        }
        result = EVALUATOR.evaluate_trace(trace)
        self.assertFalse(result["passed"])
        self.assertEqual(1, result["metrics"]["primary_work_violations"])
        self.assertTrue(any(
            "delegated-program primary_action must have an empty write_set" in error
            for error in result["errors"]
        ))

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

    def test_accepts_v4_bounded_scout_round_and_freeze(self) -> None:
        result = EVALUATOR.evaluate_trace({
            "schema_version": 4,
            "semantic_fork": semantic_fork(),
            "evidence_budget": {
                "round": 1, "scout_count": 2, "status": "STOPPED", "stop_reason": "FREEZE",
            },
            "budget": {"max_active": 2, "max_depth": 1},
            "events": [
                {"type": "route", "mode": "PARALLEL_SCOUTS",
                 "decision_question": "Which boundary owns the behavior?",
                 "rationale": "two complementary ownership axes"},
                {"type": "delegate", "agent": "a", "assignment_id": "source", "tier": "economy",
                 "depth": 1, "dispatch_receipt": "host:source", "write_set": [],
                 "capsule": scout_capsule("source", "definitions")},
                {"type": "delegate", "agent": "b", "assignment_id": "runtime", "tier": "economy",
                 "depth": 1, "dispatch_receipt": "host:runtime", "write_set": [],
                 "capsule": scout_capsule("runtime", "runtime-trace")},
                {"type": "result", "agent": "a", "assignment_id": "source", "status": "success",
                 "evidence": ["Owner.py:10"], "source_fingerprint": "abc"},
                {"type": "result", "agent": "b", "assignment_id": "runtime", "status": "success",
                 "evidence": ["trace.log:4"], "source_fingerprint": "abc"},
                acceptance("source"),
                acceptance("runtime"),
                {"type": "evidence_gate", "round": 1, "status": "STOPPED",
                 "stop_reason": "FREEZE", "result": "DISCRIMINATING",
                 "evidence": ["Owner.py:10", "trace.log:4"]},
                {"type": "integrate", "acceptance": ["boundary frozen"],
                 "evidence": ["Owner.py:10", "trace.log:4"]},
            ],
        })
        self.assertTrue(result["passed"], result["errors"])
        self.assertEqual(0, result["metrics"]["scout_budget_violations"])

    def test_accepts_canonical_unknown_semantic_fork(self) -> None:
        result = EVALUATOR.evaluate_trace({
            "schema_version": 4,
            "semantic_fork": semantic_fork(
                "OPEN", source="USER", evidence_can_decide="unknown"
            ),
            "evidence_budget": {
                "round": 1, "scout_count": 0, "status": "STOPPED", "stop_reason": "ASK_USER",
            },
            "events": [
                {"type": "route", "mode": "SINGLE_OWNER",
                 "decision_question": "Which boundary owns the behavior?",
                 "rationale": "retain the decision with the primary while evidence scope is unknown"},
            ],
        })
        self.assertTrue(result["passed"], result["errors"])

    def test_v4_route_requires_native_nonempty_decision_question(self) -> None:
        result = EVALUATOR.evaluate_trace({
            "schema_version": 4,
            "semantic_fork": semantic_fork(),
            "events": [
                {"type": "route", "mode": "SINGLE_OWNER", "decision_question": None,
                 "rationale": "malformed adapter input"},
            ],
        })
        self.assertFalse(result["passed"])
        self.assertTrue(any("route lacks decision_question" in error for error in result["errors"]))

    def test_v4_rejects_duplicate_assignment_identity_without_overwriting_state(self) -> None:
        result = EVALUATOR.evaluate_trace({
            "schema_version": 4,
            "semantic_fork": semantic_fork(),
            "budget": {"max_active": 2, "max_depth": 1},
            "events": [
                {"type": "route", "mode": "BOUNDED_WORKER",
                 "decision_question": "Which boundary owns the behavior?",
                 "rationale": "two claimed slices"},
                {"type": "delegate", "agent": "a", "assignment_id": "same", "tier": "balanced",
                 "depth": 1, "dispatch_receipt": "host:a", "write_set": [],
                 "capsule": v4_capsule("a", "implementation")},
                {"type": "delegate", "agent": "b", "assignment_id": "same", "tier": "balanced",
                 "depth": 1, "dispatch_receipt": "host:b", "write_set": [],
                 "capsule": v4_capsule("b", "implementation")},
            ],
        })
        self.assertFalse(result["passed"])
        self.assertTrue(any("duplicates assignment_id" in error for error in result["errors"]))

    def test_malformed_v4_lists_return_errors_instead_of_crashing(self) -> None:
        result = EVALUATOR.evaluate_trace({
            "schema_version": 4,
            "semantic_fork": semantic_fork(),
            "events": [
                {"type": "route", "mode": "BOUNDED_WORKER",
                 "decision_question": "Which boundary owns the behavior?",
                 "rationale": "malformed adapter input"},
                {"type": "delegate", "agent": "worker", "assignment_id": "work",
                 "tier": "balanced", "depth": 1, "dispatch_receipt": "host:work",
                 "write_set": [{}], "capsule": v4_capsule("work", "implementation")},
            ],
        })
        self.assertFalse(result["passed"])
        self.assertTrue(any("write_set" in error for error in result["errors"]))

    def test_invalid_observation_reopen_is_limited_to_one_round(self) -> None:
        result = EVALUATOR.evaluate_trace({
            "schema_version": 4,
            "semantic_fork": semantic_fork(),
            "evidence_budget": {
                "round": 3, "scout_count": 0, "status": "STOPPED",
                "stop_reason": "INVALID_OBSERVATION",
            },
            "events": [
                {"type": "route", "mode": "PARALLEL_SCOUTS",
                 "decision_question": "Which boundary owns the behavior?", "rationale": "claimed repair"},
                {"type": "evidence_gate", "round": 1, "status": "STOPPED",
                 "stop_reason": "INVALID_OBSERVATION", "result": "INVALID", "evidence": ["e:1"]},
                {"type": "evidence_reopen", "round": 2, "reason": "INVALID_OBSERVATION",
                 "locator": "e:1"},
                {"type": "evidence_gate", "round": 2, "status": "STOPPED",
                 "stop_reason": "INVALID_OBSERVATION", "result": "INVALID", "evidence": ["e:2"]},
                {"type": "evidence_reopen", "round": 3, "reason": "INVALID_OBSERVATION",
                 "locator": "e:2"},
            ],
        })
        self.assertFalse(result["passed"])
        self.assertTrue(any("default one observation-apparatus" in warning for warning in result["warnings"]))

    def test_rejects_legacy_semantic_fork_shapes_in_v4(self) -> None:
        legacy = semantic_fork()
        legacy["options"] = ["boundary-a", "boundary-b"]
        legacy["architectural_consequences"] = ["ownership"]
        result = EVALUATOR.evaluate_trace({
            "schema_version": 4,
            "semantic_fork": legacy,
            "events": [
                {"type": "route", "mode": "SINGLE_OWNER",
                 "decision_question": "Which boundary owns the behavior?",
                 "rationale": "schema validation"},
            ],
        })
        self.assertFalse(result["passed"])
        self.assertTrue(any("options[0] must be an object" in error for error in result["errors"]))
        self.assertTrue(any("architectural_consequences must be an object" in error
                            for error in result["errors"]))

    def test_accepts_v4_expansion_only_after_invalid_observation(self) -> None:
        result = EVALUATOR.evaluate_trace({
            "schema_version": 4,
            "semantic_fork": semantic_fork(),
            "evidence_budget": {
                "round": 2, "scout_count": 1, "status": "STOPPED", "stop_reason": "FREEZE",
            },
            "budget": {"max_active": 1, "max_depth": 1},
            "events": [
                {"type": "route", "mode": "PARALLEL_SCOUTS",
                 "decision_question": "Which boundary owns the behavior?",
                 "rationale": "replace one invalid observation"},
                {"type": "delegate", "agent": "a", "assignment_id": "fixture", "tier": "economy",
                 "depth": 1, "dispatch_receipt": "host:fixture", "write_set": [],
                 "capsule": scout_capsule("fixture", "fixture")},
                {"type": "result", "agent": "a", "assignment_id": "fixture", "status": "success",
                 "evidence": ["fixture.log:invalid"], "source_fingerprint": "abc"},
                acceptance("fixture"),
                {"type": "evidence_gate", "round": 1, "status": "STOPPED",
                 "stop_reason": "INVALID_OBSERVATION", "result": "INVALID",
                 "evidence": ["fixture.log:invalid"]},
                {"type": "evidence_reopen", "round": 2, "reason": "INVALID_OBSERVATION",
                 "locator": "fixture.log:invalid"},
                {"type": "delegate", "agent": "b", "assignment_id": "replacement", "tier": "economy",
                 "depth": 1, "dispatch_receipt": "host:replacement", "write_set": [],
                 "capsule": scout_capsule("source", "source", round_number=2,
                                          expansion_reason="INVALID_OBSERVATION")},
                {"type": "result", "agent": "b", "assignment_id": "replacement", "status": "success",
                 "evidence": ["Owner.py:10"], "source_fingerprint": "abc"},
                acceptance("replacement"),
                {"type": "evidence_gate", "round": 2, "status": "STOPPED",
                 "stop_reason": "FREEZE", "result": "DISCRIMINATING",
                 "evidence": ["Owner.py:10"]},
                {"type": "integrate", "acceptance": ["boundary frozen"],
                 "evidence": ["fixture.log:invalid", "Owner.py:10"]},
            ],
        })
        self.assertTrue(result["passed"], result["errors"])

    def test_accepts_v4_new_candidate_reopen_after_stopped_gate(self) -> None:
        result = EVALUATOR.evaluate_trace({
            "schema_version": 4,
            "semantic_fork": semantic_fork(),
            "evidence_budget": {
                "round": 2, "scout_count": 1, "status": "STOPPED", "stop_reason": "FREEZE",
            },
            "budget": {"max_active": 1, "max_depth": 1},
            "events": [
                {"type": "route", "mode": "PARALLEL_SCOUTS",
                 "decision_question": "Which boundary owns the behavior?",
                 "rationale": "a newly evidenced candidate changes the decision ledger"},
                {"type": "delegate", "agent": "a", "assignment_id": "first", "tier": "economy",
                 "depth": 1, "dispatch_receipt": "host:first", "write_set": [],
                 "capsule": scout_capsule("source", "definitions")},
                {"type": "result", "agent": "a", "assignment_id": "first", "status": "success",
                 "evidence": ["Owner.py:10"], "source_fingerprint": "abc"},
                acceptance("first"),
                {"type": "evidence_gate", "round": 1, "status": "STOPPED",
                 "stop_reason": "FREEZE", "result": "DISCRIMINATING",
                 "evidence": ["Owner.py:10"]},
                {"type": "evidence_reopen", "round": 2, "reason": "NEW_CANDIDATE",
                 "locator": "Plugin.py:20"},
                {"type": "delegate", "agent": "b", "assignment_id": "new-candidate",
                 "tier": "economy", "depth": 1, "dispatch_receipt": "host:new-candidate",
                 "write_set": [],
                 "capsule": scout_capsule("plugin", "registration", round_number=2,
                                          expansion_reason="NEW_CANDIDATE")},
                {"type": "result", "agent": "b", "assignment_id": "new-candidate",
                 "status": "success", "evidence": ["Plugin.py:20"],
                 "source_fingerprint": "abc"},
                acceptance("new-candidate"),
                {"type": "evidence_gate", "round": 2, "status": "STOPPED",
                 "stop_reason": "FREEZE", "result": "DISCRIMINATING",
                 "evidence": ["Plugin.py:20"]},
                {"type": "integrate", "acceptance": ["candidate ledger reconciled"],
                 "evidence": ["Owner.py:10", "Plugin.py:20"]},
            ],
        })
        self.assertTrue(result["passed"], result["errors"])

    def test_rejects_scout_round_after_discriminating_evidence(self) -> None:
        result = EVALUATOR.evaluate_trace({
            "schema_version": 4,
            "semantic_fork": semantic_fork(),
            "evidence_budget": {
                "round": 2, "scout_count": 1, "status": "STOPPED", "stop_reason": "BLOCKER",
            },
            "budget": {"max_active": 1, "max_depth": 1},
            "events": [
                {"type": "route", "mode": "PARALLEL_SCOUTS",
                 "decision_question": "Which boundary owns the behavior?", "rationale": "claimed scan"},
                {"type": "delegate", "agent": "a", "assignment_id": "first", "tier": "economy",
                 "depth": 1, "dispatch_receipt": "host:first", "write_set": [],
                 "capsule": scout_capsule("source", "source")},
                {"type": "result", "agent": "a", "assignment_id": "first", "status": "success",
                 "evidence": ["Owner.py:10"], "source_fingerprint": "abc"},
                acceptance("first"),
                {"type": "evidence_gate", "round": 1, "status": "STOPPED",
                 "stop_reason": "FREEZE", "result": "DISCRIMINATING",
                 "evidence": ["Owner.py:10"]},
                {"type": "delegate", "agent": "b", "assignment_id": "extra", "tier": "economy",
                 "depth": 1, "dispatch_receipt": "host:extra", "write_set": [],
                 "capsule": scout_capsule("everything", "broad", round_number=2,
                                          expansion_reason="HIGH_RISK_GAP")},
                {"type": "result", "agent": "b", "assignment_id": "extra", "status": "success",
                 "evidence": ["Other.py:2"], "source_fingerprint": "abc"},
                acceptance("extra"),
                {"type": "evidence_gate", "round": 2, "status": "STOPPED",
                 "stop_reason": "BLOCKER", "result": "INCONCLUSIVE",
                 "evidence": ["Other.py:2"]},
                {"type": "integrate", "acceptance": ["recorded"],
                 "evidence": ["Owner.py:10", "Other.py:2"]},
            ],
        })
        self.assertFalse(result["passed"])
        self.assertEqual(1, result["metrics"]["scout_rounds_after_discriminating_evidence"])
        self.assertTrue(any("after discovery stopped" in error for error in result["errors"]))

    def test_more_than_two_scouts_is_diagnostic_with_explicit_capacity(self) -> None:
        events: list[dict[str, object]] = [
            {"type": "route", "mode": "PARALLEL_SCOUTS",
             "decision_question": "Which boundary owns the behavior?", "rationale": "claimed scan"},
        ]
        for number in range(3):
            assignment = f"scan-{number}"
            events.append({
                "type": "delegate", "agent": assignment, "assignment_id": assignment,
                "tier": "economy", "depth": 1, "dispatch_receipt": f"host:{assignment}",
                "write_set": [], "capsule": scout_capsule(assignment, f"axis-{number}"),
            })
        for number in range(3):
            assignment = f"scan-{number}"
            events.append({"type": "result", "agent": assignment, "assignment_id": assignment,
                           "status": "success", "evidence": [f"evidence:{number}"],
                           "source_fingerprint": "abc"})
            events.append(acceptance(assignment))
        events.extend([
            {"type": "evidence_gate", "round": 1, "status": "STOPPED",
             "stop_reason": "FREEZE", "result": "DISCRIMINATING",
             "evidence": ["evidence:0"]},
            {"type": "integrate", "acceptance": ["recorded"], "evidence": ["evidence:0"]},
        ])
        result = EVALUATOR.evaluate_trace({
            "schema_version": 4,
            "semantic_fork": semantic_fork(),
            "evidence_budget": {
                "round": 1, "scout_count": 3, "status": "STOPPED", "stop_reason": "FREEZE",
            },
            "budget": {"max_active": 3, "max_depth": 1},
            "events": events,
        })
        self.assertTrue(result["passed"], result["errors"])
        self.assertGreater(result["metrics"]["scout_budget_violations"], 0)
        self.assertTrue(any("exceeds default limit 2" in item for item in result["warnings"]))

    def test_rejects_scout_without_decision_question_or_hypothesis(self) -> None:
        scout = scout_capsule("source", "source")
        scout.pop("hypothesis")
        result = EVALUATOR.evaluate_trace({
            "schema_version": 4,
            "semantic_fork": semantic_fork(),
            "evidence_budget": {
                "round": 1, "scout_count": 1, "status": "STOPPED", "stop_reason": "FREEZE",
            },
            "events": [
                {"type": "route", "mode": "PARALLEL_SCOUTS", "rationale": "claimed scan"},
                {"type": "delegate", "agent": "scout", "assignment_id": "scout",
                 "tier": "economy", "depth": 1, "dispatch_receipt": "host:scout",
                 "write_set": [], "capsule": scout},
                {"type": "result", "agent": "scout", "assignment_id": "scout",
                 "status": "success", "evidence": ["Owner.py:10"], "source_fingerprint": "abc"},
                acceptance("scout"),
                {"type": "evidence_gate", "round": 1, "status": "STOPPED",
                 "stop_reason": "FREEZE", "result": "DISCRIMINATING",
                 "evidence": ["Owner.py:10"]},
                {"type": "integrate", "acceptance": ["recorded"], "evidence": ["Owner.py:10"]},
            ],
        })
        self.assertFalse(result["passed"])
        self.assertTrue(any("route lacks decision_question" in error for error in result["errors"]))
        self.assertTrue(any("requires nonempty hypothesis" in error for error in result["errors"]))

    def test_rejects_design_implementation_and_review_while_fork_open(self) -> None:
        for work_class in ("documentation", "contract_design", "implementation", "review"):
            with self.subTest(work_class=work_class):
                work = v4_capsule("candidate", work_class)
                if work_class == "review":
                    work.update({"review_targets": ["candidate"], "material_risks": ["security"]})
                result = EVALUATOR.evaluate_trace({
                    "schema_version": 4,
                    "semantic_fork": semantic_fork("OPEN", source="USER"),
                    "artifacts": [{"artifact_id": "candidate", "status": "retained"}],
                    "events": [
                        {"type": "route", "mode": "BOUNDED_WORKER",
                         "decision_question": "Which boundary owns the behavior?",
                         "rationale": "claimed premature work"},
                        {"type": "delegate", "agent": "worker", "assignment_id": "work",
                         "tier": "strong", "depth": 1, "dispatch_receipt": "host:work",
                         "write_set": [], "capsule": work},
                        {"type": "result", "agent": "worker", "assignment_id": "work",
                         "status": "success", "evidence": ["candidate:1"],
                         "source_fingerprint": "abc"},
                        acceptance("work"),
                        {"type": "integrate", "acceptance": ["claimed"], "evidence": ["candidate:1"]},
                    ],
                })
                self.assertFalse(result["passed"])
                self.assertGreater(
                    result["metrics"]["semantic_fork_admission_violations"], 0
                )

    def test_rejects_v4_implementation_before_relevant_contract_freeze(self) -> None:
        result = EVALUATOR.evaluate_trace({
            "schema_version": 4,
            "semantic_fork": semantic_fork(),
            "program": v4_program(contract_state="proposed"),
            "events": [
                {"type": "route", "stage_id": "implementation", "mode": "BOUNDED_WORKER",
                 "decision_question": "Which boundary owns the behavior?",
                 "rationale": "claimed implementation readiness"},
            ],
        })
        self.assertFalse(result["passed"])
        self.assertTrue(any("requires contract 'feature-api' to be frozen" in error
                            for error in result["errors"]))
        self.assertGreater(result["metrics"]["stage_admission_violations"], 0)

    def test_accepts_v4_implementation_after_semantic_and_contract_gates(self) -> None:
        worker = with_write_permission(v4_capsule("service.py", "implementation"), "service.py")
        worker.update({
            "depends_on": ["decision"],
            "contract_revisions": {"feature-api": "r1"},
        })
        result = EVALUATOR.evaluate_trace({
            "schema_version": 4,
            "semantic_fork": semantic_fork(source="USER"),
            "program": v4_program(),
            "events": [
                {"type": "route", "stage_id": "implementation", "mode": "BOUNDED_WORKER",
                 "decision_question": "Which boundary owns the behavior?",
                 "rationale": "resolved semantics and frozen relevant contract"},
                {"type": "delegate", "stage_id": "implementation", "agent": "worker",
                 "assignment_id": "implementation", "tier": "balanced", "depth": 1,
                 "dispatch_receipt": "host:implementation", "write_set": ["service.py"],
                 "capsule": worker},
                {"type": "result", "stage_id": "implementation", "agent": "worker",
                 "assignment_id": "implementation", "status": "success",
                 "evidence": ["service.py:test"], "source_fingerprint": "abc"},
                acceptance("implementation", artifacts_checked=True, stage_id="implementation"),
                {"type": "integrate", "stage_id": "implementation",
                 "acceptance": ["implementation accepted"], "evidence": ["service.py:test"]},
            ],
        })
        self.assertTrue(result["passed"], result["errors"])
        self.assertEqual(0, result["metrics"]["stage_admission_violations"])

    def test_rejects_review_when_disposition_invalidates_admission(self) -> None:
        result = EVALUATOR.evaluate_trace(
            review_disposition_trace("ADMISSION_PRECONDITION_INVALIDATED")
        )
        self.assertFalse(result["passed"])
        self.assertEqual(1, result["metrics"]["review_of_later_discarded_artifact"])
        self.assertEqual(1, result["metrics"]["premature_review_admission_violations"])

    def test_accepts_review_finding_that_discards_retained_artifact(self) -> None:
        result = EVALUATOR.evaluate_trace(review_disposition_trace("REVIEW_FINDING"))
        self.assertTrue(result["passed"], result["errors"])
        self.assertEqual(1, result["metrics"]["review_of_later_discarded_artifact"])
        self.assertEqual(0, result["metrics"]["premature_review_admission_violations"])

    def test_rejects_review_without_retained_target_or_material_risk(self) -> None:
        reviewer = v4_capsule("candidate", "review")
        reviewer.update({"review_targets": ["candidate"], "material_risks": []})
        result = EVALUATOR.evaluate_trace({
            "schema_version": 4,
            "semantic_fork": semantic_fork(),
            "artifacts": [{"artifact_id": "candidate", "status": "candidate"}],
            "events": [
                {"type": "route", "mode": "INDEPENDENT_REVIEW",
                 "decision_question": "Which boundary owns the behavior?",
                 "rationale": "claimed review"},
                {"type": "delegate", "agent": "reviewer", "assignment_id": "review",
                 "tier": "strong", "depth": 1, "dispatch_receipt": "host:review",
                 "write_set": [], "capsule": reviewer},
                {"type": "result", "agent": "reviewer", "assignment_id": "review",
                 "status": "success", "evidence": ["finding:1"], "source_fingerprint": "abc"},
                acceptance("review"),
                {"type": "integrate", "acceptance": ["recorded"], "evidence": ["finding:1"]},
            ],
        })
        self.assertFalse(result["passed"])
        self.assertEqual(2, result["metrics"]["review_admission_violations"])

    def test_duplicate_stage_kind_is_diagnostic_when_dependencies_are_satisfied(self) -> None:
        trace = compact_cross_module_trace()
        trace["program"]["stages"].insert(1, {
            "stage_id": "second-contract-check",
            "stage_kind": "semantic_decision_contract_freeze",
            "objective": "Confirm the second independent contract boundary",
            "depends_on": ["decision"],
            "required_contracts": [],
            "entry_gate": "first contract accepted",
            "route_mode": "SINGLE_OWNER",
            "exit_gate": "second contract accepted",
            "status": "completed",
        })
        result = EVALUATOR.evaluate_trace(trace)
        self.assertTrue(result["passed"], result["errors"])
        self.assertTrue(any("stage_kind duplicates" in warning for warning in result["warnings"]))


if __name__ == "__main__":
    unittest.main()
