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
COMPACT_CAPSULE_FIELDS = {
    "objective",
    "decision",
    "allowed_scope",
    "acceptance",
    "permissions",
    "directive_revision",
    "work_class",
    "source_fingerprint",
}
READ_ONLY_WORK_CLASSES = {"evidence_scout", "review", "validation"}
PRIMARY_CONTROL_ACTIONS = {
    "design",
    "shared_contract",
    "coordination",
    "acceptance",
    "integration",
    "delivery",
}
PRIMARY_DELEGATED_WORK_ACTIONS = {
    "leaf_implementation",
    "documentation",
    "review",
    "validation",
}
TIER_ORDER = {"economy": 0, "balanced": 1, "strong": 2}
JUDGMENT_FLOOR = {"mechanical": "economy", "bounded_reasoning": "balanced", "architectural": "strong"}
IMPACT_FLOOR = {"local": "economy", "shared": "strong", "irreversible": "strong"}
ORACLE_FLOOR = {"deterministic": "economy", "evidence_backed": "balanced", "judgment": "strong"}
STAGE_KINDS = (
    "discovery",
    "semantic_decision_contract_freeze",
    "implementation",
    "integration",
    "review",
    "validation",
)
WORK_CLASSES = {
    "evidence_scout",
    "documentation",
    "contract_design",
    "implementation",
    "integration",
    "review",
    "validation",
}
FORK_STATUSES = {"NOT_APPLICABLE", "OPEN", "RESOLVED"}
EVIDENCE_STATUSES = {"OPEN", "STOPPED"}
EVIDENCE_RESULTS = {
    "PLANNED",
    "DISCRIMINATING",
    "INVALID",
    "INCONCLUSIVE",
    "SCOPE_INVALID",
}
EVIDENCE_STOP_REASONS = {
    "FREEZE",
    "ASK_USER",
    "BLOCKER",
    "INVALID_OBSERVATION",
    "SOURCE_DRIFT",
    "HIGH_RISK_GAP",
}
TERMINAL_DISCOVERY_REASONS = {"FREEZE", "ASK_USER", "BLOCKER"}
DISCOVERY_REOPEN_REASONS = {
    "NEW_CANDIDATE",
    "INVALID_OBSERVATION",
    "SOURCE_DRIFT",
    "HIGH_RISK_GAP",
}
ARTIFACT_DISPOSITION_REASONS = {
    "REVIEW_FINDING",
    "EXTERNAL_INVALIDATION",
    "ADMISSION_PRECONDITION_INVALIDATED",
    "OWNER_DECISION",
}


def _nonempty(value: Any) -> bool:
    return value not in (None, "", [], {})


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _evidence_locators(value: Any) -> bool:
    """Evidence is a locator or locator list, never a boolean agreement signal."""
    return _nonempty_string(value) or (
        isinstance(value, list)
        and bool(value)
        and all(_nonempty_string(item) for item in value)
    )


def _enum(value: Any, allowed: set[str] | dict[str, Any] | tuple[str, ...]) -> bool:
    return isinstance(value, str) and value in allowed


def _validate_capability_floor(value: Any, path: str, errors: list[str]) -> str | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        errors.append(f"{path} must be an object")
        return None
    dimensions = (
        ("judgment", JUDGMENT_FLOOR),
        ("impact", IMPACT_FLOOR),
        ("oracle", ORACLE_FLOOR),
    )
    floors: list[str] = []
    for field, mapping in dimensions:
        current = value.get(field)
        if not _enum(current, mapping):
            errors.append(f"{path}.{field} is invalid")
        else:
            floors.append(mapping[str(current)])
    declared = value.get("minimum_tier")
    if not _enum(declared, TIER_ORDER):
        errors.append(f"{path}.minimum_tier is invalid")
        return None
    if floors:
        required = max(floors, key=lambda tier: TIER_ORDER[tier])
        if TIER_ORDER[str(declared)] < TIER_ORDER[required]:
            errors.append(f"{path}.minimum_tier {declared!r} is below derived floor {required!r}")
    return str(declared)


def _normalized_string_set(value: Any, path: str, errors: list[str]) -> set[str]:
    if not isinstance(value, list):
        errors.append(f"{path} must be a normalized string list")
        return set()
    result = {item for item in value if _nonempty_string(item)}
    if len(result) != len(value):
        errors.append(f"{path} must contain only unique nonempty strings")
    return result


def _acceptance_signals(value: Any) -> set[str]:
    if isinstance(value, dict):
        return {signal.strip() for signal in value if _nonempty_string(signal)}
    if isinstance(value, list):
        return {signal.strip() for signal in value if _nonempty_string(signal)}
    return set()


def _expand_compact_capsule(
    capsule: dict[str, Any], *, depth: int, trace_budget: dict[str, Any]
) -> dict[str, Any]:
    """Expand policy defaults without making workers restate control-plane boilerplate."""
    expanded = dict(capsule)
    source_fingerprint = capsule.get("source_fingerprint")
    expanded.setdefault("excluded_scope", ["everything outside allowed_scope"])
    expanded.setdefault("inputs", [{"source_fingerprint": source_fingerprint}])
    expanded.setdefault("acceptance_owner", "primary")
    expanded.setdefault(
        "output_contract",
        [
            "status",
            "changed_artifacts",
            "evidence",
            "unverified_items",
            "scope_or_contract_conflicts",
        ],
    )
    expanded.setdefault(
        "stop_conditions",
        ["scope drift", "source drift", "permission need", "failed acceptance"],
    )
    expanded.setdefault(
        "escalation_triggers",
        ["shared-contract decision", "new material risk", "non-deterministic oracle"],
    )
    expanded.setdefault("parent_assignment_id", "primary")
    expanded.setdefault("depth", depth)
    expanded.setdefault("budget", {"max_children": 0, "max_active": trace_budget.get("max_active", 2)})
    expanded.setdefault("delegation", "denied")
    return expanded


def _validate_semantic_fork(
    value: Any, errors: list[str], *, required: bool
) -> dict[str, Any] | None:
    if value is None and not required:
        return None
    if not isinstance(value, dict):
        errors.append("semantic_fork must be an object")
        return None
    if not _nonempty_string(value.get("decision_question")):
        errors.append("semantic_fork.decision_question must be nonempty")
    status = value.get("status")
    if not isinstance(status, str) or status not in FORK_STATUSES:
        errors.append("semantic_fork.status is invalid")
    evidence_can_decide = value.get("evidence_can_decide")
    if not (
        evidence_can_decide is True
        or evidence_can_decide is False
        or evidence_can_decide == "unknown"
    ):
        errors.append("semantic_fork.evidence_can_decide must be true, false, or 'unknown'")
    options = value.get("options")
    if not isinstance(options, list):
        errors.append("semantic_fork.options must be a list")
        options = []
    option_ids: set[str] = set()
    for index, option in enumerate(options):
        if not isinstance(option, dict):
            errors.append(f"semantic_fork.options[{index}] must be an object")
            continue
        option_id_value = option.get("id")
        option_id = option_id_value.strip() if isinstance(option_id_value, str) else ""
        if not option_id or not _nonempty_string(option.get("contract")):
            errors.append(f"semantic_fork.options[{index}] requires id and contract")
        elif option_id in option_ids:
            errors.append(f"semantic_fork.options[{index}].id duplicates {option_id!r}")
        else:
            option_ids.add(option_id)
    consequences = value.get("architectural_consequences")
    if not isinstance(consequences, dict):
        errors.append("semantic_fork.architectural_consequences must be an object")
        consequences = {}
    material_consequences = {
        key: consequence
        for key, consequence in consequences.items()
        if _nonempty_string(key) and _nonempty_string(consequence)
    }
    if _enum(status, {"OPEN", "RESOLVED"}):
        if len(options) < 2:
            errors.append(f"semantic_fork.status={status} requires at least two options")
        if not material_consequences:
            errors.append(
                f"semantic_fork.status={status} requires a material architectural consequence"
            )
    elif status == "NOT_APPLICABLE" and len(options) >= 2 and material_consequences:
        errors.append(
            "semantic_fork cannot be NOT_APPLICABLE when multiple material contract options are declared"
        )
    resolution = value.get("resolution")
    if status == "RESOLVED":
        if not isinstance(resolution, dict):
            errors.append("semantic_fork RESOLVED requires resolution")
        else:
            if not _enum(resolution.get("source"), {"EVIDENCE", "USER"}):
                errors.append("semantic_fork.resolution.source must be EVIDENCE or USER")
            if resolution.get("source") == "EVIDENCE" and evidence_can_decide is not True:
                errors.append(
                    "semantic_fork.resolution.source=EVIDENCE requires evidence_can_decide=true"
                )
            for field in ("decision", "locator"):
                if not _nonempty_string(resolution.get(field)):
                    errors.append(f"semantic_fork.resolution.{field} must be nonempty")
    elif resolution is not None:
        errors.append("semantic_fork resolution is valid only when status=RESOLVED")
    return value


def _validate_evidence_budget(
    value: Any, errors: list[str], *, required: bool
) -> dict[str, Any] | None:
    if value is None and not required:
        return None
    if not isinstance(value, dict):
        errors.append("evidence_budget must be an object")
        return None
    round_number = value.get("round")
    scout_count = value.get("scout_count")
    if not isinstance(round_number, int) or isinstance(round_number, bool) or round_number < 1:
        errors.append("evidence_budget.round must be a positive integer")
    if not isinstance(scout_count, int) or isinstance(scout_count, bool) or scout_count < 0:
        errors.append("evidence_budget.scout_count must be a non-negative integer")
    status = value.get("status")
    if not isinstance(status, str) or status not in EVIDENCE_STATUSES:
        errors.append("evidence_budget.status is invalid")
    stop_reason = value.get("stop_reason")
    if status == "STOPPED" and not _enum(stop_reason, EVIDENCE_STOP_REASONS):
        errors.append("evidence_budget STOPPED requires a valid stop_reason")
    if status == "OPEN" and stop_reason is not None:
        errors.append("evidence_budget OPEN must not declare stop_reason")
    return value


def _validate_artifacts(value: Any, errors: list[str]) -> dict[str, str]:
    if value is None:
        return {}
    if not isinstance(value, list):
        errors.append("artifacts must be a list")
        return {}
    artifacts: dict[str, str] = {}
    for index, artifact in enumerate(value):
        prefix = f"artifacts[{index}]"
        if not isinstance(artifact, dict):
            errors.append(f"{prefix} must be an object")
            continue
        artifact_id = str(artifact.get("artifact_id", "")).strip()
        status = artifact.get("status")
        if not artifact_id:
            errors.append(f"{prefix}.artifact_id must be nonempty")
        elif artifact_id in artifacts:
            errors.append(f"{prefix}.artifact_id duplicates {artifact_id!r}")
        elif _enum(status, {"candidate", "retained", "discarded"}):
            artifacts[artifact_id] = str(status)
        if not _enum(status, {"candidate", "retained", "discarded"}):
            errors.append(f"{prefix}.status is invalid")
    return artifacts


def _validate_program(
    program: Any, errors: list[str], warnings: list[str], *, admission_schema: bool
) -> dict[str, Any] | None:
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
    stage_kinds_seen: set[str] = set()
    previous_stage_kind_index = -1
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
        stage_kind = stage.get("stage_kind")
        if admission_schema:
            if not _enum(stage_kind, STAGE_KINDS):
                errors.append(f"{prefix}.stage_kind is invalid")
            else:
                stage_kind = str(stage_kind)
                stage_kind_index = STAGE_KINDS.index(stage_kind)
                if stage_kind in stage_kinds_seen:
                    warnings.append(f"{prefix}.stage_kind duplicates {stage_kind!r}; inspect whether this stage adds value")
                if stage_kind_index <= previous_stage_kind_index:
                    warnings.append(f"{prefix}.stage_kind is out of canonical order; dependency admission remains authoritative")
                stage_kinds_seen.add(stage_kind)
                previous_stage_kind_index = stage_kind_index
        if not isinstance(stage.get("depends_on"), list):
            errors.append(f"{prefix}.depends_on must be a list")
        if admission_schema and not isinstance(stage.get("required_contracts"), list):
            errors.append(f"{prefix}.required_contracts must be a list")
        if not _nonempty(stage.get("entry_gate")):
            errors.append(f"{prefix}.entry_gate must be nonempty")
        if not _enum(stage.get("route_mode"), ROUTE_MODES):
            errors.append(f"{prefix}.route_mode is invalid")
        if not _nonempty(stage.get("exit_gate")):
            errors.append(f"{prefix}.exit_gate must be nonempty")
        if not _enum(stage.get("status"), {"pending", "active", "blocked", "completed"}):
            errors.append(f"{prefix}.status is invalid")
        if admission_schema and stage_kind == "review":
            if not _nonempty(stage.get("review_targets")):
                errors.append(f"{prefix}.review_targets must be nonempty")
            if not _nonempty(stage.get("material_risks")):
                errors.append(f"{prefix}.material_risks must be nonempty")

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
        if not _enum(contract.get("state"), {"proposed", "frozen", "superseded"}):
            errors.append(f"{prefix}.state is invalid")
        if not _nonempty(contract.get("owner")):
            errors.append(f"{prefix}.owner must be nonempty")

    if admission_schema and current is not None:
        required_contracts = current.get("required_contracts", [])
        if current.get("stage_kind") == "implementation" and not required_contracts:
            errors.append("program implementation stage requires relevant required_contracts")
        if isinstance(required_contracts, list):
            for contract_id in required_contracts:
                contract = contract_by_id.get(str(contract_id))
                if contract is None:
                    errors.append(
                        f"program.current_stage requires unknown contract {contract_id!r}"
                    )
                elif contract.get("state") != "frozen":
                    errors.append(
                        f"program.current_stage requires contract {contract_id!r} to be frozen"
                    )

    return {
        "current_stage": current_stage,
        "current": current,
        "stages": stage_by_id,
        "current_stage_kind": current.get("stage_kind") if current else None,
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

    schema_version = trace.get("schema_version", 1)
    if not isinstance(schema_version, int) or isinstance(schema_version, bool) or schema_version < 1:
        errors.append("schema_version must be a positive integer")
        schema_version = 1
    admission_schema = schema_version >= 4
    compact_schema = schema_version >= 5
    declared_route_modes = {
        str(event.get("mode"))
        for event in events
        if isinstance(event, dict)
        and event.get("type") == "route"
        and _enum(event.get("mode"), ROUTE_MODES)
    }
    program_state = _validate_program(
        trace.get("program"), errors, warnings, admission_schema=admission_schema
    )
    has_program = trace.get("program") is not None
    strict_schema = schema_version >= 2 or has_program or any(
        isinstance(event, dict)
        and (_enum(event.get("type"), {"accept", "primary_action"}) or "dispatch_receipt" in event)
        for event in events
    )
    authority_schema = schema_version >= 3
    decision_state_required = admission_schema and not (
        compact_schema
        and not has_program
        and declared_route_modes == {"SINGLE_OWNER"}
    )
    semantic_fork = _validate_semantic_fork(
        trace.get("semantic_fork"), errors, required=decision_state_required
    )
    evidence_budget = _validate_evidence_budget(
        trace.get("evidence_budget"), errors, required=False
    )
    artifact_state = _validate_artifacts(trace.get("artifacts"), errors)

    semantic_fork_status = (semantic_fork or {}).get("status")
    if admission_schema and semantic_fork_status == "OPEN" and evidence_budget is None:
        errors.append("semantic_fork.status=OPEN requires evidence_budget")
    current_stage_kind = (program_state or {}).get("current_stage_kind")
    stage_admission_violations = 0
    if (
        admission_schema
        and semantic_fork_status == "OPEN"
        and _enum(current_stage_kind, {"implementation", "integration", "review", "validation"})
    ):
        stage_admission_violations += 1
        errors.append(
            f"program stage {current_stage_kind!r} is forbidden while semantic_fork.status=OPEN"
        )

    budget = trace.get("budget") if isinstance(trace.get("budget"), dict) else {}
    max_active_value = budget.get("max_active", 2)
    if (
        not isinstance(max_active_value, int)
        or isinstance(max_active_value, bool)
        or max_active_value < 1
    ):
        errors.append("budget.max_active must be a positive integer")
        max_active = 2
    else:
        max_active = max_active_value
    max_depth_value = budget.get("max_depth", 1)
    if (
        not isinstance(max_depth_value, int)
        or isinstance(max_depth_value, bool)
        or max_depth_value < 1
    ):
        errors.append("budget.max_depth must be a positive integer")
        max_depth = 1
    else:
        max_depth = max_depth_value
    route_count = 0
    route_mode: str | None = None
    integration_count = 0
    invalidated_obligations: set[str] = set()
    retired_assignments: set[str] = set()
    assignment_supersedes: dict[str, set[str]] = {}
    collected_assignments: set[str] = set()
    integrated_assignments: set[str] = set()
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
    primary_work_violations = 0
    contract_gate_violations = 0
    semantic_fork_admission_violations = 0
    scout_budget_violations = 0
    review_admission_violations = 0
    review_of_later_discarded_artifact = 0
    premature_review_admission_violations = 0
    active_contract_revisions: dict[str, dict[str, Any]] = {}
    current_contract_revisions: dict[str, Any] = {
        contract_id: contract.get("revision")
        for contract_id, contract in (program_state or {}).get("contracts", {}).items()
        if contract.get("state") == "frozen"
    }
    assignment_contract_revisions: dict[str, dict[str, Any]] = {}
    stale_contract_results = 0
    assignment_capsules: dict[str, dict[str, Any]] = {}
    assignment_work_class: dict[str, str] = {}
    assignment_directive_revision: dict[str, str] = {}
    required_directive_revision: dict[str, str] = {}
    current_directive_revision = trace.get("directive_revision")
    if current_directive_revision is not None and not _nonempty_string(current_directive_revision):
        errors.append("directive_revision must be a nonempty identity when present")
    task_binding = {
        field: trace[field]
        for field in ("task_id", "run_id", "workspace_id")
        if field in trace
    }
    for field, value in task_binding.items():
        if not _nonempty_string(value):
            errors.append(f"{field} must be a nonempty identity when present")
    assignment_source_fingerprint: dict[str, str] = {}
    compact_assignments: set[str] = set()
    assignment_scout_round: dict[str, int] = {}
    route_decision_question: str | None = None
    scout_counts_by_round: dict[int, int] = {}
    scout_axes_by_round: dict[int, set[str]] = {}
    evidence_gates: dict[int, dict[str, Any]] = {}
    evidence_reopens: dict[int, str] = {}
    terminal_discovery_gate: dict[str, Any] | None = None
    scout_rounds_after_discriminating_evidence: set[int] = set()
    reviewed_targets: set[str] = set()
    seen_assignment_ids: set[str] = set()
    invalid_observation_reopens = 0

    if admission_schema and current_stage_kind == "implementation" and program_state:
        for contract_id in (program_state.get("current") or {}).get("required_contracts", []):
            contract = program_state["contracts"].get(str(contract_id))
            if contract is None or contract.get("state") != "frozen":
                stage_admission_violations += 1
                contract_gate_violations += 1
    if admission_schema and current_stage_kind == "review" and program_state:
        review_stage = program_state.get("current") or {}
        for target in review_stage.get("review_targets", []):
            if artifact_state.get(str(target)) != "retained":
                review_admission_violations += 1
                stage_admission_violations += 1
                errors.append(
                    f"program review target {str(target)!r} is not a retained artifact"
                )

    for index, event in enumerate(events):
        if not isinstance(event, dict):
            errors.append(f"event[{index}] must be an object")
            continue
        event_type = event.get("type")
        if _enum(event_type, {"delegate", "result", "accept", "integrate"}):
            for field, expected_identity in task_binding.items():
                if event.get(field) != expected_identity:
                    errors.append(f"event[{index}].{field} does not match trace identity")

        if event_type == "route":
            route_count += 1
            if not _enum(event.get("mode"), ROUTE_MODES):
                errors.append(f"event[{index}] has invalid route mode")
            else:
                route_mode = str(event["mode"])
            raw_decision_question = event.get("decision_question")
            decision_question = (
                raw_decision_question.strip()
                if _nonempty_string(raw_decision_question)
                else None
            )
            decision_question_required = admission_schema and not (
                compact_schema
                and event.get("mode") == "SINGLE_OWNER"
                and not has_program
            )
            if decision_question_required and decision_question is None:
                errors.append(f"event[{index}] route lacks decision_question")
            elif decision_question:
                route_decision_question = decision_question
            if not _nonempty(event.get("rationale")):
                errors.append(f"event[{index}] route lacks rationale")
            if admission_schema and event.get("mode") == "PARALLEL_SCOUTS":
                if evidence_budget is None:
                    errors.append(f"event[{index}] PARALLEL_SCOUTS requires evidence_budget")
                raw_fork_question = (semantic_fork or {}).get("decision_question")
                fork_question = raw_fork_question.strip() if _nonempty_string(raw_fork_question) else None
                if decision_question and fork_question and decision_question != fork_question:
                    errors.append(
                        f"event[{index}] route decision_question must match semantic_fork.decision_question"
                    )
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
            raw_agent = event.get("agent")
            raw_assignment = event.get("assignment_id")
            agent = raw_agent.strip() if _nonempty_string(raw_agent) else ""
            assignment = raw_assignment.strip() if _nonempty_string(raw_assignment) else ""
            raw_write_set = event.get("write_set", [])
            write_set = _normalized_string_set(
                [] if raw_write_set is None else raw_write_set,
                f"event[{index}].write_set",
                errors,
            )
            if not agent or not assignment:
                errors.append(f"event[{index}] delegate requires agent and assignment_id")
                continue
            if admission_schema and assignment in seen_assignment_ids:
                errors.append(f"event[{index}] duplicates assignment_id {assignment!r}")
                continue
            seen_assignment_ids.add(assignment)
            if agent in active:
                errors.append(f"event[{index}] agent {agent!r} is already active")
            tier = event.get("tier")
            if not _enum(tier, TIER_ORDER):
                errors.append(f"event[{index}] delegate uses an unknown capability tier")
            raw_dispatch_receipt = event.get("dispatch_receipt")
            dispatch_receipt = (
                raw_dispatch_receipt.strip() if _nonempty_string(raw_dispatch_receipt) else ""
            )
            if strict_schema and not dispatch_receipt:
                errors.append(f"event[{index}] delegate lacks accepted dispatch_receipt")
            elif dispatch_receipt in dispatch_receipts:
                errors.append(f"event[{index}] reuses dispatch_receipt {dispatch_receipt!r}")
            else:
                dispatch_receipts.add(dispatch_receipt)
            depth_value = event.get("depth", 1)
            if (
                not isinstance(depth_value, int)
                or isinstance(depth_value, bool)
                or depth_value < 1
            ):
                errors.append(f"event[{index}] depth must be a positive integer")
                depth = 1
            else:
                depth = depth_value
            if depth > max_depth:
                errors.append(f"event[{index}] depth {depth} exceeds max_depth {max_depth}")
            capsule = event.get("capsule")
            if not isinstance(capsule, dict):
                errors.append(f"event[{index}] delegate lacks Assignment Capsule")
            else:
                minimum_tier = _validate_capability_floor(
                    capsule.get("capability_floor"),
                    f"event[{index}] capsule.capability_floor",
                    errors,
                )
                if (
                    minimum_tier is not None
                    and _enum(tier, TIER_ORDER)
                    and TIER_ORDER[str(tier)] < TIER_ORDER[minimum_tier]
                ):
                    errors.append(
                        f"event[{index}] tier {tier!r} is below capsule capability floor {minimum_tier!r}"
                    )
                capsule_profile = capsule.get("profile")
                if capsule_profile is not None and capsule_profile != "compact":
                    errors.append(f"event[{index}] capsule.profile must be compact when present")
                if capsule_profile == "compact":
                    if not compact_schema:
                        errors.append(
                            f"event[{index}] compact capsule requires schema_version >= 5"
                        )
                    missing_compact = sorted(
                        field
                        for field in COMPACT_CAPSULE_FIELDS
                        if not _nonempty(capsule.get(field))
                    )
                    if missing_compact:
                        errors.append(
                            f"event[{index}] compact capsule missing: {', '.join(missing_compact)}"
                        )
                    if depth != 1:
                        errors.append(
                            f"event[{index}] compact capsule supports depth-one leaf delegation only"
                        )
                    capsule = _expand_compact_capsule(
                        capsule, depth=depth, trace_budget=budget
                    )
                    compact_assignments.add(assignment)
                if authority_schema:
                    required_capsule_fields = AUTHORITY_CAPSULE_FIELDS
                else:
                    required_capsule_fields = STRICT_CAPSULE_FIELDS if strict_schema else CAPSULE_FIELDS
                missing = sorted(field for field in required_capsule_fields if not _nonempty(capsule.get(field)))
                if missing:
                    errors.append(f"event[{index}] capsule missing: {', '.join(missing)}")
                if admission_schema and not _nonempty_string(capsule.get("directive_revision")):
                    errors.append(f"event[{index}] capsule.directive_revision must be nonempty")
                elif _nonempty_string(capsule.get("directive_revision")):
                    if current_directive_revision is not None and capsule["directive_revision"] != current_directive_revision:
                        errors.append(f"event[{index}] capsule.directive_revision does not match current directive")
                    assignment_directive_revision[assignment] = str(
                        capsule["directive_revision"]
                    )
                    required_directive_revision[assignment] = str(capsule["directive_revision"])
                if "source_fingerprint" in capsule:
                    assignment_source_fingerprint[assignment] = str(
                        capsule.get("source_fingerprint", "")
                    ).strip()
                signals = _acceptance_signals(capsule.get("acceptance")) if strict_schema else set()
                if strict_schema and not signals:
                    errors.append(f"event[{index}] capsule acceptance must declare named signals")
                assignment_acceptance[assignment] = signals
                assignment_acceptance_owner[assignment] = str(capsule.get("acceptance_owner", ""))
                if admission_schema:
                    work_class = capsule.get("work_class")
                    if not _enum(work_class, WORK_CLASSES):
                        errors.append(f"event[{index}] capsule work_class is invalid")
                    else:
                        work_class = str(work_class)
                        assignment_work_class[assignment] = work_class
                        if work_class in READ_ONLY_WORK_CLASSES and write_set:
                            errors.append(
                                f"event[{index}] work_class {work_class!r} must be read-only"
                            )
                        if semantic_fork_status == "OPEN" and work_class in {
                            "documentation",
                            "contract_design",
                            "implementation",
                            "integration",
                            "review",
                        }:
                            semantic_fork_admission_violations += 1
                            stage_admission_violations += 1
                            errors.append(
                                f"event[{index}] {work_class} delegation is forbidden while semantic_fork.status=OPEN"
                            )

                        allowed_by_stage = {
                            "discovery": {"evidence_scout"},
                            "semantic_decision_contract_freeze": {
                                "evidence_scout", "documentation", "contract_design"
                            },
                            "implementation": {"implementation"},
                            "integration": {"integration"},
                            "review": {"review"},
                            "validation": {"validation"},
                        }
                        if (
                            isinstance(current_stage_kind, str)
                            and current_stage_kind in allowed_by_stage
                            and work_class not in allowed_by_stage[current_stage_kind]
                        ):
                            stage_admission_violations += 1
                            errors.append(
                                f"event[{index}] work_class {work_class!r} is not admitted in stage "
                                f"{current_stage_kind!r}"
                            )

                        if route_mode == "PARALLEL_SCOUTS":
                            if work_class != "evidence_scout":
                                scout_budget_violations += 1
                                errors.append(
                                    f"event[{index}] PARALLEL_SCOUTS accepts only evidence_scout work"
                                )
                            for field in ("hypothesis", "discriminator", "evidence_axis"):
                                if not _nonempty(capsule.get(field)):
                                    errors.append(
                                        f"event[{index}] scout capsule requires nonempty {field}"
                                    )
                            if capsule.get("decision") != route_decision_question:
                                errors.append(
                                    f"event[{index}] scout decision must match route decision_question"
                                )
                            if write_set:
                                errors.append(f"event[{index}] evidence scout must be read-only")
                            scout_round = capsule.get("scout_round")
                            if not isinstance(scout_round, int) or scout_round < 1:
                                errors.append(
                                    f"event[{index}] scout_round must be a positive integer"
                                )
                            else:
                                assignment_scout_round[assignment] = scout_round
                                if terminal_discovery_gate is not None:
                                    scout_budget_violations += 1
                                    scout_rounds_after_discriminating_evidence.add(scout_round)
                                    errors.append(
                                        f"event[{index}] scout dispatched after discovery stopped with "
                                        f"{terminal_discovery_gate['stop_reason']}"
                                    )
                                count = scout_counts_by_round.get(scout_round, 0) + 1
                                scout_counts_by_round[scout_round] = count
                                if count > 2:
                                    scout_budget_violations += 1
                                    warnings.append(
                                        f"event[{index}] scout round {scout_round} exceeds default limit 2"
                                    )
                                evidence_axis = str(capsule.get("evidence_axis", "")).strip()
                                axes = scout_axes_by_round.setdefault(scout_round, set())
                                if evidence_axis and evidence_axis in axes:
                                    errors.append(
                                        f"event[{index}] scout round {scout_round} duplicates evidence_axis "
                                        f"{evidence_axis!r}"
                                    )
                                if evidence_axis:
                                    axes.add(evidence_axis)
                                expansion_reason = capsule.get("expansion_reason")
                                if scout_round == 1:
                                    if expansion_reason is not None:
                                        errors.append(
                                            f"event[{index}] first scout round must not declare expansion_reason"
                                        )
                                else:
                                    reopen_reason = evidence_reopens.get(scout_round)
                                    if not _enum(reopen_reason, DISCOVERY_REOPEN_REASONS):
                                        scout_budget_violations += 1
                                        errors.append(
                                            f"event[{index}] scout round {scout_round} lacks an admissible evidence_reopen"
                                        )
                                    if expansion_reason != reopen_reason:
                                        errors.append(
                                            f"event[{index}] scout expansion_reason must match evidence_reopen"
                                        )

                        if work_class == "review":
                            review_targets = capsule.get("review_targets")
                            material_risks = capsule.get("material_risks")
                            if not isinstance(review_targets, list) or not review_targets:
                                review_admission_violations += 1
                                errors.append(
                                    f"event[{index}] review requires nonempty review_targets"
                                )
                            else:
                                for target in review_targets:
                                    target_id = str(target)
                                    reviewed_targets.add(target_id)
                                    if artifact_state.get(target_id) != "retained":
                                        review_admission_violations += 1
                                        errors.append(
                                            f"event[{index}] review target {target_id!r} is not retained"
                                        )
                            if not isinstance(material_risks, list) or not material_risks:
                                review_admission_violations += 1
                                errors.append(
                                    f"event[{index}] review requires named material_risks"
                                )
                if authority_schema:
                    capsule_depth = capsule.get("depth")
                    if not isinstance(capsule_depth, int) or capsule_depth != depth:
                        errors.append(f"event[{index}] capsule depth must match delegate depth")
                    delegation = capsule.get("delegation")
                    if not _enum(delegation, {"denied", "brokered"}):
                        errors.append(f"event[{index}] capsule delegation must be denied or brokered")
                    broker_enforced = budget.get("spawn_broker_enforced") is True
                    if delegation == "brokered" and not broker_enforced:
                        errors.append(f"event[{index}] brokered delegation requires spawn_broker_enforced=true")
                    raw_parent_assignment = capsule.get("parent_assignment_id")
                    parent_assignment = (
                        raw_parent_assignment.strip()
                        if _nonempty_string(raw_parent_assignment)
                        else ""
                    )
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
                            parent_scope_set = _normalized_string_set(
                                parent_scope,
                                f"event[{index}] parent allowed_scope",
                                errors,
                            )
                            child_scope_set = _normalized_string_set(
                                child_scope,
                                f"event[{index}] child allowed_scope",
                                errors,
                            )
                            if not child_scope_set.issubset(parent_scope_set):
                                errors.append(f"event[{index}] child allowed_scope exceeds parent authority")
                            parent_permissions = parent_capsule.get("permissions")
                            child_permissions = capsule.get("permissions")
                            if isinstance(parent_permissions, dict) and isinstance(child_permissions, dict):
                                for permission in ("read", "write", "external_side_effects", "secrets"):
                                    parent_values = parent_permissions.get(permission, [])
                                    child_values = child_permissions.get(permission, [])
                                    parent_value_set = _normalized_string_set(
                                        parent_values,
                                        f"event[{index}] parent permissions.{permission}",
                                        errors,
                                    )
                                    child_value_set = _normalized_string_set(
                                        child_values,
                                        f"event[{index}] child permissions.{permission}",
                                        errors,
                                    )
                                    if not child_value_set.issubset(parent_value_set):
                                        errors.append(
                                            f"event[{index}] child permissions.{permission} exceeds parent authority"
                                        )
                                parent_write_set = _normalized_string_set(
                                    parent_permissions.get("write", []),
                                    f"event[{index}] parent permissions.write",
                                    errors,
                                )
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
            contract_revisions: dict[str, Any] = {}
            if has_program:
                if event.get("stage_id") != (program_state or {}).get("current_stage"):
                    errors.append(f"event[{index}] delegate.stage_id must match program.current_stage")
                if not isinstance(capsule, dict):
                    pass
                else:
                    if not isinstance(capsule.get("depends_on"), list):
                        errors.append(f"event[{index}] program capsule.depends_on must be a list")
                    else:
                        dependencies = _normalized_string_set(
                            capsule["depends_on"], f"event[{index}] capsule.depends_on", errors
                        )
                        stages = (program_state or {}).get("stages", {})
                        for dependency in dependencies:
                            stage = stages.get(dependency)
                            if stage is not None and stage.get("status") == "completed":
                                continue
                            if dependency in accepted_assignments:
                                if (
                                    assignment_directive_revision.get(dependency)
                                    != required_directive_revision.get(dependency)
                                    or any(
                                        current_contract_revisions.get(contract_id) != revision
                                        for contract_id, revision in assignment_contract_revisions.get(dependency, {}).items()
                                    )
                                ):
                                    errors.append(f"event[{index}] dependency {dependency!r} has stale acceptance")
                                continue
                            errors.append(
                                f"event[{index}] dependency {dependency!r} must reference a completed stage "
                                "or an already accepted assignment"
                            )
                    if not isinstance(capsule.get("contract_revisions"), dict):
                        errors.append(f"event[{index}] program capsule.contract_revisions must be an object")
                    else:
                        contract_revisions = capsule["contract_revisions"]
                        if program_state:
                            if write_set and program_state["has_shared_contracts"]:
                                if admission_schema:
                                    declared_contracts = {
                                        str(contract_id)
                                        for contract_id in (program_state["current"] or {}).get(
                                            "required_contracts", []
                                        )
                                    }
                                else:
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
                                elif revision != current_contract_revisions.get(str(contract_id)):
                                    contract_gate_violations += 1
                                    errors.append(
                                        f"event[{index}] contract {contract_id!r} revision does not match frozen revision"
                                    )
            if admission_schema:
                raw_retry_of = event.get("retry_of")
                retry_of = raw_retry_of.strip() if _nonempty_string(raw_retry_of) else None
                if raw_retry_of is not None and retry_of is None:
                    errors.append(f"event[{index}] retry_of must be a nonempty assignment_id")
                if retry_of is not None:
                    if retry_of not in failed_assignments:
                        errors.append(
                            f"event[{index}] retry_of references assignment without a recorded failure"
                        )
                    required_tier = escalated_assignments.pop(retry_of, None)
                    if required_tier is None:
                        weak_retry_count += 1
                        errors.append(
                            f"event[{index}] retries failed assignment {retry_of!r} without escalation"
                        )
                    elif _enum(tier, TIER_ORDER) and TIER_ORDER[tier] < TIER_ORDER[required_tier]:
                        errors.append(
                            f"event[{index}] retry tier {tier!r} is below escalated tier {required_tier!r}"
                        )
            elif assignment in failed_assignments and assignment not in escalated_assignments:
                weak_retry_count += 1
                errors.append(f"event[{index}] retries failed assignment {assignment!r} without escalation")
            elif assignment in failed_assignments:
                required_tier = escalated_assignments.pop(assignment)
                if _enum(tier, TIER_ORDER) and TIER_ORDER[tier] < TIER_ORDER[required_tier]:
                    errors.append(
                        f"event[{index}] retry tier {tier!r} is below escalated tier {required_tier!r}"
                    )
            assignment_write_set[assignment] = write_set
            if isinstance(capsule, dict):
                permissions = capsule.get("permissions")
                if not isinstance(permissions, dict):
                    errors.append(f"event[{index}] capsule permissions must be an object")
                else:
                    declared_writes = _normalized_string_set(
                        permissions.get("write", []),
                        f"event[{index}] capsule permissions.write",
                        errors,
                    )
                    if declared_writes != write_set:
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
                    if admission_schema:
                        relevant_contracts = {
                            str(contract_id)
                            for contract_id in (program_state["current"] or {}).get(
                                "required_contracts", []
                            )
                        }
                    else:
                        relevant_contracts = set(program_state["contracts"])
                    frozen_contracts = {
                        contract_id: revision
                        for contract_id, revision in current_contract_revisions.items()
                        if contract_id in relevant_contracts
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
            if "supersedes" in event:
                raw_supersedes = event["supersedes"]
                replacements = _normalized_string_set(
                    [raw_supersedes] if _nonempty_string(raw_supersedes) else raw_supersedes,
                    f"event[{index}].supersedes", errors,
                )
                if not replacements or replacements - invalidated_obligations:
                    errors.append(f"event[{index}] supersedes must reference outstanding invalidated assignments")
                assignment_supersedes[assignment] = replacements
            active[agent] = write_set
            assignment_for_agent[agent] = assignment
            active_contract_revisions[agent] = contract_revisions
            assignment_contract_revisions[assignment] = dict(contract_revisions)
            if _enum(tier, TIER_ORDER):
                assignment_tier[assignment] = str(tier)
            successful_assignments.discard(assignment)
            accepted_assignments.discard(assignment)
            rejected_assignments.discard(assignment)
            result_source_fingerprint.pop(assignment, None)
            max_observed_active = max(max_observed_active, len(active))
            if len(active) > max_active:
                diagnostics = errors if "max_active" in budget else warnings
                diagnostics.append(f"event[{index}] active Agents {len(active)} exceed max_active {max_active}")

        elif event_type == "contract_update":
            if not has_program:
                errors.append(f"event[{index}] contract_update requires an OrchestrationProgram")
            if event.get("owner") != "primary":
                errors.append(f"event[{index}] contract_update owner must be primary")
            revisions = event.get("contract_revisions")
            if not isinstance(revisions, dict) or not revisions:
                errors.append(f"event[{index}] contract_update.contract_revisions must be a nonempty object")
                revisions = {}
            if not _evidence_locators(event.get("evidence")):
                errors.append(f"event[{index}] contract_update lacks evidence")
            changed_contracts: set[str] = set()
            for contract_id, revision in revisions.items():
                normalized_id = str(contract_id)
                if normalized_id not in (program_state or {}).get("contracts", {}):
                    errors.append(f"event[{index}] contract_update references unknown contract {contract_id!r}")
                    continue
                if not _nonempty_string(revision):
                    errors.append(f"event[{index}] contract_update revision for {contract_id!r} must be nonempty")
                    continue
                if current_contract_revisions.get(normalized_id) != revision:
                    changed_contracts.add(normalized_id)
                current_contract_revisions[normalized_id] = revision
            integrated_assignments.difference_update(
                assignment
                for assignment, revisions_at_dispatch in assignment_contract_revisions.items()
                if any(contract_id in revisions_at_dispatch for contract_id in changed_contracts)
            )
            for assignment, revisions_at_dispatch in assignment_contract_revisions.items():
                if assignment not in retired_assignments and any(
                    contract_id in revisions_at_dispatch for contract_id in changed_contracts
                ):
                    if compact_schema or any(
                        isinstance(item, dict) and ("supersedes" in item or "cancelled_assignment_ids" in item)
                        for item in events
                    ):
                        invalidated_obligations.add(assignment)
                    successful_assignments.discard(assignment)
                    accepted_assignments.discard(assignment)
                    rejected_assignments.discard(assignment)
            affected_active = {
                assignment_for_agent[agent]
                for agent in active
                if any(
                    active_contract_revisions.get(agent, {}).get(contract_id)
                    != current_contract_revisions.get(contract_id)
                    for contract_id in changed_contracts
                    if contract_id in active_contract_revisions.get(agent, {})
                )
            }
            stopped_assignments = _normalized_string_set(
                event.get("stopped_assignment_ids", []),
                f"event[{index}].stopped_assignment_ids",
                errors,
            )
            missing_stops = sorted(affected_active - stopped_assignments)
            if missing_stops:
                contract_gate_violations += len(missing_stops)
                errors.append(
                    f"event[{index}] contract_update did not stop affected active assignments: "
                    + ", ".join(missing_stops)
                )
            for assignment in stopped_assignments & affected_active:
                failed_assignments.add(assignment)
                successful_assignments.discard(assignment)
                accepted_assignments.discard(assignment)
                agent = next(
                    (candidate for candidate, current in assignment_for_agent.items() if current == assignment),
                    None,
                )
                if agent is not None:
                    active.pop(agent, None)
                    assignment_for_agent.pop(agent, None)
                    active_contract_revisions.pop(agent, None)

            cancelled = _normalized_string_set(
                event.get("cancelled_assignment_ids", []), f"event[{index}].cancelled_assignment_ids", errors
            )
            if cancelled - invalidated_obligations:
                errors.append(f"event[{index}] cancellation must reference outstanding invalidated assignments")
            retired_assignments.update(cancelled & invalidated_obligations)
            invalidated_obligations.difference_update(cancelled)

        elif event_type == "directive_update":
            if event.get("owner") != "primary":
                errors.append(f"event[{index}] directive_update owner must be primary")
            revision = event.get("directive_revision")
            if not _nonempty_string(revision):
                errors.append(f"event[{index}] directive_update requires directive_revision")
                continue
            current_directive_revision = revision
            affected = _normalized_string_set(
                event.get("affected_assignment_ids"), f"event[{index}].affected_assignment_ids", errors
            )
            stopped = _normalized_string_set(
                event.get("stopped_assignment_ids", []), f"event[{index}].stopped_assignment_ids", errors
            )
            if not _evidence_locators(event.get("evidence")):
                errors.append(f"event[{index}] directive_update requires evidence locators")
            for assignment in affected:
                if assignment not in seen_assignment_ids:
                    errors.append(f"event[{index}] directive_update references unknown assignment {assignment!r}")
                    continue
                if assignment in retired_assignments:
                    errors.append(f"event[{index}] directive_update cannot revive retired assignment {assignment!r}")
                    continue
                invalidated_obligations.add(assignment)
                required_directive_revision[assignment] = revision
                integrated_assignments.discard(assignment)
                successful_assignments.discard(assignment)
                accepted_assignments.discard(assignment)
                rejected_assignments.discard(assignment)
                agent = next((key for key, value in assignment_for_agent.items() if value == assignment), None)
                if agent is not None:
                    if assignment not in stopped:
                        errors.append(f"event[{index}] directive_update did not stop affected assignment {assignment!r}")
                    else:
                        active.pop(agent, None)
                        assignment_for_agent.pop(agent, None)
                        active_contract_revisions.pop(agent, None)
                        failed_assignments.add(assignment)

            cancelled = _normalized_string_set(
                event.get("cancelled_assignment_ids", []), f"event[{index}].cancelled_assignment_ids", errors
            )
            if cancelled - affected:
                errors.append(f"event[{index}] cancellation must reference affected assignments")
            retired_assignments.update(cancelled & invalidated_obligations)
            invalidated_obligations.difference_update(cancelled)

        elif event_type == "user_message":
            # Passive messages may be observed, but need no routine bookkeeping.
            # Actual changed obligations use directive_update / contract_update.
            if not _enum(event.get("message_class"), {"QUERY", "REMINDER"}):
                errors.append(f"event[{index}] changed obligations require directive_update or contract_update")
            if (
                event.get("affects_saved_next") is True
                or event.get("affected_assignment_ids")
                or event.get("directive_changed") is True
                or event.get("contract_revisions")
            ):
                errors.append(f"event[{index}] passive user_message must not change the active route or obligations")

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
            if expected == assignment and agent in active:
                collected_assignments.add(assignment)
            status = event.get("status")
            if status == "success":
                if assignment_directive_revision.get(assignment) != required_directive_revision.get(assignment):
                    errors.append(f"event[{index}] successful result uses a superseded directive")
                if "directive_revision" in event and event["directive_revision"] != assignment_directive_revision.get(assignment):
                    errors.append(f"event[{index}] result directive_revision does not match capsule")
                if assignment in compact_assignments:
                    directive_revision = event.get("directive_revision")
                    if directive_revision != assignment_directive_revision.get(assignment):
                        errors.append(
                            f"event[{index}] compact result directive_revision does not match capsule"
                        )
                    expected_contracts = assignment_contract_revisions.get(assignment, {})
                    if expected_contracts and event.get("contract_revisions") != expected_contracts:
                        errors.append(
                            f"event[{index}] compact result contract_revisions do not match capsule"
                        )
                    for field in ("changed_artifacts", "unverified_items", "scope_or_contract_conflicts"):
                        if not isinstance(event.get(field), list):
                            errors.append(
                                f"event[{index}] compact result {field} must be a list"
                            )
                    changed_artifacts = event.get("changed_artifacts")
                    if isinstance(changed_artifacts, list):
                        if assignment_write_set.get(assignment) and not changed_artifacts:
                            errors.append(
                                f"event[{index}] compact write result lacks changed_artifacts"
                            )
                        if (
                            not assignment_write_set.get(assignment)
                            and changed_artifacts
                        ):
                            errors.append(
                                f"event[{index}] compact read-only result declares changed_artifacts"
                            )
                stale_contracts = sorted(
                    contract_id
                    for contract_id, revision in assignment_contract_revisions.get(assignment, {}).items()
                    if current_contract_revisions.get(contract_id) != revision
                )
                if stale_contracts:
                    stale_contract_results += 1
                    contract_gate_violations += 1
                    errors.append(
                        f"event[{index}] successful result cites superseded contracts: "
                        + ", ".join(stale_contracts)
                    )
                successful_assignments.add(assignment)
                if not _evidence_locators(event.get("evidence")):
                    errors.append(f"event[{index}] successful result lacks evidence")
                if not _nonempty_string(event.get("source_fingerprint")):
                    errors.append(f"event[{index}] successful result lacks source_fingerprint")
                else:
                    result_fingerprint = str(event["source_fingerprint"])
                    if (
                        assignment in assignment_source_fingerprint
                        and result_fingerprint
                        != assignment_source_fingerprint.get(assignment)
                    ):
                        errors.append(
                            f"event[{index}] compact result source_fingerprint does not match capsule"
                        )
                    result_source_fingerprint[assignment] = result_fingerprint
            elif _enum(status, {"failed", "blocked", "stale"}):
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
            if assignment_directive_revision.get(assignment) != required_directive_revision.get(assignment):
                errors.append(f"event[{index}] acceptance references a superseded directive")
            if "directive_revision" in event and event["directive_revision"] != required_directive_revision.get(assignment):
                errors.append(f"event[{index}] acceptance directive_revision does not match current assignment")
            stale_contracts = sorted(
                contract_id
                for contract_id, revision in assignment_contract_revisions.get(assignment, {}).items()
                if current_contract_revisions.get(contract_id) != revision
            )
            if stale_contracts:
                contract_gate_violations += 1
                errors.append(
                    f"event[{index}] acceptance references superseded contracts: "
                    + ", ".join(stale_contracts)
                )
            expected_owner = assignment_acceptance_owner.get(assignment)
            if not expected_owner or event.get("owner") != expected_owner:
                errors.append(f"event[{index}] acceptance owner does not match capsule")
            if event.get("scope_checked") is not True:
                errors.append(f"event[{index}] acceptance must confirm scope_checked=true")
            if assignment_write_set.get(assignment) and event.get("artifacts_checked") is not True:
                errors.append(f"event[{index}] write acceptance must confirm artifacts_checked=true")
            fingerprint = str(event.get("source_fingerprint", "")).strip()
            if not _nonempty_string(event.get("source_fingerprint")):
                errors.append(f"event[{index}] acceptance lacks source_fingerprint")
            elif result_source_fingerprint.get(assignment) != fingerprint:
                errors.append(f"event[{index}] acceptance source_fingerprint does not match result")
            matrix = event.get("acceptance_matrix")
            if not isinstance(matrix, dict):
                errors.append(f"event[{index}] acceptance_matrix must be an object")
                matrix = {}
            expected_signals = assignment_acceptance.get(assignment, set())
            missing_signals = sorted(
                signal for signal in expected_signals if signal not in matrix or not _evidence_locators(matrix[signal])
            )
            if missing_signals:
                errors.append(
                    f"event[{index}] acceptance_matrix missing evidence for: {', '.join(missing_signals)}"
                )
            if status == "accepted":
                acceptance_count += 1
                accepted_assignments.add(assignment)
                replacements = assignment_supersedes.get(assignment, set())
                retired_assignments.update(replacements)
                invalidated_obligations.difference_update(replacements)
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
            if not _enum(from_tier, TIER_ORDER) or not _enum(to_tier, TIER_ORDER):
                errors.append(f"event[{index}] escalation uses an unknown capability tier")
            elif TIER_ORDER[to_tier] <= TIER_ORDER[from_tier]:
                errors.append(f"event[{index}] escalation does not increase capability")
            if not _nonempty(event.get("facts")) or not _nonempty(event.get("evidence")):
                errors.append(f"event[{index}] escalation lacks facts or evidence locators")
            if (
                assignment in failed_assignments
                and _enum(from_tier, TIER_ORDER)
                and _enum(to_tier, TIER_ORDER)
                and TIER_ORDER[to_tier] > TIER_ORDER[from_tier]
                and from_tier == expected_from_tier
            ):
                escalated_assignments[assignment] = str(to_tier)

        elif event_type == "evidence_gate":
            if not admission_schema:
                errors.append(f"event[{index}] evidence_gate requires schema_version >= 4")
                continue
            if route_mode != "PARALLEL_SCOUTS":
                errors.append(f"event[{index}] evidence_gate requires PARALLEL_SCOUTS")
            round_number = event.get("round")
            if not isinstance(round_number, int) or round_number < 1:
                errors.append(f"event[{index}] evidence_gate.round must be a positive integer")
                continue
            if round_number in evidence_gates:
                errors.append(f"event[{index}] duplicates evidence gate for round {round_number}")
            if scout_counts_by_round.get(round_number, 0) == 0:
                errors.append(f"event[{index}] evidence gate has no scouts in round {round_number}")
            round_assignments = {
                assignment
                for assignment, assigned_round in assignment_scout_round.items()
                if assigned_round == round_number
            }
            missing_acceptance = sorted(round_assignments - accepted_assignments)
            if missing_acceptance:
                errors.append(
                    f"event[{index}] evidence gate precedes scout acceptance: "
                    + ", ".join(missing_acceptance)
                )
            if any(
                assignment_work_class.get(assignment_for_agent.get(agent, "")) == "evidence_scout"
                for agent in active
            ):
                errors.append(f"event[{index}] evidence gate occurs while scouts are active")
            status = event.get("status")
            stop_reason = event.get("stop_reason")
            result = event.get("result")
            if not _enum(status, EVIDENCE_STATUSES):
                errors.append(f"event[{index}] evidence_gate.status is invalid")
            if not _enum(result, EVIDENCE_RESULTS):
                errors.append(f"event[{index}] evidence_gate.result is invalid")
            if status == "STOPPED" and not _enum(stop_reason, EVIDENCE_STOP_REASONS):
                errors.append(f"event[{index}] stopped evidence gate requires valid stop_reason")
            if status == "OPEN" and stop_reason is not None:
                errors.append(f"event[{index}] open evidence gate must not declare stop_reason")
            if status == "STOPPED" and not _nonempty(event.get("evidence")):
                errors.append(f"event[{index}] stopped evidence gate lacks evidence locators")
            expected_result = {
                "FREEZE": "DISCRIMINATING",
                "ASK_USER": "SCOPE_INVALID",
                "INVALID_OBSERVATION": "INVALID",
            }.get(stop_reason)
            if expected_result is not None and result != expected_result:
                errors.append(
                    f"event[{index}] evidence gate {stop_reason} requires result={expected_result}"
                )
            gate = {
                "round": round_number,
                "status": status,
                "stop_reason": stop_reason,
                "result": result,
            }
            evidence_gates[round_number] = gate
            if _enum(stop_reason, TERMINAL_DISCOVERY_REASONS):
                terminal_discovery_gate = gate

        elif event_type == "evidence_reopen":
            if not admission_schema:
                errors.append(f"event[{index}] evidence_reopen requires schema_version >= 4")
                continue
            round_number = event.get("round")
            reason = event.get("reason")
            if not isinstance(round_number, int) or round_number < 2:
                errors.append(f"event[{index}] evidence_reopen.round must be an integer >= 2")
                continue
            if round_number in evidence_reopens:
                errors.append(f"event[{index}] duplicates evidence_reopen for round {round_number}")
            prior_gate = evidence_gates.get(round_number - 1)
            if prior_gate is None or prior_gate.get("status") != "STOPPED":
                errors.append(
                    f"event[{index}] evidence_reopen requires a stopped gate for round {round_number - 1}"
                )
            if not _enum(reason, DISCOVERY_REOPEN_REASONS):
                errors.append(f"event[{index}] evidence_reopen.reason is invalid")
            if not _nonempty(event.get("locator")):
                errors.append(f"event[{index}] evidence_reopen requires locator")
            if (
                reason == "INVALID_OBSERVATION"
                and (prior_gate or {}).get("stop_reason") != "INVALID_OBSERVATION"
            ):
                errors.append(
                    f"event[{index}] INVALID_OBSERVATION reopen requires that prior stop reason"
                )
            if reason == "INVALID_OBSERVATION":
                invalid_observation_reopens += 1
                if invalid_observation_reopens > 1:
                    warnings.append(
                        f"event[{index}] INVALID_OBSERVATION exceeds the default one observation-apparatus reopen; inspect progress evidence"
                    )
            if _enum(reason, DISCOVERY_REOPEN_REASONS):
                evidence_reopens[round_number] = str(reason)
                terminal_discovery_gate = None

        elif event_type == "artifact_disposition":
            if not admission_schema:
                errors.append(f"event[{index}] artifact_disposition requires schema_version >= 4")
                continue
            artifact_id = str(event.get("artifact_id", "")).strip()
            status = event.get("status")
            if not artifact_id:
                errors.append(f"event[{index}] artifact_disposition requires artifact_id")
                continue
            if artifact_id not in artifact_state:
                errors.append(f"event[{index}] artifact_disposition references unknown artifact")
            if not _enum(status, {"candidate", "retained", "discarded"}):
                errors.append(f"event[{index}] artifact_disposition.status is invalid")
                continue
            if not _nonempty(event.get("evidence")):
                errors.append(f"event[{index}] artifact_disposition lacks evidence")
            disposition_reason = event.get("reason")
            if not _enum(disposition_reason, ARTIFACT_DISPOSITION_REASONS):
                errors.append(f"event[{index}] artifact_disposition.reason is invalid")
            artifact_state[artifact_id] = str(status)
            if status == "discarded" and artifact_id in reviewed_targets:
                review_of_later_discarded_artifact += 1
                if disposition_reason == "ADMISSION_PRECONDITION_INVALIDATED":
                    premature_review_admission_violations += 1
                    review_admission_violations += 1
                    errors.append(
                        f"event[{index}] reviewed artifact {artifact_id!r} was discarded because "
                        "its review admission precondition was invalid"
                    )

        elif event_type == "integrate":
            if has_program and event.get("stage_id") != (program_state or {}).get("current_stage"):
                errors.append(f"event[{index}] integrate.stage_id must match program.current_stage")
            integration_count += 1
            if active:
                errors.append(f"event[{index}] integration precedes terminal results for active assignments")
            if (any(isinstance(item, dict) and item.get("type") == "delegate" for item in events)
                    and not collected_assignments and not retired_assignments):
                errors.append(f"event[{index}] integration occurs before any delegated result was collected")
            stale_directives = sorted(
                assignment for assignment in accepted_assignments
                if assignment_directive_revision.get(assignment) != required_directive_revision.get(assignment)
            )
            if stale_directives:
                errors.append(f"event[{index}] integrates assignments against superseded directives: {', '.join(stale_directives)}")
            stale_accepted = sorted(
                assignment
                for assignment in accepted_assignments
                if any(
                    current_contract_revisions.get(contract_id) != revision
                    for contract_id, revision in assignment_contract_revisions.get(assignment, {}).items()
                )
            )
            if stale_accepted:
                contract_gate_violations += 1
                errors.append(
                    f"event[{index}] integrates assignments against superseded contracts: "
                    + ", ".join(stale_accepted)
                )
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
            if strict_schema and successful_assignments and not _evidence_locators(event.get("evidence")):
                errors.append(f"event[{index}] integration lacks evidence")
            eligible = accepted_assignments if strict_schema else successful_assignments
            if strict_schema and result_source_fingerprint and not eligible and not retired_assignments:
                errors.append(f"event[{index}] integration has no current accepted result")
            integrating = eligible
            if "assignment_ids" in event:
                integrating = _normalized_string_set(
                    event["assignment_ids"], f"event[{index}].assignment_ids", errors
                )
                if integrating - eligible:
                    errors.append(f"event[{index}] integration references assignments without current acceptance")
            integrated_assignments.update(integrating & eligible)

        elif event_type == "primary_action":
            primary_action_count += 1
            if has_program and event.get("stage_id") != (program_state or {}).get("current_stage"):
                errors.append(f"event[{index}] primary_action.stage_id must match program.current_stage")
            action_class = event.get("action_class")
            allowed_actions = {
                "design", "shared_contract", "coordination", "acceptance", "integration",
                "validation", "delivery", "leaf_implementation", "documentation", "review",
            }
            if not _enum(action_class, allowed_actions):
                errors.append(f"event[{index}] primary_action has invalid action_class")
            delegated_program = has_program and route_mode != "SINGLE_OWNER"
            if delegated_program and _enum(action_class, PRIMARY_DELEGATED_WORK_ACTIONS):
                primary_work_violations += 1
                errors.append(
                    f"event[{index}] primary_action {action_class!r} is forbidden in a delegated program; "
                    "primary is control-plane-only"
                )
            if (
                admission_schema
                and semantic_fork_status == "OPEN"
                and _enum(
                    action_class,
                    {"design", "shared_contract", "leaf_implementation", "documentation", "review"},
                )
            ):
                semantic_fork_admission_violations += 1
                stage_admission_violations += 1
                errors.append(
                    f"event[{index}] primary_action {action_class!r} is forbidden while "
                    "semantic_fork.status=OPEN"
                )
            raw_write_set = event.get("write_set", [])
            write_set = _normalized_string_set(
                [] if raw_write_set is None else raw_write_set,
                f"event[{index}].write_set",
                errors,
            )
            if delegated_program and write_set:
                primary_work_violations += 1
                errors.append(
                    f"event[{index}] delegated-program primary_action must have an empty write_set"
                )
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
    if invalidated_obligations:
        errors.append(
            "trace ends with uncovered invalidated assignments: "
            + ", ".join(sorted(invalidated_obligations))
        )
    if strict_schema and accepted_assignments - integrated_assignments:
        errors.append(
            "trace ends with accepted results lacking subsequent integration: "
            + ", ".join(sorted(accepted_assignments - integrated_assignments))
        )
    if admission_schema and route_mode == "PARALLEL_SCOUTS":
        rounds = sorted(scout_counts_by_round)
        if not rounds or rounds[0] != 1 or rounds != list(range(1, rounds[-1] + 1)):
            scout_budget_violations += 1
            errors.append("scout rounds must start at 1 and advance without gaps")
        if not evidence_gates:
            scout_budget_violations += 1
            errors.append("schema-version-4 scout trace requires an evidence_gate")
        elif rounds:
            last_round = rounds[-1]
            last_gate = evidence_gates.get(last_round)
            if last_gate is None:
                scout_budget_violations += 1
                errors.append("final scout round lacks an evidence_gate")
            else:
                if last_gate.get("status") != "STOPPED":
                    scout_budget_violations += 1
                    errors.append("completed scout trace requires a stopped final evidence gate")
                if evidence_budget is not None:
                    if evidence_budget.get("round") != last_round:
                        errors.append("evidence_budget.round does not match final scout round")
                    if evidence_budget.get("scout_count") != scout_counts_by_round.get(last_round):
                        errors.append("evidence_budget.scout_count does not match final scout round")
                    if evidence_budget.get("status") != last_gate.get("status"):
                        errors.append("evidence_budget.status does not match final evidence gate")
                    if evidence_budget.get("stop_reason") != last_gate.get("stop_reason"):
                        errors.append("evidence_budget.stop_reason does not match final evidence gate")
                stop_reason = last_gate.get("stop_reason")
                if stop_reason == "FREEZE" and semantic_fork_status == "OPEN":
                    semantic_fork_admission_violations += 1
                    errors.append("FREEZE evidence gate cannot leave semantic_fork.status=OPEN")
                if stop_reason == "ASK_USER" and semantic_fork_status != "OPEN":
                    errors.append("ASK_USER evidence gate requires semantic_fork.status=OPEN")

    return {
        "passed": not errors,
        "errors": errors,
        "warnings": warnings,
        "metrics": {
            "delegations": delegate_count,
            "dispatch_receipts": len(dispatch_receipts),
            "compact_assignments": len(compact_assignments),
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
            "primary_work_violations": primary_work_violations,
            "contract_gate_violations": contract_gate_violations,
            "stale_contract_results": stale_contract_results,
            "scout_budget_violations": scout_budget_violations,
            "scout_rounds_after_discriminating_evidence": len(
                scout_rounds_after_discriminating_evidence
            ),
            "invalid_observation_reopens": invalid_observation_reopens,
            "semantic_fork_admission_violations": semantic_fork_admission_violations,
            "stage_admission_violations": stage_admission_violations,
            "review_admission_violations": review_admission_violations,
            "review_of_later_discarded_artifact": review_of_later_discarded_artifact,
            "premature_review_admission_violations": premature_review_admission_violations,
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
