#!/usr/bin/env python3
"""Evaluate normalized multi-agent orchestration traces without starting agents."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROUTE_MODES = {
    "SINGLE_OWNER",
    "PARALLEL_SCOUTS",
    "BOUNDED_WORKER",
    "INDEPENDENT_REVIEW",
    "SEQUENTIAL_HANDOFF",
}
CAPSULE_FIELDS = {
    "objective",
    "decision",
    "allowed_scope",
    "excluded_scope",
    "inputs",
    "acceptance",
    "output_contract",
    "stop_conditions",
    "escalation_triggers",
    "permissions",
}
STRICT_CAPSULE_FIELDS = CAPSULE_FIELDS | {"acceptance_owner"}
AUTHORITY_CAPSULE_FIELDS = STRICT_CAPSULE_FIELDS | {
    "parent_assignment_id",
    "depth",
    "budget",
    "delegation",
}
TIER_ORDER = {"economy": 0, "balanced": 1, "strong": 2}


def _nonempty(value: Any) -> bool:
    return value not in (None, "", [], {})


def _acceptance_signals(value: Any) -> set[str]:
    if isinstance(value, dict):
        return {str(signal) for signal in value if str(signal).strip()}
    if isinstance(value, list):
        return {str(signal) for signal in value if str(signal).strip()}
    return set()


def _validate_program(program: Any, errors: list[str]) -> dict[str, Any] | None:
    """Validate the optional program envelope and return its indexed state."""
    if program is None:
        return None
    if not isinstance(program, dict):
        errors.append("program must be an object")
        return None

    required = ("program_id", "primary_role", "current_stage", "stages")
    for field in required:
        if not _nonempty(program.get(field)):
            errors.append(f"program.{field} must be nonempty")
    if program.get("primary_role") != "ORCHESTRATOR_INTEGRATOR":
        errors.append("program.primary_role must be ORCHESTRATOR_INTEGRATOR")

    stages = program.get("stages")
    stage_by_id: dict[str, dict[str, Any]] = {}
    if not isinstance(stages, list):
        errors.append("program.stages must be a list")
        stages = []
    for index, stage in enumerate(stages):
        prefix = f"program.stages[{index}]"
        if not isinstance(stage, dict):
            errors.append(f"{prefix} must be an object")
            continue
        stage_id = str(stage.get("stage_id", "")).strip()
        if not stage_id:
            errors.append(f"{prefix}.stage_id must be nonempty")
        elif stage_id in stage_by_id:
            errors.append(f"{prefix}.stage_id duplicates {stage_id!r}")
        else:
            stage_by_id[stage_id] = stage
        if not _nonempty(stage.get("objective")):
            errors.append(f"{prefix}.objective must be nonempty")
        if not isinstance(stage.get("depends_on"), list):
            errors.append(f"{prefix}.depends_on must be a list")
        if not _nonempty(stage.get("entry_gate")):
            errors.append(f"{prefix}.entry_gate must be nonempty")
        if stage.get("route_mode") not in ROUTE_MODES:
            errors.append(f"{prefix}.route_mode is invalid")
        if not _nonempty(stage.get("exit_gate")):
            errors.append(f"{prefix}.exit_gate must be nonempty")
        if stage.get("status") not in {"pending", "active", "blocked", "completed"}:
            errors.append(f"{prefix}.status is invalid")

    current_stage = str(program.get("current_stage", "")).strip()
    current = stage_by_id.get(current_stage)
    if current is None:
        errors.append("program.current_stage must reference a declared stage")
    elif current.get("status") != "active":
        errors.append("program.current_stage must have status=active")
    elif isinstance(current.get("depends_on"), list):
        for dependency in current["depends_on"]:
            dependency_id = str(dependency)
            dependency_stage = stage_by_id.get(dependency_id)
            if dependency_stage is None:
                errors.append(
                    f"program.current_stage dependency {dependency_id!r} is not a declared stage"
                )
            elif dependency_stage.get("status") != "completed":
                errors.append(
                    f"program.current_stage dependency {dependency_id!r} must be completed"
                )

    contracts = program.get("shared_contracts", [])
    contract_by_id: dict[str, dict[str, Any]] = {}
    if not isinstance(contracts, list):
        errors.append("program.shared_contracts must be a list")
        contracts = []
    for index, contract in enumerate(contracts):
        prefix = f"program.shared_contracts[{index}]"
        if not isinstance(contract, dict):
            errors.append(f"{prefix} must be an object")
            continue
        contract_id = str(contract.get("contract_id", "")).strip()
        if not contract_id:
            errors.append(f"{prefix}.contract_id must be nonempty")
        elif contract_id in contract_by_id:
            errors.append(f"{prefix}.contract_id duplicates {contract_id!r}")
        else:
            contract_by_id[contract_id] = contract
        if not _nonempty(contract.get("revision")):
            errors.append(f"{prefix}.revision must be nonempty")
        if contract.get("state") not in {"proposed", "frozen", "superseded"}:
            errors.append(f"{prefix}.state is invalid")
        if not _nonempty(contract.get("owner")):
            errors.append(f"{prefix}.owner must be nonempty")

    return {
        "current_stage": current_stage,
        "current": current,
        "contracts": contract_by_id,
        "has_shared_contracts": bool(contracts),
        "stage_count": len(stages),
    }


def evaluate_trace(trace: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    events = trace.get("events")
    if not isinstance(events, list):
        return {"passed": False, "errors": ["events must be a list"], "warnings": [], "metrics": {}}

    program_state = _validate_program(trace.get("program"), errors)
    has_program = trace.get("program") is not None
    schema_version = trace.get("schema_version", 1)
    if not isinstance(schema_version, int) or schema_version < 1:
        errors.append("schema_version must be a positive integer")
        schema_version = 1
    strict_schema = schema_version >= 2 or has_program or any(
        isinstance(event, dict)
        and (event.get("type") in {"accept", "primary_action"} or "dispatch_receipt" in event)
        for event in events
    )
    authority_schema = schema_version >= 3

    budget = trace.get("budget") if isinstance(trace.get("budget"), dict) else {}
    max_active = int(budget.get("max_active", 2))
    max_depth = int(budget.get("max_depth", 1))
    route_count = 0
    route_mode: str | None = None
    integration_count = 0
    delegate_count = 0
    escalation_count = 0
    weak_retry_count = 0
    active: dict[str, set[str]] = {}
    assignment_for_agent: dict[str, str] = {}
    failed_assignments: set[str] = set()
    escalated_assignments: dict[str, str] = {}
    successful_assignments: set[str] = set()
    accepted_assignments: set[str] = set()
    rejected_assignments: set[str] = set()
    assignment_acceptance: dict[str, set[str]] = {}
    assignment_acceptance_owner: dict[str, str] = {}
    assignment_write_set: dict[str, set[str]] = {}
    assignment_tier: dict[str, str] = {}
    result_source_fingerprint: dict[str, str] = {}
    dispatch_receipts: set[str] = set()
    acceptance_count = 0
    rejection_count = 0
    max_observed_active = 0
    primary_action_count = 0
    primary_leaf_violations = 0
    contract_gate_violations = 0
    active_contract_revisions: dict[str, dict[str, Any]] = {}
    assignment_capsules: dict[str, dict[str, Any]] = {}

    for index, event in enumerate(events):
        if not isinstance(event, dict):
            errors.append(f"event[{index}] must be an object")
            continue
        event_type = event.get("type")

        if event_type == "route":
            route_count += 1
            if event.get("mode") not in ROUTE_MODES:
                errors.append(f"event[{index}] has invalid route mode")
            else:
                route_mode = str(event["mode"])
            if not _nonempty(event.get("rationale")):
                errors.append(f"event[{index}] route lacks rationale")
            if has_program:
                if program_state is None:
                    errors.append(f"event[{index}] route cannot bind invalid program")
                else:
                    if event.get("stage_id") != program_state["current_stage"]:
                        errors.append(f"event[{index}] route.stage_id must match program.current_stage")
                    current = program_state["current"]
                    if current and event.get("mode") != current.get("route_mode"):
                        errors.append(f"event[{index}] route.mode must match current stage route_mode")

        elif event_type == "delegate":
            delegate_count += 1
            if route_count == 0:
                errors.append(f"event[{index}] delegate occurs before RouteDecision")
            agent = str(event.get("agent", ""))
            assignment = str(event.get("assignment_id", ""))
            if not agent or not assignment:
                errors.append(f"event[{index}] delegate requires agent and assignment_id")
                continue
            if agent in active:
                errors.append(f"event[{index}] agent {agent!r} is already active")
            tier = event.get("tier")
            if tier not in TIER_ORDER:
                errors.append(f"event[{index}] delegate uses an unknown capability tier")
            dispatch_receipt = str(event.get("dispatch_receipt", "")).strip()
            if strict_schema and not dispatch_receipt:
                errors.append(f"event[{index}] delegate lacks accepted dispatch_receipt")
            elif dispatch_receipt in dispatch_receipts:
                errors.append(f"event[{index}] reuses dispatch_receipt {dispatch_receipt!r}")
            else:
                dispatch_receipts.add(dispatch_receipt)
            depth = int(event.get("depth", 1))
            if depth > max_depth:
                errors.append(f"event[{index}] depth {depth} exceeds max_depth {max_depth}")
            capsule = event.get("capsule")
            if not isinstance(capsule, dict):
                errors.append(f"event[{index}] delegate lacks Assignment Capsule")
            else:
                if authority_schema:
                    required_capsule_fields = AUTHORITY_CAPSULE_FIELDS
                else:
                    required_capsule_fields = STRICT_CAPSULE_FIELDS if strict_schema else CAPSULE_FIELDS
                missing = sorted(field for field in required_capsule_fields if not _nonempty(capsule.get(field)))
                if missing:
                    errors.append(f"event[{index}] capsule missing: {', '.join(missing)}")
                signals = _acceptance_signals(capsule.get("acceptance")) if strict_schema else set()
                if strict_schema and not signals:
                    errors.append(f"event[{index}] capsule acceptance must declare named signals")
                assignment_acceptance[assignment] = signals
                assignment_acceptance_owner[assignment] = str(capsule.get("acceptance_owner", ""))
                if authority_schema:
                    capsule_depth = capsule.get("depth")
                    if not isinstance(capsule_depth, int) or capsule_depth != depth:
                        errors.append(f"event[{index}] capsule depth must match delegate depth")
                    delegation = capsule.get("delegation")
                    if delegation not in {"denied", "brokered"}:
                        errors.append(f"event[{index}] capsule delegation must be denied or brokered")
                    broker_enforced = budget.get("spawn_broker_enforced") is True
                    if delegation == "brokered" and not broker_enforced:
                        errors.append(f"event[{index}] brokered delegation requires spawn_broker_enforced=true")
                    parent_assignment = str(capsule.get("parent_assignment_id", "")).strip()
                    if depth == 1 and parent_assignment != "primary":
                        errors.append(f"event[{index}] depth-one capsule parent_assignment_id must be primary")
                    if depth > 1:
                        parent_capsule = assignment_capsules.get(parent_assignment)
                        if parent_capsule is None:
                            errors.append(f"event[{index}] nested delegate lacks an active declared parent capsule")
                        else:
                            if parent_assignment not in assignment_for_agent.values():
                                errors.append(f"event[{index}] nested delegate parent assignment is not active")
                            if parent_capsule.get("delegation") != "brokered":
                                errors.append(f"event[{index}] nested delegate parent does not permit brokered delegation")
                            parent_depth = parent_capsule.get("depth")
                            if not isinstance(parent_depth, int) or depth != parent_depth + 1:
                                errors.append(f"event[{index}] child depth must be exactly parent depth + 1")
                            parent_scope = parent_capsule.get("allowed_scope")
                            child_scope = capsule.get("allowed_scope")
                            if not isinstance(parent_scope, list) or not isinstance(child_scope, list):
                                errors.append(f"event[{index}] authority scopes must be normalized lists")
                            elif not set(child_scope).issubset(set(parent_scope)):
                                errors.append(f"event[{index}] child allowed_scope exceeds parent authority")
                            parent_permissions = parent_capsule.get("permissions")
                            child_permissions = capsule.get("permissions")
                            if isinstance(parent_permissions, dict) and isinstance(child_permissions, dict):
                                for permission in ("read", "write", "external_side_effects", "secrets"):
                                    parent_values = parent_permissions.get(permission, [])
                                    child_values = child_permissions.get(permission, [])
                                    if not isinstance(parent_values, list) or not isinstance(child_values, list):
                                        errors.append(
                                            f"event[{index}] permissions.{permission} must be a normalized list"
                                        )
                                    elif not set(child_values).issubset(set(parent_values)):
                                        errors.append(
                                            f"event[{index}] child permissions.{permission} exceeds parent authority"
                                        )
                                parent_write_set = set(parent_permissions.get("write", []))
                                if not write_set.issubset(parent_write_set):
                                    errors.append(f"event[{index}] child write_set exceeds parent authority")
                            else:
                                errors.append(f"event[{index}] nested authority permissions must be objects")
                            parent_budget = parent_capsule.get("budget")
                            child_budget = capsule.get("budget")
                            if isinstance(parent_budget, dict) and isinstance(child_budget, dict):
                                for budget_field in ("token_budget", "max_children"):
                                    parent_value = parent_budget.get(budget_field)
                                    child_value = child_budget.get(budget_field)
                                    if (
                                        isinstance(parent_value, (int, float))
                                        and isinstance(child_value, (int, float))
                                        and child_value > parent_value
                                    ):
                                        errors.append(
                                            f"event[{index}] child budget.{budget_field} exceeds parent authority"
                                        )
                            else:
                                errors.append(f"event[{index}] nested authority budgets must be objects")
                    assignment_capsules[assignment] = capsule
            write_set = set(event.get("write_set") or [])
            contract_revisions: dict[str, Any] = {}
            if has_program:
                if event.get("stage_id") != (program_state or {}).get("current_stage"):
                    errors.append(f"event[{index}] delegate.stage_id must match program.current_stage")
                if not isinstance(capsule, dict):
                    pass
                else:
                    if not isinstance(capsule.get("depends_on"), list):
                        errors.append(f"event[{index}] program capsule.depends_on must be a list")
                    if not isinstance(capsule.get("contract_revisions"), dict):
                        errors.append(f"event[{index}] program capsule.contract_revisions must be an object")
                    else:
                        contract_revisions = capsule["contract_revisions"]
                        if program_state:
                            if write_set and program_state["has_shared_contracts"]:
                                declared_contracts = set(program_state["contracts"])
                                cited_contracts = {str(contract_id) for contract_id in contract_revisions}
                                missing_contracts = sorted(declared_contracts - cited_contracts)
                                extra_contracts = sorted(cited_contracts - declared_contracts)
                                if missing_contracts or extra_contracts:
                                    contract_gate_violations += 1
                                    details = []
                                    if missing_contracts:
                                        details.append("missing " + ", ".join(missing_contracts))
                                    if extra_contracts:
                                        details.append("unknown " + ", ".join(extra_contracts))
                                    errors.append(
                                        f"event[{index}] program capsule.contract_revisions must cover program shared contracts ("
                                        + "; ".join(details)
                                        + ")"
                                    )
                            for contract_id, revision in contract_revisions.items():
                                contract = program_state["contracts"].get(str(contract_id))
                                if contract is None:
                                    contract_gate_violations += 1
                                    errors.append(
                                        f"event[{index}] contract_revisions references unknown contract {contract_id!r}"
                                    )
                                elif contract.get("state") != "frozen":
                                    contract_gate_violations += 1
                                    errors.append(
                                        f"event[{index}] contract {contract_id!r} is unresolved for worker write"
                                    )
                                elif revision != contract.get("revision"):
                                    contract_gate_violations += 1
                                    errors.append(
                                        f"event[{index}] contract {contract_id!r} revision does not match frozen revision"
                                    )
            if assignment in failed_assignments and assignment not in escalated_assignments:
                weak_retry_count += 1
                errors.append(f"event[{index}] retries failed assignment {assignment!r} without escalation")
            elif assignment in failed_assignments:
                required_tier = escalated_assignments.pop(assignment)
                if tier in TIER_ORDER and TIER_ORDER[tier] < TIER_ORDER[required_tier]:
                    errors.append(
                        f"event[{index}] retry tier {tier!r} is below escalated tier {required_tier!r}"
                    )
            assignment_write_set[assignment] = write_set
            if isinstance(capsule, dict):
                permissions = capsule.get("permissions")
                if not isinstance(permissions, dict):
                    errors.append(f"event[{index}] capsule permissions must be an object")
                else:
                    declared_writes = permissions.get("write", [])
                    if not isinstance(declared_writes, list):
                        errors.append(f"event[{index}] capsule permissions.write must be a list")
                    elif set(declared_writes) != write_set:
                        errors.append(f"event[{index}] write_set does not match capsule permissions.write")
            if tier == "economy" and write_set and isinstance(capsule, dict):
                economy_requirements = {
                    "execution_class": "mechanical",
                    "contract_state": "frozen",
                    "oracle": "deterministic",
                }
                for field, expected in economy_requirements.items():
                    if capsule.get(field) != expected:
                        errors.append(
                            f"event[{index}] economy write requires capsule {field}={expected!r}"
                        )
                if capsule.get("risk_flags") != []:
                    errors.append(f"event[{index}] economy write requires empty risk_flags")
                if capsule.get("reversible") is not True:
                    errors.append(f"event[{index}] economy write requires reversible=true")
            for other_agent, other_writes in active.items():
                overlap = sorted(write_set & other_writes)
                if overlap:
                    errors.append(
                        f"event[{index}] overlapping active writes for {agent!r} and {other_agent!r}: {', '.join(overlap)}"
                    )
            if has_program and write_set and program_state:
                concurrent_writers = [
                    other_agent for other_agent, other_writes in active.items() if other_writes
                ]
                if concurrent_writers and program_state["has_shared_contracts"]:
                    frozen_contracts = {
                        contract_id: contract["revision"]
                        for contract_id, contract in program_state["contracts"].items()
                        if contract.get("state") == "frozen"
                    }
                    participants = [(agent, contract_revisions)] + [
                        (other_agent, active_contract_revisions.get(other_agent, {}))
                        for other_agent in concurrent_writers
                    ]
                    for participant, revisions in participants:
                        missing = sorted(
                            contract_id
                            for contract_id, revision in frozen_contracts.items()
                            if revisions.get(contract_id) != revision
                        )
                        if missing:
                            contract_gate_violations += 1
                            errors.append(
                                f"event[{index}] concurrent write worker {participant!r} lacks frozen contracts: "
                                + ", ".join(missing)
                            )
            active[agent] = write_set
            assignment_for_agent[agent] = assignment
            active_contract_revisions[agent] = contract_revisions
            if tier in TIER_ORDER:
                assignment_tier[assignment] = str(tier)
            successful_assignments.discard(assignment)
            accepted_assignments.discard(assignment)
            rejected_assignments.discard(assignment)
            result_source_fingerprint.pop(assignment, None)
            max_observed_active = max(max_observed_active, len(active))
            if len(active) > max_active:
                errors.append(f"event[{index}] active Agents {len(active)} exceed max_active {max_active}")

        elif event_type == "result":
            if has_program and event.get("stage_id") != (program_state or {}).get("current_stage"):
                errors.append(f"event[{index}] result.stage_id must match program.current_stage")
            agent = str(event.get("agent", ""))
            assignment = str(event.get("assignment_id", ""))
            if agent not in active:
                errors.append(f"event[{index}] result references inactive agent {agent!r}")
            expected = assignment_for_agent.get(agent)
            if expected and assignment != expected:
                errors.append(f"event[{index}] assignment {assignment!r} does not match active {expected!r}")
            status = event.get("status")
            if status == "success":
                successful_assignments.add(assignment)
                if not _nonempty(event.get("evidence")):
                    errors.append(f"event[{index}] successful result lacks evidence")
                if not _nonempty(event.get("source_fingerprint")):
                    errors.append(f"event[{index}] successful result lacks source_fingerprint")
                else:
                    result_source_fingerprint[assignment] = str(event["source_fingerprint"])
            elif status in {"failed", "blocked", "stale"}:
                failed_assignments.add(assignment)
                successful_assignments.discard(assignment)
                accepted_assignments.discard(assignment)
            else:
                errors.append(f"event[{index}] has invalid result status")
            active.pop(agent, None)
            assignment_for_agent.pop(agent, None)
            active_contract_revisions.pop(agent, None)

        elif event_type == "accept":
            if has_program and event.get("stage_id") != (program_state or {}).get("current_stage"):
                errors.append(f"event[{index}] accept.stage_id must match program.current_stage")
            assignment = str(event.get("assignment_id", ""))
            status = event.get("status")
            if assignment not in successful_assignments:
                errors.append(f"event[{index}] acceptance references assignment without collected success")
            expected_owner = assignment_acceptance_owner.get(assignment)
            if not expected_owner or event.get("owner") != expected_owner:
                errors.append(f"event[{index}] acceptance owner does not match capsule")
            if event.get("scope_checked") is not True:
                errors.append(f"event[{index}] acceptance must confirm scope_checked=true")
            if assignment_write_set.get(assignment) and event.get("artifacts_checked") is not True:
                errors.append(f"event[{index}] write acceptance must confirm artifacts_checked=true")
            fingerprint = str(event.get("source_fingerprint", "")).strip()
            if not fingerprint:
                errors.append(f"event[{index}] acceptance lacks source_fingerprint")
            elif result_source_fingerprint.get(assignment) != fingerprint:
                errors.append(f"event[{index}] acceptance source_fingerprint does not match result")
            matrix = event.get("acceptance_matrix")
            if not isinstance(matrix, dict):
                errors.append(f"event[{index}] acceptance_matrix must be an object")
                matrix = {}
            expected_signals = assignment_acceptance.get(assignment, set())
            missing_signals = sorted(
                signal for signal in expected_signals if signal not in matrix or not _nonempty(matrix[signal])
            )
            if missing_signals:
                errors.append(
                    f"event[{index}] acceptance_matrix missing evidence for: {', '.join(missing_signals)}"
                )
            if status == "accepted":
                acceptance_count += 1
                accepted_assignments.add(assignment)
                rejected_assignments.discard(assignment)
            elif status == "rejected":
                rejection_count += 1
                accepted_assignments.discard(assignment)
                rejected_assignments.add(assignment)
                failed_assignments.add(assignment)
            else:
                errors.append(f"event[{index}] has invalid acceptance status")

        elif event_type == "escalate":
            escalation_count += 1
            assignment = str(event.get("assignment_id", ""))
            from_tier = event.get("from_tier")
            to_tier = event.get("to_tier")
            if assignment not in failed_assignments:
                errors.append(f"event[{index}] escalates assignment without a recorded failure")
            expected_from_tier = assignment_tier.get(assignment)
            if expected_from_tier is not None and from_tier != expected_from_tier:
                errors.append(
                    f"event[{index}] escalation from_tier {from_tier!r} does not match failed tier {expected_from_tier!r}"
                )
            if from_tier not in TIER_ORDER or to_tier not in TIER_ORDER:
                errors.append(f"event[{index}] escalation uses an unknown capability tier")
            elif TIER_ORDER[to_tier] <= TIER_ORDER[from_tier]:
                errors.append(f"event[{index}] escalation does not increase capability")
            if not _nonempty(event.get("facts")) or not _nonempty(event.get("evidence")):
                errors.append(f"event[{index}] escalation lacks facts or evidence locators")
            if (
                assignment in failed_assignments
                and from_tier in TIER_ORDER
                and to_tier in TIER_ORDER
                and TIER_ORDER[to_tier] > TIER_ORDER[from_tier]
                and from_tier == expected_from_tier
            ):
                escalated_assignments[assignment] = str(to_tier)

        elif event_type == "integrate":
            if has_program and event.get("stage_id") != (program_state or {}).get("current_stage"):
                errors.append(f"event[{index}] integrate.stage_id must match program.current_stage")
            integration_count += 1
            if strict_schema:
                pending_acceptance = sorted(successful_assignments - accepted_assignments)
                if pending_acceptance:
                    errors.append(
                        f"event[{index}] integrates collected results without acceptance: {', '.join(pending_acceptance)}"
                    )
                if rejected_assignments:
                    errors.append(
                        f"event[{index}] integrates rejected assignments: {', '.join(sorted(rejected_assignments))}"
                    )
            if strict_schema and not _nonempty(event.get("acceptance")):
                errors.append(f"event[{index}] integration lacks acceptance mapping")
            if strict_schema and successful_assignments and not _nonempty(event.get("evidence")):
                errors.append(f"event[{index}] integration lacks evidence")

        elif event_type == "primary_action":
            primary_action_count += 1
            if has_program and event.get("stage_id") != (program_state or {}).get("current_stage"):
                errors.append(f"event[{index}] primary_action.stage_id must match program.current_stage")
            action_class = event.get("action_class")
            allowed_actions = {
                "design", "shared_contract", "coordination", "acceptance", "integration",
                "validation", "delivery", "leaf_implementation",
            }
            if action_class not in allowed_actions:
                errors.append(f"event[{index}] primary_action has invalid action_class")
            write_set = set(event.get("write_set") or [])
            if active and action_class == "leaf_implementation":
                primary_leaf_violations += 1
                errors.append(f"event[{index}] primary_action leaf_implementation is forbidden while workers are active")
            if active and write_set:
                for agent, worker_writes in active.items():
                    overlap = sorted(write_set & worker_writes)
                    if overlap:
                        errors.append(
                            f"event[{index}] primary_action overlaps active worker {agent!r}: {', '.join(overlap)}"
                        )

        else:
            errors.append(f"event[{index}] has unknown type {event_type!r}")

    if route_count != 1:
        errors.append(f"trace requires exactly one RouteDecision; found {route_count}")
    if route_mode == "SINGLE_OWNER" and delegate_count:
        errors.append("SINGLE_OWNER trace must not contain delegate events")
    if route_mode in ROUTE_MODES - {"SINGLE_OWNER"} and delegate_count == 0:
        errors.append(f"{route_mode} trace requires at least one accepted dispatch")
    if strict_schema and delegate_count and len(dispatch_receipts) != delegate_count:
        errors.append("strict trace requires one accepted dispatch_receipt per delegate")
    if active:
        errors.append(f"trace ends with active Agents: {', '.join(sorted(active))}")
    if delegate_count and integration_count == 0:
        errors.append("delegated trace lacks integration")
    unaccepted = sorted(successful_assignments - accepted_assignments)
    if strict_schema and unaccepted:
        errors.append(f"trace ends with collected results lacking acceptance: {', '.join(unaccepted)}")

    return {
        "passed": not errors,
        "errors": errors,
        "warnings": warnings,
        "metrics": {
            "delegations": delegate_count,
            "dispatch_receipts": len(dispatch_receipts),
            "escalations": escalation_count,
            "weak_retry_count": weak_retry_count,
            "max_observed_active": max_observed_active,
            "successful_assignments": len(successful_assignments),
            "accepted_assignments": len(accepted_assignments),
            "acceptances": acceptance_count,
            "rejections": rejection_count,
            "failed_assignments": len(failed_assignments),
            "programs": int(has_program),
            "program_stages": (program_state or {}).get("stage_count", 0),
            "primary_actions": primary_action_count,
            "primary_leaf_violations": primary_leaf_violations,
            "contract_gate_violations": contract_gate_violations,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trace", nargs="?", type=Path, help="JSON trace; omit to read stdin")
    args = parser.parse_args()
    try:
        raw = args.trace.read_text(encoding="utf-8") if args.trace else sys.stdin.read()
        trace = json.loads(raw)
        if not isinstance(trace, dict):
            raise ValueError("top-level JSON value must be an object")
        result = evaluate_trace(trace)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"passed": False, "errors": [str(error)]}, ensure_ascii=False, indent=2))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
