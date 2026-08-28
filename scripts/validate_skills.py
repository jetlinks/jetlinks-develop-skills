#!/usr/bin/env python3
"""Validate repository skill packages without third-party dependencies."""

from __future__ import annotations

import argparse
import ast
import filecmp
import json
import re
import sys
from pathlib import Path


NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
GENERIC_SKILLS = {"systematic-solving", "task-continuity", "code-navigation", "agent-orchestration"}
REQUIRED_SKILL_CONTRACTS = {
    "agent-orchestration": {
        "SKILL.md": (
            "RouteDecision",
            "SINGLE_OWNER",
            "Assignment Capsule",
            "Result Packet",
            "accepted dispatch receipt",
            "at most two active delegated slices",
            "After one failed attempt",
            "overlapping files",
            "Hard-disable multi-Agent tools",
            "spawn broker",
            "schema_version: 5",
            "profile: compact",
            "merely to populate",
            "SemanticFork",
            "EvidenceBudget",
            "evidence_reopen",
        ),
        "references/orchestration-and-routing-rules.md": (
            "CAPABILITY_MISMATCH",
            "CAPSULE_DEFECT",
            "SOURCE_DRIFT",
            "INVALID_OBSERVATION",
            "CONTRACT_DEFECT",
            "IMPLEMENTATION_DEFECT",
            "Default delegation depth: one",
            "one or two",
            "same capability tier",
            "Capsule authority is monotonic",
            "delegation: denied",
            "NEW_CANDIDATE",
            "ADMISSION_PRECONDITION_INVALIDATED",
            "Apply control-plane checks progressively",
            "checks state already produced",
            "compact form",
        ),
        "references/evaluation-cases.md": (
            "Short mechanical change",
            "Host without subagents",
            "same-slice retry",
            "overlapping writes",
            "scripts/evaluate_orchestration_trace.py",
            "Advice-only delegation false positive",
            "Leaf attempts recursive delegation",
            "Brokered nested scope attenuation",
            "New candidate reopens a stopped gate",
            "Review finding legitimately discards a retained artifact",
            "Compact cross-module implementation",
            "Packet completion is not an evidence task",
        ),
        "references/codex-adapter.md": (
            "agents.max_depth",
            "Do not add an enabled Stage Manager profile",
            "descendant scope / write-set ACL",
        ),
    },
    "task-continuity": {
        "SKILL.md": (
            "READY",
            "SNAPSHOT_REQUIRED",
            "RESUME_AUDIT",
            "Source Snapshot",
            "Contract",
            "Checkpoint",
            "DecisionState",
            "Resume",
            "consecutive_matching_audits",
            "first_allowed_action",
            "COMPACT_CONTINUATION",
            "COLD_HANDOFF",
            "EXTERNAL_RETRY",
            "previous_productive_action_id",
            "pre_compaction_next_action_id",
            "post_compaction_first_productive_action_id",
            "SemanticFork",
            "EvidenceBudget",
            "SCOPE_INVALID",
            "conversation_cursor_at_snapshot",
            "directive_revision_at_snapshot",
            "MainlineReturnAnchor",
        ),
        "references/task-state-and-recovery-rules.md": (
            "Continuity Metadata",
            "LoadedRules",
            "audit_fingerprint",
            "Checkpoint.Validated",
            "Checkpoint.In-flight",
            "RESUME_AUDIT -> READY",
            "生产修改",
            "区分检查",
            "真实阻塞",
            "resume_audit_tool_rounds <= 1",
            "unmanaged_manifest_digest",
            "conversation_cursor_at_snapshot",
            "directive_revision_at_snapshot",
            "MainlineReturnAnchor",
            "do_not_reopen",
            "semantic_fork:",
            "evidence_budget:",
            "latest_discriminating_evidence",
        ),
        "references/evaluation-cases.md": (
            "验证失败后立即压缩",
            "同阶段连续两次压缩",
            "同一恢复切片连续五次压缩",
            "空泛 Next",
            "规则 revision 未变化",
            "Continuation 对比协议",
            "Full-context oracle",
            "Ablation continuation",
            "陈旧胶囊下修改",
            "用户禁止提交",
            "无关代码图注入",
            "scripts/evaluate_continuity_trace.py",
            "压缩续跑单批次",
            "外部重试",
            "压缩前后动作身份连续",
            "正确动作前的恢复入口偏航",
            "未解决语义分叉后压缩",
            "已解决语义分叉后压缩",
            "已停止取证预算后压缩",
        ),
    },
    "systematic-solving": {
        "SKILL.md": (
            "stale consumer / oracle",
            "invalid fixture / input",
            "mechanical assembly defect",
            "SemanticFork",
            "EvidenceBudget",
            "SCOPE_INVALID",
        ),
        "references/evaluation-cases.md": (
            "停滞后再次实施",
            "混合失败批次",
            "语义分叉",
            "EvidenceBudget=STOPPED",
        ),
    },
    "code-navigation": {
        "SKILL.md": (
            "adaptive local structure view",
            "eager repository-wide graph",
        ),
        "references/navigation-and-evidence-rules.md": (
            "自适应局部图策略",
            "任务相关性门禁",
            "decision_question",
            "target_languages",
            "source fingerprint",
            "增量刷新受影响节点",
        ),
    },
    "jetlinks-router": {
        "SKILL.md": (
            "Before ordinary classification",
            "first_allowed_action",
            "Graph size is not evidence of relevance",
            "current_decision",
            "minimum_skills",
            "SemanticFork",
            "scripts/evaluate_route_trace.py",
        ),
        "references/ai-prompt.md": (
            "continuation fast path",
            "decision question",
            "目标语言",
            "user_confirmation_required",
            "unique_next",
        ),
        "references/context-recovery-rules.md": (
            "validate_continuity_state.py",
            "suggested_gate",
            "普通 router 分类",
            "SemanticFork.status=OPEN",
        ),
        "references/evaluation-cases.md": (
            "最小领域组合",
            "匹配 compact continuation",
            "SemanticFork.status=OPEN",
            "scripts/evaluate_route_trace.py",
        ),
    },
}

# Python helpers are executable contracts, not prose.  Check their AST shape and
# require the negative tests that prove the important gates.  This deliberately
# avoids importing or executing code from an arbitrary repository during a
# structural validation pass; the coherent-stage test command executes these
# suites once after edits are integrated.
REQUIRED_PYTHON_CONTRACTS = {
    "agent-orchestration": {
        "scripts/evaluate_orchestration_trace.py": {
            "functions": ("evaluate_trace",),
        },
        "scripts/test_orchestration_tools.py": {
            "tests": (
                "test_v4_route_requires_native_nonempty_decision_question",
                "test_v4_rejects_duplicate_assignment_identity_without_overwriting_state",
                "test_malformed_v4_lists_return_errors_instead_of_crashing",
                "test_invalid_observation_reopen_is_limited_to_one_round",
                "test_rejects_design_implementation_and_review_while_fork_open",
            ),
        },
    },
    "systematic-solving": {
        "scripts/evaluate_systematic_trace.py": {
            "functions": ("evaluate_trace",),
        },
        "scripts/test_systematic_tools.py": {
            "tests": (
                "test_user_resolution_must_match_cited_decision_and_locator",
                "test_invalid_reopen_must_cite_current_round_and_cannot_repeat",
                "test_completed_inconclusive_round_requires_explicit_stop",
                "test_malformed_enum_values_do_not_crash",
            ),
        },
    },
    "task-continuity": {
        "scripts/validate_continuity_state.py": {
            "functions": ("validate_state",),
        },
        "scripts/evaluate_continuity_trace.py": {
            "functions": ("evaluate_trace",),
        },
        "scripts/prepare_resume_context.py": {
            "functions": ("project_context",),
        },
        "scripts/test_continuity_tools.py": {
            "tests": (
                "test_open_semantic_fork_blocks_solution_mutation",
                "test_stopped_open_semantic_fork_rejects_more_evidence_without_reopen",
                "test_semantic_options_are_not_silently_truncated",
                "test_wrong_productive_action_does_not_close_recovery_deviation_window",
            ),
        },
    },
    "jetlinks-router": {
        "scripts/evaluate_route_trace.py": {
            "functions": ("evaluate_trace",),
        },
        "scripts/test_router_tools.py": {
            "tests": (
                "test_accepts_exact_minimum_skill_route",
                "test_rejects_unadmitted_skill_load",
                "test_matching_compact_route_reuses_rules_and_hits_saved_next",
                "test_matching_compact_route_rejects_reload_and_reclassification",
                "test_open_semantic_fork_rejects_solution_route",
            ),
        },
    },
}
FORBIDDEN_SKILL_CONTRACTS = {
    "task-continuity": {
        "references/task-state-and-recovery-rules.md": (
            "Resume.audit_fingerprint",
            "维护两个有界逻辑视图",
        ),
    },
}
AUTHOR_LOCAL_PATTERNS = {
    "/Users/": "macOS user absolute path",
    "/home/": "Linux user absolute path",
    "C:\\Users\\": "Windows user absolute path",
    ".cc-switch/": "author-specific installation path",
}
IGNORED_NAMES = {".DS_Store", "__pycache__"}


def parse_frontmatter(path: Path) -> tuple[dict[str, str], list[str]]:
    errors: list[str] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, [f"{path}: missing YAML frontmatter"]
    try:
        end = next(index for index, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration:
        return {}, [f"{path}: unterminated YAML frontmatter"]

    metadata: dict[str, str] = {}
    for line_number, line in enumerate(lines[1:end], 2):
        if not line.strip():
            continue
        if line.startswith((" ", "\t")) or ":" not in line:
            errors.append(f"{path}:{line_number}: unsupported nested or malformed frontmatter")
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip("\"'")

    unexpected = sorted(set(metadata) - {"name", "description"})
    if unexpected:
        errors.append(f"{path}: unexpected frontmatter fields: {', '.join(unexpected)}")
    for required in ("name", "description"):
        if not metadata.get(required):
            errors.append(f"{path}: missing non-empty {required}")
    return metadata, errors


def validate_links(path: Path, repository_root: Path) -> list[str]:
    errors: list[str] = []
    for raw_target in LINK_PATTERN.findall(path.read_text(encoding="utf-8")):
        target = raw_target.strip().strip("<>")
        if not target or target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        target_path = target.split("#", 1)[0]
        if not target_path or any(marker in target_path for marker in ("<", ">", "${")):
            continue
        resolved = (path.parent / target_path).resolve()
        if not resolved.exists():
            errors.append(f"{path}: broken local link {raw_target}")
            continue
        try:
            resolved.relative_to(repository_root.resolve())
        except ValueError:
            errors.append(f"{path}: local link escapes repository root: {raw_target}")
    return errors


def validate_interface(path: Path) -> list[str]:
    if not path.exists():
        return [f"{path}: missing agents/openai.yaml"]
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    if not re.search(r"(?m)^interface:\s*$", text):
        errors.append(f"{path}: missing interface mapping")
    for field in ("display_name", "short_description", "default_prompt"):
        if not re.search(rf"(?m)^\s{{2}}{field}:\s*.+$", text):
            errors.append(f"{path}: missing interface.{field}")
    return errors


def validate_generic_portability(skill_root: Path) -> list[str]:
    if skill_root.name not in GENERIC_SKILLS:
        return []
    errors: list[str] = []
    for path in sorted(skill_root.rglob("*")):
        if not path.is_file() or path.name in IGNORED_NAMES:
            continue
        text = path.read_text(encoding="utf-8")
        for pattern, label in AUTHOR_LOCAL_PATTERNS.items():
            if pattern in text:
                errors.append(f"{path}: generic skill contains {label}: {pattern}")
    return errors


def validate_required_contract_markers(skill_root: Path) -> list[str]:
    """Smoke-check documented contract markers; executable tests prove behavior."""
    required_files = REQUIRED_SKILL_CONTRACTS.get(skill_root.name)
    if required_files is None:
        return []
    errors: list[str] = []
    for relative, markers in required_files.items():
        path = skill_root / relative
        if not path.is_file():
            errors.append(f"{path}: required contract-marker file missing")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                errors.append(f"{path}: missing required contract marker: {marker}")
    return errors


def _test_methods(tree: ast.AST) -> dict[str, ast.FunctionDef | ast.AsyncFunctionDef]:
    methods: dict[str, ast.FunctionDef | ast.AsyncFunctionDef] = {}
    for node in getattr(tree, "body", []):
        if not isinstance(node, ast.ClassDef):
            continue
        is_test_case = any(
            (isinstance(base, ast.Name) and base.id == "TestCase")
            or (isinstance(base, ast.Attribute) and base.attr == "TestCase")
            for base in node.bases
        )
        if not is_test_case:
            continue
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name.startswith("test_"):
                methods[item.name] = item
    return methods


def validate_python_contracts(skill_root: Path) -> list[str]:
    """Validate executable contract structure without executing repository code."""

    required_files = REQUIRED_PYTHON_CONTRACTS.get(skill_root.name)
    if required_files is None:
        return []
    errors: list[str] = []
    for relative, contract in required_files.items():
        path = skill_root / relative
        if not path.is_file():
            errors.append(f"{path}: required executable contract file missing")
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (OSError, SyntaxError) as error:
            errors.append(f"{path}: invalid Python executable contract: {error}")
            continue

        functions = {
            node.name: node
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        for name in contract.get("functions", ()):
            function = functions.get(name)
            if function is None:
                errors.append(f"{path}: missing executable contract function {name}")
                continue
            has_input = bool(function.args.args or function.args.kwonlyargs)
            has_gate = any(isinstance(node, (ast.If, ast.Try)) for node in ast.walk(function))
            has_return = any(isinstance(node, ast.Return) for node in ast.walk(function))
            if not (has_input and has_gate and has_return):
                errors.append(
                    f"{path}: executable contract function {name} is structurally incomplete; "
                    "it must consume input, apply a conditional gate, and return a result"
                )

        methods = _test_methods(tree)
        for name in contract.get("tests", ()):
            method = methods.get(name)
            if method is None:
                errors.append(f"{path}: missing required behavioral test {name}")
            elif not any(
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr.startswith("assert")
                for node in ast.walk(method)
            ):
                errors.append(f"{path}: behavioral test {name} has no executable assertion")
    return errors


def validate_forbidden_contracts(skill_root: Path) -> list[str]:
    """Reject superseded contract shapes that would create parallel state schemas."""
    forbidden_files = FORBIDDEN_SKILL_CONTRACTS.get(skill_root.name)
    if forbidden_files is None:
        return []
    errors: list[str] = []
    for relative, markers in forbidden_files.items():
        path = skill_root / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker in text:
                errors.append(f"{path}: contains superseded behavioral contract marker: {marker}")
    return errors


def iter_files(root: Path) -> dict[str, Path]:
    return {
        str(path.relative_to(root)): path
        for path in root.rglob("*")
        if path.is_file() and not any(part in IGNORED_NAMES for part in path.parts)
    }


def validate_mirror(skill_root: Path, mirror_root: Path) -> list[str]:
    mirror_skill = mirror_root / skill_root.name
    if not mirror_skill.is_dir():
        return [f"{mirror_skill}: installed mirror missing"]
    source_files = iter_files(skill_root)
    mirror_files = iter_files(mirror_skill)
    errors: list[str] = []
    for relative in sorted(set(source_files) - set(mirror_files)):
        errors.append(f"{mirror_skill / relative}: installed mirror file missing")
    for relative in sorted(set(mirror_files) - set(source_files)):
        errors.append(f"{mirror_skill / relative}: stale installed mirror file")
    for relative in sorted(set(source_files) & set(mirror_files)):
        if not filecmp.cmp(source_files[relative], mirror_files[relative], shallow=False):
            errors.append(f"{mirror_skill / relative}: installed mirror differs from source")
    return errors


def validate_codex_adapter(repository_root: Path, *, required: bool = False) -> list[str]:
    """Validate the optional project adapter when agent-orchestration is present."""
    if not (repository_root / "agent-orchestration" / "SKILL.md").is_file():
        return []

    errors: list[str] = []
    config_path = repository_root / ".codex" / "config.toml"
    if not config_path.is_file():
        # The skill is host-neutral.  Validate Codex files only when a project
        # deliberately installs that optional adapter.
        return [f"{config_path}: Codex adapter config missing"] if required else []
    try:
        config_text = config_path.read_text(encoding="utf-8")
    except OSError as error:
        return [f"{config_path}: cannot read config: {error}"]
    features_match = re.search(r"(?ms)^\[features\]\s*$\n(.*?)(?=^\[|\Z)", config_text)
    if features_match is None:
        errors.append(f"{config_path}: missing [features] table")
    else:
        multi_agent = re.search(
            r"(?m)^multi_agent\s*=\s*(true|false)\s*$",
            features_match.group(1),
        )
        if multi_agent is None or multi_agent.group(1) != "true":
            errors.append(f"{config_path}: primary features.multi_agent must be true")

    agents_match = re.search(r"(?ms)^\[agents\]\s*$\n(.*?)(?=^\[|\Z)", config_text)
    if agents_match is None:
        errors.append(f"{config_path}: missing [agents] table")
    else:
        agents_text = agents_match.group(1)
        current_max = re.search(r"(?m)^max_concurrent_threads_per_session\s*=\s*([0-9]+)\s*$", agents_text)
        legacy_max = re.search(r"(?m)^max_threads\s*=\s*([0-9]+)\s*$", agents_text)
        if current_max is not None and legacy_max is not None:
            errors.append(f"{config_path}: use only one concurrency field")
        max_match = current_max or legacy_max
        if max_match is None or int(max_match.group(1)) < 1:
            errors.append(
                f"{config_path}: max_concurrent_threads_per_session or max_threads must be a positive integer"
            )
        max_depth = re.search(r"(?m)^max_depth\s*=\s*([0-9]+)\s*$", agents_text)
        if max_depth is None or int(max_depth.group(1)) != 1:
            errors.append(f"{config_path}: agents.max_depth must be exactly 1 for the flat adapter")
        for field in ("default_subagent_model", "default_subagent_reasoning_effort"):
            value = re.search(rf'(?m)^{field}\s*=\s*"([^"\r\n]*)"\s*$', agents_text)
            if value is not None and not value.group(1).strip():
                errors.append(f"{config_path}: agents.{field} must be non-empty when present")

    required_profiles = {
        "bounded-explorer.toml": {"name": "bounded_explorer", "read_only": True},
        "mechanical-worker.toml": {
            "name": "mechanical_worker",
            "model": "gpt-5.6-luna",
            "reasoning": "medium",
            "sandbox": "workspace-write",
        },
        "bounded-worker.toml": {"name": "bounded_worker", "read_only": False},
        "stage-reviewer.toml": {"name": "stage_reviewer", "read_only": True},
    }
    seen_names: set[str] = set()
    for filename, requirements in required_profiles.items():
        expected_name = requirements["name"]
        read_only = requirements.get("read_only", False)
        path = repository_root / ".codex" / "agents" / filename
        if not path.is_file():
            errors.append(f"{path}: required Codex Agent profile missing")
            continue
        try:
            profile_text = path.read_text(encoding="utf-8")
        except OSError as error:
            errors.append(f"{path}: cannot read profile: {error}")
            continue
        profile: dict[str, str] = {}
        for field in ("name", "description"):
            value = re.search(rf'(?m)^{field}\s*=\s*"([^"\r\n]+)"\s*$', profile_text)
            if value is None or not value.group(1).strip():
                errors.append(f"{path}: {field} must be a non-empty string")
            else:
                profile[field] = value.group(1)
        instructions_match = re.search(
            r'(?ms)^developer_instructions\s*=\s*"""\s*\n(.*?)^"""\s*$',
            profile_text,
        ) or re.search(r'(?m)^developer_instructions\s*=\s*"([^"\r\n]+)"\s*$', profile_text)
        if instructions_match is None or not instructions_match.group(1).strip():
            errors.append(f"{path}: developer_instructions must be a non-empty string")
            instructions = ""
        else:
            instructions = instructions_match.group(1)
            profile["developer_instructions"] = instructions
        name = profile.get("name")
        if name != expected_name:
            errors.append(f"{path}: name must be {expected_name!r}")
        if isinstance(name, str) and name in seen_names:
            errors.append(f"{path}: duplicate Codex Agent name {name!r}")
        if isinstance(name, str):
            seen_names.add(name)
        sandbox_match = re.search(r'(?m)^sandbox_mode\s*=\s*"([^"\r\n]+)"\s*$', profile_text)
        sandbox_mode = sandbox_match.group(1) if sandbox_match else None
        if read_only and sandbox_mode != "read-only":
            errors.append(f"{path}: read-only profile must set sandbox_mode = 'read-only'")
        expected_sandbox = requirements.get("sandbox")
        if expected_sandbox is not None and sandbox_mode != expected_sandbox:
            errors.append(f"{path}: sandbox_mode must be {expected_sandbox!r}")
        for field, expected_value in (("model", requirements.get("model")), ("model_reasoning_effort", requirements.get("reasoning"))):
            if expected_value is None:
                continue
            value = re.search(rf'(?m)^{field}\s*=\s*"([^"\r\n]+)"\s*$', profile_text)
            actual_value = value.group(1) if value is not None else None
            if actual_value != expected_value:
                errors.append(f"{path}: {field} must be {expected_value!r}")
        if "spawn further agents" not in instructions:
            errors.append(f"{path}: profile must prohibit recursive Agent fan-out")
        if "hard upper bounds" not in instructions or "escalation request" not in instructions:
            errors.append(f"{path}: profile must treat capsule authority as bounded and escalate scope needs")
    return errors


def discover_skills(repository_root: Path) -> list[Path]:
    return sorted(path.parent for path in repository_root.glob("*/SKILL.md"))


def validate_repository(
    repository_root: Path,
    mirror_root: Path | None = None,
    *,
    codex_adapter: bool | None = None,
) -> dict[str, object]:
    skills = discover_skills(repository_root)
    errors: list[str] = []
    names: set[str] = set()
    for skill_root in skills:
        metadata, frontmatter_errors = parse_frontmatter(skill_root / "SKILL.md")
        errors.extend(frontmatter_errors)
        name = metadata.get("name", "")
        if name and name != skill_root.name:
            errors.append(f"{skill_root}: frontmatter name {name!r} does not match directory")
        if name and not NAME_PATTERN.fullmatch(name):
            errors.append(f"{skill_root}: invalid skill name {name!r}")
        if name in names:
            errors.append(f"{skill_root}: duplicate skill name {name!r}")
        names.add(name)
        errors.extend(validate_interface(skill_root / "agents" / "openai.yaml"))
        for markdown in sorted(skill_root.rglob("*.md")):
            errors.extend(validate_links(markdown, repository_root))
        errors.extend(validate_generic_portability(skill_root))
        errors.extend(validate_required_contract_markers(skill_root))
        errors.extend(validate_python_contracts(skill_root))
        errors.extend(validate_forbidden_contracts(skill_root))
        if mirror_root is not None:
            errors.extend(validate_mirror(skill_root, mirror_root))

    if not skills:
        errors.append(f"{repository_root}: no root-level skill packages found")
    should_validate_codex_adapter = (
        (repository_root / ".codex").exists()
        if codex_adapter is None
        else codex_adapter
    )
    if should_validate_codex_adapter:
        errors.extend(validate_codex_adapter(repository_root, required=True))
    return {
        "repository": str(repository_root),
        "skill_count": len(skills),
        "skills": [path.name for path in skills],
        "mirror": str(mirror_root) if mirror_root else None,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository", nargs="?", default=".", type=Path)
    parser.add_argument("--mirror-root", type=Path, help="compare every skill with an installed mirror")
    parser.add_argument(
        "--validate-codex-adapter",
        action="store_true",
        help="require and validate the optional project-scoped Codex adapter",
    )
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args()
    mirror_root = args.mirror_root.resolve() if args.mirror_root else None
    result = validate_repository(
        args.repository.resolve(),
        mirror_root,
        codex_adapter=True if args.validate_codex_adapter else None,
    )
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif result["errors"]:
        print(f"FAIL: {len(result['errors'])} validation error(s)")
        for error in result["errors"]:
            print(f"- {error}")
    else:
        mirror_note = f"; mirror={result['mirror']}" if result["mirror"] else ""
        print(f"PASS: {result['skill_count']} skill package(s){mirror_note}")
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
