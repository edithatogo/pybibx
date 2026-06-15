#!/usr/bin/env python3
"""Smoke checks for the repo-local Conductor swarm launcher."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "conductor_swarm.py"


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=REPO,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    plan = run(["plan", "--json"])
    assert_true(plan.returncode == 0, plan.stderr)
    assert_true(json.loads(plan.stdout)["lanes"]["codex_orchestrator"]["model"] == "gpt-5.5", "missing codex model")

    prompt = run(["prompt", "--lane", "cline", "--phase", "Phase 1"])
    assert_true(prompt.returncode == 0, prompt.stderr)
    assert_true("Do not revert" in prompt.stdout, "prompt missing no-revert instruction")
    assert_true("deepseek-v4-flash" in prompt.stdout, "prompt missing Cline model")

    good = run(["validate-config", "--json"])
    assert_true(good.returncode == 0, good.stdout + good.stderr)
    assert_true(json.loads(good.stdout)["status"] == "ok", "default config did not validate")

    with tempfile.TemporaryDirectory() as tmp:
        bad_config = Path(tmp) / "bad.json"
        bad_config.write_text(
            json.dumps(
                {
                    "assignments": [
                        {
                            "lane": "codex",
                            "track_phase": "A",
                            "file_ownership": ["conductor"],
                            "acceptance_criteria": ["ok"],
                            "no_revert_instruction": "Do not revert anything.",
                        },
                        {
                            "lane": "swarm-review",
                            "track_phase": "B",
                            "file_ownership": ["conductor/design.md"],
                            "acceptance_criteria": ["ok"],
                            "no_revert_instruction": "Do not revert anything.",
                        },
                    ]
                }
            )
        )
        bad = run(["validate-config", "--config", str(bad_config), "--json"])
        assert_true(bad.returncode == 2, "overlap config should fail")
        assert_true("overlapping" in bad.stdout, "overlap failure was not explicit")

    codex_dry = run(["run-codex", "--phase", "Phase 1"])
    assert_true(codex_dry.returncode in {0, 2}, codex_dry.stdout + codex_dry.stderr)
    if codex_dry.returncode == 0:
        assert_true("DRY RUN:" in codex_dry.stdout, "codex dry-run did not stay dry")

    cline_dry = run(["run-cline", "--phase", "Phase 1"])
    assert_true(cline_dry.returncode in {0, 2}, cline_dry.stdout + cline_dry.stderr)
    if cline_dry.returncode == 2:
        assert_true("Blocked before Cline launch" in cline_dry.stdout, "cline block not explicit")

    print("conductor swarm smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

