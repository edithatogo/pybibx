#!/usr/bin/env python3
"""Conductor swarm launcher for PyBibX.

The launcher is intentionally conservative:
- run blocker checks before any worker command;
- require explicit --execute for agent launch commands;
- fail closed when Cline/DeepSeek cannot be verified for this checkout.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
TRACK_ID = "provider_ontology_foundation_20260614"
TRACK_PLAN = REPO / "conductor" / "tracks" / TRACK_ID / "plan.md"
DEFAULT_CONFIG = REPO / "conductor" / "swarm_assignments.json"
DEFAULT_EVIDENCE_DIR = REPO / "conductor" / "swarm_runs"
CODEX_BIN = "/Applications/Codex.app/Contents/Resources/codex"
CLINE_BIN = "cline"
CODEX_MODEL = "gpt-5.5"
CLINE_PROVIDER = "deepseek"
CLINE_MODEL = "deepseek-v4-flash"
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


@dataclass(frozen=True)
class Check:
    name: str
    status: str
    detail: str


@dataclass(frozen=True)
class Assignment:
    lane: str
    track_phase: str
    file_ownership: list[str]
    acceptance_criteria: list[str]
    no_revert_instruction: str


def run(cmd: list[str], *, timeout: int = 15) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=REPO,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )


def clean_output(text: str) -> str:
    return ANSI_RE.sub("", text).strip()


def command_path(command: str) -> str | None:
    if "/" in command:
        return command if Path(command).exists() else None
    return shutil.which(command)


def git_clean_check() -> Check:
    result = run(["git", "status", "--porcelain=v1"])
    if result.returncode != 0:
        return Check("git_status", "blocked", clean_output(result.stderr) or "git status failed")
    if result.stdout.strip():
        return Check("git_status", "blocked", "worktree has uncommitted changes")
    return Check("git_status", "ok", "worktree clean")


def git_upstream_check() -> Check:
    upstream = run(["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"])
    if upstream.returncode != 0:
        return Check("git_upstream", "warn", "no upstream configured")
    counts = run(["git", "rev-list", "--left-right", "--count", "HEAD...@{upstream}"])
    if counts.returncode != 0:
        return Check("git_upstream", "warn", clean_output(counts.stderr) or "could not compare upstream")
    ahead, behind = counts.stdout.strip().split()
    return Check("git_upstream", "ok", f"ahead {ahead}, behind {behind}; ahead is allowed but reported")


def codex_check() -> Check:
    path = command_path(CODEX_BIN)
    if not path:
        return Check("codex_cli", "blocked", f"not found at {CODEX_BIN}")
    result = run([path, "exec", "--help"])
    if result.returncode != 0:
        return Check("codex_cli", "blocked", clean_output(result.stderr) or "codex exec --help failed")
    return Check("codex_cli", "ok", path)


def cline_cli_check() -> Check:
    path = command_path(CLINE_BIN)
    if not path:
        return Check("cline_cli", "blocked", "cline not found on PATH")
    result = run([path, "--help"])
    if result.returncode != 0:
        return Check("cline_cli", "blocked", clean_output(result.stderr) or "cline --help failed")
    return Check("cline_cli", "ok", path)


def cline_provider_check() -> Check:
    path = command_path(CLINE_BIN)
    if not path:
        return Check("cline_provider", "blocked", "cline CLI unavailable")

    result = run([path, "config", "--json"])
    output = clean_output(result.stdout + "\n" + result.stderr)
    if result.returncode != 0:
        return Check("cline_provider", "blocked", output or "cline config --json failed")
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return Check("cline_provider", "blocked", "cline config --json did not emit JSON in this environment")

    redacted = redact(data)
    text = json.dumps(redacted, sort_keys=True).lower()
    if CLINE_PROVIDER in text and CLINE_MODEL.lower() in text:
        return Check("cline_provider", "ok", f"{CLINE_PROVIDER}/{CLINE_MODEL} present in redacted config")
    return Check("cline_provider", "blocked", f"{CLINE_PROVIDER}/{CLINE_MODEL} not present in redacted config")


def track_check() -> Check:
    if not TRACK_PLAN.exists():
        return Check("track_plan", "blocked", f"missing {TRACK_PLAN.relative_to(REPO)}")
    text = TRACK_PLAN.read_text()
    required = [CODEX_MODEL, CLINE_MODEL, "Codex swarm"]
    missing = [term for term in required if term not in text]
    if missing:
        return Check("track_plan", "blocked", f"missing terms: {', '.join(missing)}")
    return Check("track_plan", "ok", str(TRACK_PLAN.relative_to(REPO)))


def redact(value: object) -> object:
    if isinstance(value, dict):
        redacted: dict[str, object] = {}
        for key, item in value.items():
            lower = key.lower()
            if any(secret in lower for secret in ("key", "token", "secret", "password", "auth")):
                redacted[key] = "<redacted>"
            else:
                redacted[key] = redact(item)
        return redacted
    if isinstance(value, list):
        return [redact(item) for item in value[:20]]
    return value


def doctor_checks() -> list[Check]:
    return [
        track_check(),
        git_clean_check(),
        git_upstream_check(),
        codex_check(),
        cline_cli_check(),
        cline_provider_check(),
    ]


def has_blocker(checks: list[Check], *, include_cline: bool) -> bool:
    for check in checks:
        if check.status == "blocked" and (include_cline or not check.name.startswith("cline_")):
            return True
    return False


def print_checks(checks: list[Check], *, as_json: bool) -> None:
    if as_json:
        print(json.dumps([asdict(check) for check in checks], indent=2))
        return
    for check in checks:
        print(f"{check.status.upper():7} {check.name}: {check.detail}")


def assignment_plan() -> dict[str, object]:
    return {
        "blockers_first": [
            "Verify track plan exists and names the requested lanes.",
            "Verify git worktree is clean before launching workers.",
            "Verify Codex CLI can run non-interactively.",
            "Verify Cline CLI exists.",
            "Verify Cline provider/model config for deepseek-v4-flash; otherwise block the Cline lane.",
        ],
        "lanes": {
            "codex_orchestrator": {
                "runner": CODEX_BIN,
                "model": CODEX_MODEL,
                "role": "orchestrator/reviewer/verifier/committer",
            },
            "cline_worker": {
                "runner": CLINE_BIN,
                "provider": CLINE_PROVIDER,
                "model": CLINE_MODEL,
                "role": "external worker in isolated worktree when provider is verified",
            },
            "codex_swarm_fallback": {
                "runner": "in-session multi-agent tool",
                "model": CODEX_MODEL,
                "role": "parallel review/exploration/verification when Cline is unavailable",
            },
        },
    }


def load_assignments(path: Path) -> list[Assignment]:
    data = json.loads(path.read_text())
    if not isinstance(data, dict) or not isinstance(data.get("assignments"), list):
        raise ValueError("config must contain an assignments list")
    assignments: list[Assignment] = []
    for index, item in enumerate(data["assignments"]):
        if not isinstance(item, dict):
            raise ValueError(f"assignment {index} must be an object")
        missing = [
            key
            for key in (
                "lane",
                "track_phase",
                "file_ownership",
                "acceptance_criteria",
                "no_revert_instruction",
            )
            if key not in item
        ]
        if missing:
            raise ValueError(f"assignment {index} missing keys: {', '.join(missing)}")
        assignment = Assignment(
            lane=str(item["lane"]),
            track_phase=str(item["track_phase"]),
            file_ownership=[str(value) for value in item["file_ownership"]],
            acceptance_criteria=[str(value) for value in item["acceptance_criteria"]],
            no_revert_instruction=str(item["no_revert_instruction"]),
        )
        if assignment.lane not in {"codex", "cline", "swarm-review"}:
            raise ValueError(f"assignment {index} has invalid lane: {assignment.lane}")
        if not assignment.file_ownership:
            raise ValueError(f"assignment {index} must declare at least one file ownership path")
        if not assignment.acceptance_criteria:
            raise ValueError(f"assignment {index} must declare acceptance criteria")
        if "do not revert" not in assignment.no_revert_instruction.lower():
            raise ValueError(f"assignment {index} must include a no-revert instruction")
        assignments.append(assignment)
    reject_overlaps(assignments)
    return assignments


def normalize_scope(scope: str) -> str:
    return scope.strip().rstrip("/")


def scopes_overlap(left: str, right: str) -> bool:
    left_norm = normalize_scope(left)
    right_norm = normalize_scope(right)
    return left_norm == right_norm or left_norm.startswith(right_norm + "/") or right_norm.startswith(left_norm + "/")


def reject_overlaps(assignments: list[Assignment]) -> None:
    for left_index, left in enumerate(assignments):
        for right_index, right in enumerate(assignments[left_index + 1 :], start=left_index + 1):
            for left_scope in left.file_ownership:
                for right_scope in right.file_ownership:
                    if scopes_overlap(left_scope, right_scope):
                        raise ValueError(
                            "overlapping file ownership between "
                            f"assignment {left_index} ({left_scope}) and assignment {right_index} ({right_scope})"
                        )


def evidence_path(lane: str, phase: str, evidence_dir: Path) -> Path:
    stamp = dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")
    safe_phase = "".join(ch if ch.isalnum() else "-" for ch in phase.lower()).strip("-")
    safe_phase = "-".join(part for part in safe_phase.split("-") if part)[:80] or "phase"
    return evidence_dir / f"{stamp}-{lane}-{safe_phase}.json"


def write_evidence(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")


def prompt_for(lane: str, phase: str) -> str:
    common = (
        f"Repository: {REPO}\n"
        f"Track: conductor/tracks/{TRACK_ID}/plan.md\n"
        f"Phase/task: {phase}\n\n"
        "You are not alone in the codebase. Do not revert changes made by others. "
        "Work only on the assigned scope. Report changed files, checks run, and blockers.\n"
    )
    if lane == "codex":
        return (
            common
            + "\nRole: Codex gpt-5.5 orchestrator. Address blockers first, integrate worker output, "
            "verify Conductor evidence, run quality gates, and commit only after checks pass.\n"
        )
    if lane == "cline":
        return (
            common
            + "\nRole: Cline deepseek-v4-flash external worker. Use an isolated worktree. "
            "Do not mark Conductor tasks complete. Return evidence for Codex review.\n"
        )
    if lane == "swarm-review":
        return (
            common
            + "\nRole: Codex swarm reviewer. Inspect only the assigned scope and produce concise "
            "findings with file references. Do not edit files unless explicitly assigned ownership.\n"
        )
    raise SystemExit(f"unknown lane: {lane}")


def run_codex(args: argparse.Namespace) -> int:
    checks = doctor_checks()
    if has_blocker(checks, include_cline=False):
        print_checks(checks, as_json=False)
        print("Blocked before Codex launch.")
        return 2
    cmd = [
        CODEX_BIN,
        "exec",
        "-C",
        str(REPO),
        "-m",
        CODEX_MODEL,
        "--sandbox",
        "workspace-write",
        "--ask-for-approval",
        "never",
        prompt_for("codex", args.phase),
    ]
    evidence = evidence_path("codex", args.phase, Path(args.evidence_dir))
    payload = {
        "lane": "codex",
        "model": CODEX_MODEL,
        "phase": args.phase,
        "command": cmd,
        "checks": [asdict(check) for check in checks],
        "dry_run": not args.execute,
        "evidence_path": str(evidence.relative_to(REPO) if evidence.is_relative_to(REPO) else evidence),
    }
    if not args.execute:
        print("DRY RUN:", " ".join(cmd))
        print("EVIDENCE:", payload["evidence_path"])
        return 0
    write_evidence(evidence, payload | {"status": "started"})
    code = subprocess.call(cmd, cwd=REPO)
    write_evidence(evidence, payload | {"status": "completed", "exit_code": code})
    return code


def run_cline(args: argparse.Namespace) -> int:
    checks = doctor_checks()
    cline = next(check for check in checks if check.name == "cline_provider")
    if cline.status != "ok":
        print_checks(checks, as_json=False)
        print("Blocked before Cline launch: deepseek-v4-flash is not verified for this checkout.")
        return 2
    if has_blocker(checks, include_cline=True):
        print_checks(checks, as_json=False)
        print("Blocked before Cline launch.")
        return 2
    cmd = [
        CLINE_BIN,
        "--cwd",
        str(REPO),
        "--worktree",
        "--provider",
        CLINE_PROVIDER,
        "--model",
        CLINE_MODEL,
        "--thinking",
        "medium",
        prompt_for("cline", args.phase),
    ]
    evidence = evidence_path("cline", args.phase, Path(args.evidence_dir))
    payload = {
        "lane": "cline",
        "provider": CLINE_PROVIDER,
        "model": CLINE_MODEL,
        "phase": args.phase,
        "command": cmd,
        "checks": [asdict(check) for check in checks],
        "dry_run": not args.execute,
        "evidence_path": str(evidence.relative_to(REPO) if evidence.is_relative_to(REPO) else evidence),
    }
    if not args.execute:
        print("DRY RUN:", " ".join(cmd))
        print("EVIDENCE:", payload["evidence_path"])
        return 0
    write_evidence(evidence, payload | {"status": "started"})
    code = subprocess.call(cmd, cwd=REPO)
    write_evidence(evidence, payload | {"status": "completed", "exit_code": code})
    return code


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="PyBibX Conductor swarm launcher")
    sub = parser.add_subparsers(dest="command", required=True)

    doctor = sub.add_parser("doctor", help="Run blocker-first checks")
    doctor.add_argument("--json", action="store_true")

    plan = sub.add_parser("plan", help="Print the lane assignment plan")
    plan.add_argument("--json", action="store_true")

    validate = sub.add_parser("validate-config", help="Validate assignment config and reject overlapping scopes")
    validate.add_argument("--config", default=str(DEFAULT_CONFIG))
    validate.add_argument("--json", action="store_true")

    prompt = sub.add_parser("prompt", help="Print a lane prompt")
    prompt.add_argument("--lane", choices=["codex", "cline", "swarm-review"], required=True)
    prompt.add_argument("--phase", required=True)

    codex = sub.add_parser("run-codex", help="Launch or dry-run Codex orchestrator")
    codex.add_argument("--phase", required=True)
    codex.add_argument("--execute", action="store_true")
    codex.add_argument("--evidence-dir", default=str(DEFAULT_EVIDENCE_DIR))

    cline = sub.add_parser("run-cline", help="Launch or dry-run Cline worker")
    cline.add_argument("--phase", required=True)
    cline.add_argument("--execute", action="store_true")
    cline.add_argument("--evidence-dir", default=str(DEFAULT_EVIDENCE_DIR))

    args = parser.parse_args(argv)
    if args.command == "doctor":
        checks = doctor_checks()
        print_checks(checks, as_json=args.json)
        return 1 if has_blocker(checks, include_cline=True) else 0
    if args.command == "plan":
        data = assignment_plan()
        if args.json:
            print(json.dumps(data, indent=2))
        else:
            print(json.dumps(data, indent=2))
        return 0
    if args.command == "validate-config":
        try:
            assignments = load_assignments(Path(args.config))
        except Exception as exc:
            if args.json:
                print(json.dumps({"status": "blocked", "error": str(exc)}, indent=2))
            else:
                print(f"BLOCKED config: {exc}")
            return 2
        data = {"status": "ok", "assignments": [asdict(item) for item in assignments]}
        if args.json:
            print(json.dumps(data, indent=2))
        else:
            print(f"OK config: {len(assignments)} assignments, no overlapping file ownership")
        return 0
    if args.command == "prompt":
        print(prompt_for(args.lane, args.phase))
        return 0
    if args.command == "run-codex":
        return run_codex(args)
    if args.command == "run-cline":
        return run_cline(args)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
