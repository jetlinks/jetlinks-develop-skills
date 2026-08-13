#!/usr/bin/env python3
"""Validate repository skill packages without third-party dependencies."""

from __future__ import annotations

import argparse
import filecmp
import json
import re
import sys
from pathlib import Path


NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
GENERIC_SKILLS = {"systematic-solving", "task-continuity", "code-navigation"}
REQUIRED_SKILL_CONTRACTS = {
    "task-continuity": {
        "SKILL.md": (
            "READY",
            "SNAPSHOT_REQUIRED",
            "RESUME_AUDIT",
            "Source Snapshot",
        ),
        "references/evaluation-cases.md": (
            "验证失败后立即压缩",
            "同阶段连续两次压缩",
            "陈旧胶囊下修改",
            "用户禁止提交",
        ),
    },
    "systematic-solving": {
        "SKILL.md": (
            "stale consumer / oracle",
            "invalid fixture / input",
            "mechanical assembly defect",
        ),
        "references/evaluation-cases.md": (
            "停滞后再次实施",
            "混合失败批次",
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


def validate_required_contracts(skill_root: Path) -> list[str]:
    """Keep cross-file behavioral contracts from silently regressing."""
    required_files = REQUIRED_SKILL_CONTRACTS.get(skill_root.name)
    if required_files is None:
        return []
    errors: list[str] = []
    for relative, markers in required_files.items():
        path = skill_root / relative
        if not path.is_file():
            errors.append(f"{path}: required behavioral contract file missing")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                errors.append(f"{path}: missing required behavioral contract marker: {marker}")
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


def discover_skills(repository_root: Path) -> list[Path]:
    return sorted(path.parent for path in repository_root.glob("*/SKILL.md"))


def validate_repository(repository_root: Path, mirror_root: Path | None = None) -> dict[str, object]:
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
        errors.extend(validate_required_contracts(skill_root))
        if mirror_root is not None:
            errors.extend(validate_mirror(skill_root, mirror_root))

    if not skills:
        errors.append(f"{repository_root}: no root-level skill packages found")
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
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args()
    mirror_root = args.mirror_root.resolve() if args.mirror_root else None
    result = validate_repository(args.repository.resolve(), mirror_root)
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
