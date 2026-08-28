#!/usr/bin/env python3
"""Evaluate normalized semantic-fork and investigation-budget traces."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


FORK_STATUSES = {"NOT_APPLICABLE", "OPEN", "RESOLVED"}
EVIDENCE_RESULTS = {
    "PLANNED",
    "DISCRIMINATING",
    "INVALID",
    "INCONCLUSIVE",
    "SCOPE_INVALID",
}
SUPPORTED_OUTCOMES = {"NONE", "FREEZE", "ASK_USER", "BLOCKER"}
STOP_REASONS = {
    "FREEZE",
    "ASK_USER",
    "BLOCKER",
    "INVALID_OBSERVATION",
    "SOURCE_DRIFT",
    "HIGH_RISK_GAP",
}
REOPEN_REASONS = {
    "NEW_CANDIDATE",
    "INVALID_OBSERVATION",
    "SOURCE_DRIFT",
    "HIGH_RISK_GAP",
}
ACTION_CLASSES = {
    "RUNTIME_NOTE",
    "MINIMAL_SYSTEM_MAP",
    "USER_QUESTION",
    "BLOCKER_REPORT",
    "CONTRACT_FREEZE",
    "AUTHORITATIVE_DESIGN",
    "API_DEEPENING",
    "PRODUCTION_IMPLEMENTATION",
    "CANDIDATE_REVIEW",
}
OPEN_FORBIDDEN_ACTIONS = {
    "CONTRACT_FREEZE",
    "AUTHORITATIVE_DESIGN",
    "API_DEEPENING",
    "PRODUCTION_IMPLEMENTATION",
    "CANDIDATE_REVIEW",
}
DESIGN_OR_IMPLEMENTATION_ACTIONS = {
    "CONTRACT_FREEZE",
    "AUTHORITATIVE_DESIGN",
    "API_DEEPENING",
    "PRODUCTION_IMPLEMENTATION",
}
INVESTIGATION_FIELDS = {
    "id",
    "mode",
    "round",
    "decision",
    "hypothesis",
    "discriminator",
    "scope",
    "stop_condition",
    "result",
}


def _nonempty(value: Any) -> bool:
    return value not in (None, "", [], {})


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _enum(value: Any, allowed: set[str]) -> bool:
    return isinstance(value, str) and value in allowed


def _strings(value: Any) -> list[str]:
    if (
        not isinstance(value, list)
        or any(not _nonempty_string(item) for item in value)
        or len(set(value)) != len(value)
    ):
        return []
    return [item.strip() for item in value]


def _validate_semantic_fork(value: Any, errors: list[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append("semantic_fork must be an object")
        return {
            "decision_question": "",
            "status": "OPEN",
            "evidence_can_decide": "unknown",
            "options": [],
            "architectural_consequences": {},
        }

    if not _nonempty_string(value.get("decision_question")):
        errors.append("semantic_fork.decision_question must be a nonempty string")
    for field in ("status", "evidence_can_decide"):
        if field not in value or not _nonempty(value.get(field)):
            errors.append(f"semantic_fork.{field} must be nonempty")
    for field in ("options", "architectural_consequences"):
        if field not in value:
            errors.append(f"semantic_fork.{field} must be present")

    status = value.get("status")
    if not _enum(status, FORK_STATUSES):
        errors.append("semantic_fork.status is invalid")
        status = "OPEN"
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
        key: item
        for key, item in consequences.items()
        if _nonempty_string(key) and _nonempty_string(item)
    }
    if status in {"OPEN", "RESOLVED"}:
        if len(options) < 2:
            errors.append(f"semantic_fork.status={status} requires at least two options")
        if not material_consequences:
            errors.append(f"semantic_fork.status={status} requires a material architectural consequence")
    elif status == "NOT_APPLICABLE" and len(options) >= 2 and material_consequences:
        errors.append(
            "semantic_fork cannot be NOT_APPLICABLE when multiple material contract options are declared"
        )

    if status == "RESOLVED":
        resolution = value.get("resolution")
        if not isinstance(resolution, dict):
            errors.append("semantic_fork.status=RESOLVED requires resolution")
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
    elif value.get("resolution") is not None:
        errors.append("semantic_fork.resolution is valid only when status=RESOLVED")

    return {
        "decision_question": str(value.get("decision_question", "")),
        "status": status,
        "evidence_can_decide": evidence_can_decide,
        "options": options,
        "architectural_consequences": consequences,
    }


def _validate_evidence_budget(value: Any, errors: list[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append("evidence_budget must be an object")
        return {"round": 1, "scout_count": 0, "status": "OPEN", "stop_reason": None}

    round_number = value.get("round")
    scout_count = value.get("scout_count")
    status = value.get("status")
    if not isinstance(round_number, int) or isinstance(round_number, bool) or round_number < 1:
        errors.append("evidence_budget.round must be a positive integer")
        round_number = 1
    if not isinstance(scout_count, int) or isinstance(scout_count, bool) or scout_count < 0:
        errors.append("evidence_budget.scout_count must be a nonnegative integer")
        scout_count = 0
    if not _enum(status, {"OPEN", "STOPPED"}):
        errors.append("evidence_budget.status must be OPEN or STOPPED")
        status = "OPEN"
    stop_reason = value.get("stop_reason")
    if status == "STOPPED" and not _enum(stop_reason, STOP_REASONS):
        errors.append("evidence_budget.status=STOPPED requires a valid stop_reason")
    if status == "OPEN" and stop_reason is not None:
        errors.append("evidence_budget.status=OPEN must not declare stop_reason")
    return {
        "round": round_number,
        "scout_count": scout_count,
        "status": status,
        "stop_reason": stop_reason,
    }


def evaluate_trace(trace: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    fork = _validate_semantic_fork(trace.get("semantic_fork"), errors)
    budget = _validate_evidence_budget(trace.get("evidence_budget"), errors)
    events = trace.get("events")
    if not isinstance(events, list):
        return {
            "passed": False,
            "errors": errors + ["events must be a list"],
            "warnings": warnings,
            "metrics": {},
        }

    policy = trace.get("budget_policy", {})
    if not isinstance(policy, dict):
        errors.append("budget_policy must be an object when present")
        policy = {}
    max_investigations = policy.get("max_investigations_per_round", 2)
    if not isinstance(max_investigations, int) or max_investigations < 1:
        errors.append("budget_policy.max_investigations_per_round must be a positive integer")
        max_investigations = 2
    if max_investigations > 2:
        override = policy.get("override")
        if not (
            isinstance(override, dict)
            and override.get("reason") == "HIGH_RISK_GAP"
            and _nonempty_string(override.get("locator"))
        ):
            errors.append(
                "a budget above two investigations requires a structured HIGH_RISK_GAP override with locator"
            )
        if max_investigations > 3:
            errors.append(
                "a HIGH_RISK_GAP override may add at most one complementary investigation to a round"
            )

    evidence: dict[str, dict[str, Any]] = {}
    user_decisions: dict[str, dict[str, Any]] = {}
    investigations_by_round: dict[int, int] = {budget["round"]: budget["scout_count"]}
    sufficient_outcome: str | None = None
    sufficient_evidence_id: str | None = None
    sufficient_result: str | None = None
    investigations = 0
    scouts = 0
    scope_invalid_evidence_count = 0
    investigations_after_budget_stop = 0
    scout_rounds_after_sufficient: set[int] = set()
    scout_rounds_after_discriminating: set[int] = set()
    unresolved_before_design = 0
    authoritative_writes_before_contract_freeze = 0
    candidate_reviews_while_open = 0
    invalid_resolution_count = 0
    budget_reopens = 0
    invalid_observation_reopens = 0
    user_questions = 0
    blocker_reports = 0
    completed_investigations_in_current_round = 0

    for index, raw_event in enumerate(events):
        if not isinstance(raw_event, dict):
            errors.append(f"event[{index}] must be an object")
            continue
        event = raw_event
        event_type = event.get("type")

        if event_type == "investigation":
            investigations += 1
            missing = sorted(field for field in INVESTIGATION_FIELDS if not _nonempty(event.get(field)))
            if missing:
                errors.append(f"event[{index}] investigation missing: {', '.join(missing)}")
            mode = event.get("mode")
            if not _enum(mode, {"OBSERVATION", "SCOUT"}):
                errors.append(f"event[{index}] investigation.mode must be OBSERVATION or SCOUT")
            elif mode == "SCOUT":
                scouts += 1
            event_round = event.get("round")
            if event_round != budget["round"]:
                errors.append(
                    f"event[{index}] investigation.round must match current evidence budget round"
                )
            if fork["status"] == "OPEN" and event.get("decision") != fork["decision_question"]:
                errors.append(
                    f"event[{index}] investigation.decision must match the open SemanticFork question"
                )
            if not isinstance(event.get("scope"), list) or not _strings(event.get("scope")):
                errors.append(f"event[{index}] investigation.scope must be a nonempty string list")
            if budget["status"] != "OPEN":
                investigations_after_budget_stop += 1
                errors.append(f"event[{index}] investigation occurs after EvidenceBudget stopped")
            if sufficient_outcome is not None:
                scout_rounds_after_sufficient.add(int(event_round) if isinstance(event_round, int) else -1)
                if sufficient_result == "DISCRIMINATING":
                    scout_rounds_after_discriminating.add(
                        int(event_round) if isinstance(event_round, int) else -1
                    )
                errors.append(
                    f"event[{index}] investigation occurs after evidence already supports {sufficient_outcome}"
                )

            if isinstance(event_round, int):
                investigations_by_round[event_round] = investigations_by_round.get(event_round, 0) + 1
                budget["scout_count"] = investigations_by_round[event_round]
                if investigations_by_round[event_round] > max_investigations:
                    errors.append(
                        f"event[{index}] round {event_round} exceeds investigation budget {max_investigations}"
                    )

            result = event.get("result")
            if not _enum(result, EVIDENCE_RESULTS):
                errors.append(f"event[{index}] investigation.result is invalid")
            elif result != "PLANNED":
                completed_investigations_in_current_round += 1
            raw_evidence_id = event.get("evidence_id")
            evidence_id = raw_evidence_id.strip() if _nonempty_string(raw_evidence_id) else ""
            if result != "PLANNED" and not evidence_id:
                errors.append(f"event[{index}] completed investigation requires evidence_id")
            elif evidence_id:
                if evidence_id in evidence:
                    errors.append(f"event[{index}] duplicates evidence_id {evidence_id!r}")
                evidence[evidence_id] = event

            supports = event.get("supports", "NONE")
            if not _enum(supports, SUPPORTED_OUTCOMES):
                errors.append(f"event[{index}] investigation.supports is invalid")
            if _enum(result, {"INVALID", "INCONCLUSIVE", "PLANNED"}) and supports != "NONE":
                errors.append(f"event[{index}] {result} evidence cannot support {supports}")
            if result == "SCOPE_INVALID":
                scope_invalid_evidence_count += 1
                if not _enum(supports, {"NONE", "ASK_USER"}):
                    errors.append(
                        f"event[{index}] SCOPE_INVALID evidence cannot support {supports}"
                    )
            if supports == "FREEZE" and fork["status"] == "OPEN" and fork["evidence_can_decide"] is False:
                errors.append(
                    f"event[{index}] evidence cannot support FREEZE when evidence_can_decide=false"
                )
            if _enum(supports, {"FREEZE", "ASK_USER", "BLOCKER"}):
                sufficient_outcome = str(supports)
                sufficient_evidence_id = evidence_id or None
                sufficient_result = str(result)

        elif event_type == "budget_stop":
            reason = event.get("reason")
            if not _enum(reason, STOP_REASONS):
                errors.append(f"event[{index}] budget_stop.reason is invalid")
            if budget["status"] == "STOPPED":
                errors.append(f"event[{index}] EvidenceBudget is already stopped")
            cited_ids = _strings(event.get("evidence_ids"))
            if _enum(reason, {"FREEZE", "ASK_USER", "BLOCKER"}):
                if not cited_ids:
                    errors.append(f"event[{index}] budget_stop {reason} requires evidence_ids")
                if sufficient_outcome != reason:
                    errors.append(
                        f"event[{index}] budget_stop {reason} lacks a matching sufficient investigation"
                    )
                if sufficient_evidence_id and sufficient_evidence_id not in cited_ids:
                    errors.append(
                        f"event[{index}] budget_stop does not cite the sufficient evidence"
                    )
                for evidence_id in cited_ids:
                    if evidence_id not in evidence:
                        errors.append(f"event[{index}] cites unknown evidence {evidence_id!r}")
            if reason == "FREEZE":
                for evidence_id in cited_ids:
                    item = evidence.get(evidence_id)
                    if item is not None and item.get("result") != "DISCRIMINATING":
                        errors.append(
                            f"event[{index}] FREEZE requires DISCRIMINATING evidence, got {item.get('result')}"
                        )
            if reason == "INVALID_OBSERVATION":
                if not cited_ids:
                    errors.append(
                        f"event[{index}] INVALID_OBSERVATION stop requires evidence_ids"
                    )
                for evidence_id in cited_ids:
                    item = evidence.get(evidence_id)
                    if item is None:
                        errors.append(f"event[{index}] cites unknown evidence {evidence_id!r}")
                    elif item.get("round") != budget["round"] or item.get("result") != "INVALID":
                        errors.append(
                            f"event[{index}] INVALID_OBSERVATION must cite INVALID evidence from current round"
                        )
            budget["status"] = "STOPPED"
            budget["stop_reason"] = reason
            sufficient_outcome = None
            sufficient_evidence_id = None
            sufficient_result = None

        elif event_type == "budget_reopen":
            budget_reopens += 1
            reason = event.get("reason")
            if budget["status"] != "STOPPED":
                errors.append(f"event[{index}] budget_reopen requires a stopped budget")
            if not _enum(reason, REOPEN_REASONS):
                errors.append(f"event[{index}] budget_reopen.reason is invalid")
            if not _nonempty_string(event.get("locator")):
                errors.append(f"event[{index}] budget_reopen requires locator")
            if reason == "INVALID_OBSERVATION" and budget.get("stop_reason") != "INVALID_OBSERVATION":
                errors.append(
                    f"event[{index}] INVALID_OBSERVATION reopen requires that stop reason"
                )
            if reason == "INVALID_OBSERVATION":
                invalid_observation_reopens += 1
                if invalid_observation_reopens > 1:
                    errors.append(
                        f"event[{index}] INVALID_OBSERVATION permits only one observation-apparatus reopen"
                    )
            next_round = event.get("round")
            if next_round != budget["round"] + 1:
                errors.append(f"event[{index}] budget_reopen.round must increment by one")
            if isinstance(next_round, int):
                budget["round"] = next_round
                investigations_by_round.setdefault(next_round, 0)
            budget["scout_count"] = 0
            budget["status"] = "OPEN"
            budget["stop_reason"] = None
            sufficient_outcome = None
            sufficient_evidence_id = None
            sufficient_result = None
            completed_investigations_in_current_round = 0

        elif event_type == "user_decision":
            raw_decision_id = event.get("id")
            decision_id = raw_decision_id.strip() if _nonempty_string(raw_decision_id) else ""
            if not decision_id or not _nonempty_string(event.get("decision")) or not _nonempty_string(event.get("locator")):
                errors.append(f"event[{index}] user_decision requires id, decision, and locator")
            elif decision_id in user_decisions:
                errors.append(f"event[{index}] duplicates user_decision id {decision_id!r}")
            else:
                user_decisions[decision_id] = event

        elif event_type == "fork_resolution":
            source = event.get("source")
            resolution_valid = True
            if fork["status"] != "OPEN":
                invalid_resolution_count += 1
                resolution_valid = False
                errors.append(f"event[{index}] fork_resolution requires SemanticFork=OPEN")
            if not _enum(source, {"EVIDENCE", "USER"}):
                invalid_resolution_count += 1
                resolution_valid = False
                errors.append(f"event[{index}] fork_resolution.source is invalid")
            if not _nonempty_string(event.get("decision")) or not _nonempty_string(event.get("locator")):
                invalid_resolution_count += 1
                resolution_valid = False
                errors.append(f"event[{index}] fork_resolution requires decision and locator")

            if source == "EVIDENCE":
                cited_ids = _strings(event.get("evidence_ids"))
                if fork["evidence_can_decide"] is False:
                    invalid_resolution_count += 1
                    resolution_valid = False
                    errors.append(
                        f"event[{index}] evidence cannot resolve a fork whose evidence_can_decide is false"
                    )
                if budget.get("stop_reason") != "FREEZE":
                    invalid_resolution_count += 1
                    resolution_valid = False
                    errors.append(f"event[{index}] evidence resolution requires budget_stop FREEZE")
                if not cited_ids:
                    invalid_resolution_count += 1
                    resolution_valid = False
                    errors.append(f"event[{index}] evidence resolution requires evidence_ids")
                for evidence_id in cited_ids:
                    item = evidence.get(evidence_id)
                    if item is None:
                        invalid_resolution_count += 1
                        resolution_valid = False
                        errors.append(f"event[{index}] cites unknown evidence {evidence_id!r}")
                    elif item.get("result") != "DISCRIMINATING":
                        invalid_resolution_count += 1
                        resolution_valid = False
                        errors.append(
                            f"event[{index}] evidence resolution cites {item.get('result')} evidence"
                        )
            elif source == "USER":
                raw_decision_id = event.get("user_decision_id")
                decision_id = raw_decision_id.strip() if _nonempty_string(raw_decision_id) else ""
                user_decision = user_decisions.get(decision_id)
                if user_decision is None:
                    invalid_resolution_count += 1
                    resolution_valid = False
                    errors.append(
                        f"event[{index}] user resolution requires a prior user_decision_id"
                    )
                elif (
                    event.get("decision") != user_decision.get("decision")
                    or event.get("locator") != user_decision.get("locator")
                ):
                    invalid_resolution_count += 1
                    resolution_valid = False
                    errors.append(
                        f"event[{index}] user resolution must exactly match the cited user decision and locator"
                    )

            if source in {"EVIDENCE", "USER"} and resolution_valid:
                fork["status"] = "RESOLVED"
                if source == "EVIDENCE":
                    fork["evidence_can_decide"] = True

        elif event_type == "action":
            action_class = event.get("action_class")
            if not _enum(action_class, ACTION_CLASSES):
                errors.append(f"event[{index}] action.action_class is invalid")
                continue
            if action_class == "USER_QUESTION":
                user_questions += 1
                if user_questions > 1:
                    errors.append(
                        f"event[{index}] an unresolved fork permits only one focused user question"
                    )
                if fork["status"] == "OPEN" and budget.get("stop_reason") != "ASK_USER":
                    errors.append(
                        f"event[{index}] USER_QUESTION on an open fork requires budget_stop ASK_USER"
                    )
            elif action_class == "BLOCKER_REPORT":
                blocker_reports += 1
            if fork["status"] == "OPEN" and action_class in OPEN_FORBIDDEN_ACTIONS:
                unresolved_before_design += 1
                if action_class in DESIGN_OR_IMPLEMENTATION_ACTIONS:
                    authoritative_writes_before_contract_freeze += 1
                if action_class == "CANDIDATE_REVIEW":
                    candidate_reviews_while_open += 1
                errors.append(
                    f"event[{index}] {action_class} is forbidden while SemanticFork is OPEN"
                )
            cited_ids = _strings(event.get("evidence_ids"))
            if action_class in DESIGN_OR_IMPLEMENTATION_ACTIONS:
                scope_invalid_ids = [
                    evidence_id
                    for evidence_id in cited_ids
                    if evidence.get(evidence_id, {}).get("result") == "SCOPE_INVALID"
                ]
                if scope_invalid_ids:
                    errors.append(
                        f"event[{index}] design or implementation cites SCOPE_INVALID evidence: "
                        + ", ".join(scope_invalid_ids)
                    )

        else:
            errors.append(f"event[{index}] has unknown type {event_type!r}")

    if sufficient_outcome is not None:
        errors.append(
            f"trace ends without stopping EvidenceBudget after evidence supports {sufficient_outcome}"
        )
    if (
        budget["status"] == "OPEN"
        and completed_investigations_in_current_round > 0
        and trace.get("trace_status") != "IN_PROGRESS"
    ):
        errors.append(
            "trace ends with completed investigations but no explicit EvidenceBudget stop; mark trace_status=IN_PROGRESS only for a genuinely live trace"
        )
    if trace.get("trace_status") != "IN_PROGRESS":
        if budget.get("stop_reason") == "FREEZE" and fork["status"] == "OPEN":
            errors.append(
                "a completed FREEZE gate must record a valid SemanticFork resolution before design or implementation"
            )
        if budget.get("stop_reason") == "ASK_USER" and fork["status"] == "OPEN" and user_questions != 1:
            errors.append(
                "a completed ASK_USER gate must emit exactly one focused USER_QUESTION"
            )
        if budget.get("stop_reason") == "BLOCKER" and blocker_reports != 1:
            errors.append(
                "a completed BLOCKER gate must emit exactly one concrete BLOCKER_REPORT"
            )

    return {
        "passed": not errors,
        "errors": errors,
        "warnings": warnings,
        "metrics": {
            "investigations": investigations,
            "scouts": scouts,
            "max_round": max(investigations_by_round, default=budget["round"]),
            "budget_reopens": budget_reopens,
            "invalid_observation_reopens": invalid_observation_reopens,
            "scope_invalid_evidence_count": scope_invalid_evidence_count,
            "investigations_after_budget_stop": investigations_after_budget_stop,
            "scout_rounds_after_sufficient_evidence": len(scout_rounds_after_sufficient),
            "scout_rounds_after_discriminating_evidence": len(
                scout_rounds_after_discriminating
            ),
            "semantic_fork_unresolved_before_design": unresolved_before_design,
            "authoritative_writes_before_contract_freeze": authoritative_writes_before_contract_freeze,
            "candidate_reviews_while_open": candidate_reviews_while_open,
            "invalid_resolution_count": invalid_resolution_count,
            "user_questions": user_questions,
            "blocker_reports": blocker_reports,
            "final_fork_status": fork["status"],
            "final_budget_status": budget["status"],
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
