# Phase 3 Capture Observation Report Template

Generated: 2026-04-27

## Status

Status: `draft`

Raw capture committed: `no`

Secrets committed: `no`

## Capture Metadata

| Field | Value |
|---|---|
| UTC timestamp | `<fill>` |
| Device serial | `emulator-5554` |
| Package | `com.qcplay.snail.android.na` |
| Activity | `org.cocos2dx.lua.AppActivity` |
| App PID at capture start | `<fill>` |
| Capture tool | `<mitmproxy/frida/tcpdump/other>` |
| Capture tool version | `<fill>` |
| Capture duration | `<fill>` |
| Private raw capture path | `<ignored/private path only>` |
| Private raw capture SHA256 | `<hash only>` |
| Redaction reviewer | `<fill>` |

## Redaction Checklist

- [ ] No tokens.
- [ ] No cookies.
- [ ] No auth headers.
- [ ] No device IDs.
- [ ] No account IDs.
- [ ] No raw request bodies.
- [ ] No raw response bodies.
- [ ] No raw capture files staged.

## Transport Observations

| Observation | Evidence | Confidence |
|---|---|---:|
| Transport type | `<HTTP/WebSocket/TCP/unknown>` | `<0.0-1.0>` |
| TLS pinning observed | `<yes/no/unknown>` | `<0.0-1.0>` |
| Login/auth endpoint shape | `<sanitized>` | `<0.0-1.0>` |
| Session refresh behavior | `<sanitized>` | `<0.0-1.0>` |
| Replay mutates state | `<yes/no/unknown>` | `<0.0-1.0>` |

## Protocol Correlation Candidates

Use Phase 2C/2G names only after there is evidence.

| Captured signal | Candidate protocol | Phase 2 reference | Notes | Confidence |
|---|---|---|---|---:|
| `<sanitized packet/message indicator>` | `<protocol name>` | `<doc/report>` | `<notes>` | `<0.0-1.0>` |

High-value target names to check first:

```text
misc@msg_arena_query_rank_score
misc@msg_arena_top_query
misc@msg_group_myrank
misc@msg_group_rank
misc@msg_group_war_group_myrank
misc@msg_group_war_group_rank
misc@msg_group_war_member_rank
misc@msg_top_rank
misc@msg_week_task_myrank
misc@msg_week_task_rank
```

## Findings

Separate verified facts from hypotheses.

### Verified Facts

- `<fill>`

### Hypotheses

- `<fill>`

## Remaining Unknowns

- `<fill>`

## QA

| Check | Result |
|---|---|
| `./scripts/phase3_capture_prep_check.sh` | `<pass/fail/proof path>` |
| `python3 ./scripts/validate_capture_report.py <this report>` | `<pass/fail>` |
| `./scripts/qa_gate.sh` | `<pass/fail/proof path>` |
| `git status --short --branch` | `<clean/no forbidden staged files>` |
