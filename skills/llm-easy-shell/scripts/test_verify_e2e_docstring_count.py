#!/usr/bin/env python3
"""Regression test for verify-e2e.py docstring `(N/N/N)` count claim.

ROOT CAUSE (2026-07-10): verify-e2e.py line 32 docstring still says
"The 3 mode counts (12/8/9) are NOT hardcoded" — but ``compute_check_count``
actually returns 21/15/10 (default / full-only / lite-only). The existing
``doc-audit --self-check`` only validates the structured ``# X checks``
comments in the Usage block (lines 25-27), not the abstract `(N/N/N)` prose
on line 32 — a structural blind spot.

This test extracts the `(N/N/N)` claim from verify-e2e.py's own docstring
and asserts it equals the runtime truth. Once it passes, the SAME assertion
can be folded into verify-e2e.py as an import-time lock so the drift can't
recur silently.

Run:
    python .claude/skills/llm-easy-shell/scripts/test_verify_e2e_docstring_count.py
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
VERIFY_E2E = PROJECT_ROOT / ".claude" / "skills" / "llm-easy-shell" / "scripts" / "verify-e2e.py"


def _load_verify_e2e():
    spec = importlib.util.spec_from_file_location("verify_e2e", VERIFY_E2E)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _extract_docstring_counts(source: str) -> tuple[int, int, int]:
    """Pull the `(N1/N2/N3)` triple from the 3 mode counts prose line."""
    match = re.search(r"\((\d+)\s*/\s*(\d+)\s*/\s*(\d+)\)", source)
    if not match is None and "3 mode counts" in source.split(match.group(0))[0][-80:]:
        return int(match.group(1)), int(match.group(2)), int(match.group(3))
    raise AssertionError(
        "verify-e2e.py docstring missing the '(N/N/N) 3 mode counts' line — "
        "add a single line like 'The 3 mode counts (X/Y/Z) are NOT hardcoded' "
        "so the regression lock has something to assert against."
    )


def test_docstring_counts_match_runtime() -> None:
    source = VERIFY_E2E.read_text(encoding="utf-8")
    claimed = _extract_docstring_counts(source)
    mod = _load_verify_e2e()
    runtime_default = mod.compute_check_count(True, True)
    runtime_full_only = mod.compute_check_count(True, False)
    runtime_lite_only = mod.compute_check_count(False, True)
    assert claimed == (runtime_default, runtime_full_only, runtime_lite_only), (
        f"docstring claim {claimed} != runtime truth "
        f"({runtime_default}/{runtime_full_only}/{runtime_lite_only}). "
        f"Update verify-e2e.py docstring to the runtime values, or the runtime "
        f"values drifted from the intended check count."
    )


if __name__ == "__main__":
    try:
        test_docstring_counts_match_runtime()
    except AssertionError as e:
        print(f"FAIL: {e}")
        sys.exit(1)
    print("PASS: verify-e2e.py docstring (N/N/N) matches compute_check_count() runtime truth")
    sys.exit(0)
