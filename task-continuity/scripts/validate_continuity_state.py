#!/usr/bin/env python3
"""Validate a host-neutral task-continuity state and recommend its next gate.

The program is deliberately read-only. Hosts are responsible for collecting the
state and lightweight observations, and for applying any recommended update.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


GATES = {"READY", "SNAPSHOT_REQUIRED", "RESUME_AUDIT"}
RECOVERY_TYPES = {"COMPACT_CONTINUATION", "COLD_HANDOFF", "EXTERNAL_RETRY"}
ACTION_TYPES = {"mutation", "check", "blocker"}
ACTION_PURPOSES = {"solution", "observation_setup", "observation_repair"}
IN_FLIGHT_STATUSES = {"planned", "active", "validation_pending", "validation_passed"}
MATCH_VALUES = {"match", "mismatch", "unknown"}
MESSAGE_CLASSES = {
    "QUERY",
    "REMINDER",
    "NEW_CONSTRAINT",
    "CONTRACT_CHANGE",
    "TEMPORARY_INTERRUPT",
    "OVERRIDE",
    "OBSERVATION",
    "DECISION",
}
PASSIVE_MESSAGE_CLASSES = {"QUERY", "REMINDER"}
INTERRUPTION_STATES = {"ACTIVE", "RESUME_READY"}
OBSERVATION_RESULTS = {"PLANNED", "DISCRIMINATING", "INVALID", "INCONCLUSIVE", "SCOPE_INVALID"}
SEMANTIC_FORK_STATUSES = {"NOT_APPLICABLE", "OPEN", "RESOLVED"}
SEMANTIC_RESOLUTION_SOURCES = {"EVIDENCE", "USER"}
EVIDENCE_BUDGET_STATUSES = {"OPEN", "STOPPED"}
EVIDENCE_STOP_REASONS = {
    "FREEZE",
    "ASK_USER",
    "BLOCKER",
    "INVALID_OBSERVATION",
    "SOURCE_DRIFT",
    "HIGH_RISK_GAP",
}
EVIDENCE_REOPEN_REASONS = {
    "NEW_CANDIDATE",
    "INVALID_OBSERVATION",
    "SOURCE_DRIFT",
    "HIGH_RISK_GAP",
}
MAX_BOUNDED_ITEMS = 7
VAGUE_ACTION = re.compile(
    r"^(?:continue|resume|proceed|start|do)\s+(?:the\s+)?(?:work|implementation|analysis|task|investigation)$"
    r"|^(?:继续|开始|恢复|推进)(?:实现|开发|分析|调查|任务|工作|处理)(?:阶段|任务|工作)?$",
    re.IGNORECASE,
)


def _diagnostic(code: str, path: str, message: str) -> dict[str, str]:
    return {"code": code, "path": path, "message": message}


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _enum(value: Any, allowed: set[str]) -> bool:
    return isinstance(value, str) and value in allowed


def _validate_string_list(
    value: Any,
    path: str,
    errors: list[dict[str, str]],
    *,
    allow_empty: bool = False,
    max_items: int = MAX_BOUNDED_ITEMS,
) -> bool:
    if not isinstance(value, list) or (not allow_empty and not value):
        errors.append(
            _diagnostic(
                "list.invalid",
                path,
                "field must be a bounded list of non-empty strings",
            )
        )
        return False
    valid = True
    if len(value) > max_items:
        errors.append(
            _diagnostic(
                "list.too_large",
                path,
                f"recommended target is {max_items} items; retain necessary semantics when exceeding it",
            )
        )
        valid = False
    if not all(_nonempty_string(item) for item in value):
        errors.append(
            _diagnostic(
                "list.invalid_item",
                path,
                "field must contain only non-empty strings",
            )
        )
        valid = False
    return valid


def _nonempty_scope(value: Any) -> bool:
    if _nonempty_string(value):
        return True
    return isinstance(value, list) and bool(value) and all(_nonempty_string(item) for item in value)


def _identity_path(value: Any, locator: Any) -> Path | None:
    """Resolve only the declared boundary against a verifiable local source root."""
    if not _nonempty_string(value) or any(char in value for char in "*?[]\\") or ":" in value:
        return None
    if not _nonempty_string(locator) or not Path(locator).is_absolute():
        return None
    path = Path(value.strip())
    if ".." in path.parts:
        return None
    try:
        root = Path(locator).resolve(strict=True)
        if not root.is_dir():
            return None
        resolved = (path if path.is_absolute() else root / path).resolve(strict=True)
        resolved.relative_to(root)
        return resolved
    except (OSError, ValueError, RuntimeError):
        return None


def _identity_paths_disjoint(action_paths: list[Path | None], missing_paths: list[Path]) -> bool:
    """Only distinct observed file objects prove disjointness without tree expansion."""
    if not action_paths or not missing_paths or any(path is None for path in action_paths):
        return False
    try:
        for first in action_paths:
            if first is None:
                return False
            for second in missing_paths:
                if first.samefile(second) or first in second.parents or second in first.parents:
                    return False
                # A directory boundary does not disclose identities of its children.
                # Do not claim its unknown descendants have no aliases elsewhere.
                if not first.is_file() or not second.is_file():
                    return False
        return True
    except (OSError, ValueError):
        return False


def _partial_source_coverage(snapshot: dict[str, Any], action: Any, warnings: list[dict[str, str]]) -> str:
    """Partial identity is sufficient only for diagnostics or proven-disjoint work."""
    if not isinstance(action, dict):
        return "unknown"
    layers = snapshot.get("missing_layers")
    scopes = snapshot.get("missing_layer_scopes")
    complete_scopes = (
        isinstance(layers, list) and bool(layers) and all(_nonempty_string(item) for item in layers)
        and isinstance(scopes, dict) and set(scopes) == set(layers)
    )
    missing_paths: list[Path] = []
    if complete_scopes:
        for layer in layers:
            items = scopes[layer]
            if not isinstance(items, list) or not items:
                complete_scopes = False
                break
            paths = [_identity_path(item, snapshot.get("locator")) for item in items]
            if any(path is None for path in paths):
                complete_scopes = False
                break
            missing_paths.extend(path for path in paths if path is not None)
    action_scope = action.get("scope")
    scope_items = [action_scope] if isinstance(action_scope, str) else action_scope
    action_paths = (
        [_identity_path(item, snapshot.get("locator")) for item in scope_items]
        if isinstance(scope_items, list) and scope_items else [None]
    )
    disjoint = complete_scopes and _identity_paths_disjoint(action_paths, missing_paths)
    diagnostic = action.get("type") == "blocker" or (
        action.get("type") == "check"
        and _enum(action.get("purpose"), {"observation_setup", "observation_repair"})
    )
    if diagnostic:
        message = "identity remains partial; allow only the bounded recovery observation or blocker, not acceptance based on missing layers"
    elif disjoint:
        message = "identity remains partial; observed file-object identities prove disjointness for the current explicit scope only"
    else:
        message = "missing identity layers may affect the current action, or their physical boundaries are unverified; observe only those boundaries before mutation or acceptance"
    warnings.append(_diagnostic(
        "source.partial_identity" if diagnostic or disjoint else "source.partial_coverage_required",
        "source_snapshot.missing_layers", message,
    ))
    return "match" if diagnostic or disjoint else "unknown"


def _stable_action_identity(action: dict[str, Any]) -> str:
    explicit = action.get("action_id")
    if _nonempty_string(explicit):
        return f"id:{explicit.strip()}"
    normalized = {
        "type": action.get("type"),
        "purpose": action.get("purpose"),
        "owner": action.get("owner"),
        "scope": action.get("scope"),
        "observable_signal": action.get("observable_signal"),
    }
    payload = json.dumps(normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _explicit_action_id(action: Any) -> str | None:
    if not isinstance(action, dict):
        return None
    value = action.get("action_id")
    return value.strip() if _nonempty_string(value) else None


def _validate_action(action: Any, path: str, errors: list[dict[str, str]]) -> None:
    if not isinstance(action, dict):
        errors.append(_diagnostic("action.not_object", path, "action must be an object"))
        return
    action_type = action.get("type")
    if not _enum(action_type, ACTION_TYPES):
        errors.append(
            _diagnostic("action.invalid_type", f"{path}.type", "type must be mutation, check, or blocker")
        )
    purpose = action.get("purpose")
    if purpose is not None and not _enum(purpose, ACTION_PURPOSES):
        errors.append(
            _diagnostic(
                "action.invalid_purpose",
                f"{path}.purpose",
                "purpose must be solution, observation_setup, or observation_repair when present",
            )
        )
    for field in ("owner", "observable_signal"):
        if not _nonempty_string(action.get(field)):
            errors.append(_diagnostic("action.missing_field", f"{path}.{field}", "field must be non-empty"))
    if not _nonempty_scope(action.get("scope")):
        errors.append(
            _diagnostic("action.missing_scope", f"{path}.scope", "scope must name bounded changed or read items")
        )
    elif isinstance(action.get("scope"), list):
        _validate_string_list(action.get("scope"), f"{path}.scope", errors)
    action_text = " ".join(
        str(action.get(field, "")).strip() for field in ("description", "owner", "observable_signal")
    ).strip()
    if VAGUE_ACTION.fullmatch(action_text) or any(
        VAGUE_ACTION.fullmatch(str(action.get(field, "")).strip())
        for field in ("description", "owner", "observable_signal")
    ):
        errors.append(
            _diagnostic(
                "action.vague",
                path,
                "Next must be an executable mutation, discriminating check, or concrete blocker report",
            )
        )


def _validate_in_flight_slice(value: Any, path: str, errors: list[dict[str, str]]) -> bool:
    if value is None or value == {}:
        return False
    if not isinstance(value, dict):
        errors.append(_diagnostic("checkpoint.invalid_in_flight", path, "in_flight must be null or an object"))
        return False
    for field in ("slice_id", "owner"):
        if not _nonempty_string(value.get(field)):
            errors.append(
                _diagnostic("checkpoint.in_flight_missing_field", f"{path}.{field}", "field must be non-empty")
            )
    status = value.get("status")
    if not _enum(status, IN_FLIGHT_STATUSES):
        errors.append(
            _diagnostic(
                "checkpoint.in_flight_invalid_status",
                f"{path}.status",
                "status must be planned, active, validation_pending, or validation_passed",
            )
        )
    if not _nonempty_scope(value.get("expected_changed_items")):
        errors.append(
            _diagnostic(
                "checkpoint.in_flight_missing_scope",
                f"{path}.expected_changed_items",
                "in-flight slice must name its bounded expected changed items",
            )
        )
    elif isinstance(value.get("expected_changed_items"), list):
        _validate_string_list(
            value.get("expected_changed_items"),
            f"{path}.expected_changed_items",
            errors,
        )
    return True


def _validate_do_not_reopen(value: Any, path: str, errors: list[dict[str, str]]) -> set[str]:
    if value is None:
        return set()
    if not isinstance(value, list):
        errors.append(_diagnostic("decision.do_not_reopen_not_list", path, "do_not_reopen must be a list"))
        return set()
    if len(value) > MAX_BOUNDED_ITEMS:
        errors.append(
            _diagnostic(
                "decision.do_not_reopen_too_large",
                path,
                f"recommended target is {MAX_BOUNDED_ITEMS} replay-prone actions",
            )
        )
    action_ids: set[str] = set()
    for index, item in enumerate(value):
        item_path = f"{path}[{index}]"
        if not isinstance(item, dict):
            errors.append(_diagnostic("decision.do_not_reopen_invalid", item_path, "entry must be an object"))
            continue
        for field in ("action_id", "reason", "reopen_when"):
            if not _nonempty_string(item.get(field)):
                errors.append(
                    _diagnostic("decision.do_not_reopen_missing_field", f"{item_path}.{field}", "field must be non-empty")
                )
        action_id = item.get("action_id")
        if _nonempty_string(action_id):
            action_ids.add(action_id.strip())
    return action_ids


def _validate_active_observation(value: Any, path: str, errors: list[dict[str, str]]) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        errors.append(_diagnostic("observation.not_object", path, "active_observation must be an object"))
        return None
    for field in ("id", "revision", "decision", "boundary", "prediction", "discriminator"):
        if not _nonempty_string(value.get(field)):
            errors.append(
                _diagnostic("observation.missing_field", f"{path}.{field}", "field must be non-empty")
            )
    for field in ("preconditions", "invalidators"):
        items = value.get(field)
        _validate_string_list(items, f"{path}.{field}", errors)
    result = value.get("result")
    if not _enum(result, OBSERVATION_RESULTS):
        errors.append(
            _diagnostic(
                "observation.invalid_result",
                f"{path}.result",
                "result must be PLANNED, DISCRIMINATING, INVALID, INCONCLUSIVE, or SCOPE_INVALID",
            )
        )
    repair_cycles = value.get("repair_cycles")
    if not isinstance(repair_cycles, int) or isinstance(repair_cycles, bool) or repair_cycles < 0:
        errors.append(
            _diagnostic(
                "observation.invalid_repair_cycles",
                f"{path}.repair_cycles",
                "repair_cycles must be a non-negative integer",
            )
        )
    if _enum(result, OBSERVATION_RESULTS - {"PLANNED"}):
        for field in ("actual_signal", "evidence_locator"):
            if not _nonempty_string(value.get(field)):
                errors.append(
                    _diagnostic(
                        "observation.missing_result_evidence",
                        f"{path}.{field}",
                        "a completed observation must record its actual signal and evidence locator",
                    )
                )
    return value


def _validate_semantic_fork(value: Any, path: str, errors: list[dict[str, str]]) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        errors.append(_diagnostic("semantic_fork.not_object", path, "semantic_fork must be an object"))
        return None
    status = value.get("status")
    if not _enum(status, SEMANTIC_FORK_STATUSES):
        errors.append(
            _diagnostic(
                "semantic_fork.invalid_status",
                f"{path}.status",
                "status must be NOT_APPLICABLE, OPEN, or RESOLVED",
            )
        )
    evidence_can_decide = value.get("evidence_can_decide")
    if not (
        evidence_can_decide is True
        or evidence_can_decide is False
        or evidence_can_decide == "unknown"
    ):
        errors.append(
            _diagnostic(
                "semantic_fork.invalid_evidence_decision",
                f"{path}.evidence_can_decide",
                "evidence_can_decide must be true, false, or 'unknown'",
            )
        )
    if not _nonempty_string(value.get("decision_question")):
        errors.append(
            _diagnostic(
                "semantic_fork.missing_question",
                f"{path}.decision_question",
                "semantic fork state must retain one focused decision question",
            )
        )
    options = value.get("options")
    valid_options = isinstance(options, list)
    if valid_options and len(options) > MAX_BOUNDED_ITEMS:
        errors.append(
            _diagnostic(
                "semantic_fork.options_too_large",
                f"{path}.options",
                f"recommended target is {MAX_BOUNDED_ITEMS} options; never truncate unresolved contracts",
            )
        )
        valid_options = False
    option_ids: set[str] = set()
    if valid_options:
        for option in options:
            if not isinstance(option, dict) or not _nonempty_string(option.get("id")) or not _nonempty_string(
                option.get("contract")
            ):
                valid_options = False
                break
            option_id = option["id"].strip()
            if option_id in option_ids:
                valid_options = False
                break
            option_ids.add(option_id)
    consequences = value.get("architectural_consequences")
    material_consequences = (
        {
            key: item
            for key, item in consequences.items()
            if _nonempty_string(key) and _nonempty_string(item)
        }
        if isinstance(consequences, dict)
        else {}
    )
    if isinstance(consequences, dict) and len(consequences) > MAX_BOUNDED_ITEMS:
        errors.append(
            _diagnostic(
                "semantic_fork.consequences_too_large",
                f"{path}.architectural_consequences",
                f"recommended target is {MAX_BOUNDED_ITEMS} consequence boundaries",
            )
        )
    if _enum(status, {"OPEN", "RESOLVED"}):
        if not valid_options or len(options) < 2:
            errors.append(
                _diagnostic(
                    "semantic_fork.invalid_options",
                    f"{path}.options",
                    "OPEN or RESOLVED semantic forks need at least two unique {id, contract} options",
                )
            )
        if not material_consequences:
            errors.append(
                _diagnostic(
                    "semantic_fork.invalid_consequences",
                    f"{path}.architectural_consequences",
                    "material consequences must map at least one affected boundary to a non-empty consequence",
                )
            )
    elif status == "NOT_APPLICABLE" and isinstance(options, list) and len(options) >= 2 and material_consequences:
        errors.append(
            _diagnostic(
                "semantic_fork.false_not_applicable",
                path,
                "multiple material contract options cannot be labelled NOT_APPLICABLE",
            )
        )
    resolution = value.get("resolution")
    if status == "RESOLVED":
        if not isinstance(resolution, dict):
            errors.append(
                _diagnostic(
                    "semantic_fork.missing_resolution",
                    f"{path}.resolution",
                    "a resolved semantic fork must record its decision source and locator",
                )
            )
        else:
            if not _enum(resolution.get("source"), SEMANTIC_RESOLUTION_SOURCES):
                errors.append(
                    _diagnostic(
                        "semantic_fork.invalid_resolution_source",
                        f"{path}.resolution.source",
                        "resolution source must be EVIDENCE or USER",
                    )
                )
            if (
                resolution.get("source") == "EVIDENCE"
                and value.get("evidence_can_decide") is not True
            ):
                errors.append(
                    _diagnostic(
                        "semantic_fork.invalid_evidence_resolution",
                        f"{path}.resolution.source",
                        "an EVIDENCE resolution requires evidence_can_decide=true",
                    )
                )
            for field in ("decision", "locator"):
                if not _nonempty_string(resolution.get(field)):
                    errors.append(
                        _diagnostic(
                            "semantic_fork.missing_resolution_field",
                            f"{path}.resolution.{field}",
                            "resolved semantic forks must preserve the selected decision and evidence locator",
                        )
                    )
    elif resolution is not None:
        errors.append(
            _diagnostic(
                "semantic_fork.premature_resolution",
                f"{path}.resolution",
                "a semantic fork can carry a selected resolution only when status=RESOLVED",
            )
        )
    return value


def _validate_evidence_budget(value: Any, path: str, errors: list[dict[str, str]]) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        errors.append(_diagnostic("evidence_budget.not_object", path, "evidence_budget must be an object"))
        return None
    for field in ("round", "scout_count"):
        field_value = value.get(field)
        minimum = 1 if field == "round" else 0
        if not isinstance(field_value, int) or isinstance(field_value, bool) or field_value < minimum:
            errors.append(
                _diagnostic(
                    "evidence_budget.invalid_count",
                    f"{path}.{field}",
                    "round must be positive and scout_count must be non-negative",
                )
            )
    status = value.get("status")
    if not _enum(status, EVIDENCE_BUDGET_STATUSES):
        errors.append(
            _diagnostic(
                "evidence_budget.invalid_status",
                f"{path}.status",
                "status must be OPEN or STOPPED",
            )
        )
    if status == "STOPPED" and not _enum(value.get("stop_reason"), EVIDENCE_STOP_REASONS):
        errors.append(
            _diagnostic(
                "evidence_budget.invalid_stop_reason",
                f"{path}.stop_reason",
                "a stopped evidence budget must record its bounded stop reason",
            )
        )
    if status == "OPEN" and value.get("stop_reason") is not None:
        errors.append(
            _diagnostic(
                "evidence_budget.open_has_stop_reason",
                f"{path}.stop_reason",
                "an open evidence budget must not carry a stop reason",
            )
        )
    return value


def _validate_evidence_reopen(
    value: Any,
    path: str,
    evidence_budget: dict[str, Any] | None,
    errors: list[dict[str, str]],
) -> dict[str, Any] | None:
    round_number = evidence_budget.get("round") if isinstance(evidence_budget, dict) else None
    if round_number == 1:
        if value is not None:
            errors.append(
                _diagnostic(
                    "evidence_reopen.unexpected",
                    path,
                    "round one must not declare evidence_reopen",
                )
            )
        return None
    if not isinstance(round_number, int) or isinstance(round_number, bool) or round_number < 2:
        return None
    if not isinstance(value, dict):
        errors.append(
            _diagnostic(
                "evidence_reopen.missing",
                path,
                "evidence budget rounds after the first must preserve their reopen reason and locator",
            )
        )
        return None
    if not _enum(value.get("reason"), EVIDENCE_REOPEN_REASONS):
        errors.append(
            _diagnostic("evidence_reopen.invalid_reason", f"{path}.reason", "reopen reason is invalid")
        )
    if not _nonempty_string(value.get("locator")):
        errors.append(
            _diagnostic("evidence_reopen.missing_locator", f"{path}.locator", "locator must be non-empty")
        )
    from_round = value.get("from_round")
    if not isinstance(from_round, int) or isinstance(from_round, bool) or from_round != round_number - 1:
        errors.append(
            _diagnostic(
                "evidence_reopen.invalid_from_round",
                f"{path}.from_round",
                "from_round must identify the immediately preceding bounded evidence round",
            )
        )
    return value


def _validate_semantic_fork_action(
    action: Any,
    path: str,
    semantic_fork: dict[str, Any] | None,
    evidence_budget: dict[str, Any] | None,
    errors: list[dict[str, str]],
) -> None:
    if semantic_fork is None or semantic_fork.get("status") != "OPEN" or not isinstance(action, dict):
        return
    if isinstance(evidence_budget, dict) and evidence_budget.get("status") == "STOPPED":
        stop_reason = evidence_budget.get("stop_reason")
        if stop_reason == "FREEZE":
            errors.append(
                _diagnostic(
                    "semantic_fork.freeze_requires_resolution",
                    path,
                    "STOPPED/FREEZE must record the semantic resolution before continuation",
                )
            )
        elif action.get("type") != "blocker":
            errors.append(
                _diagnostic(
                    "evidence_budget.stopped_blocks_evidence",
                    path,
                    "a stopped evidence budget permits only its focused user decision or real blocker; further evidence requires a new OPEN round with evidence_reopen",
                )
            )
    if action.get("type") == "mutation" and not _enum(
        action.get("purpose"), {"observation_setup", "observation_repair"}
    ):
        errors.append(
            _diagnostic(
                "semantic_fork.open_blocks_solution",
                path,
                "an OPEN semantic fork permits only bounded evidence work or a focused blocker, not a solution mutation",
            )
        )


def _validate_observation_action(
    action: Any,
    path: str,
    observation: dict[str, Any] | None,
    errors: list[dict[str, str]],
) -> None:
    if observation is None or not isinstance(action, dict) or action.get("type") != "mutation":
        return
    result = observation.get("result")
    purpose = action.get("purpose")
    repair_cycles = observation.get("repair_cycles")
    if result == "DISCRIMINATING":
        if purpose != "solution":
            errors.append(
                _diagnostic(
                    "observation.discriminating_requires_solution_purpose",
                    f"{path}.purpose",
                    "a mutation selected by a discriminating observation must declare purpose=solution",
                )
            )
    elif result == "PLANNED":
        if purpose != "observation_setup":
            errors.append(
                _diagnostic(
                    "observation.planned_blocks_solution",
                    path,
                    "a planned observation permits only purpose=observation_setup mutations or a bounded check",
                )
            )
    elif result == "INVALID":
        if repair_cycles == 0 and purpose == "observation_repair":
            return
        errors.append(
            _diagnostic(
                "observation.invalid_blocks_mutation",
                path,
                "an invalid observation permits at most one declared observation_repair cycle",
            )
        )
    elif _enum(result, {"INCONCLUSIVE", "SCOPE_INVALID"}):
        errors.append(
            _diagnostic(
                (
                    "observation.scope_invalid_blocks_mutation"
                    if result == "SCOPE_INVALID"
                    else "observation.inconclusive_blocks_mutation"
                ),
                path,
                (
                    "scope-invalid evidence may justify a focused user question but cannot authorize a solution mutation"
                    if result == "SCOPE_INVALID"
                    else "an inconclusive observation requires a check, reframe, or blocker before mutation"
                ),
            )
        )
def _revision_map(items: Any, path: str, errors: list[dict[str, str]]) -> dict[str, str]:
    if not isinstance(items, list):
        errors.append(_diagnostic("ledger.not_list", path, "revision ledger must be a list"))
        return {}
    result: dict[str, str] = {}
    for index, item in enumerate(items):
        item_path = f"{path}[{index}]"
        if not isinstance(item, dict) or not _nonempty_string(item.get("id")):
            errors.append(_diagnostic("ledger.invalid_entry", item_path, "entry must contain a non-empty id"))
            continue
        if not _nonempty_string(item.get("revision")):
            errors.append(
                _diagnostic("ledger.missing_revision", f"{item_path}.revision", "revision must be non-empty")
            )
            continue
        result[item["id"]] = item["revision"]
    return result


def _compare_ledger(
    recorded: dict[str, str], observed: Any, label: str, mismatches: list[dict[str, str]]
) -> str:
    if not isinstance(observed, dict):
        return "unknown"
    if recorded == observed:
        return "match"
    missing = sorted(set(recorded) - set(observed))
    added = sorted(set(observed) - set(recorded))
    changed = sorted(key for key in set(recorded) & set(observed) if recorded[key] != observed[key])
    mismatches.append(
        _diagnostic(
            f"revision.{label}_mismatch",
            f"observed.{label}",
            f"revision ledger differs; missing={missing}, added={added}, changed={changed}",
        )
    )
    return "mismatch"


def _validate_accepted_constraints(value: Any, path: str, errors: list[dict[str, str]], *, required: bool = False) -> None:
    if value is None and not required:
        return
    if not isinstance(value, list) or (required and not value):
        errors.append(_diagnostic("constraints.missing_delta", path, "accepted constraints require a list of stable id/text records"))
        return
    seen: set[str] = set()
    for index, item in enumerate(value):
        if not isinstance(item, dict) or not _nonempty_string(item.get("id")):
            errors.append(_diagnostic("constraints.invalid_entry", f"{path}[{index}]", "each accepted constraint requires a stable id"))
            continue
        if not _enum(item.get("status", "active"), {"active", "revoked"}) or (item.get("status") != "revoked" and not _nonempty_string(item.get("text"))):
            errors.append(_diagnostic("constraints.invalid_entry", f"{path}[{index}]", "active constraints require text; status must be active or revoked"))
        if item["id"] in seen:
            errors.append(_diagnostic("constraints.duplicate_id", f"{path}[{index}].id", "constraint ids must be unique within one accepted revision"))
        seen.add(item["id"])
        if "scope" in item:
            _validate_string_list(item["scope"], f"{path}[{index}].scope", errors)


def _validate_message_effect(
    value: Any,
    message_class: Any,
    path: str,
    errors: list[dict[str, str]],
) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        errors.append(
            _diagnostic(
                "message_effect.not_object",
                path,
                "an advanced conversation cursor requires a classified message_effect object",
            )
        )
        return None
    _validate_accepted_constraints(value.get("accepted_constraints"), f"{path}.accepted_constraints", errors, required=message_class == "NEW_CONSTRAINT")
    affects_saved_next = value.get("affects_saved_next")
    if not isinstance(affects_saved_next, bool):
        errors.append(
            _diagnostic(
                "message_effect.invalid_next_impact",
                f"{path}.affects_saved_next",
                "affects_saved_next must be true or false",
            )
        )
    assignment_ids = value.get("affected_assignment_ids", [])
    _validate_string_list(
        assignment_ids,
        f"{path}.affected_assignment_ids",
        errors,
        allow_empty=True,
    )
    interruption_state = value.get("interruption_state")
    if interruption_state is not None and not _enum(interruption_state, INTERRUPTION_STATES):
        errors.append(
            _diagnostic(
                "message_effect.invalid_interruption_state",
                f"{path}.interruption_state",
                "interruption_state must be ACTIVE or RESUME_READY",
            )
        )
    if message_class in PASSIVE_MESSAGE_CLASSES and (
        affects_saved_next is not False or bool(assignment_ids)
    ):
        errors.append(
            _diagnostic(
                "message_effect.passive_message_has_impact",
                path,
                "QUERY and REMINDER must not invalidate Next or reassign workers",
            )
        )
    if message_class == "TEMPORARY_INTERRUPT" and not _enum(interruption_state, INTERRUPTION_STATES):
        errors.append(
            _diagnostic(
                "message_effect.interruption_state_required",
                f"{path}.interruption_state",
                "TEMPORARY_INTERRUPT requires ACTIVE or RESUME_READY state",
            )
        )
    return value


def _validate_return_anchor(
    value: Any,
    path: str,
    errors: list[dict[str, str]],
) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        errors.append(_diagnostic("return_anchor.not_object", path, "return anchor must be an object"))
        return None
    for field in (
        "interruption_id",
        "original_task_id",
        "saved_stage",
        "saved_next_action_id",
        "frozen_contract_revision",
        "source_fingerprint",
        "interrupt_objective",
        "resume_condition",
    ):
        if not _nonempty_string(value.get(field)):
            errors.append(
                _diagnostic(
                    "return_anchor.missing_field",
                    f"{path}.{field}",
                    "field must be non-empty",
                )
            )
    _validate_string_list(
        value.get("active_assignment_ids", []),
        f"{path}.active_assignment_ids",
        errors,
        allow_empty=True,
    )
    return value


def validate_state(document: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    mismatches: list[dict[str, str]] = []
    comparisons = {
        "source": "unknown",
        "source_coverage": "match",
        "contract": "unknown",
        "directive": "unknown",
        "instruction": "unknown",
        "conversation": "unknown",
        "message_effect": "match",
        "return_anchor": "match",
        "references": "unknown",
        "rules": "unknown",
    }

    if not isinstance(document, dict):
        return {
            "valid": False,
            "ready": False,
            "suggested_gate": "SNAPSHOT_REQUIRED",
            "comparisons": comparisons,
            "errors": [_diagnostic("document.not_object", "$", "document must be a JSON object")],
            "warnings": [],
            "mismatches": [],
        }

    capsule = document.get("recovery_capsule")
    metadata = document.get("continuity_metadata")
    snapshot = document.get("source_snapshot")
    observed = document.get("observed")
    if not isinstance(capsule, dict):
        errors.append(_diagnostic("capsule.missing", "recovery_capsule", "Recovery Capsule must be an object"))
        capsule = {}
    if not isinstance(metadata, dict):
        errors.append(_diagnostic("metadata.missing", "continuity_metadata", "Continuity Metadata must be an object"))
        metadata = {}
    if not isinstance(snapshot, dict):
        errors.append(_diagnostic("snapshot.missing", "source_snapshot", "Source Snapshot must be an object"))
        snapshot = {}
    if observed is not None and not isinstance(observed, dict):
        errors.append(_diagnostic("observed.not_object", "observed", "observed must be an object when present"))
        observed = None

    sections: dict[str, dict[str, Any]] = {}
    for name in ("contract", "checkpoint", "decision_state", "resume"):
        section = capsule.get(name)
        if not isinstance(section, dict):
            errors.append(_diagnostic("capsule.missing_section", f"recovery_capsule.{name}", "section must be an object"))
            section = {}
        sections[name] = section

    contract = sections["contract"]
    checkpoint = sections["checkpoint"]
    decision = sections["decision_state"]
    resume = sections["resume"]

    _validate_accepted_constraints(contract.get("accepted_constraints"), "recovery_capsule.contract.accepted_constraints", errors)
    for field in ("task_id", "revision", "locator", "objective"):
        if not _nonempty_string(contract.get(field)):
            errors.append(
                _diagnostic("contract.missing_field", f"recovery_capsule.contract.{field}", "field must be non-empty")
            )
    _validate_string_list(
        contract.get("constraints"),
        "recovery_capsule.contract.constraints",
        errors,
    )
    _validate_string_list(
        contract.get("acceptance"),
        "recovery_capsule.contract.acceptance",
        errors,
    )
    if not _nonempty_string(checkpoint.get("phase")):
        errors.append(_diagnostic("checkpoint.missing_phase", "recovery_capsule.checkpoint.phase", "phase must be non-empty"))
    has_in_flight_slice = _validate_in_flight_slice(
        checkpoint.get("in_flight"),
        "recovery_capsule.checkpoint.in_flight",
        errors,
    )
    validated = checkpoint.get("validated")
    if not isinstance(validated, list):
        errors.append(
            _diagnostic("checkpoint.validated_not_list", "recovery_capsule.checkpoint.validated", "validated must be a list")
        )
        validated = []
    elif len(validated) > 1:
        errors.append(
            _diagnostic(
                "checkpoint.validated_too_large",
                "recovery_capsule.checkpoint.validated",
                "normally retain the latest validated boundary; extra valid evidence is an efficiency concern",
            )
        )
    for index, item in enumerate(validated):
        item_path = f"recovery_capsule.checkpoint.validated[{index}]"
        if not isinstance(item, dict):
            errors.append(_diagnostic("checkpoint.invalid_validated", item_path, "validated item must be an object"))
            continue
        if not _nonempty_string(item.get("stage")):
            errors.append(_diagnostic("checkpoint.missing_stage", f"{item_path}.stage", "stage must be non-empty"))
        evidence = item.get("evidence")
        if not isinstance(evidence, dict) or not _nonempty_string(evidence.get("locator")):
            errors.append(
                _diagnostic("checkpoint.missing_evidence", f"{item_path}.evidence", "validated stage needs an evidence locator")
            )
        saved_checkpoint = item.get("checkpoint")
        if not isinstance(saved_checkpoint, dict) or not _nonempty_string(saved_checkpoint.get("id")):
            errors.append(
                _diagnostic("checkpoint.missing_identity", f"{item_path}.checkpoint", "validated stage needs a checkpoint id")
            )
    for field in ("active_hypothesis", "acceptance_status"):
        if not _nonempty_string(decision.get(field)):
            errors.append(
                _diagnostic("decision.missing_field", f"recovery_capsule.decision_state.{field}", "field must be non-empty")
            )
    do_not_reopen = _validate_do_not_reopen(
        decision.get("do_not_reopen"),
        "recovery_capsule.decision_state.do_not_reopen",
        errors,
    )
    active_observation = _validate_active_observation(
        decision.get("active_observation"),
        "recovery_capsule.decision_state.active_observation",
        errors,
    )
    semantic_fork = _validate_semantic_fork(
        decision.get("semantic_fork"),
        "recovery_capsule.decision_state.semantic_fork",
        errors,
    )
    evidence_budget = _validate_evidence_budget(
        decision.get("evidence_budget"),
        "recovery_capsule.decision_state.evidence_budget",
        errors,
    )
    _validate_evidence_reopen(
        decision.get("evidence_reopen"),
        "recovery_capsule.decision_state.evidence_reopen",
        evidence_budget,
        errors,
    )
    if semantic_fork is not None and semantic_fork.get("status") == "OPEN" and evidence_budget is None:
        errors.append(
            _diagnostic(
                "semantic_fork.missing_evidence_budget",
                "recovery_capsule.decision_state.evidence_budget",
                "an OPEN semantic fork must preserve its bounded evidence budget",
            )
        )
    if active_observation is not None:
        comparisons["observation"] = "unknown"

    boundary_values: dict[str, str] = {}
    boundary_objects = {
        "recovery_capsule.contract": contract,
        "recovery_capsule.checkpoint": checkpoint,
        "recovery_capsule.decision_state": decision,
        "recovery_capsule.resume": resume,
        "continuity_metadata": metadata,
        "source_snapshot": snapshot,
    }
    if isinstance(observed, dict) and "boundary_id" in observed:
        boundary_objects["observed"] = observed
    for path, value in boundary_objects.items():
        boundary_id = value.get("boundary_id")
        if not _nonempty_string(boundary_id):
            errors.append(_diagnostic("boundary.missing", f"{path}.boundary_id", "boundary_id must be non-empty"))
        else:
            boundary_values[path] = boundary_id
    if len(set(boundary_values.values())) > 1:
        errors.append(
            _diagnostic("boundary.inconsistent", "boundary_id", f"logical views do not share one boundary: {boundary_values}")
        )

    gate = resume.get("gate")
    if not _enum(gate, GATES):
        errors.append(_diagnostic("resume.invalid_gate", "recovery_capsule.resume.gate", "gate is invalid"))
    recovery_type = resume.get("recovery_type")
    if not _enum(recovery_type, RECOVERY_TYPES):
        errors.append(
            _diagnostic(
                "resume.invalid_recovery_type",
                "recovery_capsule.resume.recovery_type",
                "recovery_type must be COMPACT_CONTINUATION, COLD_HANDOFF, or EXTERNAL_RETRY",
            )
        )
    elif recovery_type != "COMPACT_CONTINUATION":
        comparisons["instruction"] = "match"
    anchors = resume.get("anchors")
    _validate_string_list(
        anchors,
        "recovery_capsule.resume.anchors",
        errors,
    )
    next_action = resume.get("next")
    first_action = resume.get("first_allowed_action")
    return_anchor = _validate_return_anchor(
        resume.get("mainline_return_anchor"),
        "recovery_capsule.resume.mainline_return_anchor",
        errors,
    )
    _validate_action(next_action, "recovery_capsule.resume.next", errors)
    _validate_action(first_action, "recovery_capsule.resume.first_allowed_action", errors)
    _validate_observation_action(
        next_action,
        "recovery_capsule.resume.next",
        active_observation,
        errors,
    )
    _validate_observation_action(
        first_action,
        "recovery_capsule.resume.first_allowed_action",
        active_observation,
        errors,
    )
    _validate_semantic_fork_action(
        next_action,
        "recovery_capsule.resume.next",
        semantic_fork,
        evidence_budget,
        errors,
    )
    _validate_semantic_fork_action(
        first_action,
        "recovery_capsule.resume.first_allowed_action",
        semantic_fork,
        evidence_budget,
        errors,
    )
    if isinstance(next_action, dict) and isinstance(first_action, dict):
        if _stable_action_identity(next_action) != _stable_action_identity(first_action):
            errors.append(
                _diagnostic(
                    "resume.action_mismatch",
                    "recovery_capsule.resume.first_allowed_action",
                    "first_allowed_action must equal Next or share its stable action_id",
                )
            )
    first_action_id = _explicit_action_id(first_action)
    if first_action_id in do_not_reopen:
        errors.append(
            _diagnostic(
                "resume.reopens_closed_action",
                "recovery_capsule.resume.first_allowed_action.action_id",
                "first_allowed_action is still listed in DecisionState.do_not_reopen",
            )
        )
    if recovery_type == "COMPACT_CONTINUATION" and isinstance(next_action, dict):
        if _explicit_action_id(next_action) is None or first_action_id is None:
            errors.append(
                _diagnostic(
                    "resume.compact_action_id_required",
                    "recovery_capsule.resume.first_allowed_action.action_id",
                    "compact continuation requires an explicit stable action_id for Next and first_allowed_action",
                )
            )
        if next_action.get("type") == "mutation" and not has_in_flight_slice:
            errors.append(
                _diagnostic(
                    "checkpoint.compact_mutation_missing_slice",
                    "recovery_capsule.checkpoint.in_flight",
                    "a compact continuation mutation must preserve its stable in-flight slice",
                )
            )

    if not _nonempty_string(metadata.get("audit_fingerprint")):
        errors.append(_diagnostic("metadata.missing_audit", "continuity_metadata.audit_fingerprint", "audit_fingerprint is required"))
    count = metadata.get("consecutive_matching_audits")
    if not isinstance(count, int) or isinstance(count, bool) or count < 0:
        errors.append(
            _diagnostic("metadata.invalid_audit_count", "continuity_metadata.consecutive_matching_audits", "count must be a non-negative integer")
        )
    pre_compaction_next_action_id = metadata.get("pre_compaction_next_action_id")
    previous_productive_action_id = metadata.get("previous_productive_action_id")
    instruction_revision_at_snapshot = metadata.get("instruction_revision_at_snapshot")
    directive_revision_at_snapshot = metadata.get(
        "directive_revision_at_snapshot",
        instruction_revision_at_snapshot,
    )
    conversation_cursor_at_snapshot = metadata.get("conversation_cursor_at_snapshot")
    if recovery_type == "COMPACT_CONTINUATION":
        if not _nonempty_string(pre_compaction_next_action_id):
            errors.append(
                _diagnostic(
                    "metadata.missing_pre_compaction_next",
                    "continuity_metadata.pre_compaction_next_action_id",
                    "compact continuation must preserve the action id committed before compaction",
                )
            )
        elif first_action_id is not None and pre_compaction_next_action_id.strip() != first_action_id:
            errors.append(
                _diagnostic(
                    "resume.pre_compaction_action_mismatch",
                    "recovery_capsule.resume.first_allowed_action.action_id",
                    "first_allowed_action must retain pre_compaction_next_action_id",
                )
            )
        if "previous_productive_action_id" not in metadata or (
            previous_productive_action_id is not None and not _nonempty_string(previous_productive_action_id)
        ):
            errors.append(
                _diagnostic(
                    "metadata.invalid_previous_productive_action",
                    "continuity_metadata.previous_productive_action_id",
                    "field must be null or a non-empty stable action id",
                )
            )
        if not _nonempty_string(directive_revision_at_snapshot):
            errors.append(
                _diagnostic(
                    "metadata.missing_directive_revision",
                    "continuity_metadata.directive_revision_at_snapshot",
                    "compact continuation must preserve the latest execution-directive revision separately",
                )
            )
        if conversation_cursor_at_snapshot is not None and not _nonempty_string(conversation_cursor_at_snapshot):
            errors.append(
                _diagnostic(
                    "metadata.invalid_conversation_cursor",
                    "continuity_metadata.conversation_cursor_at_snapshot",
                    "conversation cursor must be a non-empty stable cursor when present",
                )
            )
    references = _revision_map(metadata.get("referenced_sources"), "continuity_metadata.referenced_sources", errors)
    rules = _revision_map(metadata.get("loaded_rules"), "continuity_metadata.loaded_rules", errors)

    for field in ("source_id", "source_fingerprint", "locator"):
        if not _nonempty_string(snapshot.get(field)):
            errors.append(_diagnostic("snapshot.missing_field", f"source_snapshot.{field}", "field must be non-empty"))
    strength = snapshot.get("strength")
    if not _enum(strength, {"strong", "partial"}):
        errors.append(
            _diagnostic(
                "snapshot.invalid_strength",
                "source_snapshot.strength",
                "strength must be strong or partial",
            )
        )
    _validate_string_list(
        snapshot.get("expected_changed_items"),
        "source_snapshot.expected_changed_items",
        errors,
        allow_empty=True,
    )
    if strength == "partial":
        _validate_string_list(
            snapshot.get("missing_layers"),
            "source_snapshot.missing_layers",
            errors,
        )
        if not _nonempty_string(snapshot.get("residual_identity_risk")):
            errors.append(
                _diagnostic("snapshot.partial_risk_missing", "source_snapshot.residual_identity_risk", "partial fingerprint must state residual identity risk")
            )

    if strength == "partial":
        comparisons["source_coverage"] = _partial_source_coverage(snapshot, next_action, warnings)
        if first_action != next_action:
            first_coverage = _partial_source_coverage(snapshot, first_action, warnings)
            if first_coverage != "match":
                comparisons["source_coverage"] = first_coverage

    if isinstance(observed, dict):
        message_class = observed.get("message_class")
        observed_cursor = observed.get("conversation_cursor")
        cursor_advanced = False
        if _nonempty_string(conversation_cursor_at_snapshot) and _nonempty_string(observed_cursor):
            cursor_advanced = observed_cursor != conversation_cursor_at_snapshot
            comparisons["conversation"] = "advanced" if cursor_advanced else "match"
        elif _nonempty_string(conversation_cursor_at_snapshot) or _nonempty_string(observed_cursor):
            comparisons["conversation"] = "unknown"
        if cursor_advanced:
            if not _enum(message_class, MESSAGE_CLASSES):
                errors.append(
                    _diagnostic(
                        "message.unclassified",
                        "observed.message_class",
                        "an advanced conversation cursor must be classified before it can affect the route",
                    )
                )
            message_effect = _validate_message_effect(
                observed.get("message_effect"),
                message_class,
                "observed.message_effect",
                errors,
            )
        else:
            message_effect = observed.get("message_effect") if isinstance(observed.get("message_effect"), dict) else None

        observed_source = observed.get("source_fingerprint")
        if _nonempty_string(observed_source):
            comparisons["source"] = "match" if observed_source == snapshot.get("source_fingerprint") else "mismatch"
            if comparisons["source"] == "mismatch":
                mismatches.append(
                    _diagnostic("source.fingerprint_mismatch", "observed.source_fingerprint", "observed source fingerprint differs from snapshot")
                )
        observed_revision = observed.get("contract_revision")
        if _nonempty_string(observed_revision):
            comparisons["contract"] = "match" if observed_revision == contract.get("revision") else "mismatch"
            if comparisons["contract"] == "mismatch":
                mismatches.append(
                    _diagnostic("contract.revision_mismatch", "observed.contract_revision", "observed contract revision differs")
                )
        observed_directive_revision = observed.get(
            "directive_revision",
            observed.get("instruction_revision"),
        )
        if _nonempty_string(observed_directive_revision) and _nonempty_string(directive_revision_at_snapshot):
            directive_changed = observed_directive_revision != directive_revision_at_snapshot
            scoped_change = (
                directive_changed
                and message_class == "NEW_CONSTRAINT"
                and isinstance(message_effect, dict)
                and message_effect.get("affects_saved_next") is False
            )
            comparisons["directive"] = "scoped_change" if scoped_change else (
                "mismatch" if directive_changed else "match"
            )
            comparisons["instruction"] = comparisons["directive"]
            if comparisons["directive"] == "mismatch":
                mismatches.append(
                    _diagnostic(
                        "directive.revision_mismatch",
                        "observed.directive_revision",
                        "execution directives affecting the saved Next differ from its captured revision",
                    )
                )
        if isinstance(message_effect, dict) and message_effect.get("affects_saved_next") is True:
            comparisons["message_effect"] = "mismatch"
            mismatches.append(
                _diagnostic(
                    "message.saved_next_invalidated",
                    "observed.message_effect.affects_saved_next",
                    "the classified message invalidates the saved Next",
                )
            )
        if message_class in PASSIVE_MESSAGE_CLASSES and comparisons["directive"] == "mismatch":
            errors.append(
                _diagnostic(
                    "message.passive_revision_change",
                    "observed.directive_revision",
                    "QUERY and REMINDER cannot silently change the directive revision",
                )
            )
        comparisons["references"] = _compare_ledger(
            references, observed.get("referenced_sources"), "referenced_sources", mismatches
        )
        comparisons["rules"] = _compare_ledger(rules, observed.get("loaded_rules"), "loaded_rules", mismatches)
        if active_observation is not None:
            observed_observation_revision = observed.get("observation_revision")
            observed_observation_result = observed.get("observation_result")
            if _nonempty_string(observed_observation_revision) and _nonempty_string(observed_observation_result):
                comparisons["observation"] = (
                    "match"
                    if observed_observation_revision == active_observation.get("revision")
                    and observed_observation_result == active_observation.get("result")
                    else "mismatch"
                )
                if comparisons["observation"] == "mismatch":
                    mismatches.append(
                        _diagnostic(
                            "observation.state_mismatch",
                            "observed.observation_revision",
                            "observed observation revision or result differs from DecisionState",
                        )
                    )

        interruption_state = message_effect.get("interruption_state") if isinstance(message_effect, dict) else None
        if message_class == "TEMPORARY_INTERRUPT" and return_anchor is None:
            errors.append(
                _diagnostic(
                    "return_anchor.required",
                    "recovery_capsule.resume.mainline_return_anchor",
                    "a temporary interrupt must preserve the original task return anchor",
                )
            )
            comparisons["return_anchor"] = "mismatch"
        elif return_anchor is not None:
            anchor_matches = (
                return_anchor.get("original_task_id") == contract.get("task_id")
                and return_anchor.get("frozen_contract_revision") == contract.get("revision")
                and return_anchor.get("source_fingerprint") == snapshot.get("source_fingerprint")
                and return_anchor.get("saved_next_action_id") == first_action_id
            )
            comparisons["return_anchor"] = "match" if anchor_matches else "mismatch"
            if not anchor_matches:
                mismatches.append(
                    _diagnostic(
                        "return_anchor.identity_mismatch",
                        "recovery_capsule.resume.mainline_return_anchor",
                        "return anchor task, contract, source, or saved Next no longer matches the mainline",
                    )
                )

    efficiency_codes = {
        "list.too_large", "decision.do_not_reopen_too_large",
        "semantic_fork.options_too_large", "semantic_fork.consequences_too_large",
        "checkpoint.validated_too_large", "metadata.invalid_audit_count",
    }
    warnings.extend({**item, "category": "efficiency"} for item in errors if item["code"] in efficiency_codes)
    errors = [item for item in errors if item["code"] not in efficiency_codes]
    readiness_keys = {"source", "source_coverage", "contract", "directive", "references", "rules", "message_effect", "return_anchor"}
    if active_observation is not None:
        readiness_keys.add("observation")
    all_matched = all(comparisons.get(key) in {"match", "scoped_change"} for key in readiness_keys)
    any_mismatch = any(value == "mismatch" for value in comparisons.values())
    interruption_active = (
        isinstance(observed, dict)
        and isinstance(observed.get("message_effect"), dict)
        and observed["message_effect"].get("interruption_state") == "ACTIVE"
    )
    if errors or any_mismatch or gate == "SNAPSHOT_REQUIRED":
        suggested_gate = "SNAPSHOT_REQUIRED"
    elif interruption_active:
        suggested_gate = "RESUME_AUDIT"
        warnings.append(
            _diagnostic(
                "return_anchor.interrupt_active",
                "observed.message_effect.interruption_state",
                "the temporary interrupt is still active; preserve the anchor and do not execute the saved mainline Next",
            )
        )
    elif all_matched:
        suggested_gate = "READY"
    else:
        suggested_gate = "RESUME_AUDIT"
        warnings.append(
            _diagnostic(
                "audit.observations_incomplete",
                "observed",
                "lightweight source, contract, reference, and rule observations are required before READY",
            )
        )
    if gate == "READY" and suggested_gate != "READY":
        errors.append(
            _diagnostic("gate.unsafe_ready", "recovery_capsule.resume.gate", "saved READY is not supported by current state")
        )
        suggested_gate = "SNAPSHOT_REQUIRED"

    return {
        "valid": not errors,
        "ready": not errors and suggested_gate == "READY",
        "saved_gate": gate,
        "suggested_gate": suggested_gate,
        "comparisons": comparisons,
        "action_identity": _stable_action_identity(next_action) if isinstance(next_action, dict) else None,
        "pre_compaction_next_action_id": pre_compaction_next_action_id,
        "previous_productive_action_id": previous_productive_action_id,
        "conversation_cursor_at_snapshot": conversation_cursor_at_snapshot,
        "directive_revision_at_snapshot": directive_revision_at_snapshot,
        "errors": errors,
        "warnings": warnings,
        "mismatches": mismatches,
    }


def _load(path: Path | None) -> Any:
    if path is None or str(path) == "-":
        return json.load(sys.stdin)
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("state", nargs="?", type=Path, help="JSON state file; omit or use - for stdin")
    parser.add_argument("--json", action="store_true", help="emit machine-readable diagnostics")
    args = parser.parse_args()
    try:
        result = validate_state(_load(args.state))
    except (OSError, json.JSONDecodeError) as error:
        result = {
            "valid": False,
            "ready": False,
            "suggested_gate": "SNAPSHOT_REQUIRED",
            "errors": [_diagnostic("input.unreadable", "$", str(error))],
            "warnings": [],
            "mismatches": [],
        }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        status = "READY" if result.get("ready") else result.get("suggested_gate", "SNAPSHOT_REQUIRED")
        print(f"{status}: valid={str(result.get('valid', False)).lower()}")
        for group in ("errors", "mismatches", "warnings"):
            for item in result.get(group, []):
                print(f"- {group[:-1]} {item['code']} at {item['path']}: {item['message']}")
    return 0 if result.get("valid") else 1


if __name__ == "__main__":
    sys.exit(main())
