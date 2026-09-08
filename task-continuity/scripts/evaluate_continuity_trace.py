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
    "reference_read",
    "rule_compare",
    "rule_reload",
    "skill_reload",
    "thread_read",
    "history_read",
    "workspace_scan",
    "graph_read",
}
PRODUCTIVE_TYPES = {"mutation", "solution_mutation", "action", "check", "verification", "blocker"}
VERIFICATION_TYPES = {"check", "verification"}
COMMENTARY_TYPES = {"commentary", "recovery_commentary"}
OBSERVATION_RESULTS = {"DISCRIMINATING", "INVALID", "INCONCLUSIVE", "SCOPE_INVALID"}
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
FULL_HISTORY_SCOPES = {"full_history", "full_task_history", "full_thread", "full_prd", "full_research"}
REPOSITORY_WIDE_SCOPES = {"repository_wide", "workspace_wide", "full_repository", "full_workspace"}
FULL_RULE_SCOPES = {"full_skill", "full_skill_set", "full_rules", "full_reference_set"}
REPLAY_RECOVERY_CLASSES = {
    "full_history_reread",
    "full_rule_reload",
    "previous_action_replay",
    "suppressed_action_replay",
    "workspace_rescan",
}
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


def _recovery_action_classes(event: dict[str, Any]) -> set[str]:
    classes = _strings(event.get("recovery_action_class")) & REPLAY_RECOVERY_CLASSES
    event_type = str(event.get("type", ""))
    scope = str(event.get("scope", "bounded"))
    if event_type in {"skill_reload", "rule_reload"} or scope in FULL_RULE_SCOPES:
        classes.add("full_rule_reload")
    if event_type == "workspace_scan" or scope in REPOSITORY_WIDE_SCOPES or event.get("repository_wide") is True:
        classes.add("workspace_rescan")
    if scope in FULL_HISTORY_SCOPES or event.get("full_history") is True:
        classes.add("full_history_reread")
    return classes


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
    pre_compaction_next_action_id = trace.get(
        "pre_compaction_next_action_id",
        inherited.get("pre_compaction_next_action_id"),
    )
    expected_action_id = trace.get(
        "expected_action_id",
        inherited.get("expected_action_id", pre_compaction_next_action_id),
    )
    if pre_compaction_next_action_id is None:
        pre_compaction_next_action_id = expected_action_id
    previous_productive_action_id = trace.get(
        "previous_productive_action_id",
        inherited.get("previous_productive_action_id"),
    )
    suppressed_action_ids = _strings(
        trace.get("suppressed_action_ids", inherited.get("suppressed_action_ids", []))
    )
    directive_revision_at_snapshot = trace.get(
        "directive_revision_at_snapshot",
        inherited.get(
            "directive_revision_at_snapshot",
            trace.get(
                "instruction_revision_at_snapshot",
                inherited.get("instruction_revision_at_snapshot"),
            ),
        ),
    )
    post_compaction_directive_revision = trace.get(
        "post_compaction_directive_revision",
        inherited.get(
            "post_compaction_directive_revision",
            trace.get(
                "post_compaction_instruction_revision",
                inherited.get("post_compaction_instruction_revision"),
            ),
        ),
    )
    explicit_directive_changed = trace.get(
        "directive_changed",
        inherited.get(
            "directive_changed",
            trace.get("instruction_changed", inherited.get("instruction_changed")),
        ),
    )
    directive_revision_compared = isinstance(explicit_directive_changed, bool) or (
        isinstance(directive_revision_at_snapshot, str)
        and isinstance(post_compaction_directive_revision, str)
    )
    if isinstance(explicit_directive_changed, bool):
        directive_changed = explicit_directive_changed
    elif isinstance(directive_revision_at_snapshot, str) and isinstance(post_compaction_directive_revision, str):
        directive_changed = directive_revision_at_snapshot != post_compaction_directive_revision
    else:
        directive_changed = None
    # Retain the old metric names for readable historical traces.
    instruction_revision_compared = directive_revision_compared
    instruction_changed = directive_changed
    conversation_cursor_at_snapshot = trace.get(
        "conversation_cursor_at_snapshot",
        inherited.get("conversation_cursor_at_snapshot"),
    )
    post_compaction_conversation_cursor = trace.get(
        "post_compaction_conversation_cursor",
        inherited.get("post_compaction_conversation_cursor"),
    )
    conversation_advanced = (
        conversation_cursor_at_snapshot != post_compaction_conversation_cursor
        if isinstance(conversation_cursor_at_snapshot, str)
        and isinstance(post_compaction_conversation_cursor, str)
        else None
    )
    expected_fingerprint = trace.get("source_fingerprint", inherited.get("source_fingerprint"))
    required_constraints = _strings(trace.get("required_constraint_ids", inherited.get("required_constraint_ids", [])))
    required_evidence = _strings(trace.get("required_evidence_ids", inherited.get("required_evidence_ids", [])))
    requires_observation_evidence = trace.get(
        "requires_discriminating_evidence",
        inherited.get("requires_discriminating_evidence", False),
    ) is True
    recovery_type = trace.get("recovery_type", inherited.get("recovery_type"))
    resume_turn = trace.get("resume_turn", inherited.get("resume_turn"))
    identity_match = trace.get("identity_match", inherited.get("identity_match")) is True
    default_matching_audit = trace.get(
        "matching_audit_number",
        inherited.get("matching_audit_number", 0),
    )

    read_keys: list[tuple[str, str, str]] = []
    productive: list[tuple[int, dict[str, Any]]] = []
    verification_keys: list[tuple[str, str, str, str]] = []
    route_deviations: list[int] = []
    recovery_route_deviations: list[dict[str, Any]] = []
    post_compaction_full_skill_reload_count = 0
    full_history_reads = 0
    full_thread_reads = 0
    repository_wide_reads = 0
    unchanged_reference_reads = 0
    matching_audit_full_reference_reads = 0
    resume_audit_tool_round_ids: set[str] = set()
    recovery_turns: dict[Any, dict[str, bool]] = {}
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
    scope_invalid_observation_used: list[int] = []
    repeated_nondiscriminating: list[int] = []
    observation_repair_budget_exceeded: list[int] = []
    solution_change_before_snapshot: list[int] = []
    snapshot_refresh_pending = False
    correct_next_seen = False
    message_route_deviations: list[dict[str, Any]] = []
    unnecessary_plan_refreshes: list[int] = []
    duplicate_reminder_revisions: list[int] = []
    missing_return_anchors: list[int] = []
    wrong_mainline_returns: list[int] = []
    stale_contract_actions: list[int] = []
    pending_return_action_id: str | None = None
    pending_return_turn: Any = None
    pending_return_ready = False
    pending_message_class: str | None = None
    mainline_invalidated = False

    for index, raw_event in enumerate(events):
        if not isinstance(raw_event, dict):
            continue
        event = raw_event
        event_type = str(event.get("type", ""))
        turn = event.get("turn", index + 1)
        turn_state = recovery_turns.setdefault(turn, {"commentary": False, "productive": False})
        if event_type in COMMENTARY_TYPES:
            turn_state["commentary"] = True

        if event_type == "user_message":
            message_class = str(event.get("message_class", ""))
            if message_class not in MESSAGE_CLASSES:
                message_route_deviations.append(
                    {"event_index": index, "class": "unclassified_user_message"}
                )
            affects_saved_next = event.get("affects_saved_next") is True
            if message_class in PASSIVE_MESSAGE_CLASSES:
                pending_message_class = message_class
                pending_return_action_id = str(
                    event.get("saved_next_action_id") or pre_compaction_next_action_id or ""
                ) or None
                pending_return_turn = turn
                pending_return_ready = True
                revision_changed = event.get("directive_changed") is True or (
                    isinstance(event.get("directive_revision_before"), str)
                    and isinstance(event.get("directive_revision_after"), str)
                    and event.get("directive_revision_before") != event.get("directive_revision_after")
                )
                if message_class == "REMINDER" and revision_changed:
                    duplicate_reminder_revisions.append(index)
                    message_route_deviations.append(
                        {"event_index": index, "class": "duplicate_reminder_revision"}
                    )
                if affects_saved_next or _strings(event.get("affected_assignment_ids")):
                    message_route_deviations.append(
                        {"event_index": index, "class": "passive_message_route_change"}
                    )
            elif message_class == "TEMPORARY_INTERRUPT":
                anchor = event.get("return_anchor")
                pending_message_class = message_class
                pending_return_ready = False
                if not isinstance(anchor, dict) or not isinstance(anchor.get("saved_next_action_id"), str):
                    missing_return_anchors.append(index)
                    message_route_deviations.append(
                        {"event_index": index, "class": "missing_return_anchor"}
                    )
                    pending_return_action_id = None
                else:
                    pending_return_action_id = anchor["saved_next_action_id"]
                    pending_return_turn = turn
            elif message_class in {"CONTRACT_CHANGE", "OVERRIDE"} or affects_saved_next:
                mainline_invalidated = True

        if event_type in {"plan_refresh", "route_refresh", "assignment_redispatch"}:
            if pending_message_class in PASSIVE_MESSAGE_CLASSES and pending_return_ready:
                unnecessary_plan_refreshes.append(index)
                message_route_deviations.append(
                    {"event_index": index, "class": "passive_message_plan_refresh"}
                )

        if event_type == "interrupt_complete" and pending_message_class == "TEMPORARY_INTERRUPT":
            pending_return_ready = True
            pending_return_turn = turn

        if event_type in {"snapshot_refreshed", "contract_snapshot_refreshed"} and event.get(
            "refreshes_user_change"
        ) is True:
            mainline_invalidated = False
        observed_constraints.update(_strings(event.get("constraint_ids")))
        observed_evidence.update(_strings(event.get("evidence_ids")))
        recovery_id = event.get("recovery_id")
        if isinstance(recovery_id, str) and recovery_id:
            cycle = recovery_cycles.setdefault(recovery_id, {"events": 0, "productive": False, "turns": set()})
            cycle["events"] += 1
            cycle["turns"].add(turn)

        event_action_id = _event_action_id(event)
        recovery_classes = _recovery_action_classes(event)
        if event_action_id in suppressed_action_ids:
            recovery_classes.add("suppressed_action_replay")
        continuity_slice_matches = (
            recovery_type == "COMPACT_CONTINUATION"
            and identity_match
            and instruction_revision_compared
            and instruction_changed is False
        )
        if continuity_slice_matches and not correct_next_seen:
            if "full_rule_reload" in recovery_classes:
                post_compaction_full_skill_reload_count += 1
            for recovery_class in sorted(recovery_classes):
                recovery_route_deviations.append(
                    {"event_index": index, "class": recovery_class}
                )
                route_deviations.append(index)
            if pending_message_class in PASSIVE_MESSAGE_CLASSES and pending_return_ready and recovery_classes:
                message_route_deviations.append(
                    {"event_index": index, "class": "passive_message_recovery_replay"}
                )

        is_productive = event.get("productive") is True or (
            event_type in PRODUCTIVE_TYPES and event.get("productive") is not False
        )
        inline_message_action = event.get("serves_user_message") is True
        if is_productive:
            if not inline_message_action:
                productive.append((index, event))
            target_action_id = pre_compaction_next_action_id or expected_action_id
            if not inline_message_action and (target_action_id is None or event_action_id == target_action_id):
                correct_next_seen = True
            turn_state["productive"] = True
            if isinstance(recovery_id, str) and recovery_id:
                recovery_cycles[recovery_id]["productive"] = True
            if event.get("serves_next") is False:
                route_deviations.append(index)
            if not inline_message_action and pending_return_ready and pending_return_action_id is not None:
                if event_action_id == pending_return_action_id:
                    if pending_message_class in PASSIVE_MESSAGE_CLASSES and turn != pending_return_turn:
                        wrong_mainline_returns.append(index)
                        message_route_deviations.append(
                            {"event_index": index, "class": "passive_message_delayed_return"}
                        )
                    pending_return_ready = False
                    pending_message_class = None
                    pending_return_action_id = None
                else:
                    wrong_mainline_returns.append(index)
                    message_route_deviations.append(
                        {"event_index": index, "class": "wrong_mainline_return"}
                    )
            if mainline_invalidated and event_type in {"mutation", "solution_mutation", "action"}:
                stale_contract_actions.append(index)
                message_route_deviations.append(
                    {"event_index": index, "class": "stale_contract_action"}
                )

        if event_type in READ_TYPES:
            target = str(event.get("target", "<unknown>"))
            revision = str(event.get("revision") or event.get("source_fingerprint") or "<unknown>")
            scope = str(event.get("scope", "bounded"))
            read_keys.append((target, revision, scope))
            if scope in FULL_HISTORY_SCOPES or event.get("full_history") is True:
                full_history_reads += 1
            target_kind = str(event.get("target_kind", ""))
            is_reference_read = event_type in {"reference_read", "thread_read", "history_read"} or target_kind in {
                "thread",
                "task",
                "issue",
                "reference",
                "research",
            }
            is_full_reference_read = scope in FULL_HISTORY_SCOPES or event.get("full_history") is True
            if scope == "full_thread" or (target_kind == "thread" and is_full_reference_read):
                full_thread_reads += 1
            revision_unchanged = (
                event.get("revision_changed") is False
                or event.get("cursor_changed") is False
                or event.get("reference_unchanged") is True
            )
            if is_reference_read and revision_unchanged:
                unchanged_reference_reads += 1
            matching_audit_number = event.get("matching_audit_number", default_matching_audit)
            if (
                is_reference_read
                and is_full_reference_read
                and isinstance(matching_audit_number, int)
                and matching_audit_number >= 2
            ):
                matching_audit_full_reference_reads += 1
            if scope in REPOSITORY_WIDE_SCOPES or event.get("repository_wide") is True:
                repository_wide_reads += 1
            in_resume_audit = (
                event.get("resume_audit") is True
                or event.get("continuity_phase") == "RESUME_AUDIT"
                or event.get("phase") == "RESUME_AUDIT"
            )
            if in_resume_audit:
                tool_round = event.get("tool_round", turn)
                resume_audit_tool_round_ids.add(str(tool_round))

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
                if result == "SCOPE_INVALID":
                    scope_invalid_observation_used.append(index)

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
    action_identity_continuity_applicable = (
        recovery_type == "COMPACT_CONTINUATION"
        and identity_match
        and instruction_revision_compared
        and instruction_changed is False
        and pre_compaction_next_action_id is not None
    )
    action_identity_continuity = (
        first_action_id == pre_compaction_next_action_id
        if action_identity_continuity_applicable and first_action_id is not None
        else None
    )
    next_action_hit = expected_action_id is None or first_action_id == expected_action_id
    if action_identity_continuity_applicable and first_event is not None and action_identity_continuity is False:
        route_deviations.append(first_index)
    elif expected_action_id is not None and first_event is not None and not next_action_hit and instruction_changed is not True:
        route_deviations.append(first_index)
    previous_action_replay = (
        action_identity_continuity_applicable
        and isinstance(previous_productive_action_id, str)
        and first_action_id == previous_productive_action_id
        and first_action_id != pre_compaction_next_action_id
    )
    if previous_action_replay and first_index is not None:
        recovery_route_deviations.append(
            {"event_index": first_index, "class": "previous_action_replay"}
        )
        route_deviations.append(first_index)
    if pending_return_ready and pending_return_action_id is not None:
        message_route_deviations.append(
            {"event_index": len(events), "class": "mainline_return_missing"}
        )
    idle_cycles = sorted(key for key, value in recovery_cycles.items() if not value["productive"])
    missing_constraints = sorted(required_constraints - observed_constraints)
    missing_evidence = sorted(required_evidence - observed_evidence)
    discriminating_count = observation_counts["DISCRIMINATING"]
    actions_per_discriminating_observation = (
        len(productive) / discriminating_count if discriminating_count else None
    )
    recovery_commentary_only_turns = sum(
        1 for value in recovery_turns.values() if value["commentary"] and not value["productive"]
    )
    first_productive_action_on_resume_turn = (
        first_turn == resume_turn if resume_turn is not None and first_turn is not None else None
    )
    compact_fast_path_applicable = (
        recovery_type == "COMPACT_CONTINUATION"
        and identity_match
        and instruction_revision_compared
        and instruction_changed is False
    )
    compact_fast_path_passed = None
    if compact_fast_path_applicable:
        compact_fast_path_passed = (
            len(resume_audit_tool_round_ids) <= 1
            and instruction_revision_compared
            and full_thread_reads == 0
            and unchanged_reference_reads == 0
            and recovery_commentary_only_turns == 0
            and first_productive_action_on_resume_turn is True
            and matching_audit_full_reference_reads == 0
            and action_identity_continuity is True
            and not recovery_route_deviations
        )

    invariant_violations = []
    for label, failed in (
        ("action_identity", action_identity_continuity is False),
        ("required_context", bool(missing_constraints or missing_evidence)),
        ("stale_contract_action", bool(stale_contract_actions)),
        ("wrong_mainline_return", bool(wrong_mainline_returns)),
        ("missing_return_anchor", bool(missing_return_anchors)),
        ("invalid_observation_evidence", bool(invalid_observation_used or scope_invalid_observation_used)),
        ("solution_without_evidence", bool(solution_without_evidence)),
        ("solution_before_snapshot", bool(solution_change_before_snapshot)),
    ):
        if failed:
            invariant_violations.append(label)
    return {
        "event_count": len(events),
        "observed_invariants_passed": not invariant_violations,
        "invariant_violations": invariant_violations,
        "acceptance_success": trace.get("acceptance_success"),
        "efficiency_targets": {"compact_fast_path_met": compact_fast_path_passed},
        "metric_semantics": "Efficiency targets and legacy compact_continuation_fast_path_passed do not determine correctness or business acceptance.",
        "first_productive_action_event": first_index,
        "first_productive_action_turn": first_turn,
        "first_action_id": first_action_id,
        "pre_compaction_next_action_id": pre_compaction_next_action_id,
        "post_compaction_first_productive_action_id": first_action_id,
        "previous_productive_action_id": previous_productive_action_id,
        "instruction_changed": instruction_changed,
        "instruction_revision_compared": instruction_revision_compared,
        "directive_changed": directive_changed,
        "directive_revision_compared": directive_revision_compared,
        "conversation_advanced": conversation_advanced,
        "action_identity_continuity_applicable": action_identity_continuity_applicable,
        "action_identity_continuity": action_identity_continuity,
        "previous_action_replay_count": 1 if previous_action_replay else 0,
        "next_action_hit": next_action_hit,
        "read_event_count": len(read_keys),
        "distinct_read_count": len(set(read_keys)),
        "repeated_read_count": repeated_reads,
        "full_history_read_count": full_history_reads,
        "full_thread_reads": full_thread_reads,
        "repository_wide_read_count": repository_wide_reads,
        "unchanged_reference_reads": unchanged_reference_reads,
        "matching_audit_full_reference_reads": matching_audit_full_reference_reads,
        "resume_audit_tool_rounds": len(resume_audit_tool_round_ids),
        "recovery_commentary_only_turns": recovery_commentary_only_turns,
        "resume_turn": resume_turn,
        "first_productive_action_on_resume_turn": first_productive_action_on_resume_turn,
        "compact_continuation_fast_path_applicable": compact_fast_path_applicable,
        "compact_continuation_fast_path_passed": compact_fast_path_passed,
        "verification_count": len(verification_keys),
        "repeated_verification_count": repeated_verifications,
        "route_deviation_count": len(set(route_deviations)),
        "route_deviation_events": sorted(set(route_deviations)),
        "message_route_deviation_count": len(message_route_deviations),
        "message_route_deviations": message_route_deviations,
        "unnecessary_plan_refresh_count": len(unnecessary_plan_refreshes),
        "duplicate_reminder_revision_count": len(duplicate_reminder_revisions),
        "missing_return_anchor_count": len(missing_return_anchors),
        "wrong_mainline_return_count": len(wrong_mainline_returns),
        "stale_contract_action_count": len(stale_contract_actions),
        "recovery_route_deviation_count": len(recovery_route_deviations),
        "recovery_route_deviations": recovery_route_deviations,
        "post_compaction_full_skill_reload_count": post_compaction_full_skill_reload_count,
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
        "scope_invalid_observation_count": observation_counts["SCOPE_INVALID"],
        "solution_change_count": solution_change_count,
        "solution_change_without_discriminating_evidence_count": len(solution_without_evidence),
        "solution_change_without_discriminating_evidence_events": solution_without_evidence,
        "invalid_observation_used_as_evidence_count": len(invalid_observation_used),
        "invalid_observation_used_as_evidence_events": invalid_observation_used,
        "scope_invalid_observation_used_as_evidence_count": len(scope_invalid_observation_used),
        "scope_invalid_observation_used_as_evidence_events": scope_invalid_observation_used,
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
            "pre_compaction_next_action_id",
            "previous_productive_action_id",
            "suppressed_action_ids",
            "instruction_revision_at_snapshot",
            "post_compaction_instruction_revision",
            "instruction_changed",
            "directive_revision_at_snapshot",
            "post_compaction_directive_revision",
            "directive_changed",
            "conversation_cursor_at_snapshot",
            "post_compaction_conversation_cursor",
            "source_fingerprint",
            "required_constraint_ids",
            "required_evidence_ids",
            "requires_discriminating_evidence",
            "recovery_type",
            "resume_turn",
            "identity_match",
            "matching_audit_number",
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
