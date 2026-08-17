#!/usr/bin/env python3
"""Evaluate normalized continuation traces without depending on an agent host."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


READ_TYPES = {
    "read",
    "capsule_read",
    "identity_compare",
    "reference_compare",
    "rule_compare",
    "history_read",
    "graph_read",
}
PRODUCTIVE_TYPES = {"mutation", "solution_mutation", "action", "check", "verification", "blocker"}
VERIFICATION_TYPES = {"check", "verification"}
OBSERVATION_RESULTS = {"DISCRIMINATING", "INVALID", "INCONCLUSIVE"}
FULL_HISTORY_SCOPES = {"full_history", "full_task_history", "full_thread", "full_prd", "full_research"}
REPOSITORY_WIDE_SCOPES = {"repository_wide", "workspace_wide", "full_repository", "full_workspace"}
RUNTIME_CONTENT_CLASSES = {
    "runtime",
    "progress",
    "stage_progress",
    "test_count",
    "test_counts",
    "test_log",
    "todo",
    "checklist",
    "attempt_history",
    "stage_summary",
    "timeline",
    "temporary_next",
}


def _strings(value: Any) -> set[str]:
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        return {item for item in value if isinstance(item, str)}
    return set()


def _event_action_id(event: dict[str, Any]) -> str | None:
    value = event.get("action_id")
    return value if isinstance(value, str) and value else None


def _observation_key(event: dict[str, Any]) -> tuple[str, str] | None:
    observation_id = event.get("observation_id")
    revision = event.get("observation_revision")
    if not isinstance(observation_id, str) or not observation_id:
        return None
    if not isinstance(revision, str) or not revision:
        return None
    return observation_id, revision


def _graph_relevance(event: dict[str, Any], expected_fingerprint: str | None) -> list[str]:
    reasons: list[str] = []
    for field in ("decision_question", "task_anchor"):
        if not isinstance(event.get(field), str) or not event[field].strip():
            reasons.append(f"missing_{field}")
    graph_fingerprint = event.get("graph_source_fingerprint") or event.get("source_fingerprint")
    task_fingerprint = event.get("task_source_fingerprint") or expected_fingerprint
    if task_fingerprint and graph_fingerprint != task_fingerprint:
        reasons.append("source_fingerprint_mismatch")
    task_languages = _strings(event.get("task_languages"))
    graph_languages = _strings(event.get("graph_languages"))
    if task_languages and (not graph_languages or task_languages.isdisjoint(graph_languages)):
        reasons.append("target_language_mismatch")
    task_scope = _strings(event.get("task_scope"))
    graph_scope = _strings(event.get("graph_scope"))
    if task_scope and (not graph_scope or task_scope.isdisjoint(graph_scope)):
        reasons.append("task_scope_mismatch")
    return reasons


def evaluate_trace(trace: dict[str, Any], inherited: dict[str, Any] | None = None) -> dict[str, Any]:
    inherited = inherited or {}
    events = trace.get("events", [])
    if not isinstance(events, list):
        raise ValueError("events must be a list")
    expected_action_id = trace.get("expected_action_id", inherited.get("expected_action_id"))
    expected_fingerprint = trace.get("source_fingerprint", inherited.get("source_fingerprint"))
    required_constraints = _strings(trace.get("required_constraint_ids", inherited.get("required_constraint_ids", [])))
    required_evidence = _strings(trace.get("required_evidence_ids", inherited.get("required_evidence_ids", [])))
    requires_observation_evidence = trace.get(
        "requires_discriminating_evidence",
        inherited.get("requires_discriminating_evidence", False),
    ) is True

    read_keys: list[tuple[str, str, str]] = []
    productive: list[tuple[int, dict[str, Any]]] = []
    verification_keys: list[tuple[str, str, str, str]] = []
    route_deviations: list[int] = []
    full_history_reads = 0
    repository_wide_reads = 0
    authoritative_runtime_leaks: list[dict[str, Any]] = []
    irrelevant_graph_injections: list[dict[str, Any]] = []
    observed_constraints: set[str] = set()
    observed_evidence: set[str] = set()
    recovery_cycles: dict[str, dict[str, Any]] = {}
    observation_results: dict[tuple[str, str], str] = {}
    latest_observation_revision: dict[str, str] = {}
    nondiscriminating_results: dict[str, int] = {}
    observation_repairs: dict[str, int] = {}
    observation_counts = {result: 0 for result in OBSERVATION_RESULTS}
    solution_change_count = 0
    solution_without_evidence: list[int] = []
    invalid_observation_used: list[int] = []
    repeated_nondiscriminating: list[int] = []
    observation_repair_budget_exceeded: list[int] = []
    solution_change_before_snapshot: list[int] = []
    snapshot_refresh_pending = False

    for index, raw_event in enumerate(events):
        if not isinstance(raw_event, dict):
            continue
        event = raw_event
        event_type = str(event.get("type", ""))
        turn = event.get("turn", index + 1)
        observed_constraints.update(_strings(event.get("constraint_ids")))
        observed_evidence.update(_strings(event.get("evidence_ids")))
        recovery_id = event.get("recovery_id")
        if isinstance(recovery_id, str) and recovery_id:
            cycle = recovery_cycles.setdefault(recovery_id, {"events": 0, "productive": False, "turns": set()})
            cycle["events"] += 1
            cycle["turns"].add(turn)

        is_productive = event.get("productive") is True or (
            event_type in PRODUCTIVE_TYPES and event.get("productive") is not False
        )
        if is_productive:
            productive.append((index, event))
            if isinstance(recovery_id, str) and recovery_id:
                recovery_cycles[recovery_id]["productive"] = True
            if event.get("serves_next") is False:
                route_deviations.append(index)

        if event_type in READ_TYPES:
            target = str(event.get("target", "<unknown>"))
            revision = str(event.get("revision") or event.get("source_fingerprint") or "<unknown>")
            scope = str(event.get("scope", "bounded"))
            read_keys.append((target, revision, scope))
            if scope in FULL_HISTORY_SCOPES or event.get("full_history") is True:
                full_history_reads += 1
            if scope in REPOSITORY_WIDE_SCOPES or event.get("repository_wide") is True:
                repository_wide_reads += 1

        if event_type in VERIFICATION_TYPES:
            verification_keys.append(
                (
                    str(event.get("check_id") or event.get("target") or "<unknown>"),
                    str(event.get("source_fingerprint") or "<unknown>"),
                    str(event.get("input_revision") or "<unknown>"),
                    str(event.get("environment") or "<unknown>"),
                )
            )

        if event_type == "observation_result":
            key = _observation_key(event)
            result = str(event.get("result", "")).upper()
            if key is not None and result in OBSERVATION_RESULTS:
                observation_results[key] = result
                latest_observation_revision[key[0]] = key[1]
                observation_counts[result] += 1
                if result in {"INVALID", "INCONCLUSIVE"}:
                    nondiscriminating_results[key[0]] = nondiscriminating_results.get(key[0], 0) + 1
                    if nondiscriminating_results[key[0]] > 1:
                        repeated_nondiscriminating.append(index)
                else:
                    nondiscriminating_results[key[0]] = 0
            if event.get("changes_decision_state") is True:
                snapshot_refresh_pending = True

        if event_type == "observation_apparatus_changed":
            observation_id = event.get("observation_id")
            if isinstance(observation_id, str) and observation_id:
                observation_repairs[observation_id] = observation_repairs.get(observation_id, 0) + 1
                if observation_repairs[observation_id] > 1:
                    observation_repair_budget_exceeded.append(index)

        if event_type == "snapshot_refreshed":
            snapshot_refresh_pending = False

        purpose = event.get("purpose")
        is_solution_change = (
            event_type == "solution_mutation"
            or event.get("solution_change") is True
            or purpose == "solution"
            or (
                requires_observation_evidence
                and event_type in {"mutation", "action"}
                and purpose not in {"observation_setup", "observation_repair"}
            )
        )
        if is_solution_change:
            solution_change_count += 1
            if snapshot_refresh_pending:
                solution_change_before_snapshot.append(index)
            requires_evidence = event.get("requires_discriminating_evidence", requires_observation_evidence) is True
            if requires_evidence:
                key = _observation_key(event)
                if key is None:
                    observation_id = event.get("observation_id")
                    revision = latest_observation_revision.get(observation_id) if isinstance(observation_id, str) else None
                    key = (observation_id, revision) if observation_id and revision else None
                result = observation_results.get(key) if key is not None else None
                if result != "DISCRIMINATING":
                    solution_without_evidence.append(index)
                if result == "INVALID":
                    invalid_observation_used.append(index)

        if event_type in {"authoritative_doc_write", "prd_write"}:
            leaked = sorted(_strings(event.get("content_classes")) & RUNTIME_CONTENT_CLASSES)
            if leaked:
                authoritative_runtime_leaks.append({"event_index": index, "classes": leaked})

        if event_type in {"graph_injection", "graph_read"}:
            reasons = _graph_relevance(event, expected_fingerprint)
            if reasons:
                irrelevant_graph_injections.append({"event_index": index, "reasons": reasons})

    repeated_reads = len(read_keys) - len(set(read_keys))
    repeated_verifications = len(verification_keys) - len(set(verification_keys))
    first_index = productive[0][0] if productive else None
    first_event = productive[0][1] if productive else None
    first_turn = first_event.get("turn", first_index + 1) if first_event is not None else None
    first_action_id = _event_action_id(first_event) if first_event is not None else None
    next_action_hit = expected_action_id is None or first_action_id == expected_action_id
    if expected_action_id is not None and first_event is not None and not next_action_hit:
        route_deviations.append(first_index)
    idle_cycles = sorted(key for key, value in recovery_cycles.items() if not value["productive"])
    missing_constraints = sorted(required_constraints - observed_constraints)
    missing_evidence = sorted(required_evidence - observed_evidence)
    discriminating_count = observation_counts["DISCRIMINATING"]
    actions_per_discriminating_observation = (
        len(productive) / discriminating_count if discriminating_count else None
    )

    return {
        "event_count": len(events),
        "first_productive_action_event": first_index,
        "first_productive_action_turn": first_turn,
        "first_action_id": first_action_id,
        "next_action_hit": next_action_hit,
        "read_event_count": len(read_keys),
        "distinct_read_count": len(set(read_keys)),
        "repeated_read_count": repeated_reads,
        "full_history_read_count": full_history_reads,
        "repository_wide_read_count": repository_wide_reads,
        "verification_count": len(verification_keys),
        "repeated_verification_count": repeated_verifications,
        "route_deviation_count": len(set(route_deviations)),
        "route_deviation_events": sorted(set(route_deviations)),
        "idle_recovery_count": len(idle_cycles),
        "idle_recovery_ids": idle_cycles,
        "authoritative_runtime_leak_count": len(authoritative_runtime_leaks),
        "authoritative_runtime_leaks": authoritative_runtime_leaks,
        "irrelevant_graph_injection_count": len(irrelevant_graph_injections),
        "irrelevant_graph_injections": irrelevant_graph_injections,
        "observed_constraint_ids": sorted(observed_constraints),
        "missing_constraint_ids": missing_constraints,
        "observed_evidence_ids": sorted(observed_evidence),
        "missing_evidence_ids": missing_evidence,
        "required_context_complete": not missing_constraints and not missing_evidence,
        "observation_result_count": sum(observation_counts.values()),
        "discriminating_observation_count": discriminating_count,
        "invalid_observation_count": observation_counts["INVALID"],
        "inconclusive_observation_count": observation_counts["INCONCLUSIVE"],
        "solution_change_count": solution_change_count,
        "solution_change_without_discriminating_evidence_count": len(solution_without_evidence),
        "solution_change_without_discriminating_evidence_events": solution_without_evidence,
        "invalid_observation_used_as_evidence_count": len(invalid_observation_used),
        "invalid_observation_used_as_evidence_events": invalid_observation_used,
        "repeated_nondiscriminating_observation_count": len(repeated_nondiscriminating),
        "repeated_nondiscriminating_observation_events": repeated_nondiscriminating,
        "observation_repair_budget_exceeded_count": len(observation_repair_budget_exceeded),
        "observation_repair_budget_exceeded_events": observation_repair_budget_exceeded,
        "solution_change_before_snapshot_refresh_count": len(solution_change_before_snapshot),
        "solution_change_before_snapshot_refresh_events": solution_change_before_snapshot,
        "productive_actions_per_discriminating_observation": actions_per_discriminating_observation,
    }


def evaluate_document(document: Any) -> dict[str, Any]:
    if not isinstance(document, dict):
        raise ValueError("trace document must be an object")
    raw_runs = document.get("runs")
    if raw_runs is None:
        return {"runs": {str(document.get("name", "trace")): evaluate_trace(document)}}
    if not isinstance(raw_runs, dict) or not raw_runs:
        raise ValueError("runs must be a non-empty object")
    inherited = {
        key: document[key]
        for key in (
            "expected_action_id",
            "source_fingerprint",
            "required_constraint_ids",
            "required_evidence_ids",
            "requires_discriminating_evidence",
        )
        if key in document
    }
    runs = {
        name: evaluate_trace(trace, inherited)
        for name, trace in raw_runs.items()
        if isinstance(name, str) and isinstance(trace, dict)
    }
    comparisons: dict[str, Any] = {}
    if "capsule" in runs:
        capsule = runs["capsule"]
        for name, metrics in runs.items():
            if name == "capsule":
                continue
            comparisons[f"capsule_vs_{name}"] = {
                "first_productive_action_turn_delta": _delta(
                    capsule["first_productive_action_turn"], metrics["first_productive_action_turn"]
                ),
                "read_event_count_delta": capsule["read_event_count"] - metrics["read_event_count"],
                "repeated_read_count_delta": capsule["repeated_read_count"] - metrics["repeated_read_count"],
                "solution_change_without_discriminating_evidence_delta": (
                    capsule["solution_change_without_discriminating_evidence_count"]
                    - metrics["solution_change_without_discriminating_evidence_count"]
                ),
                "solution_change_before_snapshot_refresh_delta": (
                    capsule["solution_change_before_snapshot_refresh_count"]
                    - metrics["solution_change_before_snapshot_refresh_count"]
                ),
                "required_context_complete": capsule["required_context_complete"],
                "other_required_context_complete": metrics["required_context_complete"],
            }
    assessment: dict[str, Any] = {}
    if "full_context" in runs and "capsule" in runs:
        assessment["capsule_preserves_required_context"] = (
            runs["full_context"]["required_context_complete"] and runs["capsule"]["required_context_complete"]
        )
        assessment["capsule_not_slower_to_first_action"] = _not_slower(
            runs["capsule"]["first_productive_action_turn"], runs["full_context"]["first_productive_action_turn"]
        )
        assessment["capsule_preserves_observation_integrity"] = (
            runs["capsule"]["solution_change_without_discriminating_evidence_count"]
            <= runs["full_context"]["solution_change_without_discriminating_evidence_count"]
            and runs["capsule"]["solution_change_before_snapshot_refresh_count"]
            <= runs["full_context"]["solution_change_before_snapshot_refresh_count"]
        )
    if "ablation" in runs:
        assessment["ablation_exposes_context_loss"] = not runs["ablation"]["required_context_complete"]
    return {"runs": runs, "comparisons": comparisons, "assessment": assessment}


def _delta(left: Any, right: Any) -> int | None:
    return left - right if isinstance(left, int) and isinstance(right, int) else None


def _not_slower(left: Any, right: Any) -> bool:
    return isinstance(left, int) and isinstance(right, int) and left <= right


def _load(path: Path | None) -> Any:
    if path is None or str(path) == "-":
        return json.load(sys.stdin)
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trace", nargs="?", type=Path, help="JSON trace file; omit or use - for stdin")
    parser.add_argument("--json", action="store_true", help="emit JSON (the default; retained for adapter clarity)")
    args = parser.parse_args()
    try:
        result = evaluate_document(_load(args.trace))
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
