#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import concurrent.futures
import json
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path


SCRIPT_ROOT = Path(__file__).parent


def load_script(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_ROOT / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ADAPTER = load_script("codex_execution_adapter")


def valid_state() -> dict:
    action = {
        "action_id": "implement-adapter",
        "type": "mutation",
        "owner": "task-continuity/scripts/codex_execution_adapter.py",
        "scope": ["task-continuity/scripts"],
        "observable_signal": "adapter behavior tests pass",
    }
    return {
        "recovery_capsule": {
            "contract": {
                "boundary_id": "b1",
                "task_id": "execution-adapter",
                "revision": "contract-r1",
                "locator": "task://execution-adapter@contract-r1",
                "objective": "enforce continuity and delivery gates",
                "constraints": ["do not use delivery as a progress log"],
                "acceptance": ["wire-level gates behave deterministically"],
            },
            "checkpoint": {
                "boundary_id": "b1",
                "phase": "implementation",
                "validated": [],
                "in_flight": {
                    "slice_id": "adapter",
                    "status": "active",
                    "owner": "task-continuity/scripts/codex_execution_adapter.py",
                    "expected_changed_items": ["task-continuity/scripts"],
                },
            },
            "decision_state": {
                "boundary_id": "b1",
                "active_hypothesis": "semantic rules need a host execution gate",
                "acceptance_status": "in_progress",
                "do_not_reopen": [
                    {
                        "action_id": "repeat-research",
                        "reason": "the adapter contract is frozen",
                        "reopen_when": "official hook payload changes",
                    }
                ],
            },
            "resume": {
                "boundary_id": "b1",
                "gate": "RESUME_AUDIT",
                "recovery_type": "COMPACT_CONTINUATION",
                "anchors": ["task-continuity/scripts/codex_execution_adapter.py"],
                "next": dict(action),
                "first_allowed_action": dict(action),
            },
        },
        "continuity_metadata": {
            "boundary_id": "b1",
            "audit_fingerprint": "audit-r1",
            "consecutive_matching_audits": 1,
            "instruction_revision_at_snapshot": "instruction-r1",
            "pre_compaction_next_action_id": "implement-adapter",
            "previous_productive_action_id": "design-adapter",
            "referenced_sources": [{"id": "codex-hooks", "revision": "2026-08-26"}],
            "loaded_rules": [{"id": "task-continuity", "revision": "rules-r1"}],
        },
        "source_snapshot": {
            "boundary_id": "b1",
            "source_id": "workspace",
            "source_fingerprint": "source-r1",
            "strength": "strong",
            "locator": "workspace://current",
            "expected_changed_items": ["task-continuity/scripts"],
            "missing_layers": [],
        },
        "observed": {
            "boundary_id": "b1",
            "source_fingerprint": "source-r1",
            "contract_revision": "contract-r1",
            "instruction_revision": "instruction-r1",
            "referenced_sources": {"codex-hooks": "2026-08-26"},
            "loaded_rules": {"task-continuity": "rules-r1"},
        },
    }


class AdapterTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.workspace = self.root / "repo"
        self.workspace.mkdir()
        subprocess.run(["git", "init", "-q", str(self.workspace)], check=True)
        subprocess.run(["git", "-C", str(self.workspace), "config", "user.email", "test@example.com"], check=True)
        subprocess.run(["git", "-C", str(self.workspace), "config", "user.name", "Test"], check=True)
        (self.workspace / "app.py").write_text("VALUE = 1\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(self.workspace), "add", "app.py"], check=True)
        subprocess.run(["git", "-C", str(self.workspace), "commit", "-qm", "initial"], check=True)
        self.state = self.root / "runtime" / "continuity.json"
        self.receipts = self.root / "runtime" / "receipts.jsonl"
        self.graph = self.root / "runtime" / "graph-dirty.json"
        self.state.parent.mkdir()
        self.state.write_text(json.dumps(valid_state()), encoding="utf-8")
        self.config = ADAPTER.AdapterConfig(
            state=self.state,
            receipts=self.receipts,
            workspace=self.workspace,
            graph_dirty=self.graph,
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def validation(self) -> dict:
        event = {
            "tool_name": "exec_command",
            "tool_use_id": "validation-1",
            "tool_input": {"cmd": "python3 -m unittest discover"},
            "tool_response": {"exit_code": 0},
            "tool_output": {"isError": False},
            "is_error": False,
            "cwd": str(self.workspace),
        }
        ADAPTER.handle_posttooluse(self.config, event)
        receipts, errors = ADAPTER._load_receipts(self.receipts)
        self.assertFalse(errors)
        return receipts[-1]

    def checkpoint(self) -> dict:
        return ADAPTER.checkpoint_stage(
            self.config, types.SimpleNamespace(stage="implementation", evidence=[])
        )

    def test_no_configuration_is_a_safe_hook_noop(self) -> None:
        empty = ADAPTER.AdapterConfig()
        event = {"tool_name": "apply_patch", "tool_input": {"patch": "ignored"}}
        self.assertEqual({}, ADAPTER.handle_pretooluse(empty, event))
        self.assertEqual({}, ADAPTER.handle_posttooluse(empty, event))
        self.assertEqual({}, ADAPTER.handle_sessionstart(empty, {"source": "compact"}))

    def test_pretooluse_blocks_leaf_recursive_delegation(self) -> None:
        event = {
            "tool_name": "spawn_agent",
            "orchestration_context": {
                "actor_role": "bounded_worker",
                "delegated_program": True,
                "delegation": "denied",
                "depth": 1,
                "max_depth": 1,
            },
        }
        denied = ADAPTER.handle_pretooluse(self.config, event)
        self.assertEqual("deny", denied["hookSpecificOutput"]["permissionDecision"])
        self.assertIn("leaf Agent delegation", denied["hookSpecificOutput"]["permissionDecisionReason"])

    def test_pretooluse_blocks_primary_source_write_in_delegated_program(self) -> None:
        event = {
            "tool_name": "apply_patch",
            "tool_input": {"patch": "change"},
            "orchestration_context": {
                "actor_role": "ORCHESTRATOR_INTEGRATOR",
                "delegated_program": True,
                "action_class": "coordination",
            },
        }
        denied = ADAPTER.handle_pretooluse(self.config, event)
        self.assertEqual("deny", denied["hookSpecificOutput"]["permissionDecision"])
        self.assertIn("fresh bounded Worker", denied["hookSpecificOutput"]["permissionDecisionReason"])

    def test_pretooluse_blocks_overlapping_write_set(self) -> None:
        event = {
            "tool_name": "apply_patch",
            "tool_input": {"patch": "change"},
            "orchestration_context": {
                "actor_role": "bounded_worker",
                "write_set": ["backend/Service.java"],
                "allowed_write_set": ["backend/Service.java"],
                "active_write_sets": [["backend/Service.java"]],
                "contract_state": "frozen",
            },
        }
        denied = ADAPTER.handle_pretooluse(self.config, event)
        self.assertEqual("deny", denied["hookSpecificOutput"]["permissionDecision"])
        self.assertIn("overlaps", denied["hookSpecificOutput"]["permissionDecisionReason"])

    def test_recovery_efficiency_alone_does_not_block_tools(self) -> None:
        event = {
            "tool_name": "exec_command",
            "tool_input": {"cmd": "sed -n 1,500p SKILL.md"},
            "continuity_context": {
                "recovery_type": "COMPACT_CONTINUATION",
                "identity_match": True,
                "first_allowed_action_pending": True,
                "first_allowed_action_id": "implement-adapter",
                "operation_class": "full_skill_reload",
            },
        }
        self.assertEqual({}, ADAPTER.handle_pretooluse(self.config, event))
        event["continuity_context"]["operation_class"] = "previous_action_replay"
        denied = ADAPTER.handle_pretooluse(self.config, event)
        self.assertEqual("deny", denied["hookSpecificOutput"]["permissionDecision"])

    def test_matching_compact_pretooluse_allows_exact_saved_action(self) -> None:
        event = {
            "tool_name": "exec_command",
            "tool_input": {"cmd": "true"},
            "continuity_context": {
                "recovery_type": "COMPACT_CONTINUATION",
                "identity_match": True,
                "first_allowed_action_pending": True,
                "first_allowed_action_id": "implement-adapter",
                "operation_class": "productive",
                "action_id": "implement-adapter",
            },
        }
        self.assertEqual({}, ADAPTER.handle_pretooluse(self.config, event))

    def test_receipt_runtime_discovers_existing_sibling_state_only(self) -> None:
        args = types.SimpleNamespace(
            state=None,
            receipts=str(self.receipts),
            workspace=str(self.workspace),
            graph_dirty=None,
        )
        discovered = ADAPTER.config_from_args(args)
        self.assertEqual(self.state.resolve(), discovered.state)
        self.state.unlink()
        self.assertIsNone(ADAPTER.config_from_args(args).state)

    def test_pretooluse_wire_denies_mutation_when_continuity_is_not_ready(self) -> None:
        document = valid_state()
        document["observed"]["source_fingerprint"] = "source-drift"
        self.state.write_text(json.dumps(document), encoding="utf-8")
        event = {"tool_name": "apply_patch", "tool_input": {"patch": "change"}}
        result = ADAPTER.handle_pretooluse(self.config, event)
        hook = result["hookSpecificOutput"]
        self.assertEqual("PreToolUse", hook["hookEventName"])
        self.assertEqual("deny", hook["permissionDecision"])
        self.assertIn("SNAPSHOT_REQUIRED", hook["permissionDecisionReason"])

        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_ROOT / "codex_execution_adapter.py"),
                "--state",
                str(self.state),
                "pretooluse",
            ],
            input=json.dumps(event),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            cwd=self.workspace,
        )
        wire = json.loads(completed.stdout)
        self.assertEqual("deny", wire["hookSpecificOutput"]["permissionDecision"])

    def test_stage_evidence_allows_commit_but_source_change_invalidates_it(self) -> None:
        self.validation()
        checkpoint = self.checkpoint()
        commit = {
            "tool_name": "exec_command",
            "tool_input": {"cmd": "git commit -m stage"},
            "cwd": str(self.workspace),
        }
        self.assertEqual({}, ADAPTER.handle_pretooluse(self.config, commit))
        before = checkpoint["source_fingerprint"]

        (self.workspace / "app.py").write_text("VALUE = 2\n", encoding="utf-8")
        source_event = {
            "tool_name": "apply_patch",
            "tool_response": {"isError": False},
            "cwd": str(self.workspace),
        }
        ADAPTER.handle_posttooluse(self.config, source_event)
        denial = ADAPTER.handle_pretooluse(self.config, commit)
        self.assertEqual("deny", denial["hookSpecificOutput"]["permissionDecision"])
        self.assertNotEqual(before, ADAPTER.source_fingerprint(self.config))
        self.assertTrue(json.loads(self.graph.read_text())["dirty"])

    def test_hook_receipt_reuses_stable_event_id(self) -> None:
        event = {
            "tool_name": "exec_command",
            "tool_use_id": "validation-idempotent",
            "tool_input": {"cmd": "python3 -m unittest discover"},
            "tool_response": {"exit_code": 0},
            "tool_output": {"isError": False},
            "is_error": False,
            "cwd": str(self.workspace),
        }
        ADAPTER.handle_posttooluse(self.config, event)
        first, errors = ADAPTER._load_receipts(self.receipts)
        self.assertFalse(errors)
        ADAPTER.handle_posttooluse(self.config, event)
        second, errors = ADAPTER._load_receipts(self.receipts)
        self.assertFalse(errors)
        self.assertEqual(len(first), len(second))
        self.assertEqual(first[-1]["receipt_id"], second[-1]["receipt_id"])
        self.assertEqual("validation-idempotent", second[-1]["event_id"])

    def test_checkpoint_binding_rejects_a_different_task(self) -> None:
        self.validation()
        self.checkpoint()
        document = valid_state()
        document["recovery_capsule"]["contract"]["task_id"] = "other-task"
        self.state.write_text(json.dumps(document), encoding="utf-8")
        commit = {
            "tool_name": "exec_command",
            "tool_input": {"cmd": "git commit -m stage"},
            "cwd": str(self.workspace),
        }
        denied = ADAPTER.handle_pretooluse(self.config, commit)
        self.assertEqual("deny", denied["hookSpecificOutput"]["permissionDecision"])
        self.assertIn("validated stage", denied["hookSpecificOutput"]["permissionDecisionReason"])

    def test_staging_and_commit_do_not_invalidate_content_fingerprint(self) -> None:
        (self.workspace / "app.py").write_text("VALUE = 3\n", encoding="utf-8")
        before_stage = ADAPTER.source_fingerprint(self.config)
        subprocess.run(["git", "-C", str(self.workspace), "add", "app.py"], check=True)
        after_stage = ADAPTER.source_fingerprint(self.config)
        subprocess.run(["git", "-C", str(self.workspace), "commit", "-qm", "stage"], check=True)
        after_commit = ADAPTER.source_fingerprint(self.config)
        self.assertEqual(before_stage, after_stage)
        self.assertEqual(after_stage, after_commit)

    def test_publish_requires_task_completion_and_accepted_agents(self) -> None:
        evidence = self.validation()
        self.checkpoint()
        publish = {
            "tool_name": "exec_command",
            "tool_input": {"cmd": "git push origin HEAD"},
            "cwd": str(self.workspace),
        }
        denied = ADAPTER.handle_pretooluse(self.config, publish)
        self.assertEqual("deny", denied["hookSpecificOutput"]["permissionDecision"])

        spawn = {
            "tool_name": "spawn_agent",
            "tool_use_id": "spawn-1",
            "tool_response": {"agent_id": "assignment-1", "isError": False},
            "cwd": str(self.workspace),
        }
        ADAPTER.handle_posttooluse(self.config, spawn)
        with self.assertRaisesRegex(ValueError, "not accepted"):
            ADAPTER.complete_task(self.config, types.SimpleNamespace(acceptance=[]))

        ADAPTER.accept_assignment(
            self.config,
            types.SimpleNamespace(
                assignment_id="assignment-1", result_receipt=None, status="accepted"
            ),
        )
        completion = ADAPTER.complete_task(
            self.config,
            types.SimpleNamespace(acceptance=[evidence["receipt_id"]]),
        )
        self.assertEqual("task_completion", completion["kind"])
        self.assertEqual({}, ADAPTER.handle_pretooluse(self.config, publish))

        review = dict(publish)
        review["tool_input"] = {"cmd": "gh pr edit --body-file pr.md"}
        self.assertEqual({}, ADAPTER.handle_pretooluse(self.config, review))

    def test_compact_session_injects_only_bounded_projection(self) -> None:
        document = valid_state()
        fingerprint = ADAPTER.source_fingerprint(self.config)
        document["source_snapshot"]["source_fingerprint"] = fingerprint
        document["observed"]["source_fingerprint"] = fingerprint
        self.state.write_text(json.dumps(document), encoding="utf-8")
        result = ADAPTER.handle_sessionstart(self.config, {"source": "compact"})
        context = json.loads(result["hookSpecificOutput"]["additionalContext"])
        self.assertTrue(context["ready"])
        self.assertEqual("implement-adapter", context["resume"]["first_allowed_action"]["action_id"])
        self.assertNotIn("referenced_sources", context)
        self.assertNotIn("loaded_rules", context)
        self.assertNotIn("raw_logs", context)

        (self.workspace / "app.py").write_text("VALUE = 9\n", encoding="utf-8")
        drifted = ADAPTER.handle_sessionstart(self.config, {"source": "compact"})
        drift_context = json.loads(drifted["hookSpecificOutput"]["additionalContext"])
        self.assertFalse(drift_context["ready"])
        self.assertEqual("SNAPSHOT_REQUIRED", drift_context["gate"])

    def post_validation(self, event_id: str, response: dict, *, tool: str = "exec_command", session: int = 17) -> None:
        ADAPTER.handle_posttooluse(self.config, {
            "tool_name": tool, "event_id": event_id, "is_error": False,
            "tool_input": {"cmd": "python3 -m unittest discover"} if tool == "exec_command" else {"session_id": session},
            "tool_response": response, "cwd": str(self.workspace),
        })

    def test_async_validation_requires_its_own_terminal_result(self) -> None:
        self.post_validation("unknown", {"output": "tool invocation succeeded"})
        self.post_validation("start", {"session_id": 17, "output": "running"})
        records, _ = ADAPTER._load_receipts(self.receipts)
        self.assertEqual(["unknown", "pending"], [item["status"] for item in records])
        start = records[-1]
        with self.assertRaises(ValueError):
            self.checkpoint()
        self.post_validation("unrelated", {"exit_code": 0}, tool="write_stdin", session=999)
        self.post_validation("still-running", {"session_id": 17}, tool="write_stdin")
        self.assertEqual(records, ADAPTER._load_receipts(self.receipts)[0])
        self.post_validation("finish", {"exit_code": 0}, tool="write_stdin")
        terminal = ADAPTER._load_receipts(self.receipts)[0][-1]
        self.assertEqual("pass", terminal["status"])
        self.assertEqual(start["receipt_id"], terminal["started_receipt_id"])
        self.assertEqual(start["command"], terminal["command"])
        self.assertEqual(start["source_fingerprint"], terminal["source_fingerprint"])
        self.checkpoint()
        self.post_validation("finish", {"exit_code": 0}, tool="write_stdin")
        self.assertEqual(4, len(ADAPTER._load_receipts(self.receipts)[0]))

    def test_async_failure_and_source_drift_cannot_become_passing_evidence(self) -> None:
        self.post_validation("start-fail", {"session_id": 17})
        self.post_validation("fail", {"exit_code": 1}, tool="write_stdin")
        self.assertEqual("fail", ADAPTER._load_receipts(self.receipts)[0][-1]["status"])
        self.post_validation("start-drift", {"session_id": 18})
        before = ADAPTER.source_fingerprint(self.config)
        (self.workspace / "app.py").write_text("VALUE = 8\n")
        self.post_validation("finish-drift", {"exit_code": 0}, tool="write_stdin", session=18)
        terminal = ADAPTER._load_receipts(self.receipts)[0][-1]
        self.assertEqual("unknown", terminal["status"])
        self.assertEqual(before, terminal["source_fingerprint"])
        with self.assertRaises(ValueError):
            self.checkpoint()

    def test_async_completion_cannot_cross_task_binding(self) -> None:
        self.post_validation("start", {"session_id": 17})
        document = valid_state()
        document["recovery_capsule"]["contract"]["task_id"] = "other-task"
        self.state.write_text(json.dumps(document))
        self.post_validation("foreign-finish", {"exit_code": 0}, tool="write_stdin")
        self.assertEqual(1, len(ADAPTER._load_receipts(self.receipts)[0]))
        with self.assertRaises(ValueError):
            self.checkpoint()

    def test_compact_drift_is_shared_across_independent_hook_processes(self) -> None:
        document = valid_state()
        fingerprint = ADAPTER.source_fingerprint(self.config)
        document["source_snapshot"]["source_fingerprint"] = fingerprint
        document["observed"]["source_fingerprint"] = fingerprint
        self.state.write_text(json.dumps(document))
        common = [sys.executable, str(SCRIPT_ROOT / "codex_execution_adapter.py"), "--state", str(self.state), "--workspace", str(self.workspace)]
        def hook(action, event):
            result = subprocess.run(common + [action], input=json.dumps(event), text=True, capture_output=True, check=True)
            return json.loads(result.stdout)
        hook("sessionstart", {"source": "compact"})
        (self.workspace / "app.py").write_text("VALUE = 7\n")
        # Known in-stage edits do not create an audit after every operation.
        self.assertEqual({}, hook("pretooluse", {"tool_name": "apply_patch"}))
        projected = hook("sessionstart", {"source": "compact"})
        self.assertFalse(json.loads(projected["hookSpecificOutput"]["additionalContext"])["ready"])
        denied = hook("pretooluse", {"tool_name": "apply_patch"})
        self.assertEqual("deny", denied["hookSpecificOutput"]["permissionDecision"])
        self.assertFalse(ADAPTER.doctor(self.config)["continuity_ready"])
        self.assertEqual(document, json.loads(self.state.read_text()))
        fingerprint = ADAPTER.source_fingerprint(self.config)
        document["source_snapshot"]["source_fingerprint"] = fingerprint
        document["observed"]["source_fingerprint"] = fingerprint
        self.state.write_text(json.dumps(document))
        self.assertEqual({}, hook("pretooluse", {"tool_name": "apply_patch"}))

    def test_broken_configured_identity_never_degrades_delivery_binding(self) -> None:
        self.validation()
        self.checkpoint()
        ADAPTER.complete_task(self.config, types.SimpleNamespace(acceptance=[]))
        for contents in ("{", "{}", "null"):
            with self.subTest(contents=contents):
                self.state.write_text(contents)
                for command in ("git commit -m done", "git push"):
                    denied = ADAPTER.handle_pretooluse(self.config, {"tool_name": "exec_command", "tool_input": {"cmd": command}})
                    self.assertEqual("deny", denied["hookSpecificOutput"]["permissionDecision"])
                self.assertFalse(ADAPTER.doctor(self.config)["task_completion_valid"])
        self.state.unlink()
        self.assertFalse(ADAPTER.doctor(self.config)["task_completion_valid"])
        unbound = ADAPTER.AdapterConfig(receipts=self.receipts, workspace=self.workspace)
        self.assertFalse(ADAPTER.doctor(unbound)["task_completion_valid"])

    def test_checkpoint_auto_selection_ignores_other_task_evidence(self) -> None:
        self.validation()
        document = valid_state()
        document["recovery_capsule"]["contract"]["task_id"] = "task-two"
        self.state.write_text(json.dumps(document))
        current = self.validation()
        checkpoint = self.checkpoint()
        self.assertEqual([current["receipt_id"]], checkpoint["evidence_receipt_ids"])

    def test_add_delete_symlink_and_mode_staging_keep_content_identity(self) -> None:
        (self.workspace / "app.py").unlink()
        (self.workspace / "new.py").write_text("VALUE = 3\n")
        (self.workspace / "new.py").chmod(0o755)
        (self.workspace / "link.py").symlink_to("new.py")
        self.validation()
        checkpoint = self.checkpoint()
        before = ADAPTER.source_fingerprint(self.config)
        subprocess.run(["git", "-C", str(self.workspace), "add", "-A"], check=True)
        self.assertEqual(before, ADAPTER.source_fingerprint(self.config))
        self.assertEqual({}, ADAPTER.handle_pretooluse(self.config, {"tool_name": "exec_command", "tool_input": {"cmd": "git commit -m stage"}}))
        subprocess.run(["git", "-C", str(self.workspace), "commit", "-qm", "stage"], check=True)
        self.assertEqual(before, ADAPTER.source_fingerprint(self.config))
        self.assertEqual(checkpoint["source_fingerprint"], before)
        (self.workspace / "new.py").chmod(0o644)
        self.assertNotEqual(before, ADAPTER.source_fingerprint(self.config))

    def test_old_fingerprint_algorithm_requires_a_new_snapshot(self) -> None:
        document = valid_state()
        document["source_snapshot"]["source_fingerprint"] = "git-worktree-sha256:" + "a" * 64
        document["observed"]["source_fingerprint"] = document["source_snapshot"]["source_fingerprint"]
        self.state.write_text(json.dumps(document))
        projection = ADAPTER.handle_sessionstart(self.config, {"source": "compact"})
        self.assertFalse(json.loads(projection["hookSpecificOutput"]["additionalContext"])["ready"])

    def test_concurrent_duplicate_hooks_append_one_receipt(self) -> None:
        command = [sys.executable, str(SCRIPT_ROOT / "codex_execution_adapter.py"),
                   "--state", str(self.state), "--receipts", str(self.receipts), "--workspace", str(self.workspace), "posttooluse"]
        event = json.dumps({"tool_name": "exec_command", "event_id": "shared-event", "tool_input": {"cmd": "python3 -m unittest"}, "tool_response": {"exit_code": 0}})
        def send(_):
            return subprocess.run(command, input=event, text=True, capture_output=True, check=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            list(pool.map(send, range(16)))
        receipts, errors = ADAPTER._load_receipts(self.receipts)
        self.assertFalse(errors)
        self.assertEqual(1, len(receipts))
        self.assertEqual("shared-event", receipts[0]["event_id"])

    def test_graph_refresh_is_demand_driven(self) -> None:
        missing = ADAPTER.graph_status(self.config)
        self.assertTrue(missing["dirty"])
        refreshed = ADAPTER.graph_refreshed(self.config)
        self.assertFalse(refreshed["dirty"])
        self.assertFalse(ADAPTER.graph_status(self.config)["dirty"])
        (self.workspace / "app.py").write_text("VALUE = 4\n", encoding="utf-8")
        self.assertTrue(ADAPTER.graph_status(self.config)["dirty"])


if __name__ == "__main__":
    unittest.main()
