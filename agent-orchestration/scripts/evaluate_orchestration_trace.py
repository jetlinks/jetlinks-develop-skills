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
TIER_ORDER = {"economy": 0, "balanced": 1, "strong": 2}


def _nonempty(value: Any) -> bool:
    return value not in (None, "", [], {})


def evaluate_trace(trace: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    events = trace.get("events")
    if not isinstance(events, list):
        return {"passed": False, "errors": ["events must be a list"], "warnings": [], "metrics": {}}

    budget = trace.get("budget") if isinstance(trace.get("budget"), dict) else {}
    max_active = int(budget.get("max_active", 2))
    max_depth = int(budget.get("max_depth", 1))
    route_count = 0
    integration_count = 0
    delegate_count = 0
    escalation_count = 0
    weak_retry_count = 0
    active: dict[str, set[str]] = {}
    assignment_for_agent: dict[str, str] = {}
    failed_assignments: set[str] = set()
    escalated_assignments: dict[str, str] = {}
    successful_assignments: set[str] = set()
    max_observed_active = 0

    for index, event in enumerate(events):
        if not isinstance(event, dict):
            errors.append(f"event[{index}] must be an object")
            continue
        event_type = event.get("type")

        if event_type == "route":
            route_count += 1
            if event.get("mode") not in ROUTE_MODES:
                errors.append(f"event[{index}] has invalid route mode")
            if not _nonempty(event.get("rationale")):
                errors.append(f"event[{index}] route lacks rationale")

        elif event_type == "delegate":
            delegate_count += 1
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
            depth = int(event.get("depth", 1))
            if depth > max_depth:
                errors.append(f"event[{index}] depth {depth} exceeds max_depth {max_depth}")
            capsule = event.get("capsule")
            if not isinstance(capsule, dict):
                errors.append(f"event[{index}] delegate lacks Assignment Capsule")
            else:
                missing = sorted(field for field in CAPSULE_FIELDS if not _nonempty(capsule.get(field)))
                if missing:
                    errors.append(f"event[{index}] capsule missing: {', '.join(missing)}")
            if assignment in failed_assignments and assignment not in escalated_assignments:
                weak_retry_count += 1
                errors.append(f"event[{index}] retries failed assignment {assignment!r} without escalation")
            elif assignment in failed_assignments:
                required_tier = escalated_assignments.pop(assignment)
                if tier in TIER_ORDER and TIER_ORDER[tier] < TIER_ORDER[required_tier]:
                    errors.append(
                        f"event[{index}] retry tier {tier!r} is below escalated tier {required_tier!r}"
                    )
            write_set = set(event.get("write_set") or [])
            for other_agent, other_writes in active.items():
                overlap = sorted(write_set & other_writes)
                if overlap:
                    errors.append(
                        f"event[{index}] overlapping active writes for {agent!r} and {other_agent!r}: {', '.join(overlap)}"
                    )
            active[agent] = write_set
            assignment_for_agent[agent] = assignment
            max_observed_active = max(max_observed_active, len(active))
            if len(active) > max_active:
                errors.append(f"event[{index}] active Agents {len(active)} exceed max_active {max_active}")

        elif event_type == "result":
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
            elif status in {"failed", "blocked", "stale"}:
                failed_assignments.add(assignment)
            else:
                errors.append(f"event[{index}] has invalid result status")
            active.pop(agent, None)
            assignment_for_agent.pop(agent, None)

        elif event_type == "escalate":
            escalation_count += 1
            assignment = str(event.get("assignment_id", ""))
            from_tier = event.get("from_tier")
            to_tier = event.get("to_tier")
            if assignment not in failed_assignments:
                errors.append(f"event[{index}] escalates assignment without a recorded failure")
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
            ):
                escalated_assignments[assignment] = str(to_tier)

        elif event_type == "integrate":
            integration_count += 1
            if not _nonempty(event.get("acceptance")):
                errors.append(f"event[{index}] integration lacks acceptance mapping")
            if successful_assignments and not _nonempty(event.get("evidence")):
                errors.append(f"event[{index}] integration lacks evidence")

        else:
            errors.append(f"event[{index}] has unknown type {event_type!r}")

    if route_count != 1:
        errors.append(f"trace requires exactly one RouteDecision; found {route_count}")
    if active:
        errors.append(f"trace ends with active Agents: {', '.join(sorted(active))}")
    if delegate_count and integration_count == 0:
        errors.append("delegated trace lacks integration")

    return {
        "passed": not errors,
        "errors": errors,
        "warnings": warnings,
        "metrics": {
            "delegations": delegate_count,
            "escalations": escalation_count,
            "weak_retry_count": weak_retry_count,
            "max_observed_active": max_observed_active,
            "successful_assignments": len(successful_assignments),
            "failed_assignments": len(failed_assignments),
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
