# TCP recv → FString ExtraSlack over-read ("0x01 byte corruption") — root-cause fix

**Date**: 2026-07-09 (tool-fix-07)

## Symptom

`FetchServerCommands()` (client sends `help`, reads reply, then sends the real
command on the same connection) was **disabled** in both `llm-shell/main.cpp`
and `llmshelllite/main.cpp` with the note *"causes a 0x01 byte corruption when
called before the actual command in -c mode"*. The workaround: hardcode a
plugin-ability list for preflight (tool-fix-284). That list drifts as abilities
are added/removed.

Reproduced: any two commands on one connection corrupt the **second** —
`ls`→`linfo`, `gamestate`→`ginfo`, and stale `0x01`/garbage for short commands.
The server literally received `\x01info`. Client `send()` was proven clean
(hex-dumped exactly `69 6e 66 6f 0a`), so the corruption was **server-side**.

## Root cause

`LLMEasyShellTcpServer.cpp` / `LLMEasyShellLiteTcpServer.cpp` built the received
command string as:

```cpp
Buffer.SetNumUninitialized(FMath::Min(PendingDataSize, BufferSize)); // no room for NUL
ClientSocket->Recv(Buffer.GetData(), Buffer.Num(), BytesRead);
FString ReceivedData = FString(ANSI_TO_TCHAR(reinterpret_cast<const char*>(Buffer.GetData())), BytesRead);
```

`FString(const TCHAR*, int32)` — **the int is `ExtraSlack` (capacity), NOT a
length cap.** The recv buffer is not null-terminated, so `ANSI_TO_TCHAR`
converts until it hits a stray NUL, over-reading stale heap bytes (the previous
response's tail / uninitialized memory) *past* `BytesRead`. Those bytes get
appended to the command, survive `RightChop`, and prepend onto the next command.

Single-command `-c` connections never showed it (no "next command" to poison) —
which is exactly why disabling the extra `help` round-trip "fixed" the symptom.

## Fix (both servers)

```cpp
Buffer.SetNumUninitialized(FMath::Min(PendingDataSize, BufferSize) + 1); // +1 for NUL
ClientSocket->Recv(Buffer.GetData(), Buffer.Num() - 1, BytesRead);
Buffer[BytesRead] = 0;                                                   // terminate exact bytes
FString ReceivedData = FString(ANSI_TO_TCHAR(reinterpret_cast<const char*>(Buffer.GetData()))); // no ExtraSlack
```

Then re-enabled `FetchServerCommands(sock)` in both clients and deleted the
hardcoded plugin-ability seed from `KNOWN_COMMANDS` (dynamic `help` fetch now
keeps preflight in sync — no drift).

**Follow-up (same day):** the Lite client's seed was cleaned immediately, but the
full `llm-shell/main.cpp` still carried the old drift-prone list — `ui`/`material`/`vfx`
plus ~40 hardcoded plugin subcommands (`python scene`, `ui dump`, `vfx generate`, …).
Those are redundant: `FetchServerCommands` inserts every live ability top-level name
from the `help` abilities array, and `PreflightValidate` matches on the **first token**,
so `python <sub>` / `ui <sub>` / etc. are already covered without enumerating subcommands.
Removed them — full primary seed now mirrors Lite (native commands + native `actor`/`editor`
combos + `python` dispatcher); plugin names live only in `FALLBACK_COMMANDS` (degraded net).
This is what finally closed the hand-maintained-plugin-list drift class that had generated
repeated `KNOWN_COMMANDS`/`FALLBACK_COMMANDS` count-sync doc-fossil churn.

## Verify (live, 15155 full + 15201 lite)

- raw socket `help→info` / `gamestate→info` / `material→info`: both ports return
  clean second commands, no residual byte.
- `llmshelllite -c info` → clean `{"success":true}` (was `'info'`).
- `material list-types` → works; preflight no longer false-alarms (`material`
  isn't seeded — recognized purely via fetch).
- `foobar` control → still flagged unknown.

## Lesson

`FString(const TCHAR*, int32)` is **ExtraSlack, not length**. To build an FString
from a non-null-terminated byte span, null-terminate first, or use an
explicit-length conversion (`FUTF8ToTCHAR(ptr, len)` + `FString(len, conv.Get())`).
Passing `BytesRead` as if it were a length silently over-reads. When a bug only
appears on the *second* message of a connection, suspect leftover/over-read in
the shared receive buffer, not the transport.
