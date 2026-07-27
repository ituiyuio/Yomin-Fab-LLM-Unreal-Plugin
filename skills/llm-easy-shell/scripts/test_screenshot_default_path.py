#!/usr/bin/env python3
"""Static regression: LLMShell screenshot default paths must point to Saved/Screenshots.

Runs in any shell; no Unreal dependency.
"""

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]

TARGETS = [
    REPO_ROOT / "Plugins" / "LLMEasyShell" / "Source" / "LLMEasyShell" / "Private" / "ShellCommand_UIShot.cpp",
    REPO_ROOT / "Plugins" / "LLMEasyShell" / "Source" / "LLMEasyShell" / "Private" / "UIInteractor.cpp",
    REPO_ROOT / "Plugins" / "LLMEasyShell" / "Source" / "LLMEasyShell" / "Private" / "UIInteractor.h",
    REPO_ROOT / "Plugins" / "LLMEasyShell" / "Source" / "LLMEasyShell" / "Public" / "LLMEasyShellTypes.h",
    REPO_ROOT / "Plugins" / "LLMEasyShell" / "Source" / "LLMEasyShell" / "Private" / "aiac" / "UI" / "UI.aia",
    REPO_ROOT / ".claude" / "skills" / "llm-easy-shell" / "references" / "commands.md",
]

FORBIDDEN = [
    re.compile(r"Saved/LLMUISpy"),
    re.compile(r"TEXT\(\"LLMUISpy\"\)"),
]

EXPECTED = {
    "ShellCommand_UIShot.cpp": re.compile(r"Saved/Screenshots/ui_shot_"),
    "UIInteractor.cpp": re.compile(r"TEXT\(\"Screenshots\"\)"),
    "UIInteractor.h": re.compile(r"Saved/Screenshots/ui_widget_"),
    "LLMEasyShellTypes.h": re.compile(r"Screenshots/ui_shot_"),
    "UI.aia": re.compile(r"Saved/Screenshots/ui_shot_"),
    "commands.md": re.compile(r"Screenshots/ui_shot_"),
}


def main() -> int:
    failures = []
    for path in TARGETS:
        if not path.exists():
            failures.append(f"missing target: {path.relative_to(REPO_ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(REPO_ROOT).as_posix()
        for pat in FORBIDDEN:
            if pat.search(text):
                failures.append(f"{rel}: still contains forbidden pattern {pat.pattern!r}")
        expected = EXPECTED.get(path.name)
        if expected and not expected.search(text):
            failures.append(f"{rel}: missing expected pattern {expected.pattern!r}")
    if failures:
        print("FAIL")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("PASS: all LLMShell screenshot defaults point to Saved/Screenshots")
    return 0


if __name__ == "__main__":
    sys.exit(main())
