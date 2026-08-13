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
            self.assertIn("missing required behavioral contract marker: READY", joined)
            self.assertIn("required behavioral contract file missing", joined)

    def test_accepts_required_behavioral_contracts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            root.mkdir()
            continuity = self.create_skill(root, "task-continuity")
            (continuity / "SKILL.md").write_text(
                "---\nname: task-continuity\ndescription: Example.\n---\n\n"
                "READY SNAPSHOT_REQUIRED RESUME_AUDIT Source Snapshot "
                "consecutive_matching_audits first_allowed_action\n",
                encoding="utf-8",
            )
            (continuity / "references" / "task-state-and-recovery-rules.md").write_text(
                "LoadedRules audit_fingerprint RESUME_AUDIT -> READY "
                "生产修改 区分检查 真实阻塞\n",
                encoding="utf-8",
            )
            (continuity / "references" / "evaluation-cases.md").write_text(
                "验证失败后立即压缩 同阶段连续两次压缩 同一恢复切片连续五次压缩 "
                "空泛 Next 规则 revision 未变化 陈旧胶囊下修改 用户禁止提交\n",
                encoding="utf-8",
            )
            result = VALIDATOR.validate_repository(root)
            self.assertEqual([], result["errors"])

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
            self.assertIn("missing required behavioral contract marker: consecutive_matching_audits", joined)
            self.assertIn("missing required behavioral contract marker: audit_fingerprint", joined)
            self.assertIn("missing required behavioral contract marker: 同一恢复切片连续五次压缩", joined)


if __name__ == "__main__":
    unittest.main()
