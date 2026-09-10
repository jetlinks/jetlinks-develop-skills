#!/usr/bin/env python3

from __future__ import annotations

import copy
import importlib.util
import os
import tempfile
import unittest
from pathlib import Path


SCRIPT_ROOT = Path(__file__).parent


def load_script(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_ROOT / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


STATE = load_script("validate_continuity_state")
TRACE = load_script("evaluate_continuity_trace")
PROJECTOR = load_script("prepare_resume_context")


def valid_state() -> dict:
    action = {
        "action_id": "implement-validator",
        "type": "mutation",
        "owner": "task-continuity/scripts/validate_continuity_state.py",
        "scope": ["validator"],
        "observable_signal": "state fixtures return the expected gate",
    }
    return {
        "recovery_capsule": {
            "contract": {
                "boundary_id": "b7",
                "task_id": "continuity-tools",
                "revision": "contract-r3",
                "locator": "task://continuity-tools@contract-r3",
                "objective": "make continuation state executable",
                "constraints": ["do not replay completed recovery work"],
                "acceptance": ["matching state reaches READY"],
            },
            "checkpoint": {
                "boundary_id": "b7",
                "phase": "implementation",
                "validated": [],
                "in_flight": {
                    "slice_id": "validator-gate",
                    "status": "active",
                    "owner": "task-continuity/scripts/validate_continuity_state.py",
                    "expected_changed_items": ["task-continuity/scripts"],
                },
            },
            "decision_state": {
                "boundary_id": "b7",
                "active_hypothesis": "missing deterministic execution layer",
                "acceptance_status": "in_progress",
                "do_not_reopen": [
                    {
                        "action_id": "reload-full-task-history",
                        "reason": "the saved task revision already contains the required facts",
                        "reopen_when": "the task revision changes or a recorded fact conflicts",
                    }
                ],
            },
            "resume": {
                "boundary_id": "b7",
                "gate": "RESUME_AUDIT",
                "recovery_type": "COMPACT_CONTINUATION",
                "anchors": ["task-continuity/scripts"],
                "next": copy.deepcopy(action),
                "first_allowed_action": copy.deepcopy(action),
            },
        },
        "continuity_metadata": {
            "boundary_id": "b7",
            "audit_fingerprint": "audit-3",
            "consecutive_matching_audits": 1,
            "instruction_revision_at_snapshot": "instruction-r3",
            "directive_revision_at_snapshot": "directive-r3",
            "conversation_cursor_at_snapshot": "cursor-3",
            "pre_compaction_next_action_id": "implement-validator",
            "previous_productive_action_id": "model-current-state",
            "referenced_sources": [{"id": "trellis-docs", "revision": "0.6.14"}],
            "loaded_rules": [{"id": "task-continuity", "revision": "sha256:rules"}],
        },
        "source_snapshot": {
            "boundary_id": "b7",
            "source_id": "workspace",
            "source_fingerprint": "sha256:tree",
            "strength": "strong",
            "locator": "workspace-state",
            "expected_changed_items": ["task-continuity/scripts"],
            "missing_layers": [],
        },
        "observed": {
            "boundary_id": "b7",
            "source_fingerprint": "sha256:tree",
            "contract_revision": "contract-r3",
            "instruction_revision": "instruction-r3",
            "directive_revision": "directive-r3",
            "conversation_cursor": "cursor-3",
            "referenced_sources": {"trellis-docs": "0.6.14"},
            "loaded_rules": {"task-continuity": "sha256:rules"},
        },
    }


def with_active_observation(
    document: dict,
    result: str,
    purpose: str,
    repair_cycles: int = 0,
) -> dict:
    observation = {
        "id": "select-solution-boundary",
        "revision": "observation-r1",
        "decision": "select the next solution level",
        "boundary": "externally observable behavior",
        "preconditions": ["the declared input and environment are available"],
        "prediction": "one candidate produces a distinct stable signal",
        "discriminator": "the stable signal excludes at least one candidate",
        "invalidators": ["the declared boundary is not reached"],
        "result": result,
        "repair_cycles": repair_cycles,
    }
    if result != "PLANNED":
        observation["actual_signal"] = f"normalized {result.lower()} signal"
        observation["evidence_locator"] = f"evidence://{result.lower()}"
    document["recovery_capsule"]["decision_state"]["active_observation"] = observation
    document["observed"]["observation_revision"] = observation["revision"]
    document["observed"]["observation_result"] = result
    for field in ("next", "first_allowed_action"):
        document["recovery_capsule"]["resume"][field]["purpose"] = purpose
    return document


def with_semantic_fork(document: dict, status: str = "OPEN") -> dict:
    fork = {
        "decision_question": "which externally visible contract should be frozen",
        "status": status,
        "evidence_can_decide": False,
        "options": [
            {"id": "snapshot", "contract": "snapshot contract"},
            {"id": "current", "contract": "current-state contract"},
        ],
        "architectural_consequences": {
            "persistence": "persistence ownership changes",
            "security": "authorization timing changes",
        },
    }
    if status == "RESOLVED":
        fork["resolution"] = {
            "source": "USER",
            "decision": "snapshot contract",
            "locator": "instruction://r4",
        }
    document["recovery_capsule"]["decision_state"].update(
        {
            "semantic_fork": fork,
            "evidence_budget": {
                "round": 1,
                "scout_count": 2,
                "status": "STOPPED",
                "stop_reason": "ASK_USER" if status == "OPEN" else "FREEZE",
            },
            "current_stage": "semantic-decision",
            "stage_entry_gate": "semantic fork must be RESOLVED before design",
            "latest_discriminating_evidence": "evidence://contract-boundaries",
        }
    )
    return document


class ContinuityStateTest(unittest.TestCase):
    def test_resume_context_projects_only_bounded_fast_path_fields(self) -> None:
        document = valid_state()
        document["recovery_capsule"]["checkpoint"]["in_flight"]["owner"] = "owner-" + ("x" * 500)
        projected = PROJECTOR.project_context(document, max_anchors=1, text_limit=80)
        self.assertTrue(projected["ready"])
        self.assertEqual("READY", projected["gate"])
        self.assertEqual("implement-validator", projected["resume"]["first_allowed_action"]["action_id"])
        self.assertEqual("task://continuity-tools@contract-r3", projected["contract"]["locator"])
        self.assertEqual(["task-continuity/scripts"], projected["resume"]["anchors"])
        self.assertEqual(
            ["do not replay completed recovery work"], projected["contract"]["constraints"]
        )
        self.assertEqual(
            "the saved task revision already contains the required facts",
            projected["decision_state"]["do_not_reopen"][0]["reason"],
        )
        self.assertEqual(document["recovery_capsule"]["checkpoint"]["in_flight"]["owner"], projected["checkpoint"]["in_flight"]["owner"])
        self.assertTrue(projected["projection_warnings"])
        self.assertNotIn("referenced_sources", projected)
        self.assertNotIn("loaded_rules", projected)
        self.assertIn("do not reload unchanged references", projected["instructions"])

    def test_resume_context_projects_mismatch_without_authorizing_mutation(self) -> None:
        document = valid_state()
        document["observed"]["source_fingerprint"] = "sha256:changed"
        projected = PROJECTOR.project_context(document)
        self.assertFalse(projected["ready"])
        self.assertEqual("SNAPSHOT_REQUIRED", projected["gate"])
        self.assertIn("source", projected["identity"]["comparisons"])
        self.assertIn("do not mutate production state", projected["instructions"])

    def test_projection_preserves_original_objective_and_current_constraints_across_turns(self) -> None:
        document = valid_state()
        contract = document["recovery_capsule"]["contract"]
        objective = ("Deliver the original task. " + "Keep the existing behavior. " * 20).strip()
        original = "A long scoped obligation: " + "preserve state; " * 30 + "do not publish."
        contract["objective"] = objective
        contract["constraints"] = [original, "old worker constraint"]
        contract["accepted_constraints"] = [{"id": "worker", "text": "old worker constraint"}]
        document["observed"].update({
            "conversation_cursor": "cursor-4", "directive_revision": "directive-r4", "message_class": "NEW_CONSTRAINT",
            "message_effect": {"affects_saved_next": False, "affected_assignment_ids": ["worker"],
                               "accepted_constraints": [{"id": "worker", "text": "current worker constraint", "scope": ["worker"]},
                                                        {"id": "format", "text": "keep the selected output format"}]},
        })
        projected = PROJECTOR.project_context(document, text_limit=80)
        self.assertTrue(projected["ready"])
        self.assertEqual(objective, projected["contract"]["objective"])
        self.assertEqual([original, "current worker constraint", "keep the selected output format"], projected["contract"]["constraints"])
        self.assertEqual("directive-r4", projected["identity"]["current_directive_revision"])
        action = projected["resume"]["first_allowed_action"]
        # Save a new boundary, then receive a status question: the task is unchanged.
        contract["constraints"] = projected["contract"]["constraints"]
        contract["accepted_constraints"] = projected["contract"]["accepted_constraints"]
        document["continuity_metadata"]["directive_revision_at_snapshot"] = "directive-r4"
        document["continuity_metadata"]["conversation_cursor_at_snapshot"] = "cursor-4"
        document["observed"].update({"conversation_cursor": "cursor-5", "message_class": "QUERY",
                                    "message_effect": {"affects_saved_next": False, "affected_assignment_ids": []}})
        queried = PROJECTOR.project_context(document, text_limit=80)
        self.assertTrue(queried["ready"])
        self.assertEqual(projected["contract"], queried["contract"])
        self.assertEqual(action, queried["resume"]["first_allowed_action"])
        # An explicit withdrawal removes that constraint, retaining all other work.
        document["observed"].update({"conversation_cursor": "cursor-6", "directive_revision": "directive-r5", "message_class": "NEW_CONSTRAINT",
            "message_effect": {"affects_saved_next": False, "affected_assignment_ids": ["worker"],
                               "accepted_constraints": [{"id": "worker", "status": "revoked"}]}})
        withdrawn = PROJECTOR.project_context(document)
        self.assertTrue(withdrawn["ready"])
        self.assertEqual([original, "keep the selected output format"], withdrawn["contract"]["constraints"])
        self.assertEqual(["format"], [item["id"] for item in withdrawn["contract"]["accepted_constraints"]])
        self.assertEqual(objective, withdrawn["contract"]["objective"])

    def test_size_targets_do_not_truncate_or_reject_valid_resume(self) -> None:
        document = valid_state()
        document["recovery_capsule"]["resume"]["anchors"] = [f"module-{index}/entry.py" for index in range(9)]
        document["recovery_capsule"]["contract"]["constraints"] = [f"Retain requirement {index}" for index in range(9)]
        projected = PROJECTOR.project_context(document, max_anchors=3)
        self.assertTrue(projected["ready"])
        self.assertEqual(9, len(projected["resume"]["anchors"]))
        self.assertEqual(9, len(projected["contract"]["constraints"]))
        self.assertTrue(projected["projection_warnings"])
        self.assertEqual({}, projected["projection_omissions"])

    def test_new_constraint_revision_without_accepted_text_is_not_ready(self) -> None:
        document = valid_state()
        document["observed"].update({"conversation_cursor": "cursor-4", "directive_revision": "directive-r4", "message_class": "NEW_CONSTRAINT",
                                    "message_effect": {"affects_saved_next": False, "affected_assignment_ids": ["worker"]}})
        projected = PROJECTOR.project_context(document)
        self.assertFalse(projected["ready"])
        self.assertIsNone(projected["resume"]["first_allowed_action"])
        self.assertIn("constraints.missing_delta", {item["code"] for item in projected["identity"]["errors"]})

    def test_matching_observations_transition_to_ready(self) -> None:
        result = STATE.validate_state(valid_state())
        self.assertTrue(result["valid"])
        self.assertTrue(result["ready"])
        self.assertEqual("READY", result["suggested_gate"])

    def test_malformed_enum_values_return_diagnostics_instead_of_crashing(self) -> None:
        mutations = (
            ("recovery_capsule.checkpoint.in_flight.status", []),
            ("recovery_capsule.resume.next.type", []),
            ("recovery_capsule.resume.next.purpose", []),
            ("recovery_capsule.resume.recovery_type", []),
        )
        for dotted_path, malformed in mutations:
            with self.subTest(path=dotted_path):
                document = valid_state()
                target = document
                parts = dotted_path.split(".")
                for part in parts[:-1]:
                    target = target[part]
                target[parts[-1]] = malformed
                result = STATE.validate_state(document)
                self.assertFalse(result["valid"])
                self.assertTrue(result["errors"])

    def test_compact_lists_are_typed_and_bounded(self) -> None:
        malformed_acceptance = valid_state()
        malformed_acceptance["recovery_capsule"]["contract"]["acceptance"] = [{}]
        self.assertFalse(STATE.validate_state(malformed_acceptance)["valid"])

        malformed_anchors = valid_state()
        malformed_anchors["recovery_capsule"]["resume"]["anchors"] = [{}]
        self.assertFalse(STATE.validate_state(malformed_anchors)["valid"])

        expanded = valid_state()
        expanded["recovery_capsule"]["checkpoint"]["validated"] = [
            {
                "stage": f"stage-{index}",
                "evidence": {"locator": f"evidence:{index}"},
                "checkpoint": {"id": f"checkpoint:{index}"},
            }
            for index in range(2)
        ]
        result = STATE.validate_state(expanded)
        self.assertTrue(result["ready"])
        self.assertIn("checkpoint.validated_too_large", {item["code"] for item in result["warnings"]})

    def test_unknown_source_strength_cannot_authorize_ready(self) -> None:
        document = valid_state()
        document["source_snapshot"]["strength"] = "garbage"
        result = STATE.validate_state(document)
        self.assertFalse(result["ready"])
        self.assertIn("snapshot.invalid_strength", {item["code"] for item in result["errors"]})

    def test_vague_next_requires_snapshot(self) -> None:
        document = valid_state()
        for field in ("next", "first_allowed_action"):
            action = document["recovery_capsule"]["resume"][field]
            action.pop("action_id")
            action["owner"] = "continue analysis"
        result = STATE.validate_state(document)
        self.assertFalse(result["valid"])
        self.assertEqual("SNAPSHOT_REQUIRED", result["suggested_gate"])
        self.assertIn("action.vague", {item["code"] for item in result["errors"]})

    def test_reference_revision_change_invalidates_saved_next(self) -> None:
        document = valid_state()
        document["observed"]["referenced_sources"]["trellis-docs"] = "0.7.0"
        result = STATE.validate_state(document)
        self.assertTrue(result["valid"])
        self.assertFalse(result["ready"])
        self.assertEqual("SNAPSHOT_REQUIRED", result["suggested_gate"])
        self.assertEqual("mismatch", result["comparisons"]["references"])

    def test_user_contract_revision_change_invalidates_saved_next(self) -> None:
        document = valid_state()
        document["observed"]["contract_revision"] = "contract-r4"
        result = STATE.validate_state(document)
        self.assertTrue(result["valid"])
        self.assertEqual("SNAPSHOT_REQUIRED", result["suggested_gate"])
        self.assertEqual("mismatch", result["comparisons"]["contract"])

    def test_user_instruction_revision_change_invalidates_saved_next(self) -> None:
        document = valid_state()
        document["observed"]["directive_revision"] = "directive-r4"
        result = STATE.validate_state(document)
        self.assertTrue(result["valid"])
        self.assertEqual("SNAPSHOT_REQUIRED", result["suggested_gate"])
        self.assertEqual("mismatch", result["comparisons"]["directive"])
        self.assertEqual("mismatch", result["comparisons"]["instruction"])

    def test_query_advances_cursor_without_invalidating_saved_next(self) -> None:
        document = valid_state()
        document["observed"].update({
            "conversation_cursor": "cursor-4",
            "message_class": "QUERY",
            "message_effect": {"affects_saved_next": False, "affected_assignment_ids": []},
        })
        result = STATE.validate_state(document)
        self.assertTrue(result["ready"])
        self.assertEqual("advanced", result["comparisons"]["conversation"])
        self.assertEqual("match", result["comparisons"]["directive"])

    def test_duplicate_reminder_does_not_refresh_revision_or_assignments(self) -> None:
        document = valid_state()
        document["observed"].update({
            "conversation_cursor": "cursor-4",
            "message_class": "REMINDER",
            "message_effect": {"affects_saved_next": False, "affected_assignment_ids": []},
        })
        result = STATE.validate_state(document)
        self.assertTrue(result["ready"])

    def test_scoped_constraint_change_preserves_unaffected_saved_next(self) -> None:
        document = valid_state()
        document["observed"].update({
            "conversation_cursor": "cursor-4",
            "directive_revision": "directive-r4",
            "message_class": "NEW_CONSTRAINT",
            "message_effect": {
                "accepted_constraints": [{"id": "frontend-format", "text": "Use the accepted frontend format", "scope": ["frontend-slice"]}],
                "affects_saved_next": False,
                "affected_assignment_ids": ["frontend-slice"],
            },
        })
        result = STATE.validate_state(document)
        self.assertTrue(result["ready"])
        self.assertEqual("scoped_change", result["comparisons"]["directive"])

    def test_constraint_change_affecting_saved_next_requires_snapshot(self) -> None:
        document = valid_state()
        document["observed"].update({
            "conversation_cursor": "cursor-4",
            "directive_revision": "directive-r4",
            "message_class": "NEW_CONSTRAINT",
            "message_effect": {
                "accepted_constraints": [{"id": "frontend-format", "text": "Use the accepted frontend format", "scope": ["frontend-slice"]}],
                "affects_saved_next": True,
                "affected_assignment_ids": ["validator-gate"],
            },
        })
        result = STATE.validate_state(document)
        self.assertEqual("SNAPSHOT_REQUIRED", result["suggested_gate"])

    def test_temporary_interrupt_holds_mainline_then_resumes_exact_next(self) -> None:
        document = valid_state()
        document["recovery_capsule"]["resume"]["mainline_return_anchor"] = {
            "interruption_id": "interrupt-1",
            "original_task_id": "continuity-tools",
            "saved_stage": "implementation",
            "saved_next_action_id": "implement-validator",
            "frozen_contract_revision": "contract-r3",
            "active_assignment_ids": [],
            "source_fingerprint": "sha256:tree",
            "interrupt_objective": "answer a bounded user question",
            "resume_condition": "the bounded question is answered",
        }
        document["observed"].update({
            "conversation_cursor": "cursor-4",
            "message_class": "TEMPORARY_INTERRUPT",
            "message_effect": {
                "affects_saved_next": False,
                "affected_assignment_ids": [],
                "interruption_state": "ACTIVE",
            },
        })
        held = STATE.validate_state(document)
        self.assertTrue(held["valid"])
        self.assertFalse(held["ready"])
        self.assertEqual("RESUME_AUDIT", held["suggested_gate"])

        document["observed"]["message_effect"]["interruption_state"] = "RESUME_READY"
        resumed = STATE.validate_state(document)
        self.assertTrue(resumed["ready"])

    def test_temporary_interrupt_rejects_stale_return_anchor(self) -> None:
        document = valid_state()
        document["recovery_capsule"]["resume"]["mainline_return_anchor"] = {
            "interruption_id": "interrupt-1",
            "original_task_id": "continuity-tools",
            "saved_stage": "implementation",
            "saved_next_action_id": "implement-validator",
            "frozen_contract_revision": "contract-r3",
            "active_assignment_ids": [],
            "source_fingerprint": "sha256:stale",
            "interrupt_objective": "handle a bounded interrupt",
            "resume_condition": "interrupt complete",
        }
        document["observed"].update({
            "conversation_cursor": "cursor-4",
            "message_class": "TEMPORARY_INTERRUPT",
            "message_effect": {
                "affects_saved_next": False,
                "affected_assignment_ids": [],
                "interruption_state": "RESUME_READY",
            },
        })
        result = STATE.validate_state(document)
        self.assertEqual("SNAPSHOT_REQUIRED", result["suggested_gate"])
        self.assertIn("return_anchor.identity_mismatch", {item["code"] for item in result["mismatches"]})

    def test_compact_continuation_preserves_pre_compaction_action_identity(self) -> None:
        document = valid_state()
        document["continuity_metadata"]["pre_compaction_next_action_id"] = "accept-stage"
        result = STATE.validate_state(document)
        self.assertFalse(result["valid"])
        self.assertIn("resume.pre_compaction_action_mismatch", {item["code"] for item in result["errors"]})

    def test_compact_mutation_requires_stable_in_flight_slice(self) -> None:
        document = valid_state()
        document["recovery_capsule"]["checkpoint"]["in_flight"] = {}
        result = STATE.validate_state(document)
        self.assertFalse(result["valid"])
        self.assertIn("checkpoint.compact_mutation_missing_slice", {item["code"] for item in result["errors"]})

    def test_first_action_cannot_reopen_a_closed_action(self) -> None:
        document = valid_state()
        document["recovery_capsule"]["decision_state"]["do_not_reopen"][0]["action_id"] = "implement-validator"
        result = STATE.validate_state(document)
        self.assertFalse(result["valid"])
        self.assertIn("resume.reopens_closed_action", {item["code"] for item in result["errors"]})

    def test_cold_handoff_does_not_require_a_pre_compaction_action_chain(self) -> None:
        document = valid_state()
        document["recovery_capsule"]["resume"]["recovery_type"] = "COLD_HANDOFF"
        for field in (
            "instruction_revision_at_snapshot",
            "pre_compaction_next_action_id",
            "previous_productive_action_id",
        ):
            document["continuity_metadata"].pop(field)
        document["observed"].pop("instruction_revision")
        result = STATE.validate_state(document)
        self.assertTrue(result["valid"])
        self.assertTrue(result["ready"])

    def test_validated_stage_requires_evidence_and_checkpoint(self) -> None:
        document = valid_state()
        document["recovery_capsule"]["checkpoint"]["validated"] = [{"stage": "scripts"}]
        result = STATE.validate_state(document)
        codes = {item["code"] for item in result["errors"]}
        self.assertIn("checkpoint.missing_evidence", codes)
        self.assertIn("checkpoint.missing_identity", codes)

    def test_partial_fingerprint_must_declare_risk(self) -> None:
        document = valid_state()
        document["source_snapshot"]["strength"] = "partial"
        document["source_snapshot"]["missing_layers"] = ["untracked"]
        result = STATE.validate_state(document)
        self.assertIn("snapshot.partial_risk_missing", {item["code"] for item in result["errors"]})

    def test_partial_identity_retains_risk_and_blocks_unobserved_action_content(self) -> None:
        document = valid_state()
        snapshot = document["source_snapshot"]
        snapshot.update(strength="partial", missing_layers=["current content"],
                        residual_identity_risk="Current action source content has not been observed.")
        for scopes in (None, {"current content": ["task-continuity/scripts"]}):
            with self.subTest(scopes=scopes):
                if scopes is not None:
                    snapshot["missing_layer_scopes"] = scopes
                result = PROJECTOR.project_context(document)
                self.assertEqual("RESUME_AUDIT", result["gate"])
                self.assertFalse(result["ready"])
                self.assertIsNone(result["resume"]["first_allowed_action"])
                self.assertEqual(snapshot["missing_layers"], result["identity"]["missing_layers"])
                self.assertEqual(snapshot["residual_identity_risk"], result["identity"]["residual_identity_risk"])
                self.assertNotIn("Identity matched", result["instructions"])

    def _partial_local_state(self, root: Path) -> dict:
        (root / "src").mkdir()
        (root / "docs").mkdir()
        (root / "src/exporter.py").write_text("def export_rows(): pass\n")
        (root / "docs/help.md").write_text("Device integration guide\n")
        document = valid_state()
        document["source_snapshot"].update(
            locator=str(root), strength="partial", missing_layers=["documentation content"],
            missing_layer_scopes={"documentation content": ["docs/help.md"]},
            residual_identity_risk="Documentation content is unavailable.",
        )
        for field in ("next", "first_allowed_action"):
            document["recovery_capsule"]["resume"][field].update(
                owner="src/exporter.py", scope=["src/exporter.py"],
            )
        return document

    def test_partial_identity_allows_proven_unrelated_scope_without_erasing_risk(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            document = self._partial_local_state(Path(directory))
            result = PROJECTOR.project_context(document)
            self.assertTrue(result["ready"], result["identity"]["errors"])
            self.assertEqual("mutation", result["resume"]["first_allowed_action"]["type"])
            self.assertEqual("partial", result["identity"]["strength"])
            self.assertIn("Identity remains partial", result["instructions"])

    def test_partial_identity_also_covers_the_action_actually_projected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            document = self._partial_local_state(Path(directory))
            document["recovery_capsule"]["resume"]["first_allowed_action"]["scope"] = ["docs/help.md"]
            result = PROJECTOR.project_context(document)
            self.assertFalse(result["ready"])
            self.assertIsNone(result["resume"]["first_allowed_action"])

    def test_partial_identity_rejects_aliases_of_the_same_physical_source(self) -> None:
        for alias_kind in ("directory_alias", "file_object_alias"):
            with self.subTest(alias_kind=alias_kind), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                document = self._partial_local_state(root)
                if alias_kind == "directory_alias":
                    (root / "src").rename(root / "generated")
                    (root / "src").symlink_to("generated", target_is_directory=True)
                    missing_path = "generated"
                    self.assertTrue((root / "src/exporter.py").samefile(root / "generated/exporter.py"))
                else:
                    os.link(root / "src/exporter.py", root / "exporter-alias.py")
                    missing_path = "exporter-alias.py"
                    self.assertTrue((root / "src/exporter.py").samefile(root / missing_path))
                document["source_snapshot"]["missing_layer_scopes"] = {"documentation content": [missing_path]}
                result = PROJECTOR.project_context(document)
                self.assertFalse(result["ready"])
                self.assertEqual("RESUME_AUDIT", result["gate"])
                self.assertIsNone(result["resume"]["first_allowed_action"])

    def test_partial_identity_cannot_infer_disjointness_from_unverified_or_open_boundaries(self) -> None:
        for boundary in ("remote", "missing", "directory", "outside_alias"):
            with self.subTest(boundary=boundary), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                document = self._partial_local_state(root)
                if boundary == "remote":
                    document["source_snapshot"]["locator"] = "workspace://remote"
                elif boundary == "missing":
                    (root / "docs/help.md").unlink()
                elif boundary == "directory":
                    document["source_snapshot"]["missing_layer_scopes"] = {"documentation content": ["docs"]}
                else:
                    (root / "docs/help.md").unlink()
                    (root / "docs/help.md").symlink_to(Path(__file__).resolve())
                self.assertFalse(PROJECTOR.project_context(document)["ready"])
                for field in ("next", "first_allowed_action"):
                    document["recovery_capsule"]["resume"][field].update(type="check", purpose="observation_setup")
                self.assertTrue(PROJECTOR.project_context(document)["ready"])

    def test_partial_identity_scope_must_cover_every_missing_layer_and_stay_inside_boundary(self) -> None:
        for scopes in ({"content": ["docs"]}, {"content": ["docs"], "nested": ["../outside"]},
                       {"content": ["docs"], "nested": ["/outside/workspace"]},
                       {"content": ["docs"], "nested": ["src/*"]}):
            with self.subTest(scopes=scopes):
                document = valid_state()
                document["source_snapshot"].update(
                    strength="partial", missing_layers=["content", "nested"],
                    missing_layer_scopes=scopes, residual_identity_risk="Source layers are incomplete.",
                )
                self.assertFalse(PROJECTOR.project_context(document)["ready"])

    def test_partial_identity_allows_recovery_read_but_not_acceptance_check(self) -> None:
        for purpose, ready in (("observation_setup", True), ("observation_repair", True), ("solution", False)):
            with self.subTest(purpose=purpose):
                document = valid_state()
                document["source_snapshot"].update(
                    strength="partial", missing_layers=["current content"],
                    residual_identity_risk="Current file content is not observed.",
                )
                for field in ("next", "first_allowed_action"):
                    document["recovery_capsule"]["resume"][field].update(type="check", purpose=purpose)
                result = PROJECTOR.project_context(document)
                self.assertEqual(ready, result["ready"])
                self.assertIn("partial", result["identity"]["strength"])

    def test_discriminating_observation_authorizes_linked_solution_mutation(self) -> None:
        document = with_active_observation(valid_state(), "DISCRIMINATING", "solution")
        result = STATE.validate_state(document)
        self.assertTrue(result["valid"])
        self.assertTrue(result["ready"])
        self.assertEqual("match", result["comparisons"]["observation"])

    def test_planned_observation_blocks_solution_but_allows_bounded_setup(self) -> None:
        blocked = STATE.validate_state(with_active_observation(valid_state(), "PLANNED", "solution"))
        self.assertIn("observation.planned_blocks_solution", {item["code"] for item in blocked["errors"]})

        allowed = STATE.validate_state(
            with_active_observation(valid_state(), "PLANNED", "observation_setup")
        )
        self.assertTrue(allowed["valid"])
        self.assertTrue(allowed["ready"])

    def test_invalid_observation_allows_one_repair_cycle_then_requires_reframe(self) -> None:
        allowed = STATE.validate_state(
            with_active_observation(valid_state(), "INVALID", "observation_repair", repair_cycles=0)
        )
        self.assertTrue(allowed["valid"])
        self.assertTrue(allowed["ready"])

        blocked = STATE.validate_state(
            with_active_observation(valid_state(), "INVALID", "observation_repair", repair_cycles=1)
        )
        self.assertIn("observation.invalid_blocks_mutation", {item["code"] for item in blocked["errors"]})

    def test_inconclusive_observation_requires_check_reframe_or_blocker(self) -> None:
        document = with_active_observation(valid_state(), "INCONCLUSIVE", "solution")
        blocked = STATE.validate_state(document)
        self.assertIn("observation.inconclusive_blocks_mutation", {item["code"] for item in blocked["errors"]})

        check_document = with_active_observation(valid_state(), "INCONCLUSIVE", "solution")
        for field in ("next", "first_allowed_action"):
            action = check_document["recovery_capsule"]["resume"][field]
            action["type"] = "check"
            action.pop("purpose")
        allowed = STATE.validate_state(check_document)
        self.assertTrue(allowed["valid"])
        self.assertTrue(allowed["ready"])

    def test_scope_invalid_observation_cannot_authorize_solution_mutation(self) -> None:
        document = with_active_observation(valid_state(), "SCOPE_INVALID", "solution")
        blocked = STATE.validate_state(document)
        self.assertIn(
            "observation.scope_invalid_blocks_mutation",
            {item["code"] for item in blocked["errors"]},
        )

        blocker_document = with_active_observation(valid_state(), "SCOPE_INVALID", "solution")
        for field in ("next", "first_allowed_action"):
            action = blocker_document["recovery_capsule"]["resume"][field]
            action["type"] = "blocker"
            action.pop("purpose")
        allowed = STATE.validate_state(blocker_document)
        self.assertTrue(allowed["valid"])
        self.assertTrue(allowed["ready"])

    def test_observed_observation_change_requires_snapshot_refresh(self) -> None:
        document = with_active_observation(valid_state(), "DISCRIMINATING", "solution")
        document["observed"]["observation_result"] = "INVALID"
        result = STATE.validate_state(document)
        self.assertTrue(result["valid"])
        self.assertFalse(result["ready"])
        self.assertEqual("SNAPSHOT_REQUIRED", result["suggested_gate"])
        self.assertEqual("mismatch", result["comparisons"]["observation"])

    def test_open_semantic_fork_blocks_solution_mutation(self) -> None:
        document = with_semantic_fork(valid_state())
        for field in ("next", "first_allowed_action"):
            document["recovery_capsule"]["resume"][field]["purpose"] = "solution"
        result = STATE.validate_state(document)
        self.assertFalse(result["valid"])
        self.assertIn("semantic_fork.open_blocks_solution", {item["code"] for item in result["errors"]})

    def test_stopped_open_semantic_fork_resumes_focused_blocker_and_projects_state(self) -> None:
        document = with_semantic_fork(valid_state())
        for field in ("next", "first_allowed_action"):
            action = document["recovery_capsule"]["resume"][field]
            action["type"] = "blocker"
            action.pop("purpose", None)
            action["observable_signal"] = "the user selects one contract or reports a real blocker"
        result = STATE.validate_state(document)
        self.assertTrue(result["valid"])
        self.assertTrue(result["ready"])
        projected = PROJECTOR.project_context(document)
        self.assertEqual("OPEN", projected["decision_state"]["semantic_fork"]["status"])
        self.assertEqual("snapshot", projected["decision_state"]["semantic_fork"]["options"][0]["id"])
        self.assertEqual("STOPPED", projected["decision_state"]["evidence_budget"]["status"])
        self.assertEqual("semantic-decision", projected["decision_state"]["current_stage"])

    def test_stopped_open_semantic_fork_rejects_more_evidence_without_reopen(self) -> None:
        document = with_semantic_fork(valid_state())
        for field in ("next", "first_allowed_action"):
            action = document["recovery_capsule"]["resume"][field]
            action["type"] = "check"
            action.pop("purpose", None)
        result = STATE.validate_state(document)
        self.assertIn(
            "evidence_budget.stopped_blocks_evidence",
            {item["code"] for item in result["errors"]},
        )

    def test_second_open_evidence_round_requires_and_projects_reopen_identity(self) -> None:
        document = with_semantic_fork(valid_state())
        decision = document["recovery_capsule"]["decision_state"]
        decision["evidence_budget"] = {
            "round": 2, "scout_count": 0, "status": "OPEN",
        }
        decision["evidence_reopen"] = {
            "reason": "NEW_CANDIDATE",
            "locator": "source://new-candidate",
            "from_round": 1,
        }
        for field in ("next", "first_allowed_action"):
            action = document["recovery_capsule"]["resume"][field]
            action["type"] = "check"
            action.pop("purpose", None)
        result = STATE.validate_state(document)
        self.assertTrue(result["valid"], result["errors"])
        projected = PROJECTOR.project_context(document)
        self.assertEqual("NEW_CANDIDATE", projected["decision_state"]["evidence_reopen"]["reason"])

    def test_semantic_options_are_not_silently_truncated(self) -> None:
        document = with_semantic_fork(valid_state())
        options = document["recovery_capsule"]["decision_state"]["semantic_fork"]["options"]
        options.extend(
            {"id": f"option-{index}", "contract": f"contract-{index}"}
            for index in range(3)
        )
        for field in ("next", "first_allowed_action"):
            action = document["recovery_capsule"]["resume"][field]
            action["type"] = "blocker"
            action.pop("purpose", None)
        projected = PROJECTOR.project_context(document)
        self.assertEqual(5, len(projected["decision_state"]["semantic_fork"]["options"]))

    def test_material_fork_cannot_be_relabeled_not_applicable(self) -> None:
        document = with_semantic_fork(valid_state())
        document["recovery_capsule"]["decision_state"]["semantic_fork"]["status"] = "NOT_APPLICABLE"
        result = STATE.validate_state(document)
        self.assertIn(
            "semantic_fork.false_not_applicable",
            {item["code"] for item in result["errors"]},
        )

    def test_resolved_semantic_fork_requires_resolution_locator(self) -> None:
        document = with_semantic_fork(valid_state(), status="RESOLVED")
        document["recovery_capsule"]["decision_state"]["semantic_fork"]["resolution"].pop("locator")
        result = STATE.validate_state(document)
        self.assertIn(
            "semantic_fork.missing_resolution_field",
            {item["code"] for item in result["errors"]},
        )

    def test_evidence_resolution_requires_evidence_can_decide_true(self) -> None:
        document = with_semantic_fork(valid_state(), status="RESOLVED")
        fork = document["recovery_capsule"]["decision_state"]["semantic_fork"]
        fork["resolution"]["source"] = "EVIDENCE"
        result = STATE.validate_state(document)
        self.assertIn(
            "semantic_fork.invalid_evidence_resolution",
            {item["code"] for item in result["errors"]},
        )

    def test_not_applicable_semantic_fork_cannot_carry_resolution(self) -> None:
        document = with_semantic_fork(valid_state())
        fork = document["recovery_capsule"]["decision_state"]["semantic_fork"]
        fork["status"] = "NOT_APPLICABLE"
        fork["options"] = []
        fork["architectural_consequences"] = {}
        fork["resolution"] = {
            "source": "USER", "decision": "unused", "locator": "instruction://r4"
        }
        result = STATE.validate_state(document)
        self.assertIn(
            "semantic_fork.premature_resolution",
            {item["code"] for item in result["errors"]},
        )


class ContinuityTraceTest(unittest.TestCase):
    def test_efficiency_targets_do_not_decide_correctness(self) -> None:
        trace = {
            "recovery_type": "COMPACT_CONTINUATION", "identity_match": True,
            "resume_turn": 1, "expected_action_id": "implement", "pre_compaction_next_action_id": "implement",
            "instruction_revision_at_snapshot": "r1", "post_compaction_instruction_revision": "r1",
            "acceptance_success": True,
            "events": [{"type": "identity_compare", "tool_round": 1, "turn": 1, "continuity_phase": "RESUME_AUDIT"},
                       {"type": "reference_compare", "tool_round": 2, "turn": 1, "continuity_phase": "RESUME_AUDIT"},
                       {"type": "mutation", "action_id": "implement", "turn": 2, "productive": True}],
        }
        metrics = TRACE.evaluate_trace(trace)
        self.assertFalse(metrics["compact_continuation_fast_path_passed"])
        self.assertTrue(metrics["observed_invariants_passed"])
        self.assertTrue(metrics["acceptance_success"])
        trace["events"][-1]["action_id"] = "unrelated-action"
        metrics = TRACE.evaluate_trace(trace)
        self.assertFalse(metrics["observed_invariants_passed"])
        self.assertIn("action_identity", metrics["invariant_violations"])

    def test_matching_compact_continuation_passes_same_turn_fast_path(self) -> None:
        metrics = TRACE.evaluate_trace(
            {
                "recovery_type": "COMPACT_CONTINUATION",
                "resume_turn": 7,
                "identity_match": True,
                "instruction_changed": False,
                "matching_audit_number": 2,
                "expected_action_id": "patch",
                "events": [
                    {
                        "type": "identity_compare",
                        "target": "source",
                        "revision": "s1",
                        "continuity_phase": "RESUME_AUDIT",
                        "tool_round": 1,
                        "turn": 7,
                    },
                    {
                        "type": "reference_compare",
                        "target": "thread",
                        "revision": "cursor-4",
                        "continuity_phase": "RESUME_AUDIT",
                        "tool_round": 1,
                        "turn": 7,
                    },
                    {"type": "mutation", "action_id": "patch", "turn": 7, "serves_next": True},
                ],
            }
        )
        self.assertEqual(1, metrics["resume_audit_tool_rounds"])
        self.assertEqual(0, metrics["full_thread_reads"])
        self.assertEqual(0, metrics["unchanged_reference_reads"])
        self.assertEqual(0, metrics["recovery_commentary_only_turns"])
        self.assertTrue(metrics["first_productive_action_on_resume_turn"])
        self.assertTrue(metrics["compact_continuation_fast_path_passed"])

    def test_compact_continuation_detects_reread_and_commentary_delay(self) -> None:
        metrics = TRACE.evaluate_trace(
            {
                "recovery_type": "COMPACT_CONTINUATION",
                "resume_turn": 9,
                "identity_match": True,
                "instruction_changed": False,
                "matching_audit_number": 3,
                "expected_action_id": "patch",
                "events": [
                    {
                        "type": "thread_read",
                        "target": "thread",
                        "target_kind": "thread",
                        "revision": "cursor-4",
                        "scope": "full_thread",
                        "cursor_changed": False,
                        "continuity_phase": "RESUME_AUDIT",
                        "tool_round": 1,
                        "turn": 9,
                    },
                    {
                        "type": "identity_compare",
                        "target": "source",
                        "revision": "s1",
                        "continuity_phase": "RESUME_AUDIT",
                        "tool_round": 2,
                        "turn": 9,
                    },
                    {"type": "recovery_commentary", "turn": 9},
                    {"type": "mutation", "action_id": "patch", "turn": 10, "serves_next": True},
                ],
            }
        )
        self.assertEqual(2, metrics["resume_audit_tool_rounds"])
        self.assertEqual(1, metrics["full_thread_reads"])
        self.assertEqual(1, metrics["unchanged_reference_reads"])
        self.assertEqual(1, metrics["matching_audit_full_reference_reads"])
        self.assertEqual(1, metrics["recovery_commentary_only_turns"])
        self.assertFalse(metrics["first_productive_action_on_resume_turn"])
        self.assertFalse(metrics["compact_continuation_fast_path_passed"])

    def test_compact_continuation_detects_recovery_entry_replay_before_correct_action(self) -> None:
        metrics = TRACE.evaluate_trace(
            {
                "recovery_type": "COMPACT_CONTINUATION",
                "resume_turn": 5,
                "identity_match": True,
                "instruction_changed": False,
                "pre_compaction_next_action_id": "accept-stage",
                "previous_productive_action_id": "implement-slice",
                "events": [
                    {"type": "skill_reload", "scope": "full_skill_set", "turn": 5},
                    {"type": "workspace_scan", "scope": "full_workspace", "turn": 5},
                    {"type": "mutation", "action_id": "accept-stage", "turn": 5},
                ],
            }
        )
        classes = {item["class"] for item in metrics["recovery_route_deviations"]}
        self.assertEqual({"full_rule_reload", "workspace_rescan"}, classes)
        self.assertTrue(metrics["action_identity_continuity"])
        self.assertFalse(metrics["compact_continuation_fast_path_passed"])
        self.assertEqual(1, metrics["post_compaction_full_skill_reload_count"])

    def test_compact_continuation_detects_previous_action_replay(self) -> None:
        metrics = TRACE.evaluate_trace(
            {
                "recovery_type": "COMPACT_CONTINUATION",
                "resume_turn": 4,
                "identity_match": True,
                "instruction_changed": False,
                "pre_compaction_next_action_id": "verify-stage",
                "previous_productive_action_id": "implement-slice",
                "events": [
                    {"type": "mutation", "action_id": "implement-slice", "turn": 4},
                ],
            }
        )
        self.assertFalse(metrics["action_identity_continuity"])
        self.assertEqual(1, metrics["previous_action_replay_count"])
        self.assertIn(
            "previous_action_replay",
            {item["class"] for item in metrics["recovery_route_deviations"]},
        )

    def test_wrong_productive_action_does_not_close_recovery_deviation_window(self) -> None:
        metrics = TRACE.evaluate_trace(
            {
                "recovery_type": "COMPACT_CONTINUATION",
                "resume_turn": 4,
                "identity_match": True,
                "instruction_changed": False,
                "pre_compaction_next_action_id": "saved-next",
                "events": [
                    {"type": "mutation", "action_id": "wrong", "turn": 4},
                    {"type": "skill_reload", "scope": "full_skill_set", "turn": 4},
                    {"type": "mutation", "action_id": "saved-next", "turn": 4},
                ],
            }
        )
        self.assertEqual(1, metrics["post_compaction_full_skill_reload_count"])
        self.assertIn(
            "full_rule_reload",
            {item["class"] for item in metrics["recovery_route_deviations"]},
        )
        self.assertFalse(metrics["compact_continuation_fast_path_passed"])

    def test_changed_user_instruction_does_not_force_stale_action_identity(self) -> None:
        metrics = TRACE.evaluate_trace(
            {
                "recovery_type": "COMPACT_CONTINUATION",
                "resume_turn": 8,
                "identity_match": True,
                "pre_compaction_next_action_id": "verify-stage",
                "instruction_revision_at_snapshot": "instruction-r1",
                "post_compaction_instruction_revision": "instruction-r2",
                "events": [
                    {"type": "action", "action_id": "answer-new-request", "turn": 8},
                ],
            }
        )
        self.assertTrue(metrics["instruction_changed"])
        self.assertFalse(metrics["action_identity_continuity_applicable"])
        self.assertIsNone(metrics["compact_continuation_fast_path_passed"])
        self.assertEqual(0, metrics["route_deviation_count"])

    def test_query_answer_returns_to_saved_next_in_same_turn_without_refresh(self) -> None:
        metrics = TRACE.evaluate_trace(
            {
                "recovery_type": "COMPACT_CONTINUATION",
                "resume_turn": 8,
                "identity_match": True,
                "pre_compaction_next_action_id": "verify-stage",
                "directive_changed": False,
                "events": [
                    {
                        "type": "user_message",
                        "message_class": "QUERY",
                        "saved_next_action_id": "verify-stage",
                        "affects_saved_next": False,
                        "turn": 8,
                    },
                    {
                        "type": "action",
                        "action_id": "answer-query",
                        "serves_user_message": True,
                        "turn": 8,
                    },
                    {"type": "mutation", "action_id": "verify-stage", "turn": 8},
                ],
            }
        )
        self.assertEqual(0, metrics["message_route_deviation_count"])
        self.assertTrue(metrics["action_identity_continuity"])

    def test_query_plan_refresh_and_delayed_return_are_detected(self) -> None:
        metrics = TRACE.evaluate_trace(
            {
                "pre_compaction_next_action_id": "verify-stage",
                "events": [
                    {
                        "type": "user_message",
                        "message_class": "QUERY",
                        "saved_next_action_id": "verify-stage",
                        "affects_saved_next": False,
                        "turn": 3,
                    },
                    {"type": "plan_refresh", "turn": 3},
                    {"type": "action", "action_id": "answer", "serves_user_message": True, "turn": 3},
                    {"type": "mutation", "action_id": "verify-stage", "turn": 4},
                ],
            }
        )
        self.assertEqual(1, metrics["unnecessary_plan_refresh_count"])
        self.assertEqual(1, metrics["wrong_mainline_return_count"])

    def test_duplicate_reminder_revision_is_detected(self) -> None:
        metrics = TRACE.evaluate_trace(
            {
                "pre_compaction_next_action_id": "verify-stage",
                "events": [
                    {
                        "type": "user_message",
                        "message_class": "REMINDER",
                        "saved_next_action_id": "verify-stage",
                        "affects_saved_next": False,
                        "directive_revision_before": "d1",
                        "directive_revision_after": "d2",
                        "turn": 2,
                    },
                    {"type": "mutation", "action_id": "verify-stage", "turn": 2},
                ],
            }
        )
        self.assertEqual(1, metrics["duplicate_reminder_revision_count"])

    def test_temporary_interrupt_requires_anchor_and_exact_return(self) -> None:
        missing = TRACE.evaluate_trace(
            {
                "events": [
                    {"type": "user_message", "message_class": "TEMPORARY_INTERRUPT", "turn": 2},
                    {"type": "interrupt_complete", "turn": 2},
                ]
            }
        )
        self.assertEqual(1, missing["missing_return_anchor_count"])

        wrong = TRACE.evaluate_trace(
            {
                "events": [
                    {
                        "type": "user_message",
                        "message_class": "TEMPORARY_INTERRUPT",
                        "return_anchor": {"saved_next_action_id": "saved-next"},
                        "turn": 2,
                    },
                    {"type": "action", "action_id": "interrupt-work", "serves_user_message": True, "turn": 2},
                    {"type": "interrupt_complete", "turn": 2},
                    {"type": "mutation", "action_id": "different-next", "turn": 2},
                ]
            }
        )
        self.assertEqual(1, wrong["wrong_mainline_return_count"])

    def test_contract_change_blocks_old_mainline_until_snapshot_refresh(self) -> None:
        metrics = TRACE.evaluate_trace(
            {
                "events": [
                    {
                        "type": "user_message",
                        "message_class": "CONTRACT_CHANGE",
                        "affects_saved_next": True,
                    },
                    {"type": "mutation", "action_id": "old-next"},
                    {"type": "contract_snapshot_refreshed", "refreshes_user_change": True},
                    {"type": "mutation", "action_id": "new-next"},
                ]
            }
        )
        self.assertEqual(1, metrics["stale_contract_action_count"])

    def test_detects_idle_reads_duplicate_check_and_prd_leak(self) -> None:
        metrics = TRACE.evaluate_trace(
            {
                "expected_action_id": "patch",
                "events": [
                    {"type": "read", "target": "PRD", "revision": "r1", "scope": "full_prd", "recovery_id": "r1"},
                    {"type": "read", "target": "PRD", "revision": "r1", "scope": "full_prd", "recovery_id": "r1"},
                    {"type": "mutation", "action_id": "patch", "turn": 2, "recovery_id": "r2"},
                    {"type": "check", "check_id": "unit", "source_fingerprint": "s1", "input_revision": "i1", "environment": "e1"},
                    {"type": "check", "check_id": "unit", "source_fingerprint": "s1", "input_revision": "i1", "environment": "e1"},
                    {"type": "prd_write", "content_classes": ["test_counts", "stage_progress"]},
                ],
            }
        )
        self.assertEqual(1, metrics["repeated_read_count"])
        self.assertEqual(1, metrics["repeated_verification_count"])
        self.assertEqual(["r1"], metrics["idle_recovery_ids"])
        self.assertEqual(1, metrics["authoritative_runtime_leak_count"])
        self.assertTrue(metrics["next_action_hit"])

    def test_rejects_python_graph_for_java_task(self) -> None:
        metrics = TRACE.evaluate_trace(
            {
                "source_fingerprint": "java-tree",
                "events": [
                    {
                        "type": "graph_injection",
                        "decision_question": "who calls AgentService",
                        "task_anchor": "AgentService",
                        "task_source_fingerprint": "java-tree",
                        "graph_source_fingerprint": "python-tree",
                        "task_languages": ["java"],
                        "graph_languages": ["python"],
                    }
                ],
            }
        )
        reasons = metrics["irrelevant_graph_injections"][0]["reasons"]
        self.assertIn("source_fingerprint_mismatch", reasons)
        self.assertIn("target_language_mismatch", reasons)

    def test_compares_full_capsule_and_ablation_context(self) -> None:
        document = {
            "expected_action_id": "patch",
            "required_constraint_ids": ["no-special-case"],
            "required_evidence_ids": ["failure-signature"],
            "runs": {
                "full_context": {
                    "events": [
                        {"type": "read", "target": "history", "scope": "full_history"},
                        {"type": "decision", "constraint_ids": ["no-special-case"], "evidence_ids": ["failure-signature"]},
                        {"type": "mutation", "action_id": "patch", "turn": 3},
                    ]
                },
                "capsule": {
                    "events": [
                        {"type": "capsule_read", "target": "capsule"},
                        {"type": "decision", "constraint_ids": ["no-special-case"], "evidence_ids": ["failure-signature"]},
                        {"type": "mutation", "action_id": "patch", "turn": 2},
                    ]
                },
                "ablation": {"events": [{"type": "mutation", "action_id": "patch", "turn": 1}]},
            },
        }
        result = TRACE.evaluate_document(document)
        self.assertTrue(result["assessment"]["capsule_preserves_required_context"])
        self.assertTrue(result["assessment"]["capsule_not_slower_to_first_action"])
        self.assertTrue(result["assessment"]["ablation_exposes_context_loss"])

    def test_invalid_observation_cannot_authorize_solution_change(self) -> None:
        metrics = TRACE.evaluate_trace(
            {
                "requires_discriminating_evidence": True,
                "events": [
                    {
                        "type": "observation_result",
                        "observation_id": "select-route",
                        "observation_revision": "r1",
                        "result": "INVALID",
                        "changes_decision_state": True,
                    },
                    {"type": "snapshot_refreshed"},
                    {
                        "type": "mutation",
                        "purpose": "solution",
                        "observation_id": "select-route",
                        "observation_revision": "r1",
                    },
                ],
            }
        )
        self.assertEqual(1, metrics["invalid_observation_count"])
        self.assertEqual(1, metrics["solution_change_without_discriminating_evidence_count"])
        self.assertEqual(1, metrics["invalid_observation_used_as_evidence_count"])

    def test_scope_invalid_observation_cannot_authorize_solution_change(self) -> None:
        metrics = TRACE.evaluate_trace(
            {
                "requires_discriminating_evidence": True,
                "events": [
                    {
                        "type": "observation_result",
                        "observation_id": "select-contract",
                        "observation_revision": "r1",
                        "result": "SCOPE_INVALID",
                        "changes_decision_state": True,
                    },
                    {"type": "snapshot_refreshed"},
                    {
                        "type": "mutation",
                        "purpose": "solution",
                        "observation_id": "select-contract",
                        "observation_revision": "r1",
                    },
                ],
            }
        )
        self.assertEqual(1, metrics["scope_invalid_observation_count"])
        self.assertEqual(1, metrics["solution_change_without_discriminating_evidence_count"])
        self.assertEqual(1, metrics["scope_invalid_observation_used_as_evidence_count"])

    def test_discriminating_observation_authorizes_solution_after_snapshot_refresh(self) -> None:
        metrics = TRACE.evaluate_trace(
            {
                "requires_discriminating_evidence": True,
                "events": [
                    {
                        "type": "observation_result",
                        "observation_id": "select-route",
                        "observation_revision": "r1",
                        "result": "DISCRIMINATING",
                        "changes_decision_state": True,
                    },
                    {"type": "snapshot_refreshed"},
                    {
                        "type": "mutation",
                        "purpose": "solution",
                        "observation_id": "select-route",
                        "observation_revision": "r1",
                    },
                ],
            }
        )
        self.assertEqual(1, metrics["discriminating_observation_count"])
        self.assertEqual(0, metrics["solution_change_without_discriminating_evidence_count"])
        self.assertEqual(0, metrics["solution_change_before_snapshot_refresh_count"])

    def test_repeated_invalid_observation_and_second_repair_are_detected(self) -> None:
        metrics = TRACE.evaluate_trace(
            {
                "events": [
                    {
                        "type": "observation_result",
                        "observation_id": "select-route",
                        "observation_revision": "r1",
                        "result": "INVALID",
                    },
                    {"type": "observation_apparatus_changed", "observation_id": "select-route"},
                    {
                        "type": "observation_result",
                        "observation_id": "select-route",
                        "observation_revision": "r2",
                        "result": "INVALID",
                    },
                    {"type": "observation_apparatus_changed", "observation_id": "select-route"},
                ]
            }
        )
        self.assertEqual(1, metrics["repeated_nondiscriminating_observation_count"])
        self.assertEqual(1, metrics["observation_repair_budget_exceeded_count"])

    def test_solution_change_before_required_snapshot_refresh_is_detected(self) -> None:
        metrics = TRACE.evaluate_trace(
            {
                "requires_discriminating_evidence": True,
                "events": [
                    {
                        "type": "observation_result",
                        "observation_id": "select-route",
                        "observation_revision": "r1",
                        "result": "DISCRIMINATING",
                        "changes_decision_state": True,
                    },
                    {
                        "type": "mutation",
                        "purpose": "solution",
                        "observation_id": "select-route",
                        "observation_revision": "r1",
                    },
                ],
            }
        )
        self.assertEqual(1, metrics["solution_change_before_snapshot_refresh_count"])

    def test_capsule_comparison_detects_observation_integrity_regression(self) -> None:
        observation = {
            "type": "observation_result",
            "observation_id": "select-route",
            "observation_revision": "r1",
            "result": "DISCRIMINATING",
            "changes_decision_state": True,
        }
        mutation = {
            "type": "mutation",
            "purpose": "solution",
            "observation_id": "select-route",
            "observation_revision": "r1",
        }
        result = TRACE.evaluate_document(
            {
                "requires_discriminating_evidence": True,
                "runs": {
                    "full_context": {
                        "events": [observation, {"type": "snapshot_refreshed"}, mutation]
                    },
                    "capsule": {"events": [mutation]},
                },
            }
        )
        self.assertFalse(result["assessment"]["capsule_preserves_observation_integrity"])
        comparison = result["comparisons"]["capsule_vs_full_context"]
        self.assertEqual(1, comparison["solution_change_without_discriminating_evidence_delta"])


if __name__ == "__main__":
    unittest.main()
