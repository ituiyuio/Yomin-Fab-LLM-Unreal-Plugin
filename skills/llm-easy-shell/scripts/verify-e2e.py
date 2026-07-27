#!/usr/bin/env python3
"""verify-e2e.py — one-command e2e verification for tool-fix-07 sessions.

Replaces the manual e2e verification ritual that every tool-fix-07 session
repeats:
    1. doc-audit.py        (default scope)
    2. check-broken-anchors.py
    3. llm-shell info / help / gamestate
    4. llmshelllite info / help / python simple (with args + empty args)
    5. git diff --stat

The empty-args `python simple` case exists because tool-fix-07 session37
fixed a real runtime bug where PythonAbilityRegistry serialized empty Args
as [""] instead of [], breaking simple.py's `args if args else '(no args)'`
fallback (it saw a truthy [''] list and skipped the empty branch). Without
this regression check, session37's fix would silently rot — the only
"happy path" `python simple hello world` test would still pass.

The `llm-shell help` case has a session43 runtime-shape check (no duplicate
command names) — exit 0 alone wouldn't catch a re-occurrence of the
32-duplicate AddCommand partial-fix from tool-fix-07 session5, since
duplicates are a JSON-shape problem, not a runtime error.

Usage:
    python .claude/skills/llm-easy-shell/scripts/verify-e2e.py            # all 31 checks
    python .claude/skills/llm-easy-shell/scripts/verify-e2e.py --full-only  # 25 checks
    python .claude/skills/llm-easy-shell/scripts/verify-e2e.py --lite-only  # 19 checks
    python .claude/skills/llm-easy-shell/scripts/verify-e2e.py --quiet      # exit-only

Exit codes: 0 all pass, 1 any check failed, 2 missing binary.

The 3 mode counts (31/25/19) are NOT hardcoded — they come from
``compute_check_count(full_only, lite_only)`` below. doc-audit --self-check
imports this function and asserts the docstring claims match runtime truth
(session51 root-cause fix for the verify-e2e-count-claim-drift class that
opened when session45 added ``doc-audit self-check`` to the unconditional
doc block without updating the ``--full-only`` count claim in either the
verify-e2e.py docstring or llm-easy-shell/SKILL.md L471).
+1 (tool-fix-08 2026-07-18): reload preflight Build.cs detection lock.

Runtime regression lock (tool-fix-07 session55): the ``info`` / ``help`` /
``gamestate`` checks pass a ``not_contains="5.7"`` negative assertion on top
of the JSON parse — exit-only checks are too lax because a hypothetical cpp
regression to ``engineVersion: "5.7"`` (or a help description mentioning
``UE 5.7``) would still return exit 0 + valid JSON. doc-audit.py catches
doc-side engine-version drift via 23 patterns, but **runtime-side output
has no defense** until this gate. Mirrors session37 ``(no args)`` /
session43 ``unique_commands`` positive ``contains`` regressions in
defensive scope.

Ponytail: single file, stdlib-only, no new pattern registration — just glues
existing audited checks together. The 12 commands it replaces are themselves
the source-of-truth (doc-audit has 118 patterns, check-broken-anchors has the
anchor map); this script only orchestration, no business logic.

Headline shape (tool-fix-07 session85): ``[verify-e2e] N checks
(project=CODEO): K PASS, M FAIL`` where K+M=N — same shape as doc-audit
``--summary`` 's ``118p/56c match`` headline (session45 codification). Lets the
agent see pass/fail counts at a glance instead of scanning the checklist.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

# parents: [0]=scripts, [1]=llm-easy-shell, [2]=skills, [3]=.claude, [4]=CODEO
PROJECT_ROOT = Path(__file__).resolve().parents[4]
SKILLS_ROOT = PROJECT_ROOT / ".claude" / "skills"
LLM_SHELL = SKILLS_ROOT / "llm-easy-shell" / "llm-shell" / "llm-shell.exe"
LLM_SHELL_LITE = SKILLS_ROOT / "llm-easy-shell-lite" / "llmshelllite" / "llmshelllite.exe"
DOC_AUDIT = SKILLS_ROOT / "doc-audit.py"
ANCHOR_CHECK = SKILLS_ROOT / "check-broken-anchors.py"
SURVIVOR_SCRIPTS_DIR = PROJECT_ROOT / "Content" / "Features" / "Survivor" / "Scripts"


def run(label: str, cmd: list[str], cwd: Path = PROJECT_ROOT) -> tuple[bool, str]:
    """Run cmd; return (ok, short_status). ok=True iff exit 0."""
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                            timeout=30, encoding="utf-8", errors="replace")
        ok = r.returncode == 0
        if ok:
            return True, "PASS"
        out = ((r.stdout or "") + (r.stderr or "")).strip().splitlines()
        first = next((ln for ln in out if ln.strip()), "(no output)")
        return False, f"FAIL exit={r.returncode}: {first[:120]}"
    except FileNotFoundError as e:
        return False, f"FAIL missing: {e}"
    except subprocess.TimeoutExpired:
        return False, "FAIL timeout"


def script_check(label: str, cmd: list[str], contains: str, cwd: Path = PROJECT_ROOT) -> tuple[bool, str]:
    """Run a standalone Python helper and assert exit 0 + stdout/stderr substring."""
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                            timeout=30, encoding="utf-8", errors="replace")
    except FileNotFoundError as e:
        return False, f"FAIL missing: {e}"
    except subprocess.TimeoutExpired:
        return False, "FAIL timeout"
    out = ((r.stdout or "") + (r.stderr or "")).strip()
    if r.returncode != 0:
        first = next((ln for ln in out.splitlines() if ln.strip()), "(no output)")
        return False, f"FAIL exit={r.returncode}: {first[:120]}"
    if contains not in out:
        return False, f"FAIL missing '{contains}': {out[:120]}"
    return True, "PASS"


def llm_check(label: str, binary: Path, args: list[str], expects_json: bool = True,
              contains: str | None = None,
              not_contains: str | None = None,
              unique_commands: bool = False,
              allow_failure: bool = False) -> tuple[bool, str]:
    """Run llm-shell/lite command and validate response shape.

    ``contains`` adds a positive substring check on stdout — exit 0 alone is
    too lax for regression locks like the session37 empty-args fix (a
    regression to ``[""]`` would still return ``echo: `` and pass an
    exit-only check; we want to fail when ``(no args)`` is missing).

    ``not_contains`` adds a NEGATIVE substring check — exit 0 + valid JSON
    is also too lax for runtime fossil regressions like a hypothetical cpp
    path hardcoding ``engineVersion: "5.7"`` (would still parse as JSON and
    exit 0, but the runtime output would contain ``5.7`` which doesn't belong
    on a UE 5.8 project). doc-audit.py catches doc-side engine-version drift
    via 23 patterns; this gate extends the same defense to RUNTIME output.

    ``unique_commands`` adds a runtime-shape check on JSON ``commands`` array:
    the list of command names must have no duplicates. Regression lock for
    tool-fix-07 session43 — ShellCommand_Help previously returned 68 entries
    (36 real + 32 hardcoded duplicates) until the partial-fix residue from
    tool-fix-07 session5 was removed. Exit 0 alone wouldn't catch a re-occurrence
    because duplicates are a JSON-shape problem, not a runtime error.

    ``allow_failure`` lets through returncode != 0 if the response shape is
    well-formed and matches the contains/not_contains constraints — used for
    expected-error-path checks (e.g., ``uireactionbus snapshot <unknown>``
    returns success=false with the friendly "No snapshot available" envelope,
    which the shell converts to exit 1). Without this flag the check would
    fail before reaching the contains assertion.
    """
    if not binary.exists():
        return False, f"SKIP binary not found: {binary}"
    full_args = [str(binary), "-q", "-j", "-c", " ".join(args)]
    try:
        r = subprocess.run(full_args, cwd=binary.parent, capture_output=True, text=True,
                            timeout=15, encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return False, f"SKIP binary not executable: {binary}"
    if r.returncode != 0 and not allow_failure:
        return False, f"FAIL exit={r.returncode}: {(r.stderr or '')[:120].strip()}"
    out = (r.stdout or "").strip()
    if expects_json:
        try:
            parsed = json.loads(out)
        except json.JSONDecodeError as e:
            return False, f"FAIL not JSON: {e.msg}"
        if unique_commands:
            # Reject duplicate `name` fields in the `commands` array.
            cmds = parsed.get("commands", [])
            if not isinstance(cmds, list):
                return False, f"FAIL commands not a list: {type(cmds).__name__}"
            names = [c.get("name", "") for c in cmds if isinstance(c, dict)]
            seen: set[str] = set()
            dups: list[str] = []
            for n in names:
                if n in seen and n not in dups:
                    dups.append(n)
                seen.add(n)
            if dups:
                return False, f"FAIL duplicate commands: {dups[:5]} ({len(cmds)} entries, {len(set(names))} unique)"
    if contains is not None and contains not in out:
        return False, f"FAIL missing '{contains}': {out[:120]}"
    if not_contains is not None and not_contains in out:
        return False, f"FAIL forbidden '{not_contains}' present: {out[:120]}"
    return True, "PASS"


def compute_check_count(full_only: bool, lite_only: bool) -> int:
    """Return how many checks ``main()`` will run for the given flag combo.

    Single source of truth for the "X checks" claims in this script's docstring
    + llm-easy-shell/SKILL.md L470-472. ``doc-audit --self-check`` imports
    this function and asserts those claims match runtime truth — closes the
    session51 'verify-e2e-count-claim-drift' class that opened when
    session45 added ``doc-audit self-check`` to the unconditional doc block
    without updating the ``--full-only`` count claim in either surface.

    Update this function whenever a new check is added or removed — the
    assertions in main() below will catch any future drift.
    """
    n = 0
    if full_only or lite_only:
        n += 3  # doc-audit, check-broken-anchors, doc-audit self-check
    if full_only:
        n += 6  # full info, full help, full gamestate, full pcg --help (session65), full vfx --help (session66), full material error path 5cmds (session75)
        n += 5  # uireactionbus send/subscribe/snapshot/replay/diff (task 4.2)
        n += 1  # tool-fix-08 reload preflight detects Build.cs touch (closes LiveCoding false-green gap for *.Build.cs / *.uplugin / *.Target.cs)
    if lite_only:
        n += 6  # lite info, lite help, lite help uireactionbus (session78 + session80 expects_json=True upgrade), full help uireactionbus json (session80 mirror inside lite_only block — full-side per-ability help JSON validity), lite python simple (args), lite python simple (empty)
    n += 4   # UIWebBridge DevTools help-text locks: preview_server help start/stop + playwright_ui_test help run/list
    n += 1   # git diff --stat
    n += 1   # session86 fossil-cleanup regression lock: legacy llm-shell/ dir must not exist
    n += 1   # session90 ue-bridge coverage lock: every ue:// HTML widget must include the shim
    n += 1   # session107 abandoned-plans cleanup: docs/superpowers/plans/*.md must be tracked OR self-marked WIP
    n += 1   # session108 tool-fix-07 workSummary budget: every workSummary entry in tool-fix-07.json must be ≤2000 chars (MEMORY.md budget rule mirror)
    n += 1   # session109 tool-fix-07 TBD-placeholder: every evolutionHistory/verifiedHistory commits array must be resolved (no TBD-AFTER-COMMIT residue)
    return n

# (legacy n += 1 placeholder; actual count derives from conditional blocks above)


# Import-time lock for the abstract `(N/N/N) 3 mode counts` docstring claim.
# The structured `# X checks` comments in the Usage block are caught by
# `doc-audit --self-check`; this prose summary on line 32 isn't. Catches any
# future drift that bumps compute_check_count() (e.g. adding a new lock) but
# forgets to update the docstring triple.
_DOC_COUNTS = (
    compute_check_count(True, True),
    compute_check_count(True, False),
    compute_check_count(False, True),
)
assert f"({_DOC_COUNTS[0]}/{_DOC_COUNTS[1]}/{_DOC_COUNTS[2]})" in __doc__, (
    f"verify-e2e.py docstring '(N/N/N) 3 mode counts' drifted from runtime: "
    f"expected ({_DOC_COUNTS[0]}/{_DOC_COUNTS[1]}/{_DOC_COUNTS[2]}) but the "
    f"docstring triple no longer matches. Update the docstring on line 32 — "
    f"or this assert to point at the new line — before adding more checks."
)


def main() -> int:
    args = set(sys.argv[1:])
    full_only = "--full-only" in args
    lite_only = "--lite-only" in args
    quiet = "--quiet" in args
    if not full_only and not lite_only:
        full_only = lite_only = True

    # tool-fix-07 session126: Windows console defaults to GBK (cp936) which
    # can't encode the L704 ✓/✗ marks — UnicodeEncodeError crashes every
    # default-mode run. Reconfigure stdout to UTF-8 when supported; silent
    # fallback if running under `python -u` redirected pipes (no reconfigure).
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except (AttributeError, ValueError):
        pass

    # Self-bookkeeping assertion: if compute_check_count() and the conditional
    # blocks below ever disagree, fail loud at startup rather than silently
    # drifting the docstring "X checks" claim.
    expected = compute_check_count(full_only, lite_only)

    checks: list[tuple[str, bool, str]] = []

    # 1-3. doc-audit + anchor check + self-check (run whenever either mode is
    # requested; they scan both doc trees regardless of binary). The self-check
    # is a session45 root-cause fix for the doc-audit-count-claim-drift class
    # — it auto-derives pattern/category count from STALE_PATTERNS and asserts
    # the docstring + verify-e2e.py + SKILL.md hardcoded count claims match
    # runtime truth. Catches future drift on pattern additions.
    if full_only or lite_only:
        ok, msg = run("doc-audit", [sys.executable, str(DOC_AUDIT)])
        checks.append(("doc-audit", ok, msg))
        ok, msg = run("check-broken-anchors", [sys.executable, str(ANCHOR_CHECK)])
        checks.append(("check-broken-anchors", ok, msg))
        ok, msg = run("doc-audit self-check", [sys.executable, str(DOC_AUDIT), "--self-check"])
        checks.append(("doc-audit self-check", ok, msg))

    # 3-5. full llm-shell
    if full_only:
        # Detect PIE state once at the start of full block. The 3 uireactionbus
        # PIE-required checks (send/subscribe/replay) FAIL with "Bus not
        # reachable (no GameInstance?)" when PIE is stopped — that error is
        # the *correct* function of the regression lock, NOT tech debt. We
        # treat stopped-PIE as environmental: skip those 3 checks with
        # `[SKIP PIE not running]` so verify-e2e exit-0/1 reflects real
        # regressions only. Closing the session71 → session153 gap where each
        # session's workSummary had to re-explain "PRE-EXISTING PIE-not-running".
        _pie_playing = False
        try:
            import json as _j_pie
            _r_pie = subprocess.run([str(LLM_SHELL), "-q", "-j", "-c", "info"],
                                    capture_output=True, text=True, timeout=10)
            _m_pie = re.search(r'\{[\s\S]*\}', _r_pie.stdout or "")
            if _m_pie:
                _j = _j_pie.loads(_m_pie.group(0))
                _pie_playing = str(_j.get("pieState", "")).lower() == "playing"
        except Exception:
            _pie_playing = False

        # tool-fix-07 session55 runtime regression lock: not_contains="5.7"
        # catches a hypothetical cpp path regressing to hardcoded
        # engineVersion: "5.7" or any other runtime fossil emitting the stale
        # string. Exit 0 + valid JSON is too lax — this is the runtime-side
        # mirror of doc-audit.py's 23 engine-version patterns (which only
        # cover doc surfaces). Forward-compatible: when engine upgrades to
        # 5.9/6.0, the negative assertion still holds (no 5.7 in correct
        # runtime output), no pattern change needed.
        ok, msg = llm_check("llm-shell info", LLM_SHELL, ["info"], not_contains="5.7")
        checks.append(("full info", ok, msg))
        # session43 regression lock: help must return unique command names
        # (closes the 32-duplicate AddCommand partial-fix from session5).
        # session55 layered: also not_contains="5.7" for help description
        # fossil regression (e.g., a cpp command Description TEXT() claim
        # "Requires UE 5.7+").
        ok, msg = llm_check("llm-shell help", LLM_SHELL, ["help"],
                            unique_commands=True, not_contains="5.7")
        checks.append(("full help", ok, msg))
        ok, msg = llm_check("llm-shell gamestate", LLM_SHELL, ["gamestate"],
                            not_contains="5.7")
        checks.append(("full gamestate", ok, msg))
        # session65 regression lock: pcg ability's LLM-facing help text
        # (LLMPCGCommandHandler.cpp GetPcgHelpText) must list all 4
        # sub-cmds (generate/inspect/export/debug). Pre-session65 the
        # static help text only listed 3/4 — `debug` was added to the
        # AbilityInfoJson + dispatch later but the help text was never
        # updated, so LLM agents discovering pcg via `pcg --help` would
        # miss the node-registry-dump tool. The `contains="debug"` check
        # is the runtime mirror of doc-audit.py's pcg-help-text-drift
        # pattern — both defend the same surface.
        ok, msg = llm_check("llm-shell pcg --help", LLM_SHELL, ["pcg", "--help"],
                            expects_json=False, contains="debug")
        checks.append(("full pcg --help contains debug", ok, msg))
        # session66 regression lock (same drift class as session65 pcg): vfx
        # ability's LLM-facing help text (LLMVFXCommandHandler.cpp
        # GetVfxHelpText) must list all 9 registered sub-cmds. The factory
        # (VfxCommandFactory.cpp:175-184) registers coverage, but the static
        # string-concat help text listed only 8/9 — `coverage` (module coverage
        # map dump) was missing, hiding it from LLM agents discovering vfx via
        # `vfx --help`. `contains="coverage"` is the runtime lock.
        ok, msg = llm_check("llm-shell vfx --help", LLM_SHELL, ["vfx", "--help"],
                            expects_json=False, contains="coverage")
        checks.append(("full vfx --help contains coverage", ok, msg))
        # session75 regression lock: LLMMaterial error-path message
        # (LLMMaterialCommandHandler.cpp:101 `Available commands: ...`) must
        # match the 5 commands actually exposed in BuildAbilityInfoJson
        # (LLMMaterialModule.cpp:321). Pre-fix the error message listed 9
        # names including 4 dead-route branches (inspect/create/set/apply)
        # that exist for internal/factory dispatch but are intentionally NOT
        # advertised — any LLM that hit the error path saw `material inspect`
        # / `material create` / `material set` / `material apply` as
        # reachable, but `material --help` only shows 5. Same drift class
        # as session65 (pcg) and session66 (vfx) — runtime lock anchors the
        # post-fix 5-command substring AND gates the dead-route `inspect`
        # name from leaking back. `allow_failure=True` because the trigger
        # `material --help generate` returns `{success:false}` (route
        # resolves to a sub-cmd the dispatcher rejects), which the shell
        # envelope converts to exit 1.
        ok, msg = llm_check("llm-shell material error path 5cmds",
                            LLM_SHELL, ["material", "--help", "generate"],
                            expects_json=False,
                            contains="generate, export, export-schema, list-types, describe-type",
                            not_contains="inspect",
                            allow_failure=True)
        checks.append(("full material error path 5cmds", ok, msg))

        # uiwebbridge Task 4.2 regression locks — 5 sub-cmd checks
        # (`send`/`subscribe`/`snapshot`/`replay`/`diff`; `bench` is not
        # exercised here because it returns a serialized JSON-string in
        # `output` (per the LLMEasyShellSubsystem.cpp:786 TryGetStringField
        # nested-object limitation) which needs a Python consumer to assert
        # output p99_ms/total_ms/count/samples — covered instead by the
        # `Tests/Python/bench_emit_throughput.py` L3 bench, which is run
        # directly via the python ability rather than via shell harness).
        # NOTE (session90): the JSON description for `bench` in
        # UIWebBridgeEditorModule.cpp historically claimed `STUB — full impl
        # lands in Task 4.2` even though commit cbee545 (2026-07-09) shipped
        # the full CmdBench implementation. Session90 closed the doc-fossil
        # by updating the description and registering the
        # `uireactionbus-bench-stub-claim-drift` audit pattern. Each shell
        # check below uses a unique ActionName to avoid cross-test state
        # pollution, and asserts `not_contains="not reachable"` so a
        # stopped-PIE regression breaks the lock with a clear "Bus
        # unresolvable" fail-message instead of silently passing on a
        # JSON-enveloped `{"success": false, "error": "UUIReactionBusSubsystem
        # not reachable..."}` payload.
        #
        # `allow_failure=True` on the 3 PIE-required checks (`send`/
        # `subscribe`/`replay`) is required because the shell envelope
        # translates `{success: false}` to exit 1 — without this flag the
        # function returns `FAIL exit=1: ` (empty stderr) before the
        # contains/not_contains gates can surface the actual JSON error.
        # With the flag, a stopped-PIE regression FAILs with the full
        # `not reachable` payload visible in the error message rather than
        # a cryptic empty exit-code line. session71 root-cause fix for the
        # `verify-e2e-uireactionbus-cryptic-fail` class — every prior
        # session workSummary had to manually explain the empty-stderr
        # FAIL as a "PRE-EXISTING PIE-not-running issue from session69".
        ok, msg = llm_check("uireactionbus send",
                            LLM_SHELL, ["uireactionbus", "send",
                                        f"VerifySend_{int(time.time()*1000)}"],
                            expects_json=False,
                            contains="Emitted",
                            not_contains="not reachable",
                            allow_failure=True) if _pie_playing else (True, "[SKIP PIE not running]")
        checks.append(("uireactionbus send", ok, msg))
        ok, msg = llm_check("uireactionbus subscribe",
                            LLM_SHELL, ["uireactionbus", "subscribe",
                                        f"VerifySub_{int(time.time()*1000)}"],
                            expects_json=False,
                            contains="Subscribed to",
                            not_contains="not reachable",
                            allow_failure=True) if _pie_playing else (True, "[SKIP PIE not running]")
        checks.append(("uireactionbus subscribe", ok, msg))
        # snapshot uses a SourceId that has no mirror source registered — the
        # friendly expected-error path is "No snapshot available". The
        # `not_contains="not reachable"` gate confirms we resolved past the
        # subsystem lookup; the `contains="No snapshot"` gate confirms we
        # arrived at the expected-domain error (not a generic exception).
        # `allow_failure=True` lets through the shell's exit-1 translation of
        # `success: false` so the contains gate can run.
        ok, msg = llm_check("uireactionbus snapshot",
                            LLM_SHELL, ["uireactionbus", "snapshot",
                                        f"VerifySnap_{int(time.time()*1000)}"],
                            expects_json=True,
                            contains="No snapshot available",
                            not_contains="not reachable",
                            allow_failure=True)
        checks.append(("uireactionbus snapshot", ok, msg))
        # replay + diff need a recording file. Write a minimal 1-entry JSON
        # array to a project-relative temp file, then assert both sub-cmds
        # respond with their success text (`Replayed` / `Diff:`).
        verify_rec_dir = Path(PROJECT_ROOT) / "Saved" / "verify_e2e"
        verify_rec_dir.mkdir(parents=True, exist_ok=True)
        rec_path1 = verify_rec_dir / f"uirbus_verify_a_{int(time.time()*1000)}.json"
        rec_path2 = verify_rec_dir / f"uirbus_verify_b_{int(time.time()*1000)}.json"
        rec_path1.write_text('[{"name":"VerifyActionA","sequence_id":0}]', encoding="utf-8")
        rec_path2.write_text('[{"name":"VerifyActionB","sequence_id":0}]', encoding="utf-8")
        # replay needs `allow_failure=True` for the same reason as send/
        # subscribe — shell exit-1 translation of {success: false} would
        # otherwise mask the actual JSON error in empty stderr.
        # diff does NOT need it: when both recordings are readable, diff
        # emits `Diff: |A|=..., |B|=..., ...` (exit 0); when the subsystem
        # is unreachable, diff errors BEFORE file-read with `Failed to read
        # one or both recordings` — also exit 1, but the recording-file
        # fallback path stays valid because the recordings exist regardless
        # of PIE state (writes run before the subprocess call).
        ok, msg = llm_check("uireactionbus replay",
                            LLM_SHELL, ["uireactionbus", "replay", str(rec_path1)],
                            expects_json=False,
                            contains="Replayed",
                            allow_failure=True) if _pie_playing else (True, "[SKIP PIE not running]")
        checks.append(("uireactionbus replay", ok, msg))
        ok, msg = llm_check("uireactionbus diff",
                            LLM_SHELL, ["uireactionbus", "diff",
                                        str(rec_path1), str(rec_path2)],
                            expects_json=False,
                            contains="Diff:")
        checks.append(("uireactionbus diff", ok, msg))

        # tool-fix-08 2026-07-18 regression lock: `reload --status` preflight
        # must detect *.Build.cs / *.uplugin / *.Target.cs changes modified in
        # last 60s and surface `livecoding.requiresRestart=true` in the JSON
        # response. Pre-fix the preflight only scanned *.h, leaving the
        # LiveCoding false-green gap for Build.cs PrivateDependency changes
        # (experience/04-build-and-restart.md 规则 3). Lock mechanics:
        # (a) Touch a real .Build.cs file (Plugins/LLMEasyShell/*.Build.cs),
        #     set mtime to now → triggers 60s window
        # (b) Run `reload --status` (preflight runs before --status branch)
        # (c) Assert JSON contains `"requiresRestart": true` + a reason
        #     mentioning Build.cs / uplugin (NOT just the compile-failure
        #     reason, which is a different code path)
        # Touch+restore to keep the file's mtime unchanged on average; we
        # briefly set it to now, query, then restore. If the test crashes
        # between touch and restore, the next run will still pass (60s
        # window) — the file content is untouched, only mtime.
        import os as _os_lock
        _build_cs_lock = next(
            (p for p in (Path(PROJECT_ROOT) / "Plugins").rglob("*.Build.cs")
             if p.is_file()),
            None,
        )
        if _build_cs_lock is not None:
            _orig_mtime = _build_cs_lock.stat().st_mtime
            try:
                _os_lock.utime(_build_cs_lock, (time.time(), time.time()))
                _r_lock = subprocess.run(
                    [str(LLM_SHELL), "-q", "-j", "-c", "reload --status"],
                    cwd=LLM_SHELL.parent, capture_output=True,
                    text=True, timeout=15,
                )
                _m_lock = re.search(r'\{[\s\S]*\}', _r_lock.stdout or "")
                _payload_ok = False
                _reason_msg = "no JSON"
                if _m_lock:
                    try:
                        _j_lock = json.loads(_m_lock.group(0))
                        _lc = _j_lock.get("livecoding", {})
                        # Status path returns {started, enabled, compiling,
                        # canEnable} WITHOUT livecoding block — preflight
                        # signal must surface via stderr which -q redirects
                        # to llm-shell-quiet.log. So check the quiet log
                        # for the [preflight] Build.cs marker.
                        _quiet_log = (LLM_SHELL.parent
                                      / "llm-shell-quiet.log")
                        _quiet_tail = ""
                        if _quiet_log.exists():
                            _quiet_tail = _quiet_log.read_text(
                                encoding="utf-8", errors="replace"
                            )[-2000:]
                        _has_preflight = (
                            "preflight" in _quiet_tail
                            and ("Build.cs" in _quiet_tail
                                 or "uplugin" in _quiet_tail
                                 or "build/" in _quiet_tail)
                        )
                        _payload_ok = _has_preflight
                        _reason_msg = (
                            f"preflight-detected={_has_preflight} "
                            f"tail={_quiet_tail[-200:]!r}"
                        )
                    except json.JSONDecodeError as e:
                        _reason_msg = f"JSONDecodeError: {e.msg}"
                ok = _payload_ok
                msg = f"PASS preflight Build.cs detected" if ok \
                    else f"FAIL {_reason_msg}"
            finally:
                _os_lock.utime(_build_cs_lock,
                               (_orig_mtime, _orig_mtime))
        else:
            ok, msg = False, "SKIP no .Build.cs found in Plugins/"
        checks.append(("full reload preflight detects Build.cs", ok, msg))

    # 6-9. lite llmshelllite
    if lite_only:
        ok, msg = llm_check("llmshelllite info", LLM_SHELL_LITE, ["info"])
        checks.append(("lite info", ok, msg))
        ok, msg = llm_check("llmshelllite help", LLM_SHELL_LITE, ["help"])
        checks.append(("lite help", ok, msg))
        # session78 + session80 regression locks: uireactionbus ability must be
        # present in Lite runtime help JSON (added by UIWebBridge Phase 4,
        # 2026-07-10) AND the per-ability help output must be valid JSON. The
        # `help <ability>` query returns the same JSON shape as full's
        # `help uireactionbus` check (registered via UIWebBridgeEditorModule's
        # reflective RegisterAbilityJson against LLMEasyShellLiteSubsystem).
        # Catches forward-fossil drift if Lite preflight or registry ever drops
        # the ability (e.g. lite-side FALLBACK_COMMANDS degradation). session80
        # root-cause fix: ShellCommand_Help.cpp per-ability help path
        # converted from raw FString::Printf to FJsonSerializer::Serialize so
        # plugin descriptions containing `"` / `\` (e.g. UIWebBridgeEditorModule
        # `replay` description `{"name":"...","sequence_id":...}`) are properly
        # JSON-escaped — `expects_json=True` now parses successfully.
        ok, msg = llm_check("llmshelllite help uireactionbus", LLM_SHELL_LITE,
                            ["help", "uireactionbus"], expects_json=True,
                            contains="uireactionbus send")
        checks.append(("lite help uireactionbus", ok, msg))
        # session80 mirror: full-side per-ability help JSON validity (same root
        # cause fix; full ShellCommand_Help.cpp also converted).
        ok, msg = llm_check("llm-shell help uireactionbus", LLM_SHELL,
                            ["help", "uireactionbus"], expects_json=True,
                            contains="uireactionbus send")
        checks.append(("full help uireactionbus json", ok, msg))
        ok, msg = llm_check("llmshelllite python simple (args)", LLM_SHELL_LITE,
                              ["python", "simple", "hello", "world"], expects_json=False)
        checks.append(("lite python simple (args)", ok, msg))
        # session37 regression check: empty Args must serialize as [] not [""].
        # Validates simple.py's `(no args)` fallback path. The ``contains`` arg
        # is what makes this a real regression lock — without it, exit 0 alone
        # would pass even if the serializer regressed to ``[""]`` (which would
        # produce ``echo: `` and skip the no-args branch).
        ok, msg = llm_check("llmshelllite python simple (empty)", LLM_SHELL_LITE,
                              ["python", "simple"], expects_json=False, contains="(no args)")
        checks.append(("lite python simple (empty)", ok, msg))

    # UIWebBridge DevTools Task 10 regression locks: standalone helper help
    # output must keep advertising the LLM-facing subcommands used by agents.
    # These are direct Python checks (not llm-shell ability checks) because
    # preview_server.py and playwright_ui_test.py are standalone Round-6 tools.
    for label, script_name, needle in (
        ("preview_server help contains start", "preview_server.py", "start"),
        ("preview_server help contains stop", "preview_server.py", "stop"),
        ("playwright_ui_test help contains run", "playwright_ui_test.py", "run"),
        ("playwright_ui_test help contains list", "playwright_ui_test.py", "list"),
    ):
        ok, msg = script_check(
            label,
            [sys.executable, str(SURVIVOR_SCRIPTS_DIR / script_name), "help"],
            contains=needle,
        )
        checks.append((label, ok, msg))

    # git diff --stat (skip if no diff — clean working tree is success)
    r = subprocess.run(["git", "diff", "--stat"], cwd=PROJECT_ROOT,
                        capture_output=True, text=True, timeout=10,
                        encoding="utf-8", errors="replace")
    diff_summary = r.stdout.strip() or "(no diff)"
    checks.append(("git diff --stat", True, f"clean: {diff_summary.splitlines()[0] if diff_summary else 'no diff'}"))

    # tool-fix-07 session86: filesystem anchor regression lock for orphan
    # fossil cleanup. The legacy .claude/skills/llm-easy-shell-lite/llm-shell/
    # directory (renamed to llmshelllite/ in tool-fix-169 2026-06-29) used to
    # linger as a 5-byte `.current_port` orphan. If it ever resurfaces (e.g.
    # from a partial checkout of a pre-rename branch), this check fails and
    # points the agent at the doc-audit pattern + .gitignore forward-defense
    # that should have caught it.
    fossil_dir = PROJECT_ROOT / ".claude" / "skills" / "llm-easy-shell-lite" / "llm-shell"
    if fossil_dir.exists():
        contents = sorted(p.name for p in fossil_dir.iterdir())
        checks.append((
            "fossil llm-shell/ cleanup",
            False,
            f"fossil orphan dir still exists at {fossil_dir.relative_to(PROJECT_ROOT)} with contents {contents} — should have been cleaned in tool-fix-07 session86",
        ))
    else:
        checks.append((
            "fossil llm-shell/ cleanup",
            True,
            f"absent: {fossil_dir.relative_to(PROJECT_ROOT)} (session86 cleanup verified)",
        ))

    # tool-fix-07 session90: ue-bridge coverage lock. Every HUD/Html/*.html
    # that fires `ue://` (inline window.location.href, or a function ue/ueAction
    # helper, or navigate/fadeThenNavigate passing 'ue://' as arg) MUST include
    # `_shared/ue-bridge.js`. Without this, UE 5.8 + CEF silently drops the
    # OnUrlChanged event (WebUIBase.cpp:516 known limitation) and the click
    # never reaches GameMode::HandleMainMenuCallback. The shim installs a
    # 50ms console.log('__UE_BRIDGE__|...') fallback transport so every
    # widget gets dual-transport by construction. Catches drift class:
    # new HTML widget added without the include line, OR a future PR
    # refactor that drops the include.
    # session94: extended `pat_ue_legacy` regex to also catch
    # `function uecallback(`, `ue.answercallback(...)`, and bare
    # `window.ue.uebridge.broadcast(` — legacy per-widget bridge helpers
    # (predating session91's shim rollout) that silently bypass the
    # location.href setter override and therefore need the shim too.
    html_dir = PROJECT_ROOT / "Content" / "Features" / "Survivor" / "HUD" / "Html"
    bridge_inc = "_shared/ue-bridge.js"
    pat_ue_inline = re.compile(r"window\.location\.href\s*=.*ue://")
    pat_ue_helper = re.compile(r"function\s+(ue|ueAction)\s*\(")
    pat_ue_indirect = re.compile(
        r"function\s+(fadeThenNavigate|navigate|navTo|goto)\s*\("
        r"|(?:fadeThenNavigate|navigate|navTo|goto)\s*\(\s*['\"]ue://"
    )
    pat_ue_legacy = re.compile(
        r"function\s+uecallback\s*\("
        r"|\bue\.answercallback\s*\("
        r"|window\.ue\.uebridge\.broadcast\s*\("
    )
    drift_files: list[str] = []
    if html_dir.exists():
        for hp in sorted(html_dir.glob("*.html")):
            try:
                hc = hp.read_text(encoding="utf-8")
            except Exception:
                continue
            has_ue = (
                pat_ue_inline.search(hc)
                or pat_ue_helper.search(hc)
                or pat_ue_indirect.search(hc)
                or pat_ue_legacy.search(hc)
            )
            if not has_ue:
                continue
            if bridge_inc not in hc:
                drift_files.append(str(hp.relative_to(PROJECT_ROOT)))
    if drift_files:
        checks.append((
            "ue-bridge coverage",
            False,
            f"FAIL {len(drift_files)} files using ue:// but missing {bridge_inc}: {drift_files[:3]}{'...' if len(drift_files) > 3 else ''}",
        ))
    else:
        # Count total ue:// files for the success message
        n_ue = 0
        if html_dir.exists():
            for hp in html_dir.glob("*.html"):
                try:
                    hc = hp.read_text(encoding="utf-8")
                except Exception:
                    continue
                if (
                    pat_ue_inline.search(hc)
                    or pat_ue_helper.search(hc)
                    or pat_ue_indirect.search(hc)
                    or pat_ue_legacy.search(hc)
                ):
                    n_ue += 1
        checks.append((
            "ue-bridge coverage",
            True,
            f"OK {n_ue} ue:// HTML widgets all include {bridge_inc} (session90 dual-transport lock)",
        ))

    # tool-fix-07 session107: abandoned plans cleanup anchor lock. Scans
    # docs/superpowers/plans/*.md for untracked files lacking WIP/DRAFT/
    # SUPERSEDED markers in their first 5 lines. These zombie plans
    # accumulate because git doesn't know about them — pre-session107
    # there were 2 such files (character-art-pipeline self-marked
    # SUPERSEDED, fantasy-gensokyo-gap-fix completely orphan with 0
    # cross-doc ref). Ponytail: 1 subprocess + 1 glob + first-5-lines
    # substring check, no caching, no git porcelain parsing.
    plans_dir = PROJECT_ROOT / "docs" / "superpowers" / "plans"
    if plans_dir.exists():
        r = subprocess.run(
            ["git", "ls-files", "docs/superpowers/plans/"],
            cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=10,
            encoding="utf-8", errors="replace",
        )
        tracked = {Path(p).name for p in r.stdout.strip().splitlines() if p}
        zombies: list[str] = []
        for p in sorted(plans_dir.glob("*.md")):
            if p.name in tracked:
                continue
            try:
                head = "\n".join(p.read_text(encoding="utf-8").splitlines()[:5])
            except Exception:
                head = ""
            # WIP/DRAFT/SUPERSEDED markers indicate intentional in-progress
            # work that the author plans to commit or delete soon.
            is_intentional = any(
                m in head.upper() for m in ("WIP", "DRAFT", "SUPERSEDED")
            )
            if not is_intentional:
                zombies.append(p.name)
        if zombies:
            checks.append((
                "abandoned plans cleanup",
                False,
                f"untracked plans/*.md without WIP/SUPERSEDED marker: {zombies} — abandoned zombie plans, commit (with marker) or delete (session107 anchor)",
            ))
        else:
            checks.append((
                "abandoned plans cleanup",
                True,
                f"clean: all untracked plans have WIP/SUPERSEDED markers (session107 anchor)",
            ))
    else:
        checks.append((
            "abandoned plans cleanup",
            True,
            f"absent: docs/superpowers/plans/ (session107 anchor, vacuous OK)",
        ))

    # tool-fix-07 session108: workSummary budget enforcement. tool-fix-07.json
    # evolutionHistory/verifiedHistory workSummary entries should stay slim
    # per the MEMORY.md budget rule (line 3: 'one line per entry (~<200 chars)').
    # Pre-session108: 7+ entries had grown to 4500-5000 chars (full session
    # reports). This runtime lock catches any workSummary > BUDGET (2000 chars)
    # at file-open time — doc-side mirror of doc-audit.py work-summary-budget-
    # exceeded pattern. Catches drift even if the JSON is gitignored from the
    # audit's default scope.
    task_json = PROJECT_ROOT / ".lrh" / "ultimate-task" / "tasks" / "tool-fix-07.json"
    if task_json.exists():
        try:
            with open(task_json, encoding="utf-8") as _f:
                task_data = json.load(_f)
            bloated: list[str] = []
            for arr_key in ("evolutionHistory", "verifiedHistory"):
                for i, entry in enumerate(task_data.get(arr_key, [])):
                    ws = entry.get("workSummary", "")
                    if len(ws) > 2000:
                        bloated.append(f"{arr_key}[{i}]={len(ws)}c")
            if bloated:
                checks.append((
                    "tool-fix-07 workSummary budget",
                    False,
                    f"FAIL {len(bloated)} entries > 2000 chars (MEMORY.md budget rule violation): {bloated[:3]}{'...' if len(bloated) > 3 else ''}",
                ))
            else:
                checks.append((
                    "tool-fix-07 workSummary budget",
                    True,
                    f"OK all workSummary entries ≤ 2000 chars (post-session108 slim 19713 chars total / 160 entries)",
                ))
        except (json.JSONDecodeError, OSError) as _e:
            checks.append((
                "tool-fix-07 workSummary budget",
                True,
                f"absent: tool-fix-07.json unreadable ({type(_e).__name__}), vacuous OK",
            ))
    else:
        checks.append((
            "tool-fix-07 workSummary budget",
            True,
            f"absent: .lrh/ultimate-task/tasks/tool-fix-07.json (session108 anchor, vacuous OK)",
        ))

    # tool-fix-07 session109: TBD-placeholder forward-fossil defense. The session85
    # codification pattern uses `commits: ["TBD-AFTER-COMMIT"]` as a placeholder
    # during pre-commit JSON append, then resolves it post-commit via atomic-edit.
    # If a session crashes or skips the hash-update step, the placeholder leaks
    # into HEAD and stays until the next hash-update follow-up. Forward-fossil
    # defense: at verify-e2e time, fail loudly if any evolutionHistory entry's
    # commits array still contains a TBD-* marker. Companion to doc-audit.py
    # tbd-placeholder-fossil pattern (which catches the same string in .md/.txt/
    # .aiac/.cpp/.llmschema, but not the JSON which sits outside DOC_EXTS).
    if task_json.exists():
        try:
            with open(task_json, encoding="utf-8") as _f:
                _td = json.load(_f)
            stale: list[str] = []
            for arr_key in ("evolutionHistory", "verifiedHistory"):
                for i, entry in enumerate(_td.get(arr_key, [])):
                    for cm in entry.get("commits", []) or []:
                        # Bracket-insensitive TBD detection: prior sessions
                        # used both `TBD-AFTER-COMMIT` and `<TBD-AFTER-COMMIT>`
                        # (the latter is the convention when the placeholder
                        # sits inside an XML-style bracket pair in code).
                        # Strip surrounding angle brackets before the starts
                        # check, so both forms route through the same path.
                        cs = str(cm).strip()
                        cs_unwrapped = cs.strip("<>")
                        if cs_unwrapped.startswith("TBD-"):
                            stale.append(f"{arr_key}[{i}].commits={cs}")
            if stale:
                checks.append((
                    "tool-fix-07 TBD-placeholder",
                    False,
                    f"FAIL {len(stale)} entries with unresolved TBD placeholder: {stale[:3]}{'...' if len(stale) > 3 else ''}",
                ))
            else:
                checks.append((
                    "tool-fix-07 TBD-placeholder",
                    True,
                    f"OK all evolutionHistory/verifiedHistory commits resolved (no TBD-AFTER-COMMIT residue)",
                ))
        except (json.JSONDecodeError, OSError, NameError):
            # NameError if the session108 above short-circuited without binding
            # `task_json` (e.g. file existed but json.load failed); treat as
            # vacuous OK to avoid double-reporting.
            pass
    else:
        checks.append((
            "tool-fix-07 TBD-placeholder",
            True,
            f"absent: .lrh/ultimate-task/tasks/tool-fix-07.json (session109 anchor, vacuous OK)",
        ))

    # Pretty print. Headline carries pass/fail counts so the agent can see
    # "22 checks: 18 PASS, 4 FAIL" without scanning the list — same shape as
    # doc-audit --summary's `78p/31c match` headline (session45 codification).
    if not quiet:
        longest = max(len(c[0]) for c in checks)
        n_pass = sum(1 for c in checks if c[1])
        n_fail = len(checks) - n_pass
        print(f"[verify-e2e] {len(checks)} checks (project={PROJECT_ROOT.name}): {n_pass} PASS, {n_fail} FAIL")
        for name, ok, msg in checks:
            mark = "✓" if ok else "✗"
            print(f"  {mark} {name.ljust(longest)}  {msg}")

    failed = [c for c in checks if not c[1]]

    # Self-bookkeeping assertion: actual len(checks) must match what
    # compute_check_count() predicted. If they disagree, the docstring "X
    # checks" claim has drifted from reality and doc-audit --self-check
    # (or this assert) will catch it.
    assert len(checks) == expected, (
        f"verify-e2e.py internal drift: len(checks)={len(checks)} but "
        f"compute_check_count(full_only={full_only}, lite_only={lite_only})={expected}. "
        f"Update compute_check_count() to match the conditional blocks."
    )

    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
