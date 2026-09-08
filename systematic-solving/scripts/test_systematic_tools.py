#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("evaluate_systematic_trace.py")
SPEC = importlib.util.spec_from_file_location("evaluate_systematic_trace", SCRIPT)
assert SPEC and SPEC.loader
EVALUATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EVALUATOR)


DECISION = "Should the durable contract preserve option A or option B?"


def open_trace(*, evidence_can_decide: object = False) -> dict[str, object]:
    return {
        "semantic_fork": {
            "decision_question": DECISION,
            "status": "OPEN",
            "evidence_can_decide": evidence_can_decide,
            "options": [
                {"id": "a", "contract": "preserve the write-time meaning"},
                {"id": "b", "contract": "resolve the current meaning"},
            ],
            "architectural_consequences": {
                "ownership": "the decision owner changes",
                "persistence": "the durable representation changes",
            },
        },
        "evidence_budget": {"round": 1, "scout_count": 0, "status": "OPEN"},
        "events": [],
    }


def investigation(
    evidence_id: str,
    *,
    result: str,
    supports: str = "NONE",
    round_number: int = 1,
    mode: str = "SCOUT",
) -> dict[str, object]:
    return {
        "type": "investigation",
        "id": f"investigate-{evidence_id}",
        "mode": mode,
        "round": round_number,
        "decision": DECISION,
        "hypothesis": f"hypothesis-{evidence_id}",
        "discriminator": "the observed contract excludes one candidate or proves evidence cannot choose",
        "scope": [f"bounded:{evidence_id}"],
        "stop_condition": "stop when the declared discriminator is observed",
        "result": result,
        "evidence_id": evidence_id,
        "supports": supports,
    }


class SystematicTraceTest(unittest.TestCase):
    def test_scope_invalid_evidence_stops_and_asks_user(self) -> None:
        trace = open_trace()
        trace["events"] = [
            investigation("e-user", result="SCOPE_INVALID", supports="ASK_USER"),
            {"type": "budget_stop", "reason": "ASK_USER", "evidence_ids": ["e-user"]},
            {"type": "action", "action_class": "USER_QUESTION"},
        ]
        result = EVALUATOR.evaluate_trace(trace)
        self.assertTrue(result["passed"], result["errors"])
        self.assertEqual(1, result["metrics"]["scope_invalid_evidence_count"])
        self.assertEqual("OPEN", result["metrics"]["final_fork_status"])
        self.assertEqual("STOPPED", result["metrics"]["final_budget_status"])

    def test_discriminating_evidence_can_resolve_and_freeze(self) -> None:
        trace = open_trace(evidence_can_decide=True)
        trace["events"] = [
            investigation("e-contract", result="DISCRIMINATING", supports="FREEZE"),
            {"type": "budget_stop", "reason": "FREEZE", "evidence_ids": ["e-contract"]},
            {
                "type": "fork_resolution",
                "source": "EVIDENCE",
                "decision": "a",
                "locator": "evidence:e-contract",
                "evidence_ids": ["e-contract"],
            },
            {
                "type": "action",
                "action_class": "CONTRACT_FREEZE",
                "evidence_ids": ["e-contract"],
            },
            {"type": "action", "action_class": "AUTHORITATIVE_DESIGN"},
        ]
        result = EVALUATOR.evaluate_trace(trace)
        self.assertTrue(result["passed"], result["errors"])
        self.assertEqual("RESOLVED", result["metrics"]["final_fork_status"])

    def test_unknown_evidence_authority_can_converge_from_discriminating_evidence(self) -> None:
        trace = open_trace(evidence_can_decide="unknown")
        trace["events"] = [
            investigation("e-contract", result="DISCRIMINATING", supports="FREEZE"),
            {"type": "budget_stop", "reason": "FREEZE", "evidence_ids": ["e-contract"]},
            {
                "type": "fork_resolution",
                "source": "EVIDENCE",
                "decision": "a",
                "locator": "evidence:e-contract",
                "evidence_ids": ["e-contract"],
            },
        ]
        result = EVALUATOR.evaluate_trace(trace)
        self.assertTrue(result["passed"], result["errors"])
        self.assertEqual("RESOLVED", result["metrics"]["final_fork_status"])

    def test_user_decision_can_resolve_after_focused_question(self) -> None:
        trace = open_trace()
        trace["events"] = [
            investigation("e-user", result="SCOPE_INVALID", supports="ASK_USER"),
            {"type": "budget_stop", "reason": "ASK_USER", "evidence_ids": ["e-user"]},
            {"type": "action", "action_class": "USER_QUESTION"},
            {
                "type": "user_decision",
                "id": "user-1",
                "decision": "b",
                "locator": "thread:answer-4",
            },
            {
                "type": "fork_resolution",
                "source": "USER",
                "decision": "b",
                "locator": "thread:answer-4",
                "user_decision_id": "user-1",
            },
            {"type": "action", "action_class": "AUTHORITATIVE_DESIGN"},
        ]
        result = EVALUATOR.evaluate_trace(trace)
        self.assertTrue(result["passed"], result["errors"])

    def test_user_resolution_must_match_cited_decision_and_locator(self) -> None:
        trace = open_trace()
        trace["events"] = [
            {"type": "user_decision", "id": "user-1", "decision": "b", "locator": "thread:b"},
            {
                "type": "fork_resolution",
                "source": "USER",
                "decision": "a",
                "locator": "thread:not-b",
                "user_decision_id": "user-1",
            },
            {"type": "action", "action_class": "AUTHORITATIVE_DESIGN"},
        ]
        result = EVALUATOR.evaluate_trace(trace)
        self.assertFalse(result["passed"])
        self.assertTrue(any("exactly match" in item for item in result["errors"]))

    def test_open_fork_rejects_design_implementation_and_candidate_review(self) -> None:
        trace = open_trace()
        trace["events"] = [
            {"type": "action", "action_class": "AUTHORITATIVE_DESIGN"},
            {"type": "action", "action_class": "API_DEEPENING"},
            {"type": "action", "action_class": "PRODUCTION_IMPLEMENTATION"},
            {"type": "action", "action_class": "CANDIDATE_REVIEW"},
        ]
        result = EVALUATOR.evaluate_trace(trace)
        self.assertFalse(result["passed"])
        self.assertEqual(4, result["metrics"]["semantic_fork_unresolved_before_design"])
        self.assertEqual(3, result["metrics"]["authoritative_writes_before_contract_freeze"])
        self.assertEqual(1, result["metrics"]["candidate_reviews_while_open"])

    def test_scope_invalid_evidence_cannot_freeze_or_resolve(self) -> None:
        trace = open_trace(evidence_can_decide=True)
        trace["events"] = [
            investigation("e-scope", result="SCOPE_INVALID", supports="FREEZE"),
            {"type": "budget_stop", "reason": "FREEZE", "evidence_ids": ["e-scope"]},
            {
                "type": "fork_resolution",
                "source": "EVIDENCE",
                "decision": "a",
                "locator": "evidence:e-scope",
                "evidence_ids": ["e-scope"],
            },
        ]
        result = EVALUATOR.evaluate_trace(trace)
        self.assertFalse(result["passed"])
        self.assertGreater(result["metrics"]["invalid_resolution_count"], 0)
        self.assertTrue(any("SCOPE_INVALID evidence cannot support FREEZE" in item for item in result["errors"]))

    def test_stops_after_sufficient_evidence_and_enforces_round_budget(self) -> None:
        trace = open_trace()
        trace["events"] = [
            investigation("e-1", result="INCONCLUSIVE"),
            investigation("e-2", result="SCOPE_INVALID", supports="ASK_USER"),
            investigation("e-3", result="INCONCLUSIVE"),
        ]
        result = EVALUATOR.evaluate_trace(trace)
        self.assertFalse(result["passed"])
        self.assertEqual(1, result["metrics"]["scout_rounds_after_sufficient_evidence"])
        self.assertTrue(any("exceeds investigation budget" in item for item in result["warnings"]))
        self.assertTrue(any("without stopping EvidenceBudget" in item for item in result["errors"]))

    def test_invalid_observation_can_open_one_bounded_next_round(self) -> None:
        trace = open_trace(evidence_can_decide="unknown")
        trace["events"] = [
            investigation("e-invalid", result="INVALID"),
            {
                "type": "budget_stop",
                "reason": "INVALID_OBSERVATION",
                "evidence_ids": ["e-invalid"],
            },
            {
                "type": "budget_reopen",
                "reason": "INVALID_OBSERVATION",
                "round": 2,
                "locator": "evidence:e-invalid",
            },
            investigation(
                "e-user",
                result="SCOPE_INVALID",
                supports="ASK_USER",
                round_number=2,
                mode="OBSERVATION",
            ),
            {"type": "budget_stop", "reason": "ASK_USER", "evidence_ids": ["e-user"]},
            {"type": "action", "action_class": "USER_QUESTION"},
        ]
        result = EVALUATOR.evaluate_trace(trace)
        self.assertTrue(result["passed"], result["errors"])
        self.assertEqual(2, result["metrics"]["max_round"])
        self.assertEqual(1, result["metrics"]["budget_reopens"])

    def test_invalid_reopen_must_cite_current_round_and_cannot_repeat(self) -> None:
        trace = open_trace(evidence_can_decide="unknown")
        trace["events"] = [
            investigation("e-invalid-1", result="INVALID"),
            {"type": "budget_stop", "reason": "INVALID_OBSERVATION", "evidence_ids": ["e-invalid-1"]},
            {"type": "budget_reopen", "reason": "INVALID_OBSERVATION", "round": 2,
             "locator": "evidence:e-invalid-1"},
            investigation("e-inconclusive", result="INCONCLUSIVE", round_number=2),
            {"type": "budget_stop", "reason": "INVALID_OBSERVATION", "evidence_ids": ["e-invalid-1"]},
            {"type": "budget_reopen", "reason": "INVALID_OBSERVATION", "round": 3,
             "locator": "evidence:e-invalid-1"},
        ]
        result = EVALUATOR.evaluate_trace(trace)
        self.assertFalse(result["passed"])
        self.assertTrue(any("current round" in item for item in result["errors"]))
        self.assertTrue(any("default one" in item for item in result["warnings"]))

    def test_completed_inconclusive_round_requires_explicit_stop(self) -> None:
        trace = open_trace()
        trace["events"] = [
            investigation("e-1", result="INCONCLUSIVE"),
            investigation("e-2", result="INCONCLUSIVE"),
        ]
        result = EVALUATOR.evaluate_trace(trace)
        self.assertFalse(result["passed"])
        self.assertTrue(any("no explicit EvidenceBudget stop" in item for item in result["errors"]))

    def test_ask_user_gate_allows_only_one_focused_question(self) -> None:
        trace = open_trace()
        trace["events"] = [
            investigation("e-user", result="SCOPE_INVALID", supports="ASK_USER"),
            {"type": "budget_stop", "reason": "ASK_USER", "evidence_ids": ["e-user"]},
            {"type": "action", "action_class": "USER_QUESTION"},
            {"type": "action", "action_class": "USER_QUESTION"},
        ]
        result = EVALUATOR.evaluate_trace(trace)
        self.assertFalse(result["passed"])
        self.assertTrue(any("only one focused" in item for item in result["errors"]))

    def test_larger_investigation_budget_is_diagnostic(self) -> None:
        trace = open_trace()
        trace["budget_policy"] = {
            "max_investigations_per_round": 3,
            "override_reason": "more confidence",
        }
        trace["trace_status"] = "IN_PROGRESS"
        trace["events"] = [investigation(f"e-{index}", result="INCONCLUSIVE") for index in range(3)]
        result = EVALUATOR.evaluate_trace(trace)
        self.assertTrue(result["passed"], result["errors"])
        self.assertTrue(any("structured HIGH_RISK_GAP" in item for item in result["warnings"]))

    def test_large_high_risk_budget_retains_efficiency_warning(self) -> None:
        trace = open_trace()
        trace["budget_policy"] = {
            "max_investigations_per_round": 100,
            "override": {
                "reason": "HIGH_RISK_GAP",
                "locator": "risk://irreversible-migration",
            },
        }
        trace["trace_status"] = "IN_PROGRESS"
        result = EVALUATOR.evaluate_trace(trace)
        self.assertTrue(result["passed"], result["errors"])
        self.assertTrue(any("default one complementary HIGH_RISK_GAP" in item
                            for item in result["warnings"]))

    def test_explicit_resource_limit_remains_hard(self) -> None:
        trace = open_trace()
        trace["trace_status"] = "IN_PROGRESS"
        trace["budget_policy"] = {"max_investigations_per_round": 2, "enforce_limit": True}
        trace["events"] = [investigation(f"e-{index}", result="INCONCLUSIVE") for index in range(3)]
        result = EVALUATOR.evaluate_trace(trace)
        self.assertFalse(result["passed"])
        self.assertTrue(any("exceeds investigation budget" in item for item in result["errors"]))

    def test_resolved_fork_does_not_make_invalid_observation_implementation_evidence(self) -> None:
        for outcome in ("DISCRIMINATING", "INVALID", "INCONCLUSIVE", "SCOPE_INVALID"):
            for action in ("CONTRACT_FREEZE", "AUTHORITATIVE_DESIGN", "API_DEEPENING", "PRODUCTION_IMPLEMENTATION"):
                with self.subTest(outcome=outcome, action=action):
                    trace = open_trace()
                    trace["events"] = [
                        {"type": "user_decision", "id": "user-1", "decision": "b", "locator": "thread:b"},
                        {"type": "fork_resolution", "source": "USER", "decision": "b",
                         "locator": "thread:b", "user_decision_id": "user-1"},
                        investigation("e-action", result=outcome),
                        {"type": "budget_stop", "reason": "SOURCE_DRIFT", "locator": "source:changed"},
                        {"type": "action", "action_class": action, "evidence_ids": ["e-action"]},
                    ]
                    result = EVALUATOR.evaluate_trace(trace)
                    if outcome == "DISCRIMINATING":
                        self.assertTrue(result["passed"], result["errors"])
                    else:
                        self.assertFalse(result["passed"])
                        self.assertTrue(any(f"e-action ({outcome})" in item for item in result["errors"]))

    def test_implementation_cannot_cite_unknown_or_malformed_evidence(self) -> None:
        for evidence_ids in (["missing"], False, [False], "missing"):
            with self.subTest(evidence_ids=evidence_ids):
                trace = open_trace()
                trace["semantic_fork"]["status"] = "NOT_APPLICABLE"
                trace["events"] = [{"type": "action", "action_class": "PRODUCTION_IMPLEMENTATION",
                                    "evidence_ids": evidence_ids}]
                result = EVALUATOR.evaluate_trace(trace)
                self.assertFalse(result["passed"])
                self.assertTrue(any("evidence" in item for item in result["errors"]))

    def test_terminal_evidence_gate_requires_its_real_next_action(self) -> None:
        ask_trace = open_trace()
        ask_trace["events"] = [
            investigation("e-user", result="SCOPE_INVALID", supports="ASK_USER"),
            {"type": "budget_stop", "reason": "ASK_USER", "evidence_ids": ["e-user"]},
        ]
        ask_result = EVALUATOR.evaluate_trace(ask_trace)
        self.assertFalse(ask_result["passed"])
        self.assertTrue(any("exactly one focused USER_QUESTION" in item
                            for item in ask_result["errors"]))

        freeze_trace = open_trace(evidence_can_decide=True)
        freeze_trace["events"] = [
            investigation("e-contract", result="DISCRIMINATING", supports="FREEZE"),
            {"type": "budget_stop", "reason": "FREEZE", "evidence_ids": ["e-contract"]},
        ]
        freeze_result = EVALUATOR.evaluate_trace(freeze_trace)
        self.assertFalse(freeze_result["passed"])
        self.assertTrue(any("must record a valid SemanticFork resolution" in item
                            for item in freeze_result["errors"]))

    def test_reopen_requires_a_valid_reason_locator_and_incremented_round(self) -> None:
        trace = open_trace()
        trace["evidence_budget"] = {
            "round": 1,
            "scout_count": 0,
            "status": "STOPPED",
            "stop_reason": "ASK_USER",
        }
        trace["events"] = [
            {"type": "budget_reopen", "reason": "MORE_RESEARCH", "round": 3},
        ]
        result = EVALUATOR.evaluate_trace(trace)
        self.assertFalse(result["passed"])
        self.assertTrue(any("reason is invalid" in item for item in result["errors"]))
        self.assertTrue(any("requires locator" in item for item in result["errors"]))
        self.assertTrue(any("increment by one" in item for item in result["errors"]))

    def test_investigation_requires_decision_bound_contract(self) -> None:
        trace = open_trace()
        incomplete = investigation("e-1", result="INCONCLUSIVE")
        incomplete.pop("discriminator")
        incomplete["decision"] = "Explore the entire repository"
        trace["events"] = [incomplete]
        result = EVALUATOR.evaluate_trace(trace)
        self.assertFalse(result["passed"])
        self.assertTrue(any("investigation missing: discriminator" in item for item in result["errors"]))
        self.assertTrue(any("must match the open SemanticFork question" in item for item in result["errors"]))

    def test_simple_contract_does_not_trigger_semantic_fork_gate(self) -> None:
        trace = {
            "semantic_fork": {
                "decision_question": "Which local implementation restores the fixed contract?",
                "status": "NOT_APPLICABLE",
                "evidence_can_decide": True,
                "options": [],
                "architectural_consequences": {},
            },
            "evidence_budget": {"round": 1, "scout_count": 0, "status": "OPEN"},
            "events": [
                {"type": "action", "action_class": "PRODUCTION_IMPLEMENTATION"},
            ],
        }
        result = EVALUATOR.evaluate_trace(trace)
        self.assertTrue(result["passed"], result["errors"])

    def test_saved_evidence_resolution_requires_evidence_authority(self) -> None:
        trace = open_trace(evidence_can_decide=False)
        semantic_fork = trace["semantic_fork"]
        assert isinstance(semantic_fork, dict)
        semantic_fork["status"] = "RESOLVED"
        semantic_fork["resolution"] = {
            "source": "EVIDENCE",
            "decision": "a",
            "locator": "evidence:old",
        }
        result = EVALUATOR.evaluate_trace(trace)
        self.assertFalse(result["passed"])
        self.assertTrue(any("requires evidence_can_decide=true" in item for item in result["errors"]))

    def test_unresolved_fork_cannot_carry_saved_resolution(self) -> None:
        trace = open_trace()
        semantic_fork = trace["semantic_fork"]
        assert isinstance(semantic_fork, dict)
        semantic_fork["resolution"] = {
            "source": "USER", "decision": "a", "locator": "instruction:old"
        }
        result = EVALUATOR.evaluate_trace(trace)
        self.assertFalse(result["passed"])
        self.assertTrue(any("valid only when status=RESOLVED" in item
                            for item in result["errors"]))

    def test_malformed_enum_values_do_not_crash(self) -> None:
        trace = open_trace()
        trace["semantic_fork"]["status"] = []
        trace["evidence_budget"]["status"] = []
        trace["events"] = [investigation("bad", result=[])]
        result = EVALUATOR.evaluate_trace(trace)
        self.assertFalse(result["passed"])
        self.assertTrue(result["errors"])


if __name__ == "__main__":
    unittest.main()
