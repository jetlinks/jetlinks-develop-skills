#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
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
            "tool_response": "OK",
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
