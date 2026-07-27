---
name: bp-cdo-commit-before-save-2026-06-26
description: "BP CDO silent failure — commit message says wire but binary lacks wire (commit before BP save), 1-line grep verify"
metadata: 
 node_type: memory
 type: feedback
 originSessionId: f388e538-b26b-41d3-b6fd-42144eeb79c9
---

# BP CDO Commit-Before-Save Silent Failure (2026-06-26)

## Root Cause

UE BP editor Save flow vs `git commit` flow are independent. Common pattern:
1. LLM/operator opens BP in UE editor, sets property in property panel
2. LLM/operator **forgets to Ctrl+S / `save /Game/.../BP_X`** before git commit
3. `git add` + `git commit` commits the **previous** on-disk bin (before the property change)
4. Commit message claims wire but committed `.uasset` lacks the wire refs
5. C++ runtime guard fires silently (`if (!CharacterVFXData) { UE_LOG warning; return; }`)
6. Feature ships as "wired" but silently no-ops at runtime

## Real Example (Session 54)

- Commit `69be288` message: "wire CharacterVFXData on BP_SurvivorPlayer CDO"
- Committed binary (64016 bytes): `grep -aoE 'DA_CharacterVFX_Default|CharacterVFXData'` → **0 matches**
- Working binary (64272 bytes, +256): same grep → 3 matches
- SurvivorPlayerCharacter.cpp:3339 `if (!CharacterVFXData)` would fire 24 times per PIE
- Fix: re-save BP in editor, commit, +256 bytes is the actual wire (TObjectPtr + soft path + GUID)

## Verify Pattern (Ponytail Rung 7)

After any BP CDO wire commit, **always** verify binary contents:

```bash
# Verify wire string actually in committed binary
grep -aoE 'PropertyName|RefAssetPath' <(git show HEAD:Content/.../BP_X.uasset) | sort -u
# Compare against working binary
grep -aoE 'PropertyName|RefAssetPath' Content/.../BP_X.uasset | sort -u
```

If committed binary has 0 matches but working binary has matches → commit was made before BP save → re-commit.

## Prevention (Root-Cause Fix)

1. After BP property edit in UE editor → **always** `save /Game/.../BP_X` (LLMEasyShell)
2. After save → **always** `git diff --stat` to confirm `.uasset` size delta matches expected (TObjectPtr ref ≈ 256 bytes per reference)
3. After commit → `git show HEAD:Content/.../BP_X.uasset | grep <ref-name>` to verify wire in committed binary
4. If size delta is 0 but commit message claims wire → it's the silent failure pattern → re-save + recommit

## Related Memory

- [[bp-cdo-debug-pattern-2026-05-19]] — BP CDO property debugging commands
-— git_precommit stale state lesson (same trust-binary-not-message pattern)
- [[ue58-teds-plugin-crash-workaround-2026-06-26]] — UE 5.8 editor crash + workarounds (editor online stability required for re-save flow)