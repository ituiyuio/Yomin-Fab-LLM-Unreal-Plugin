---
name: ue-restore-packages-dialog-blocker
description: "Force-killed UE5.7 editor leaves \"Restore Packages\" modal that blocks restart forever — delete Saved/Autosaves/PackageRestoreData.json to dismiss"
metadata: 
 node_type: memory
 type: feedback
 originSessionId: 72fdc994-e247-4286-957b-7f45b3379f41
---

When `llm-shell --restart` force-kills `UnrealEditor.exe` (graceful shutdown times out), the next launch shows a modal "Restore Packages" dialog with "Discard and Continue" / "Restore Now" buttons. In autonomous / headless sessions no one clicks, and:
- Editor process is up (3-4 GB RAM)
- TCP port 15151 is in LISTENING
- But all TCP connect attempts SYN_SENT → timeout (the modal blocks the editor's message pump)
- Sending Enter via PowerShell `PostMessage` doesn't dismiss it (window doesn't have standard button IDs)
- Editor appears "alive" but unreachable for hours

**Fix**: delete `Saved/Autosaves/PackageRestoreData.json` BEFORE the next restart. The file is UTF-16:
```
{ "RestoreEnabled": true, "Packages": [{"PackagePathName": "/Game/...", "AutoSavePath": "Game/..._Auto1.umap"}] }
```
Removing it makes the editor launch without showing the dialog. The `_AutoN.umap` files in `Saved/Autosaves/Game/.../` can stay (they're just .umap backups).

**Why:** A 5-second fix that took 30 minutes to diagnose. The dialog isn't shown in `Get-Process | MainWindowTitle` reliably because the parent UnrealWindow may have the title while child controls are focus targets.

**How to apply:** Whenever a `restart` cycle happens and the post-restart editor takes >2 min to respond on port 15151, immediately `rm Saved/Autosaves/PackageRestoreData.json` and restart again. Add a pre-check to the restart script that does this proactively.

Related: see [[ue-editor-state]] for the editor-state awareness pattern.
