#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("validate_skills.py")
SPEC = importlib.util.spec_from_file_location("validate_skills", SCRIPT)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class ValidateSkillsTest(unittest.TestCase):
    def create_skill(self, root: Path, name: str = "sample-skill") -> Path:
        skill = root / name
        (skill / "agents").mkdir(parents=True)
        (skill / "references").mkdir()
        (skill / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: Example skill.\n---\n\n"
            "Read [`references/rules.md`](references/rules.md).\n",
            encoding="utf-8",
        )
        (skill / "references" / "rules.md").write_text("# Rules\n", encoding="utf-8")
        (skill / "agents" / "openai.yaml").write_text(
            'interface:\n  display_name: "Sample"\n  short_description: "Sample skill"\n'
            '  default_prompt: "Use sample skill."\n',
            encoding="utf-8",
        )
        return skill

    def test_accepts_complete_skill_and_identical_mirror(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            mirror = Path(directory) / "mirror"
            root.mkdir()
            mirror.mkdir()
            self.create_skill(root)
            self.create_skill(mirror)
            result = VALIDATOR.validate_repository(root, mirror)
            self.assertEqual([], result["errors"])
            self.assertEqual(1, result["skill_count"])

    def test_rejects_broken_link_and_stale_mirror(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            mirror = Path(directory) / "mirror"
            root.mkdir()
            mirror.mkdir()
            source = self.create_skill(root)
            self.create_skill(mirror)
            (source / "references" / "rules.md").unlink()
            result = VALIDATOR.validate_repository(root, mirror)
            joined = "\n".join(result["errors"])
            self.assertIn("broken local link", joined)
            self.assertIn("stale installed mirror file", joined)

    def test_rejects_author_local_path_in_generic_skill(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            root.mkdir()
            skill = self.create_skill(root, "task-continuity")
            (skill / "references" / "rules.md").write_text("Use /Users/example/state.\n", encoding="utf-8")
            result = VALIDATOR.validate_repository(root)
            self.assertTrue(any("macOS user absolute path" in error for error in result["errors"]))

    def test_rejects_missing_continuity_state_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            root.mkdir()
            self.create_skill(root, "task-continuity")
            result = VALIDATOR.validate_repository(root)
            joined = "\n".join(result["errors"])
            self.assertIn("missing required contract marker: READY", joined)
            self.assertIn("required contract-marker file missing", joined)

    def test_rejects_marker_only_behavioral_contracts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            root.mkdir()
            continuity = self.create_skill(root, "task-continuity")
            (continuity / "SKILL.md").write_text(
                "---\nname: task-continuity\ndescription: Example.\n---\n\n"
                "READY SNAPSHOT_REQUIRED RESUME_AUDIT Source Snapshot "
                "Contract Checkpoint DecisionState Resume "
                "consecutive_matching_audits first_allowed_action "
                "COMPACT_CONTINUATION COLD_HANDOFF EXTERNAL_RETRY "
                "previous_productive_action_id pre_compaction_next_action_id "
                "post_compaction_first_productive_action_id SemanticFork EvidenceBudget "
                "SCOPE_INVALID\n",
                encoding="utf-8",
            )
            (continuity / "references" / "task-state-and-recovery-rules.md").write_text(
                "Continuity Metadata LoadedRules audit_fingerprint RESUME_AUDIT -> READY "
                "Checkpoint.Validated Checkpoint.In-flight 生产修改 区分检查 真实阻塞 "
                "resume_audit_tool_rounds <= 1 unmanaged_manifest_digest "
                "conversation_cursor_at_snapshot directive_revision_at_snapshot MainlineReturnAnchor "
                "do_not_reopen semantic_fork: evidence_budget: "
                "latest_discriminating_evidence\n",
                encoding="utf-8",
            )
            (continuity / "references" / "evaluation-cases.md").write_text(
                "验证失败后立即压缩 同阶段连续两次压缩 同一恢复切片连续五次压缩 "
                "空泛 Next 规则 revision 未变化 Continuation 对比协议 "
                "Full-context oracle Ablation continuation 陈旧胶囊下修改 用户禁止提交 "
                "无关代码图注入 scripts/evaluate_continuity_trace.py 压缩续跑单批次 外部重试 "
                "压缩前后动作身份连续 正确动作前的恢复入口偏航\n"
                "未解决语义分叉后压缩 已解决语义分叉后压缩 已停止取证预算后压缩\n",
                encoding="utf-8",
            )
            (continuity / "scripts").mkdir()
            (continuity / "scripts" / "validate_continuity_state.py").write_text(
                "def _validate_evidence_budget():\n    return None\n"
                "def validate_state():\n    pre_compaction_next_action_id = None\n"
                "    marker = 'semantic_fork.open_blocks_solution'\n"
                "    return {'suggested_gate': 'SNAPSHOT_REQUIRED'}\n",
                encoding="utf-8",
            )
            (continuity / "scripts" / "evaluate_continuity_trace.py").write_text(
                "def evaluate_trace():\n    return {'repeated_read_count': 0, "
                "'irrelevant_graph_injection_count': 0, 'full_thread_reads': 0, "
                "'unchanged_reference_reads': 0, 'compact_continuation_fast_path_passed': True, "
                "'post_compaction_first_productive_action_id': None, "
                "'recovery_route_deviation_count': 0, "
                "'post_compaction_full_skill_reload_count': 0, "
                "'scope_invalid_observation_count': 0}\n",
                encoding="utf-8",
            )
            (continuity / "scripts" / "prepare_resume_context.py").write_text(
                "def project_context():\n    return {'gate': 'SNAPSHOT_REQUIRED', "
                "'first_allowed_action': None}\n"
                "MARKERS = 'SNAPSHOT_REQUIRED first_allowed_action do not reload unchanged "
                "references semantic_fork evidence_budget'\n",
                encoding="utf-8",
            )
            result = VALIDATOR.validate_repository(root)
            joined = "\n".join(result["errors"])
            self.assertIn("structurally incomplete", joined)
            self.assertIn("required executable contract file missing", joined)

    def test_rejects_missing_anti_idle_resume_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            root.mkdir()
            continuity = self.create_skill(root, "task-continuity")
            (continuity / "SKILL.md").write_text(
                "---\nname: task-continuity\ndescription: Example.\n---\n\n"
                "READY SNAPSHOT_REQUIRED RESUME_AUDIT Source Snapshot\n",
                encoding="utf-8",
            )
            (continuity / "references" / "task-state-and-recovery-rules.md").write_text(
                "LoadedRules\n",
                encoding="utf-8",
            )
            (continuity / "references" / "evaluation-cases.md").write_text(
                "验证失败后立即压缩 同阶段连续两次压缩 陈旧胶囊下修改 用户禁止提交\n",
                encoding="utf-8",
            )
            result = VALIDATOR.validate_repository(root)
            joined = "\n".join(result["errors"])
            self.assertIn("missing required contract marker: consecutive_matching_audits", joined)
            self.assertIn("missing required contract marker: audit_fingerprint", joined)
            self.assertIn("missing required contract marker: 同一恢复切片连续五次压缩", joined)

    def test_rejects_missing_continuation_evaluation_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            root.mkdir()
            continuity = self.create_skill(root, "task-continuity")
            (continuity / "SKILL.md").write_text(
                "---\nname: task-continuity\ndescription: Example.\n---\n\n"
                "READY SNAPSHOT_REQUIRED RESUME_AUDIT Source Snapshot Contract Checkpoint "
                "DecisionState Resume consecutive_matching_audits first_allowed_action\n",
                encoding="utf-8",
            )
            (continuity / "references" / "task-state-and-recovery-rules.md").write_text(
                "Continuity Metadata LoadedRules audit_fingerprint RESUME_AUDIT -> READY "
                "生产修改 区分检查 真实阻塞\n",
                encoding="utf-8",
            )
            (continuity / "references" / "evaluation-cases.md").write_text(
                "验证失败后立即压缩 同阶段连续两次压缩 同一恢复切片连续五次压缩 "
                "空泛 Next 规则 revision 未变化 陈旧胶囊下修改 用户禁止提交\n",
                encoding="utf-8",
            )
            result = VALIDATOR.validate_repository(root)
            joined = "\n".join(result["errors"])
            self.assertIn("missing required contract marker: Continuation 对比协议", joined)
            self.assertIn("missing required contract marker: Ablation continuation", joined)

    def test_rejects_superseded_continuity_schema(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            root.mkdir()
            continuity = self.create_skill(root, "task-continuity")
            (continuity / "SKILL.md").write_text(
                "---\nname: task-continuity\ndescription: Example.\n---\n\n"
                "READY SNAPSHOT_REQUIRED RESUME_AUDIT Source Snapshot Contract Checkpoint "
                "DecisionState Resume consecutive_matching_audits first_allowed_action\n",
                encoding="utf-8",
            )
            (continuity / "references" / "task-state-and-recovery-rules.md").write_text(
                "Continuity Metadata LoadedRules audit_fingerprint RESUME_AUDIT -> READY "
                "Checkpoint.Validated Checkpoint.In-flight 生产修改 区分检查 真实阻塞\n"
                "Resume.audit_fingerprint 维护两个有界逻辑视图\n",
                encoding="utf-8",
            )
            (continuity / "references" / "evaluation-cases.md").write_text(
                "验证失败后立即压缩 同阶段连续两次压缩 同一恢复切片连续五次压缩 "
                "空泛 Next 规则 revision 未变化 Continuation 对比协议 Full-context oracle "
                "Ablation continuation 陈旧胶囊下修改 用户禁止提交\n",
                encoding="utf-8",
            )
            result = VALIDATOR.validate_repository(root)
            joined = "\n".join(result["errors"])
            self.assertIn("superseded behavioral contract marker: Resume.audit_fingerprint", joined)
            self.assertIn("superseded behavioral contract marker: 维护两个有界逻辑视图", joined)

    def test_validates_codex_agent_adapter(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / "agent-orchestration"
            skill.mkdir()
            (skill / "SKILL.md").write_text("---\nname: agent-orchestration\ndescription: Test.\n---\n", encoding="utf-8")
            agents = root / ".codex" / "agents"
            agents.mkdir(parents=True)
            (root / ".codex" / "config.toml").write_text(
                "[features]\nmulti_agent = true\n\n[agents]\nmax_threads = 2\nmax_depth = 1\ninterrupt_message = true\n",
                encoding="utf-8",
            )
            profiles = {
                "bounded-explorer.toml": ("bounded_explorer", True),
                "mechanical-worker.toml": ("mechanical_worker", False),
                "bounded-worker.toml": ("bounded_worker", False),
                "stage-reviewer.toml": ("stage_reviewer", True),
            }
            for filename, (name, read_only) in profiles.items():
                sandbox = 'sandbox_mode = "read-only"\n' if read_only else ""
                mechanical_settings = (
                    'model = "gpt-5.6-luna"\nmodel_reasoning_effort = "medium"\n'
                    'sandbox_mode = "workspace-write"\n'
                    if name == "mechanical_worker"
                    else ""
                )
                (agents / filename).write_text(
                    f'name = "{name}"\ndescription = "Test profile"\n{sandbox}{mechanical_settings}'
                    'developer_instructions = "Treat scope as hard upper bounds; return an escalation request. '
                    'Do not spawn further agents."\n',
                    encoding="utf-8",
                )
            self.assertEqual([], VALIDATOR.validate_codex_adapter(root))

            (root / ".codex" / "config.toml").write_text(
                "[features]\nmulti_agent = true\n\n[agents]\n"
                "max_threads = 2\nmax_depth = 2\ninterrupt_message = true\n",
                encoding="utf-8",
            )
            errors = VALIDATOR.validate_codex_adapter(root)
            self.assertTrue(any("agents.max_depth must be exactly 1" in error for error in errors))

            (root / ".codex" / "config.toml").write_text(
                "[features]\nmulti_agent = true\n\n[agents]\nmax_threads = 2\n"
                "max_depth = 1\ninterrupt_message = true\n",
                encoding="utf-8",
            )

            (agents / "bounded-explorer.toml").write_text(
                'name = "bounded_explorer"\ndescription = "Test profile"\n'
                'sandbox_mode = "workspace-write"\n'
                'developer_instructions = "Treat scope as hard upper bounds; return an escalation request. '
                'Do not spawn further agents."\n',
                encoding="utf-8",
            )
            errors = VALIDATOR.validate_codex_adapter(root)
            self.assertTrue(any("read-only profile" in error for error in errors))

            (agents / "mechanical-worker.toml").write_text(
                'name = "mechanical_worker"\ndescription = "Test profile"\n'
                'model = "gpt-5.6-terra"\nmodel_reasoning_effort = "high"\n'
                'sandbox_mode = "read-only"\n'
                'developer_instructions = "Treat scope as hard upper bounds; return an escalation request. '
                'Do not spawn further agents."\n',
                encoding="utf-8",
            )
            errors = VALIDATOR.validate_codex_adapter(root)
            joined = "\n".join(errors)
            self.assertIn("model must be 'gpt-5.6-luna'", joined)
            self.assertIn("model_reasoning_effort must be 'medium'", joined)
            self.assertIn("sandbox_mode must be 'workspace-write'", joined)

            (agents / "mechanical-worker.toml").unlink()
            errors = VALIDATOR.validate_codex_adapter(root)
            self.assertTrue(any("mechanical-worker.toml: required Codex Agent profile missing" in error for error in errors))

    def test_codex_adapter_is_optional_without_project_configuration(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / "agent-orchestration"
            skill.mkdir()
            (skill / "SKILL.md").write_text(
                "---\nname: agent-orchestration\ndescription: Host-neutral test.\n---\n",
                encoding="utf-8",
            )
            self.assertEqual([], VALIDATOR.validate_codex_adapter(root))
            self.assertTrue(
                any(
                    "Codex adapter config missing" in error
                    for error in VALIDATOR.validate_codex_adapter(root, required=True)
                )
            )

    def test_accepts_current_codex_agent_concurrency_schema(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / "agent-orchestration"
            skill.mkdir()
            (skill / "SKILL.md").write_text("---\nname: agent-orchestration\ndescription: Test.\n---\n", encoding="utf-8")
            agents = root / ".codex" / "agents"
            agents.mkdir(parents=True)
            (root / ".codex" / "config.toml").write_text(
                "[features]\nmulti_agent = true\n\n"
                "[agents]\nmax_concurrent_threads_per_session = 2\nmax_depth = 1\n"
                'default_subagent_model = "balanced"\n'
                'default_subagent_reasoning_effort = "medium"\n',
                encoding="utf-8",
            )
            profiles = {
                "bounded-explorer.toml": ("bounded_explorer", True),
                "mechanical-worker.toml": ("mechanical_worker", False),
                "bounded-worker.toml": ("bounded_worker", False),
                "stage-reviewer.toml": ("stage_reviewer", True),
            }
            for filename, (name, read_only) in profiles.items():
                sandbox = 'sandbox_mode = "read-only"\n' if read_only else ""
                mechanical_settings = (
                    'model = "gpt-5.6-luna"\nmodel_reasoning_effort = "medium"\n'
                    'sandbox_mode = "workspace-write"\n'
                    if name == "mechanical_worker"
                    else ""
                )
                (agents / filename).write_text(
                    f'name = "{name}"\ndescription = "Test profile"\n{sandbox}{mechanical_settings}'
                    'developer_instructions = "Treat scope as hard upper bounds; return an escalation request. '
                    'Do not spawn further agents."\n',
                    encoding="utf-8",
                )
            self.assertEqual([], VALIDATOR.validate_codex_adapter(root))


if __name__ == "__main__":
    unittest.main()
