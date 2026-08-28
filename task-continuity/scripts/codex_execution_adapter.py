#!/usr/bin/env python3
"""Optional Codex hook adapter for continuity receipts and delivery gates.

The portable task-continuity protocol does not depend on Codex, Git, or local
files.  This adapter is an opt-in execution layer for hosts that provide Codex
hook events.  It reads one explicit continuity-state file and/or appends to one
explicit JSONL receipt ledger; with neither configured, every hook is a safe
no-op.

Environment variables are equivalent to the common command-line options:

* ``TASK_CONTINUITY_STATE``: portable continuity state JSON.
* ``TASK_CONTINUITY_RECEIPTS``: append-only execution receipt ledger.
* ``TASK_CONTINUITY_WORKSPACE``: workspace used for source fingerprints.
* ``TASK_CONTINUITY_GRAPH_DIRTY``: optional code-index dirty marker.

Hook events are read from stdin and hook responses are written to stdout.  The
adapter deliberately gates only high-confidence actions; it does not attempt to
interpret every possible shell mutation or replace normal sandboxing/review.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

try:
    from prepare_resume_context import project_context
    from validate_continuity_state import validate_state
except ImportError:  # pragma: no cover - supports importlib-based test hosts
    from importlib.util import module_from_spec, spec_from_file_location

    def _load_sibling(name: str):
        spec = spec_from_file_location(name, Path(__file__).with_name(f"{name}.py"))
        if spec is None or spec.loader is None:
            raise ImportError(f"cannot load {name}")
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    project_context = _load_sibling("prepare_resume_context").project_context
    validate_state = _load_sibling("validate_continuity_state").validate_state


SCHEMA_VERSION = 1
SOURCE_TOOLS = {"apply_patch", "edit", "write"}
SHELL_TOOLS = {"bash", "shell", "shell_command", "local_shell", "exec_command"}
SPAWN_TOOLS = {"spawn_agent", "create_agent"}
RESULT_TOOLS = {"wait_agent", "wait_agents", "collect_agent", "collect_agents"}
VALIDATION_RE = re.compile(
    r"(?:^|[;&|]\s*)(?:\S+/)?(?:"
    r"mvn(?:w)?(?:\s+[^;&|]*)?\s+(?:test|verify)|"
    r"gradle(?:w)?(?:\s+[^;&|]*)?\s+(?:test|check|build)|"
    r"(?:npm|pnpm|yarn)\s+(?:run\s+)?(?:test|lint|typecheck|check|build)|"
    r"pytest|python(?:3)?\s+-m\s+(?:pytest|unittest)|"
    r"cargo\s+(?:test|check|clippy)|go\s+test|"
    r"dotnet\s+(?:test|build)|swift\s+test|make\s+(?:test|check|lint)"
    r")(?:\s|$)",
    re.IGNORECASE,
)
COMMIT_RE = re.compile(r"(?:^|[;&|]\s*)git(?:\s+[^;&|]*)?\s+commit(?:\s|$)", re.IGNORECASE)
PUSH_RE = re.compile(r"(?:^|[;&|]\s*)git(?:\s+[^;&|]*)?\s+push(?:\s|$)", re.IGNORECASE)
PR_MUTATION_RE = re.compile(
    r"(?:^|[;&|]\s*)gh\s+pr\s+(?:create|edit|ready|reopen|comment|merge)(?:\s|$)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class AdapterConfig:
    state: Path | None = None
    receipts: Path | None = None
    workspace: Path | None = None
    graph_dirty: Path | None = None

    @property
    def enabled(self) -> bool:
        return self.state is not None or self.receipts is not None or self.graph_dirty is not None


def _path(value: str | None) -> Path | None:
    return Path(value).expanduser().resolve() if value else None


def config_from_args(args: argparse.Namespace) -> AdapterConfig:
    receipts = _path(args.receipts or os.environ.get("TASK_CONTINUITY_RECEIPTS"))
    state = _path(args.state or os.environ.get("TASK_CONTINUITY_STATE"))
    if state is None and receipts is not None:
        sibling_state = receipts.parent / "continuity.json"
        if sibling_state.is_file():
            state = sibling_state.resolve()
    return AdapterConfig(
        state=state,
        receipts=receipts,
        workspace=_path(args.workspace or os.environ.get("TASK_CONTINUITY_WORKSPACE")),
        graph_dirty=_path(args.graph_dirty or os.environ.get("TASK_CONTINUITY_GRAPH_DIRTY")),
    )


def _read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _hook_input() -> dict[str, Any]:
    try:
        value = json.load(sys.stdin)
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid hook JSON: {error}") from error
    if not isinstance(value, dict):
        raise ValueError("hook input must be a JSON object")
    return value


def _hook_output(event: str, **values: Any) -> dict[str, Any]:
    return {"hookSpecificOutput": {"hookEventName": event, **values}}


def _deny(reason: str) -> dict[str, Any]:
    return _hook_output(
        "PreToolUse",
        permissionDecision="deny",
        permissionDecisionReason=reason[:1200],
    )


def _tool_name(event: dict[str, Any]) -> str:
    raw = str(event.get("tool_name") or event.get("toolName") or "")
    return re.split(r"[.:/]", raw)[-1].strip().lower()


def _tool_input(event: dict[str, Any]) -> dict[str, Any]:
    value = event.get("tool_input", event.get("toolInput", {}))
    return value if isinstance(value, dict) else {}


def _command(event: dict[str, Any]) -> str:
    tool_input = _tool_input(event)
    for key in ("cmd", "command", "script"):
        value = tool_input.get(key)
        if isinstance(value, str):
            return value.strip()
    return ""


def _walk(value: Any) -> Iterable[tuple[str, Any]]:
    if isinstance(value, dict):
        for key, item in value.items():
            yield str(key), item
            yield from _walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk(item)


def _response(event: dict[str, Any]) -> Any:
    return event.get(
        "tool_response",
        event.get("toolResponse", event.get("tool_output", event.get("toolOutput"))),
    )


def _exit_code(event: dict[str, Any]) -> int | None:
    response = _response(event)
    for key, value in _walk(response):
        if key in {"exit_code", "exitCode"} and isinstance(value, int) and not isinstance(value, bool):
            return value
    if isinstance(response, str):
        match = re.search(r"(?:exit(?:ed)?(?:\s+with)?\s+code|exit_code)\D{0,8}(-?\d+)", response, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None


def _tool_succeeded(event: dict[str, Any]) -> bool | None:
    response = _response(event)
    for key in ("is_error", "isError"):
        if isinstance(event.get(key), bool):
            return not event[key]
    for key, value in _walk(event.get("tool_output", event.get("toolOutput"))):
        if key in {"isError", "is_error"} and isinstance(value, bool):
            return not value
    for key, value in _walk(response):
        if key in {"isError", "is_error"} and isinstance(value, bool):
            return not value
    code = _exit_code(event)
    if code is not None:
        return code == 0
    return None


def _run_git(workspace: Path, *args: str) -> bytes:
    completed = subprocess.run(
        ["git", "-C", str(workspace), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=20,
    )
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", "replace").strip()
        raise ValueError(detail or f"git {' '.join(args)} failed")
    return completed.stdout


def _workspace(config: AdapterConfig, event: dict[str, Any] | None = None) -> Path:
    if config.workspace is not None:
        return config.workspace
    if event:
        raw = event.get("cwd")
        if isinstance(raw, str) and raw.strip():
            return Path(raw).expanduser().resolve()
    return Path.cwd().resolve()


def _runtime_exclusions(config: AdapterConfig, root: Path) -> set[str]:
    result: set[str] = set()
    for candidate in (config.state, config.receipts, config.graph_dirty):
        if candidate is None:
            continue
        try:
            result.add(candidate.relative_to(root).as_posix())
        except ValueError:
            pass
    return result


def _working_mode(path: Path, fallback: str) -> str:
    try:
        mode = path.lstat().st_mode
    except OSError:
        return "deleted"
    if stat.S_ISLNK(mode):
        return "120000"
    if stat.S_ISDIR(mode):
        return fallback
    return "100755" if mode & stat.S_IXUSR else "100644"


def source_fingerprint(config: AdapterConfig, event: dict[str, Any] | None = None) -> str:
    """Hash current Git worktree content, stable across staging and commit metadata."""

    workspace = _workspace(config, event)
    root = Path(_run_git(workspace, "rev-parse", "--show-toplevel").decode().strip()).resolve()
    exclusions = _runtime_exclusions(config, root)
    modified = {
        item.decode("utf-8", "surrogateescape")
        for item in _run_git(root, "diff-files", "--name-only", "-z").split(b"\0")
        if item
    }
    entries = _run_git(root, "ls-files", "--stage", "-z").split(b"\0")
    digest = hashlib.sha256()
    seen: set[str] = set()
    for raw in entries:
        if not raw:
            continue
        metadata, separator, raw_path = raw.partition(b"\t")
        if not separator:
            continue
        path = raw_path.decode("utf-8", "surrogateescape")
        if path in exclusions:
            continue
        parts = metadata.decode("ascii", "replace").split()
        if len(parts) < 3:
            continue
        mode, blob, stage = parts[:3]
        if stage != "0":
            digest.update(f"conflict\0{path}\0{mode}\0{blob}\0{stage}\0".encode("utf-8", "surrogateescape"))
            continue
        seen.add(path)
        if path in modified:
            work_path = root / path
            mode = _working_mode(work_path, mode)
            if mode == "deleted":
                blob = "deleted"
            elif work_path.is_dir():  # submodule or unusual tracked directory
                nested_config = AdapterConfig(workspace=work_path)
                blob = source_fingerprint(nested_config)
            else:
                blob = _run_git(root, "hash-object", f"--path={path}", "--", path).decode().strip()
        digest.update(f"tracked\0{path}\0{mode}\0{blob}\0".encode("utf-8", "surrogateescape"))

    untracked = _run_git(root, "ls-files", "--others", "--exclude-standard", "-z").split(b"\0")
    for raw in untracked:
        if not raw:
            continue
        path = raw.decode("utf-8", "surrogateescape")
        if path in exclusions or path in seen:
            continue
        work_path = root / path
        mode = _working_mode(work_path, "100644")
        if work_path.is_symlink():
            content = os.readlink(work_path).encode("utf-8", "surrogateescape")
        else:
            content = work_path.read_bytes()
        blob = hashlib.sha256(content).hexdigest()
        digest.update(f"untracked\0{path}\0{mode}\0{blob}\0".encode("utf-8", "surrogateescape"))
    return "git-worktree-sha256:" + digest.hexdigest()


def _load_receipts(path: Path | None) -> tuple[list[dict[str, Any]], list[str]]:
    if path is None or not path.exists():
        return [], []
    receipts: list[dict[str, Any]] = []
    errors: list[str] = []
    with path.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as error:
                errors.append(f"line {line_number}: {error.msg}")
                continue
            if not isinstance(item, dict):
                errors.append(f"line {line_number}: receipt must be an object")
                continue
            receipts.append(item)
    return receipts, errors


def _append_receipt(config: AdapterConfig, kind: str, **values: Any) -> dict[str, Any] | None:
    if config.receipts is None:
        return None
    payload = {
        "schema_version": SCHEMA_VERSION,
        "kind": kind,
        "timestamp_ns": time.time_ns(),
        **values,
    }
    identity = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    payload["receipt_id"] = "receipt-" + hashlib.sha256(identity.encode()).hexdigest()[:20]
    encoded = (json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n").encode()
    config.receipts.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(config.receipts, os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o600)
    try:
        os.write(descriptor, encoded)
    finally:
        os.close(descriptor)
    return payload


def _receipt_index(receipts: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        str(item["receipt_id"]): item
        for item in receipts
        if isinstance(item.get("receipt_id"), str)
    }


def _passed_evidence(item: dict[str, Any], fingerprint: str) -> bool:
    return (
        item.get("kind") in {"validation", "evidence"}
        and item.get("status") == "pass"
        and item.get("source_fingerprint") == fingerprint
    )


def _valid_checkpoint(
    receipts: list[dict[str, Any]], fingerprint: str
) -> tuple[dict[str, Any] | None, str | None]:
    index = _receipt_index(receipts)
    for item in reversed(receipts):
        if item.get("kind") != "stage_checkpoint":
            continue
        if item.get("source_fingerprint") != fingerprint:
            return None, "latest stage checkpoint does not cover the current source fingerprint"
        evidence_ids = item.get("evidence_receipt_ids")
        if not isinstance(evidence_ids, list) or not evidence_ids:
            return None, "latest stage checkpoint has no evidence receipts"
        if not all(
            isinstance(receipt_id, str)
            and receipt_id in index
            and _passed_evidence(index[receipt_id], fingerprint)
            for receipt_id in evidence_ids
        ):
            return None, "latest stage checkpoint references missing, failed, or stale evidence"
        return item, None
    return None, "no validated coherent-stage checkpoint exists"


def _assignment_state(receipts: list[dict[str, Any]]) -> dict[str, str]:
    states: dict[str, str] = {}
    for item in receipts:
        assignment_id = item.get("assignment_id")
        if not isinstance(assignment_id, str) or not assignment_id:
            continue
        if item.get("kind") == "agent_dispatch":
            states[assignment_id] = "dispatched"
        elif item.get("kind") == "agent_result_observed":
            states[assignment_id] = "observed"
        elif item.get("kind") == "agent_acceptance":
            states[assignment_id] = "accepted" if item.get("status") == "accepted" else "rejected"
    return states


def _valid_completion(
    receipts: list[dict[str, Any]], fingerprint: str
) -> tuple[dict[str, Any] | None, str | None]:
    checkpoint, reason = _valid_checkpoint(receipts, fingerprint)
    if checkpoint is None:
        return None, reason
    assignments = _assignment_state(receipts)
    unresolved = sorted(key for key, value in assignments.items() if value != "accepted")
    if unresolved:
        return None, "delegated assignments are not accepted: " + ", ".join(unresolved[:5])
    index = _receipt_index(receipts)
    for item in reversed(receipts):
        if item.get("kind") != "task_completion":
            continue
        if item.get("source_fingerprint") != fingerprint:
            return None, "latest task completion does not cover the current source fingerprint"
        if item.get("stage_checkpoint_id") != checkpoint.get("receipt_id"):
            return None, "latest task completion does not reference the current stage checkpoint"
        evidence_ids = item.get("acceptance_receipt_ids")
        if not isinstance(evidence_ids, list) or not evidence_ids:
            return None, "latest task completion has no acceptance evidence"
        if not all(
            isinstance(receipt_id, str)
            and receipt_id in index
            and _passed_evidence(index[receipt_id], fingerprint)
            for receipt_id in evidence_ids
        ):
            return None, "latest task completion references missing, failed, or stale evidence"
        return item, None
    return None, "the whole task has not been marked complete with acceptance evidence"


def _continuity_gate(config: AdapterConfig) -> tuple[bool, str]:
    if config.state is None:
        return True, "continuity state is not configured"
    try:
        result = validate_state(_read_json(config.state))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return False, f"continuity state unavailable: {error}"
    if result.get("ready"):
        return True, "READY"
    diagnostics = result.get("errors") or result.get("mismatches") or []
    return False, f"continuity gate is {result.get('suggested_gate', 'SNAPSHOT_REQUIRED')}: {str(diagnostics)[:700]}"


def _state_with_current_resume_observation(
    config: AdapterConfig, event: dict[str, Any]
) -> tuple[dict[str, Any], str | None]:
    """Overlay a comparable Git observation at a compact-session boundary.

    A different host may own a different fingerprint format.  In that case the
    portable state's own ``observed`` value remains authoritative; this adapter
    never pretends that two unlike formats are comparable.
    """

    document = _read_json(config.state)  # type: ignore[arg-type]
    snapshot = document.get("source_snapshot")
    saved = snapshot.get("source_fingerprint") if isinstance(snapshot, dict) else None
    if not isinstance(saved, str) or not saved.startswith("git-worktree-sha256:"):
        return document, "source fingerprint is owned by another host adapter"
    current, error = _current_fingerprint(config, event)
    if current is None:
        raise ValueError("cannot compare compact-session source identity: " + str(error))
    observed = document.get("observed")
    if not isinstance(observed, dict):
        observed = {}
        document["observed"] = observed
    observed["source_fingerprint"] = current
    return document, None


def _current_fingerprint(config: AdapterConfig, event: dict[str, Any] | None = None) -> tuple[str | None, str | None]:
    try:
        return source_fingerprint(config, event), None
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        return None, str(error)


def handle_pretooluse(config: AdapterConfig, event: dict[str, Any]) -> dict[str, Any]:
    if not config.enabled:
        return {}
    tool = _tool_name(event)
    command = _command(event) if tool in SHELL_TOOLS else ""
    if tool in SOURCE_TOOLS:
        ready, reason = _continuity_gate(config)
        if not ready:
            return _deny(reason)
    delivery_kind = None
    if command and COMMIT_RE.search(command):
        delivery_kind = "commit"
    elif command and (PUSH_RE.search(command) or PR_MUTATION_RE.search(command)):
        delivery_kind = "publish"
    if delivery_kind and config.receipts is not None:
        receipts, errors = _load_receipts(config.receipts)
        if errors:
            return _deny("execution receipt ledger is malformed: " + "; ".join(errors[:3]))
        fingerprint, error = _current_fingerprint(config, event)
        if fingerprint is None:
            return _deny("cannot establish current source fingerprint: " + str(error))
        if delivery_kind == "commit":
            checkpoint, reason = _valid_checkpoint(receipts, fingerprint)
            if checkpoint is None:
                return _deny(
                    "git commit requires a current validated stage: "
                    + str(reason)
                    + ". Record/reuse current-source evidence, then run checkpoint-stage once for the coherent stage"
                    + (f"; ledger={config.receipts}" if config.receipts else "")
                )
        else:
            completion, reason = _valid_completion(receipts, fingerprint)
            if completion is None:
                return _deny(
                    "publish/review requires whole-task acceptance: "
                    + str(reason)
                    + ". Accept all delegated results and run complete-task once after final acceptance"
                    + (f"; ledger={config.receipts}" if config.receipts else "")
                )
    return {}


def _assignment_id(event: dict[str, Any]) -> str:
    for key, value in _walk(_response(event)):
        if key in {"agent_id", "agentId", "assignment_id", "assignmentId", "task_id", "taskId"}:
            if isinstance(value, (str, int)) and str(value).strip():
                return str(value).strip()
    tool_input = _tool_input(event)
    for key in ("target", "assignment_id", "task_name"):
        value = tool_input.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return str(event.get("tool_use_id") or event.get("toolUseId") or "unknown-assignment")


def _mark_graph(config: AdapterConfig, fingerprint: str | None, dirty: bool) -> None:
    if config.graph_dirty is None:
        return
    payload = {
        "schema_version": SCHEMA_VERSION,
        "dirty": dirty,
        "source_fingerprint": fingerprint,
        "updated_at_ns": time.time_ns(),
    }
    config.graph_dirty.parent.mkdir(parents=True, exist_ok=True)
    temporary = config.graph_dirty.with_name(config.graph_dirty.name + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, config.graph_dirty)


def handle_posttooluse(config: AdapterConfig, event: dict[str, Any]) -> dict[str, Any]:
    if not config.enabled:
        return {}
    tool = _tool_name(event)
    command = _command(event) if tool in SHELL_TOOLS else ""
    succeeded = _tool_succeeded(event)
    receipt_worthy = (
        tool in SOURCE_TOOLS
        or tool in SPAWN_TOOLS
        or tool in RESULT_TOOLS
        or bool(command and (VALIDATION_RE.search(command) or COMMIT_RE.search(command) or PUSH_RE.search(command) or PR_MUTATION_RE.search(command)))
    )
    fingerprint = None
    if receipt_worthy:
        fingerprint, _ = _current_fingerprint(config, event)
    if tool in SOURCE_TOOLS and succeeded is not False:
        _append_receipt(config, "source_changed", tool=tool, source_fingerprint=fingerprint)
        _mark_graph(config, fingerprint, True)
    if command and VALIDATION_RE.search(command):
        code = _exit_code(event)
        status_value = (
            "pass"
            if code == 0 or (code is None and succeeded is True)
            else "fail"
            if code is not None or succeeded is False
            else "unknown"
        )
        _append_receipt(
            config,
            "validation",
            command=command[:1200],
            exit_code=code,
            status_source="exit_code" if code is not None else "host_error_flag" if succeeded is not None else "unknown",
            status=status_value,
            source_fingerprint=fingerprint,
        )
    if tool in SPAWN_TOOLS and succeeded is not False:
        _append_receipt(
            config,
            "agent_dispatch",
            assignment_id=_assignment_id(event),
            tool_use_id=event.get("tool_use_id") or event.get("toolUseId"),
            source_fingerprint=fingerprint,
        )
    if tool in RESULT_TOOLS and succeeded is not False:
        _append_receipt(
            config,
            "agent_result_observed",
            assignment_id=_assignment_id(event),
            source_fingerprint=fingerprint,
        )
    if command and (COMMIT_RE.search(command) or PUSH_RE.search(command) or PR_MUTATION_RE.search(command)):
        kind = "commit" if COMMIT_RE.search(command) else "push" if PUSH_RE.search(command) else "pr_mutation"
        _append_receipt(
            config,
            "delivery",
            delivery_kind=kind,
            status="pass" if succeeded is True else "fail" if succeeded is False else "unknown",
            source_fingerprint=fingerprint,
        )
    return {}


def handle_precompact(config: AdapterConfig, event: dict[str, Any]) -> dict[str, Any]:
    if config.state is None:
        return {}
    try:
        document, ownership_note = _state_with_current_resume_observation(config, event)
        result = validate_state(document)
        ready = bool(result.get("ready"))
        reason = str(result.get("suggested_gate", "SNAPSHOT_REQUIRED"))
        if ownership_note:
            reason += ": " + ownership_note
    except (OSError, ValueError, json.JSONDecodeError) as error:
        ready, reason = False, str(error)
    _append_receipt(config, "precompact_gate", status="ready" if ready else "not_ready", detail=reason)
    return {}


def handle_sessionstart(config: AdapterConfig, event: dict[str, Any]) -> dict[str, Any]:
    source = str(event.get("source") or event.get("session_source") or "").lower()
    if config.state is None or source != "compact":
        return {}
    try:
        document, ownership_note = _state_with_current_resume_observation(config, event)
        projection = project_context(document)
        if ownership_note:
            projection.setdefault("identity", {})["adapter_comparison"] = ownership_note
        context = json.dumps(projection, ensure_ascii=False, separators=(",", ":"))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        context = json.dumps(
            {
                "gate": "SNAPSHOT_REQUIRED",
                "ready": False,
                "instructions": f"Continuity state could not be projected: {error}",
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )
    return _hook_output("SessionStart", additionalContext=context)


def record_evidence(config: AdapterConfig, args: argparse.Namespace) -> dict[str, Any]:
    fingerprint, error = _current_fingerprint(config)
    if fingerprint is None:
        raise ValueError("cannot establish current source fingerprint: " + str(error))
    receipt = _append_receipt(
        config,
        "evidence",
        evidence_kind=args.evidence_kind,
        locator=args.locator,
        label=args.label,
        status=args.status,
        source_fingerprint=fingerprint,
    )
    if receipt is None:
        raise ValueError("TASK_CONTINUITY_RECEIPTS or --receipts is required")
    return receipt


def checkpoint_stage(config: AdapterConfig, args: argparse.Namespace) -> dict[str, Any]:
    if config.receipts is None:
        raise ValueError("TASK_CONTINUITY_RECEIPTS or --receipts is required")
    receipts, errors = _load_receipts(config.receipts)
    if errors:
        raise ValueError("execution receipt ledger is malformed: " + "; ".join(errors[:3]))
    fingerprint, error = _current_fingerprint(config)
    if fingerprint is None:
        raise ValueError("cannot establish current source fingerprint: " + str(error))
    index = _receipt_index(receipts)
    evidence_ids = list(dict.fromkeys(args.evidence or []))
    if not evidence_ids:
        evidence_ids = [
            str(item["receipt_id"])
            for item in receipts
            if isinstance(item.get("receipt_id"), str) and _passed_evidence(item, fingerprint)
        ]
    if not evidence_ids or not all(
        receipt_id in index and _passed_evidence(index[receipt_id], fingerprint)
        for receipt_id in evidence_ids
    ):
        raise ValueError("stage checkpoint requires passed evidence for the current source fingerprint")
    receipt = _append_receipt(
        config,
        "stage_checkpoint",
        stage_id=args.stage,
        evidence_receipt_ids=evidence_ids,
        source_fingerprint=fingerprint,
    )
    assert receipt is not None
    return receipt


def accept_assignment(config: AdapterConfig, args: argparse.Namespace) -> dict[str, Any]:
    if config.receipts is None:
        raise ValueError("TASK_CONTINUITY_RECEIPTS or --receipts is required")
    receipts, errors = _load_receipts(config.receipts)
    if errors:
        raise ValueError("execution receipt ledger is malformed: " + "; ".join(errors[:3]))
    states = _assignment_state(receipts)
    if args.assignment_id not in states:
        raise ValueError(f"unknown assignment: {args.assignment_id}")
    fingerprint, error = _current_fingerprint(config)
    if fingerprint is None:
        raise ValueError("cannot establish current source fingerprint: " + str(error))
    receipt = _append_receipt(
        config,
        "agent_acceptance",
        assignment_id=args.assignment_id,
        result_receipt_id=args.result_receipt,
        status=args.status,
        source_fingerprint=fingerprint,
    )
    assert receipt is not None
    return receipt


def complete_task(config: AdapterConfig, args: argparse.Namespace) -> dict[str, Any]:
    if config.receipts is None:
        raise ValueError("TASK_CONTINUITY_RECEIPTS or --receipts is required")
    receipts, errors = _load_receipts(config.receipts)
    if errors:
        raise ValueError("execution receipt ledger is malformed: " + "; ".join(errors[:3]))
    fingerprint, error = _current_fingerprint(config)
    if fingerprint is None:
        raise ValueError("cannot establish current source fingerprint: " + str(error))
    checkpoint, reason = _valid_checkpoint(receipts, fingerprint)
    if checkpoint is None:
        raise ValueError(str(reason))
    assignments = _assignment_state(receipts)
    unresolved = sorted(key for key, value in assignments.items() if value != "accepted")
    if unresolved:
        raise ValueError("delegated assignments are not accepted: " + ", ".join(unresolved[:5]))
    index = _receipt_index(receipts)
    evidence_ids = list(dict.fromkeys(args.acceptance or checkpoint.get("evidence_receipt_ids", [])))
    if not evidence_ids or not all(
        receipt_id in index and _passed_evidence(index[receipt_id], fingerprint)
        for receipt_id in evidence_ids
    ):
        raise ValueError("task completion requires passed acceptance evidence for the current source fingerprint")
    receipt = _append_receipt(
        config,
        "task_completion",
        stage_checkpoint_id=checkpoint["receipt_id"],
        acceptance_receipt_ids=evidence_ids,
        source_fingerprint=fingerprint,
    )
    assert receipt is not None
    return receipt


def doctor(config: AdapterConfig) -> dict[str, Any]:
    receipts, ledger_errors = _load_receipts(config.receipts)
    fingerprint, fingerprint_error = _current_fingerprint(config) if config.enabled else (None, None)
    ready, continuity_detail = _continuity_gate(config)
    checkpoint = completion = None
    checkpoint_error = completion_error = None
    if config.receipts is not None and fingerprint is not None:
        checkpoint, checkpoint_error = _valid_checkpoint(receipts, fingerprint)
        completion, completion_error = _valid_completion(receipts, fingerprint)
    workspace = _workspace(config)
    runtime_inside_workspace = []
    for candidate in (config.state, config.receipts, config.graph_dirty):
        if candidate is None:
            continue
        try:
            candidate.relative_to(workspace)
            runtime_inside_workspace.append(str(candidate))
        except ValueError:
            pass
    return {
        "enabled": config.enabled,
        "state": str(config.state) if config.state else None,
        "receipts": str(config.receipts) if config.receipts else None,
        "graph_dirty": str(config.graph_dirty) if config.graph_dirty else None,
        "continuity_ready": ready,
        "continuity_detail": continuity_detail,
        "receipt_count": len(receipts),
        "ledger_errors": ledger_errors,
        "source_fingerprint": fingerprint,
        "fingerprint_error": fingerprint_error,
        "stage_checkpoint_valid": checkpoint is not None,
        "stage_checkpoint_detail": checkpoint_error,
        "task_completion_valid": completion is not None,
        "task_completion_detail": completion_error,
        "runtime_inside_workspace": runtime_inside_workspace,
    }


def graph_refreshed(config: AdapterConfig) -> dict[str, Any]:
    fingerprint, error = _current_fingerprint(config)
    if fingerprint is None:
        raise ValueError("cannot establish current source fingerprint: " + str(error))
    _mark_graph(config, fingerprint, False)
    return {"dirty": False, "source_fingerprint": fingerprint}


def graph_status(config: AdapterConfig) -> dict[str, Any]:
    if config.graph_dirty is None:
        return {"configured": False, "dirty": None}
    if not config.graph_dirty.exists():
        return {"configured": True, "dirty": True, "reason": "marker missing"}
    try:
        marker = _read_json(config.graph_dirty)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return {"configured": True, "dirty": True, "reason": str(error)}
    fingerprint, error = _current_fingerprint(config)
    dirty = bool(marker.get("dirty")) or fingerprint is None or marker.get("source_fingerprint") != fingerprint
    return {
        "configured": True,
        "dirty": dirty,
        "marker_fingerprint": marker.get("source_fingerprint"),
        "source_fingerprint": fingerprint,
        "reason": error,
    }


def _add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--state", help="portable continuity state JSON")
    parser.add_argument("--receipts", help="append-only receipt ledger JSONL")
    parser.add_argument("--workspace", help="workspace used for source fingerprints")
    parser.add_argument("--graph-dirty", help="optional code-index dirty marker JSON")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    _add_common(parser)
    subparsers = parser.add_subparsers(dest="action", required=True)
    for action in ("pretooluse", "posttooluse", "precompact", "sessionstart", "doctor", "graph-status", "graph-refreshed"):
        subparsers.add_parser(action)
    evidence = subparsers.add_parser("record-evidence")
    evidence.add_argument("--kind", dest="evidence_kind", required=True, choices=("review", "inspection", "artifact", "runtime"))
    evidence.add_argument("--locator", required=True)
    evidence.add_argument("--label", required=True)
    evidence.add_argument("--status", choices=("pass", "fail"), required=True)
    checkpoint = subparsers.add_parser("checkpoint-stage")
    checkpoint.add_argument("--stage", required=True)
    checkpoint.add_argument("--evidence", action="append", default=[])
    acceptance = subparsers.add_parser("accept-assignment")
    acceptance.add_argument("--assignment-id", required=True)
    acceptance.add_argument("--result-receipt")
    acceptance.add_argument("--status", choices=("accepted", "rejected"), required=True)
    complete = subparsers.add_parser("complete-task")
    complete.add_argument("--acceptance", action="append", default=[])
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    config = config_from_args(args)
    try:
        if args.action in {"pretooluse", "posttooluse", "precompact", "sessionstart"}:
            event = _hook_input()
            handlers = {
                "pretooluse": handle_pretooluse,
                "posttooluse": handle_posttooluse,
                "precompact": handle_precompact,
                "sessionstart": handle_sessionstart,
            }
            output = handlers[args.action](config, event)
        elif args.action == "record-evidence":
            output = record_evidence(config, args)
        elif args.action == "checkpoint-stage":
            output = checkpoint_stage(config, args)
        elif args.action == "accept-assignment":
            output = accept_assignment(config, args)
        elif args.action == "complete-task":
            output = complete_task(config, args)
        elif args.action == "doctor":
            output = doctor(config)
        elif args.action == "graph-status":
            output = graph_status(config)
        else:
            output = graph_refreshed(config)
    except (OSError, ValueError, json.JSONDecodeError, subprocess.SubprocessError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False))
        return 1
    print(json.dumps(output, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
