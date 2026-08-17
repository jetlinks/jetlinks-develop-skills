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
ACTION_TYPES = {"mutation", "check", "blocker"}
ACTION_PURPOSES = {"solution", "observation_setup", "observation_repair"}
MATCH_VALUES = {"match", "mismatch", "unknown"}
OBSERVATION_RESULTS = {"PLANNED", "DISCRIMINATING", "INVALID", "INCONCLUSIVE"}
VAGUE_ACTION = re.compile(
    r"^(?:continue|resume|proceed|start|do)\s+(?:the\s+)?(?:work|implementation|analysis|task|investigation)$"
    r"|^(?:继续|开始|恢复|推进)(?:实现|开发|分析|调查|任务|工作|处理)(?:阶段|任务|工作)?$",
    re.IGNORECASE,
)


def _diagnostic(code: str, path: str, message: str) -> dict[str, str]:
    return {"code": code, "path": path, "message": message}


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _nonempty_scope(value: Any) -> bool:
    if _nonempty_string(value):
        return True
    return isinstance(value, list) and bool(value) and all(_nonempty_string(item) for item in value)


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


def _validate_action(action: Any, path: str, errors: list[dict[str, str]]) -> None:
    if not isinstance(action, dict):
        errors.append(_diagnostic("action.not_object", path, "action must be an object"))
        return
    action_type = action.get("type")
    if action_type not in ACTION_TYPES:
        errors.append(
            _diagnostic("action.invalid_type", f"{path}.type", "type must be mutation, check, or blocker")
        )
    purpose = action.get("purpose")
    if purpose is not None and purpose not in ACTION_PURPOSES:
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
        if not isinstance(items, list) or not items or not all(_nonempty_string(item) for item in items):
            errors.append(
                _diagnostic(
                    "observation.invalid_list",
                    f"{path}.{field}",
                    "field must be a non-empty list of bounded statements",
                )
            )
    result = value.get("result")
    if result not in OBSERVATION_RESULTS:
        errors.append(
            _diagnostic(
                "observation.invalid_result",
                f"{path}.result",
                "result must be PLANNED, DISCRIMINATING, INVALID, or INCONCLUSIVE",
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
    if result in OBSERVATION_RESULTS - {"PLANNED"}:
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
    elif result == "INCONCLUSIVE":
        errors.append(
            _diagnostic(
                "observation.inconclusive_blocks_mutation",
                path,
                "an inconclusive observation requires a check, reframe, or blocker before mutation",
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


def validate_state(document: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    mismatches: list[dict[str, str]] = []
    comparisons = {"source": "unknown", "contract": "unknown", "references": "unknown", "rules": "unknown"}

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

    for field in ("task_id", "revision", "objective"):
        if not _nonempty_string(contract.get(field)):
            errors.append(
                _diagnostic("contract.missing_field", f"recovery_capsule.contract.{field}", "field must be non-empty")
            )
    if not isinstance(contract.get("acceptance"), list) or not contract.get("acceptance"):
        errors.append(
            _diagnostic("contract.missing_acceptance", "recovery_capsule.contract.acceptance", "acceptance must be a non-empty list")
        )
    if not _nonempty_string(checkpoint.get("phase")):
        errors.append(_diagnostic("checkpoint.missing_phase", "recovery_capsule.checkpoint.phase", "phase must be non-empty"))
    validated = checkpoint.get("validated")
    if not isinstance(validated, list):
        errors.append(
            _diagnostic("checkpoint.validated_not_list", "recovery_capsule.checkpoint.validated", "validated must be a list")
        )
        validated = []
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
    active_observation = _validate_active_observation(
        decision.get("active_observation"),
        "recovery_capsule.decision_state.active_observation",
        errors,
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
    if gate not in GATES:
        errors.append(_diagnostic("resume.invalid_gate", "recovery_capsule.resume.gate", "gate is invalid"))
    anchors = resume.get("anchors")
    if not isinstance(anchors, list):
        errors.append(_diagnostic("resume.anchors_not_list", "recovery_capsule.resume.anchors", "anchors must be a list"))
    next_action = resume.get("next")
    first_action = resume.get("first_allowed_action")
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
    if isinstance(next_action, dict) and isinstance(first_action, dict):
        if _stable_action_identity(next_action) != _stable_action_identity(first_action):
            errors.append(
                _diagnostic(
                    "resume.action_mismatch",
                    "recovery_capsule.resume.first_allowed_action",
                    "first_allowed_action must equal Next or share its stable action_id",
                )
            )

    if not _nonempty_string(metadata.get("audit_fingerprint")):
        errors.append(_diagnostic("metadata.missing_audit", "continuity_metadata.audit_fingerprint", "audit_fingerprint is required"))
    count = metadata.get("consecutive_matching_audits")
    if not isinstance(count, int) or isinstance(count, bool) or count < 0:
        errors.append(
            _diagnostic("metadata.invalid_audit_count", "continuity_metadata.consecutive_matching_audits", "count must be a non-negative integer")
        )
    references = _revision_map(metadata.get("referenced_sources"), "continuity_metadata.referenced_sources", errors)
    rules = _revision_map(metadata.get("loaded_rules"), "continuity_metadata.loaded_rules", errors)

    for field in ("source_id", "source_fingerprint", "strength", "locator"):
        if not _nonempty_string(snapshot.get(field)):
            errors.append(_diagnostic("snapshot.missing_field", f"source_snapshot.{field}", "field must be non-empty"))
    strength = snapshot.get("strength")
    if isinstance(strength, str) and strength.startswith("partial"):
        for field in ("missing_layers", "expected_changed_items"):
            if not isinstance(snapshot.get(field), list) or not snapshot.get(field):
                errors.append(
                    _diagnostic("snapshot.partial_undeclared", f"source_snapshot.{field}", "partial fingerprint must declare this non-empty list")
                )
        if not _nonempty_string(snapshot.get("residual_identity_risk")):
            errors.append(
                _diagnostic("snapshot.partial_risk_missing", "source_snapshot.residual_identity_risk", "partial fingerprint must state residual identity risk")
            )

    if isinstance(observed, dict):
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

    all_matched = all(value == "match" for value in comparisons.values())
    any_mismatch = any(value == "mismatch" for value in comparisons.values())
    if errors or any_mismatch or gate == "SNAPSHOT_REQUIRED":
        suggested_gate = "SNAPSHOT_REQUIRED"
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
