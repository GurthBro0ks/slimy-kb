# Phase 3 Wire-Capture Prep

Generated: 2026-04-27

## Status

Prep complete. No live traffic capture was started.

Proof:

```text
/tmp/proof_snail_phase3_capture_prep_20260427T205158Z
```

## Runtime Check

Observed before adding capture tooling:

| Check | Result |
|---|---|
| `adb devices` | `emulator-5554 device` |
| Android boot | `sys.boot_completed=1` |
| Package installed | `com.qcplay.snail.android.na` |
| Resolved activity | `com.qcplay.snail.android.na/org.cocos2dx.lua.AppActivity` |
| App PID | `7211` |
| Top activity | `com.qcplay.snail.android.na/org.cocos2dx.lua.AppActivity` |

The emulator was already running, so the `snail-recon` fallback did not need to start a new AVD during this prep pass.

## Added Artifacts

- `scripts/phase3_capture_prep_check.sh`
- `docs/capture/phase3_wire_capture_runbook.md`
- `docs/capture/phase3_capture_report_template.md`

## Safety Gates

The prep checker verifies Git ignore coverage for representative sensitive paths:

- `.pcap`
- `.pcapng`
- `.flow`
- `.har`
- raw auth header scratch files under `data/raw/`
- token JSON scratch files under `data/raw/`
- `.env`-style files

Raw capture directories are created only under ignored/private paths:

```text
captures/private/phase3/
data/raw/phase3-wire/
```

## Correlation Inputs

The next live capture pass should use:

- `docs/protocol/phase2c_filetree_protocol_report.md`
- `docs/protocol/rank_group_arena_data_flow_map.md`
- `reports/phase2g-manager-trace-20260427T132529Z.md`

## Result

Phase 3 prep is ready. Phase 4 remains blocked until a later capture proves transport, auth flow, replay constraints, and rank/group packet correlation.
