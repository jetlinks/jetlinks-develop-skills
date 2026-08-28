#!/usr/bin/env python3
"""Project bounded model-facing context for a compact-session adapter.

The projector is read-only. It consumes the JSON state accepted by
``validate_continuity_state.py`` and emits only the fields needed to resume a
task. Hosts decide whether and where to inject the result; this script never
updates the capsule, source, tools, or VCS.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    from validate_continuity_state import validate_state
except ImportError:  # pragma: no cover - only relevant to unusual import hosts
    from importlib.util import module_from_spec, spec_from_file_location

    _spec = spec_from_file_location(
        "validate_continuity_state",
        Path(__file__).with_name("validate_continuity_state.py"),
    )
    if _spec is None or _spec.loader is None:
        raise
    _module = module_from_spec(_spec)
    _spec.loader.exec_module(_module)
    validate_state = _module.validate_state


def _text(value: Any, limit: int) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    value = value.strip()
    return value if len(value) <= limit else value[: max(0, limit - 1)] + "…"


def _action(action: Any, limit: int) -> dict[str, Any] | None:
    if not isinstance(action, dict):
        return None
    result: dict[str, Any] = {}
    for key in ("action_id", "type", "purpose", "owner", "scope", "observable_signal"):
        value = action.get(key)
        if key == "scope" and isinstance(value, list):
            result[key] = [short for item in value if (short := _text(item, limit))]
        elif key in {"action_id", "type", "purpose"} and value is not None:
            result[key] = value
        else:
            short = _text(value, limit)
            if short is not None:
                result[key] = short
    return result


def _in_flight(value: Any, limit: int) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    result: dict[str, Any] = {}
    for key in ("slice_id", "status", "owner"):
        short = _text(value.get(key), limit)
        if short is not None:
            result[key] = short
    items = value.get("expected_changed_items")
    if isinstance(items, list):
        result["expected_changed_items"] = [short for item in items if (short := _text(item, limit))]
    return result


def _validated(value: Any, limit: int) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    result: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        projected: dict[str, Any] = {}
        for key in ("stage", "evidence", "checkpoint"):
            if key in {"evidence", "checkpoint"} and isinstance(item.get(key), dict):
                nested = item[key]
                projected[key] = {
                    nested_key: short
                    for nested_key in ("locator", "id")
                    if (short := _text(nested.get(nested_key), limit))
                }
            else:
                short = _text(item.get(key), limit)
                if short is not None:
                    projected[key] = short
        result.append(projected)
    return result


def project_context(document: dict[str, Any], max_anchors: int = 7, text_limit: int = 360) -> dict[str, Any]:
    """Return a bounded projection plus the validator's current gate decision."""

    validation = validate_state(document)
    capsule = document.get("recovery_capsule") if isinstance(document.get("recovery_capsule"), dict) else {}
    contract = capsule.get("contract") if isinstance(capsule.get("contract"), dict) else {}
    checkpoint = capsule.get("checkpoint") if isinstance(capsule.get("checkpoint"), dict) else {}
    decision = capsule.get("decision_state") if isinstance(capsule.get("decision_state"), dict) else {}
    resume = capsule.get("resume") if isinstance(capsule.get("resume"), dict) else {}
    metadata = document.get("continuity_metadata") if isinstance(document.get("continuity_metadata"), dict) else {}
    snapshot = document.get("source_snapshot") if isinstance(document.get("source_snapshot"), dict) else {}
    anchor_values = resume.get("anchors") if isinstance(resume.get("anchors"), list) else []
    projection_omissions: dict[str, int] = {}
    if len(anchor_values) > max_anchors:
        projection_omissions["resume.anchors"] = len(anchor_values) - max_anchors
    projection_ready = bool(validation.get("ready")) and not projection_omissions

    observation_value = decision.get("active_observation")
    observation = None
    if isinstance(observation_value, dict):
        observation = {
            key: short
            for key in (
                "id",
                "revision",
                "result",
                "decision",
                "boundary",
                "prediction",
                "discriminator",
                "actual_signal",
                "evidence_locator",
            )
            if (short := _text(observation_value.get(key), text_limit))
        }
        for key in ("preconditions", "invalidators"):
            items = observation_value.get(key)
            if isinstance(items, list):
                observation[key] = [
                    short for item in items if (short := _text(item, text_limit))
                ]

    semantic_fork_value = decision.get("semantic_fork")
    semantic_fork = None
    if isinstance(semantic_fork_value, dict):
        options = []
        for item in semantic_fork_value.get("options", []):
            if not isinstance(item, dict):
                continue
            projected_option = {
                key: short
                for key in ("id", "contract")
                if (short := _text(item.get(key), text_limit))
            }
            if projected_option:
                options.append(projected_option)
        consequences_value = semantic_fork_value.get("architectural_consequences")
        consequences = {}
        if isinstance(consequences_value, dict):
            for key, value in consequences_value.items():
                short_key = _text(key, text_limit)
                short_value = _text(value, text_limit)
                if short_key and short_value:
                    consequences[short_key] = short_value
        semantic_fork = {
            "decision_question": _text(semantic_fork_value.get("decision_question"), text_limit),
            "status": semantic_fork_value.get("status"),
            "evidence_can_decide": semantic_fork_value.get("evidence_can_decide"),
            "options": options,
            "architectural_consequences": consequences,
        }
        resolution = semantic_fork_value.get("resolution")
        if isinstance(resolution, dict):
            semantic_fork["resolution"] = {
                key: short
                for key in ("source", "decision", "locator")
                if (short := _text(resolution.get(key), text_limit))
            }

    evidence_budget_value = decision.get("evidence_budget")
    evidence_budget = None
    if isinstance(evidence_budget_value, dict):
        evidence_budget = {
            key: evidence_budget_value.get(key)
            for key in ("round", "scout_count", "status", "stop_reason")
            if evidence_budget_value.get(key) is not None
        }

    evidence_reopen_value = decision.get("evidence_reopen")
    evidence_reopen = None
    if isinstance(evidence_reopen_value, dict):
        evidence_reopen = {
            "reason": _text(evidence_reopen_value.get("reason"), text_limit),
            "locator": _text(evidence_reopen_value.get("locator"), text_limit),
            "from_round": evidence_reopen_value.get("from_round"),
        }

    return_anchor_value = resume.get("mainline_return_anchor")
    return_anchor = None
    if isinstance(return_anchor_value, dict):
        return_anchor = {
            key: short
            for key in (
                "interruption_id",
                "original_task_id",
                "saved_stage",
                "saved_next_action_id",
                "frozen_contract_revision",
                "source_fingerprint",
                "interrupt_objective",
                "resume_condition",
            )
            if (short := _text(return_anchor_value.get(key), text_limit))
        }
        return_anchor["active_assignment_ids"] = [
            short
            for item in return_anchor_value.get("active_assignment_ids", [])
            if (short := _text(item, text_limit))
        ]

    return {
        "gate": (
            validation.get("suggested_gate", "SNAPSHOT_REQUIRED")
            if not projection_omissions
            else "SNAPSHOT_REQUIRED"
        ),
        "ready": projection_ready,
        "projection_omissions": projection_omissions,
        "recovery_type": resume.get("recovery_type"),
        "contract": {
            "task_id": _text(contract.get("task_id"), text_limit),
            "revision": _text(contract.get("revision"), text_limit),
            "locator": _text(contract.get("locator"), text_limit),
            "objective": _text(contract.get("objective"), text_limit),
            "constraints": [
                short for item in contract.get("constraints", [])
                if (short := _text(item, text_limit))
            ],
            "acceptance": [
                short for item in contract.get("acceptance", [])
                if (short := _text(item, text_limit))
            ],
        },
        "checkpoint": {
            "boundary_id": _text(checkpoint.get("boundary_id"), text_limit),
            "phase": _text(checkpoint.get("phase"), text_limit),
            "in_flight": _in_flight(checkpoint.get("in_flight"), text_limit),
            "validated": _validated(checkpoint.get("validated"), text_limit),
        },
        "decision_state": {
            "active_hypothesis": _text(decision.get("active_hypothesis"), text_limit),
            "acceptance_status": _text(decision.get("acceptance_status"), text_limit),
            "current_stage": _text(decision.get("current_stage"), text_limit),
            "stage_entry_gate": _text(decision.get("stage_entry_gate"), text_limit),
            "latest_discriminating_evidence": _text(
                decision.get("latest_discriminating_evidence"), text_limit
            ),
            "do_not_reopen": [
                {
                    key: short
                    for key in ("action_id", "reason", "reopen_when")
                    if (short := _text(item.get(key), text_limit))
                }
                for item in decision.get("do_not_reopen", [])
                if isinstance(item, dict)
            ],
            "active_observation": observation,
            "semantic_fork": semantic_fork,
            "evidence_budget": evidence_budget,
            "evidence_reopen": evidence_reopen,
        },
        "resume": {
            "boundary_id": _text(resume.get("boundary_id"), text_limit),
            "anchors": [
                short for item in anchor_values[:max_anchors]
                if (short := _text(item, text_limit))
            ],
            "next": _action(resume.get("next"), text_limit),
            "first_allowed_action": _action(resume.get("first_allowed_action"), text_limit),
            "mainline_return_anchor": return_anchor,
        },
        "identity": {
            "source_id": _text(snapshot.get("source_id"), text_limit),
            "source_fingerprint": _text(snapshot.get("source_fingerprint"), text_limit),
            "strength": _text(snapshot.get("strength"), text_limit),
            "audit_fingerprint": _text(metadata.get("audit_fingerprint"), text_limit),
            "pre_compaction_next_action_id": _text(metadata.get("pre_compaction_next_action_id"), text_limit),
            "previous_productive_action_id": _text(metadata.get("previous_productive_action_id"), text_limit),
            "conversation_cursor_at_snapshot": _text(metadata.get("conversation_cursor_at_snapshot"), text_limit),
            "directive_revision_at_snapshot": _text(
                metadata.get("directive_revision_at_snapshot", metadata.get("instruction_revision_at_snapshot")),
                text_limit,
            ),
            "comparisons": validation.get("comparisons", {}),
            "mismatches": validation.get("mismatches", []),
        },
        "instructions": (
            "Identity matched: execute first_allowed_action in this resumed turn; do not reload unchanged references."
            if projection_ready
            else "Identity or bounded projection is not ready: reconcile only the reported mismatches or omissions, refresh the capsule, and do not mutate production state."
        ),
    }


def _load(path: Path | None) -> Any:
    if path is None or str(path) == "-":
        return json.load(sys.stdin)
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("state", nargs="?", type=Path, help="JSON state file; omit or use - for stdin")
    parser.add_argument("--max-anchors", type=int, default=7)
    parser.add_argument("--text-limit", type=int, default=360)
    args = parser.parse_args()
    if args.max_anchors < 1 or args.text_limit < 40:
        parser.error("--max-anchors must be positive and --text-limit must be at least 40")
    try:
        document = _load(args.state)
        if not isinstance(document, dict):
            raise ValueError("state document must be an object")
        output = project_context(document, args.max_anchors, args.text_limit)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
