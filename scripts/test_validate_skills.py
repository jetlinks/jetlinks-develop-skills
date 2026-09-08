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

    def create_contract_resources(self, skill: Path) -> None:
        """Create the declared package interfaces; prose has no fixed wording."""
        for relative in VALIDATOR.REQUIRED_SKILL_RESOURCES.get(skill.name, ()):
            path = skill / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("# Current rules\n\nUse relevant task evidence.\n", encoding="utf-8")
        for relative, contract in VALIDATOR.REQUIRED_PYTHON_CONTRACTS.get(skill.name, {}).items():
            path = skill / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            if contract.get("test_suite"):
                content = (
                    "import unittest\n\nclass ContractTest(unittest.TestCase):\n"
                    "    def test_reworded_case(self):\n"
                    "        self.assertEqual(1, 1)\n"
                )
            else:
                content = "\n".join(
                    f"def {name}(document):\n    return {{'input': document}}\n"
                    for name in contract["functions"]
                )
            path.write_text(content, encoding="utf-8")

    def test_rejects_missing_public_resource(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = self.create_skill(root, "task-continuity")
            self.create_contract_resources(skill)
            (skill / "references" / "task-state-and-recovery-rules.md").unlink()
            result = VALIDATOR.validate_repository(root)
            self.assertTrue(any("required skill resource missing" in item for item in result["errors"]))

    def test_accepts_reworded_rules_and_renamed_test_cases(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = self.create_skill(root, "task-continuity")
            self.create_contract_resources(skill)
            (skill / "SKILL.md").write_text(
                "---\nname: task-continuity\ndescription: Resume a task.\n---\n\n"
                "Continue from the current objective and saved next step.\n",
                encoding="utf-8",
            )
            result = VALIDATOR.validate_repository(root)
            self.assertEqual([], result["errors"])

    def test_words_do_not_replace_executable_resources(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = self.create_skill(root, "task-continuity")
            self.create_contract_resources(skill)
            script = skill / "scripts" / "validate_continuity_state.py"
            script.write_text(
                "CONTRACT = 'READY SNAPSHOT_REQUIRED validate_state'\n",
                encoding="utf-8",
            )
            result = VALIDATOR.validate_repository(root)
            self.assertTrue(
                any("missing executable contract function validate_state" in item for item in result["errors"])
            )

    def test_rejects_invalid_python_and_inputless_public_entry(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = self.create_skill(root, "task-continuity")
            self.create_contract_resources(skill)
            (skill / "scripts" / "validate_continuity_state.py").write_text(
                "def validate_state():\n    return {}\n", encoding="utf-8"
            )
            (skill / "scripts" / "prepare_resume_context.py").write_text(
                "def project_context(document\n", encoding="utf-8"
            )
            result = VALIDATOR.validate_repository(root)
            joined = "\n".join(result["errors"])
            self.assertIn("must accept input", joined)
            self.assertIn("invalid Python executable contract", joined)

    def test_rejects_empty_required_resource_and_assertion_free_suite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = self.create_skill(root, "task-continuity")
            self.create_contract_resources(skill)
            (skill / "references" / "evaluation-cases.md").write_text("", encoding="utf-8")
            (skill / "scripts" / "test_continuity_tools.py").write_text(
                "import unittest\nclass EmptyTest(unittest.TestCase):\n"
                "    def test_placeholder(self):\n        pass\n",
                encoding="utf-8",
            )
            result = VALIDATOR.validate_repository(root)
            joined = "\n".join(result["errors"])
            self.assertIn("required skill resource is empty", joined)
            self.assertIn("test suite must contain an executable assertion", joined)

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
