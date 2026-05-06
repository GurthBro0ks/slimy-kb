# Phase 3 Passive Startup Capture

Generated: 2026-04-27

## Status

Status: `sanitized`

Raw capture committed: `no`

Secrets committed: `no`

## Capture Metadata

| Field | Value |
|---|---|
| UTC timestamp | `20260427T213957Z` |
| Device serial | `emulator-5554` |
| Package | `com.qcplay.snail.android.na` |
| Activity | `org.cocos2dx.lua.AppActivity` |
| App PID after capture | `14133` |
| Capture tool | device `tcpdump` |
| Capture mode | passive startup packet capture |
| Capture duration | about 55 seconds |
| Private raw capture path | `captures/private/phase3/20260427T213957Z/passive_startup_20260427T213957Z.pcap` |
| Private raw capture SHA256 | `3a9b12fc42949aa22f8319dc537bbe65485585b5b3121386175f4618ed63bc94` |
| Private raw capture size | `363264` bytes |
| Packet count | `3245` |
| Kernel drops | `0` |
| Remote device temp cleanup | completed |

## Redaction Checklist

- [x] No tokens.
- [x] No cookies.
- [x] No auth headers.
- [x] No device IDs.
- [x] No account IDs.
- [x] No raw request bodies.
- [x] No raw response bodies.
- [x] No raw capture files staged.

## What Was Captured

The capture was started before forcing the app closed and relaunching it. No user taps, protocol replay, API client calls, or decrypted request inspection were performed.

This is a packet-level startup capture only. It is not process-attributed, so all transport observations are candidate signals until a process-aware or proxy-assisted pass confirms they belong to Super Snail.

## Transport Observations

| Observation | Evidence | Confidence |
|---|---|---:|
| Valid PCAP produced | Host `tcpdump -r` parsed the private PCAP successfully | `0.95` |
| Dominant encrypted web transport present | Remote service port summary showed TCP/443 and UDP/443 activity | `0.75` |
| Cleartext HTTP transport present somewhere in emulator traffic | Remote service port summary showed TCP/80 activity | `0.40` |
| Possible game/custom transport candidate | Remote service port summary showed low-volume TCP/3000 activity during app startup window; later socket attribution tied it to `:jpushremote`, not the main process | `0.25` |
| DNS activity present | Remote service port summary showed UDP/53 activity | `0.90` |
| App-specific attribution | Not proven by passive PCAP alone | `0.20` |

Sanitized remote service port summary:

| Protocol | Remote service port | Packet count |
|---|---:|---:|
| TCP | `443` | `2506` |
| TCP | `80` | `286` |
| UDP | `443` | `264` |
| UDP | `53` | `126` |
| TCP | `3000` | `19` |
| TCP | `8099` | `11` |
| TCP | `55010` | `11` |
| TCP | `8010` | `10` |

Protocol family summary:

| Direction / family | Packet count |
|---|---:|
| outbound IPv4 | `1386` |
| inbound IPv4 | `1847` |
| outbound IPv6 | `6` |
| inbound IPv6 | `2` |

## Protocol Correlation Candidates

No Phase 2 protocol names can be correlated yet. The passive PCAP did not expose message names, request bodies, or process-attributed flows.

| Captured signal | Candidate protocol | Phase 2 reference | Notes | Confidence |
|---|---|---|---|---:|
| low-volume TCP/3000 during startup window | unknown | `reports/phase3-socket-attribution-20260427T2144Z.md` | candidate auxiliary push/remote channel; not currently main-process API evidence | `0.25` |

## Verified Facts

- A raw PCAP was captured privately and parsed successfully.
- The private capture had `3245` packets and `0` kernel drops.
- The app was running after capture with PID `14133`.
- The raw PCAP remained under ignored `captures/private/phase3/`.
- Device-side temporary capture files were removed after pull.

## Hypotheses

- TCP/3000 may be an auxiliary push/remote channel, because later socket attribution tied it to `com.qcplay.snail.android.na:jpushremote`.
- TCP/443 or UDP/443 may include platform, CDN, or game traffic; passive capture alone cannot separate them.
- A proxy-assisted or Frida-assisted pass is needed to determine auth flow and message framing.

## Remaining Unknowns

- Auth flow.
- Token/session behavior.
- TLS pinning behavior.
- Exact transport ownership by process.
- Whether TCP/3000 belongs to Super Snail.
- Packet-to-protocol correlation against Phase 2C/2G targets.
- Replay safety.

## QA

| Check | Result |
|---|---|
| `./scripts/phase3_capture_prep_check.sh` | `PASS`, `/tmp/proof_snail_phase3_capture_prep_20260427T213807Z` |
| `python3 ./scripts/validate_capture_report.py reports/phase3-passive-startup-capture-20260427T213957Z.md` | `PASS` |
| `./scripts/qa_gate.sh` | `PASS`, `/home/mint/projects/slimy_snail/.harness/proofs/proof_20260427T214255Z` |
| `git status --short --branch` | raw capture ignored; only safe report/tracking files pending sync |
