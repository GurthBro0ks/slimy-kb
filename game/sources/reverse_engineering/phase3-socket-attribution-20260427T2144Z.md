# Phase 3 Socket Attribution

Generated: 2026-04-27

## Status

Status: `sanitized`

Raw capture committed: `no`

Secrets committed: `no`

## Purpose

The passive startup PCAP showed low-volume TCP/3000 traffic, but passive tcpdump cannot attribute packets to a process. This check used Android socket ownership to decide whether TCP/3000 is likely the main game transport.

## Commands

Sanitized command forms:

```bash
adb -s emulator-5554 shell pidof -s com.qcplay.snail.android.na
adb -s emulator-5554 shell ss -tnp
adb -s emulator-5554 shell 'tr "\\0" " " < /proc/<pid>/cmdline'
```

## Process Facts

| Process | PID | UID | Role |
|---|---:|---:|---|
| `com.qcplay.snail.android.na` | `14133` | `10192` | main game process |
| `com.qcplay.snail.android.na:jpushremote` | `14559` | `10192` | push/remote auxiliary process |

Both processes share the same app UID.

## Socket Attribution Summary

Endpoint IPs are intentionally omitted from this committed report.

| Process | Observed remote service ports | Current interpretation |
|---|---|---|
| main game process | TCP/443, TCP/80 | primary candidate for game/client web transport |
| `:jpushremote` process | TCP/3000, TCP/443 | push/remote auxiliary channel, not currently the primary main-process API path |
| WebView/Google/Chrome processes | TCP/443, UDP/443 | platform/webview background traffic, not game-specific without more evidence |

## Impact On Previous Capture Report

The earlier passive startup report treated TCP/3000 as a candidate custom/game transport because it appeared during the app startup window. Socket attribution narrows that:

- TCP/3000 is owned by `com.qcplay.snail.android.na:jpushremote`.
- Main game process sockets observed in the attribution window were TCP/443 and TCP/80.
- TCP/3000 should not be treated as the primary rank/API transport unless later Frida/proxy evidence shows the main game logic uses the `:jpushremote` channel for protocol messages.

## Updated Hypotheses

| Hypothesis | Confidence |
|---|---:|
| Main process uses HTTPS/TLS-backed transport for at least some startup traffic | `0.70` |
| TCP/3000 is an auxiliary push/remote channel | `0.75` |
| TCP/3000 is the main rank/API client transport | `0.25` |
| Proxy or Frida evidence is still needed for auth/message correlation | `0.95` |

## Remaining Unknowns

- Which TCP/443 sockets carry game protocol traffic versus platform/CDN traffic.
- Whether TCP/80 is bootstrap/config/CDN traffic or unrelated webview behavior.
- Whether TLS pinning blocks mitmproxy inspection.
- Whether request bodies contain protocol names, numeric message IDs, or custom binary framing.
- Packet-to-protocol correlation against Phase 2C/2G targets.

## Next Step

Run a proxy-readiness pass against the main process TCP/443 path:

1. Confirm emulator proxy settings can be applied and removed cleanly.
2. Start mitmproxy/mitmdump in private capture mode.
3. Relaunch the app.
4. If no HTTP(S) flows appear, move to Frida-assisted TLS/pinning discovery.

Do not commit raw mitmproxy flow files, HAR files, headers, cookies, tokens, or request/response bodies.
