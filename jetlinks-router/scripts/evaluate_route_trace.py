#!/usr/bin/env python3
"""Evaluate a host-neutral focused-skill routing trace without loading skills."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ACTION_TYPES = {"mutation", "check", "dispatch", "collect", "blocker"}
MUTATION_PURPOSES = {"solution", "observation_setup", "observation_repair"}
DISPATCH_WORK_CLASSES = {
    "evidence_scout",
    "documentation",
    "contract_design",
    "implementation",
    "integration",
    "review",
    "validation",
}


def _text(value: Any) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def _string_list(value: Any, path: str, errors: list[str], *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (not allow_empty and not value):
        errors.append(f"{path} must be a {'possibly empty ' if allow_empty else ''}list of unique nonempty strings")
        return []
    result = [item.strip() for item in value if isinstance(item, str) and item.strip()]
    if len(result) != len(value) or len(set(result)) != len(result):
        errors.append(f"{path} must contain only unique nonempty strings")
    return result


def _validate_action(value: Any, path: str, errors: list[str]) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        errors.append(f"{path} must be an executable action object")
        return None
    if _text(value.get("action_id")) is None:
        errors.append(f"{path}.action_id must be nonempty")
    action_type = value.get("type")
    if not isinstance(action_type, str) or action_type not in ACTION_TYPES:
        errors.append(f"{path}.type must be mutation, check, dispatch, collect, or blocker")
    purpose = value.get("purpose")
    if action_type == "mutation" and (not isinstance(purpose, str) or purpose not in MUTATION_PURPOSES):
        errors.append(
            f"{path}.purpose must be solution, observation_setup, or observation_repair for mutation"
        )
    work_class = value.get("work_class")
    if action_type == "dispatch" and (not isinstance(work_class, str) or work_class not in DISPATCH_WORK_CLASSES):
        errors.append(f"{path}.work_class is invalid or missing for dispatch")
    if _text(value.get("owner")) is None:
        errors.append(f"{path}.owner must be nonempty")
    _string_list(value.get("scope"), f"{path}.scope", errors)
    if _text(value.get("observable_signal")) is None:
        errors.append(f"{path}.observable_signal must be nonempty")
    return value


def evaluate_trace(document: Any) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(document, dict):
        return {"passed": False, "errors": ["trace must be an object"], "warnings": [], "metrics": {}}

    envelope = document.get("route_envelope")
    if not isinstance(envelope, dict):
        errors.append("route_envelope must be an object")
        envelope = {}
    if _text(envelope.get("current_decision")) is None:
        errors.append("route_envelope.current_decision must be nonempty")
    minimum_skills = _string_list(
        envelope.get("minimum_skills"), "route_envelope.minimum_skills", errors
    )
    confirmation = envelope.get("user_confirmation_required")
    if confirmation != "none" and _text(confirmation) is None:
        errors.append("route_envelope.user_confirmation_required must be 'none' or one focused decision")
    unique_next = _validate_action(envelope.get("unique_next"), "route_envelope.unique_next", errors)
    unique_next_action_id = (
        _text(unique_next.get("action_id")) if isinstance(unique_next, dict) else None
    )

    semantic_fork = document.get("semantic_fork")
    evidence_budget = document.get("evidence_budget")
    if semantic_fork is not None and not isinstance(semantic_fork, dict):
        errors.append("semantic_fork must be an object when present")
        semantic_fork = None
    if isinstance(semantic_fork, dict) and semantic_fork.get("status") == "OPEN":
        if not isinstance(evidence_budget, dict):
            errors.append("an OPEN semantic fork must retain evidence_budget")
        if isinstance(unique_next, dict):
            action_type = unique_next.get("type")
            purpose = unique_next.get("purpose")
            work_class = unique_next.get("work_class")
            if action_type == "mutation" and (
                not isinstance(purpose, str) or purpose not in {"observation_setup", "observation_repair"}
            ):
                errors.append("an OPEN semantic fork cannot route authoritative or solution work")
            if action_type == "dispatch" and work_class != "evidence_scout":
                errors.append("an OPEN semantic fork may dispatch only a bounded evidence scout")
        if (
            isinstance(evidence_budget, dict)
            and evidence_budget.get("status") == "STOPPED"
            and evidence_budget.get("stop_reason") in {"ASK_USER", "BLOCKER"}
            and isinstance(unique_next, dict)
            and unique_next.get("type") != "blocker"
        ):
            errors.append("a stopped OPEN semantic fork must route its focused blocker")

    events = document.get("events")
    if not isinstance(events, list):
        errors.append("events must be a list")
        events = []
    loaded_skills: list[str] = []
    ordinary_classification_events: list[int] = []
    productive_actions: list[dict[str, Any]] = []
    for index, event in enumerate(events):
        if not isinstance(event, dict):
            errors.append(f"event[{index}] must be an object")
            continue
        event_type = event.get("type")
        if event_type == "skill_load":
            skill = _text(event.get("skill"))
            if skill is None:
                errors.append(f"event[{index}].skill must be nonempty")
            else:
                loaded_skills.append(skill)
        elif event_type == "ordinary_classification":
            ordinary_classification_events.append(index)
        elif event_type == "action" and event.get("productive") is not False:
            productive_actions.append(event)

    minimum_set = set(minimum_skills)
    extra_loaded = sorted(set(loaded_skills) - minimum_set)
    if extra_loaded:
        warnings.append("loaded skills exceed minimum_skills: " + ", ".join(extra_loaded))
    if len(loaded_skills) != len(set(loaded_skills)):
        warnings.append("the same skill was loaded repeatedly in one route")

    recovery = document.get("recovery")
    compact_match = (
        isinstance(recovery, dict)
        and recovery.get("type") == "COMPACT_CONTINUATION"
        and recovery.get("identity_match") is True
        and recovery.get("instruction_changed") is False
        and recovery.get("loaded_rules_match") is True
    )
    saved_next = _text(recovery.get("saved_next_action_id")) if isinstance(recovery, dict) else None
    first_action_id = _text(productive_actions[0].get("action_id")) if productive_actions else None
    if first_action_id is not None and first_action_id != unique_next_action_id:
        errors.append("the first productive action must execute route_envelope.unique_next")
    if compact_match:
        if loaded_skills:
            warnings.append("matching compact continuation reloaded skills despite matching LoadedRules")
        if ordinary_classification_events:
            warnings.append("matching compact continuation reran ordinary classification")
        if saved_next is None or unique_next_action_id != saved_next or first_action_id != saved_next:
            errors.append("matching compact continuation must execute the saved first action")
    elif minimum_set and set(loaded_skills) != minimum_set:
        warnings.append("skill load events differ from the planned minimum; inspect reuse or route changes")

    return {
        "passed": not errors,
        "errors": errors,
        "warnings": warnings,
        "metrics": {
            "minimum_skill_count": len(minimum_set),
            "loaded_skill_count": len(loaded_skills),
            "extra_loaded_skill_count": len(extra_loaded),
            "ordinary_classification_count": len(ordinary_classification_events),
            "compact_fast_path_applicable": compact_match,
            "saved_next_action_hit": first_action_id == saved_next if compact_match else None,
        },
    }


def _load(path: Path | None) -> Any:
    if path is None or str(path) == "-":
        return json.load(sys.stdin)
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trace", nargs="?", type=Path, help="JSON trace; omit or use - for stdin")
    args = parser.parse_args()
    try:
        result = evaluate_trace(_load(args.trace))
    except (OSError, json.JSONDecodeError, ValueError) as error:
        result = {"passed": False, "errors": [str(error)], "metrics": {}}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
