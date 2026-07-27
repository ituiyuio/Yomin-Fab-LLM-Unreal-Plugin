#!/usr/bin/env python3
"""Regression test for verify-e2e.py session85 headline `N PASS, M FAIL` shape.

ROOT CAUSE: prior to session85 the headline was just ``21 checks (project=CODEO):``
which forced LLM agents to scan the per-check ok/x list to learn pass/fail counts.
Session85 makes the counts explicit at the top. This test pins the format so a
future edit can't drop the counts or re-order them.

Run:
    python .claude/skills/llm-easy-shell/scripts/test_verify_e2e_headline.py
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
VERIFY_E2E = PROJECT_ROOT / ".claude" / "skills" / "llm-easy-shell" / "scripts" / "verify-e2e.py"


def _run_headline_capture() -> str:
    """Run verify-e2e in default mode and return the FIRST line of stdout.
    That's the headline — only this matters for the format assertion. The
    rest of the output can be empty/garbled for the test's purposes.
    """
    r = subprocess.run(
        [sys.executable, str(VERIFY_E2E)],
        cwd=PROJECT_ROOT, capture_output=True, text=True,
        timeout=60, encoding="utf-8", errors="replace",
    )
    out = (r.stdout or "").strip().splitlines()
    return out[0] if out else ""


def test_headline_has_pass_fail_counts() -> None:
    headline = _run_headline_capture()
    # Expected format: "[verify-e2e] N checks (project=CODEO): K PASS, M FAIL"
    pattern = re.compile(
        r"\[verify-e2e\]\s+(\d+)\s+checks\s+\(project=[^)]+\):\s+(\d+)\s+PASS,\s+(\d+)\s+FAIL"
    )
    m = pattern.search(headline)
    assert m is not None, (
        f"verify-e2e headline has wrong shape; expected "
        f"'[verify-e2e] N checks (project=CODEO): K PASS, M FAIL' "
        f"(session85 codification), got: {headline!r}"
    )
    total, n_pass, n_fail = int(m.group(1)), int(m.group(2)), int(m.group(3))
    assert n_pass + n_fail == total, (
        f"headline totals don't match: {n_pass}+{n_fail}={n_pass+n_fail} "
        f"but claimed total {total}"
    )


if __name__ == "__main__":
    try:
        test_headline_has_pass_fail_counts()
    except AssertionError as e:
        print(f"FAIL: {e}")
        sys.exit(1)
    print("PASS: verify-e2e.py headline has session85 N PASS, M FAIL shape")
    sys.exit(0)
