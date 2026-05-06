# Phase 3 Wire-Capture Prep Runbook

Generated: 2026-04-27

## Scope

This runbook prepares for owned-device Super Snail traffic research. It does not authorize committing raw traffic, account data, auth headers, cookies, tokens, device IDs, or session identifiers.

Phase 3 starts with runtime readiness and safety gates. Live capture should only begin after the prep check passes.

## Required Preflight

Run from the project root:

```bash
cat ./AGENTS.md
cat ./claude-progress.md
source ./init.sh
./scripts/phase3_capture_prep_check.sh
```

The prep script must pass before any traffic capture work.

It verifies:

- `adb` sees `emulator-5554`.
- If the emulator is down, the script attempts to start the `snail-recon` AVD.
- Android boot is complete.
- `com.qcplay.snail.android.na` is installed.
- `com.qcplay.snail.android.na/org.cocos2dx.lua.AppActivity` resolves.
- The app has a PID and is the resumed/top activity.
- Private capture paths are ignored by Git.
- `./scripts/qa_gate.sh` passes.

## Private Capture Storage

Raw captures stay ignored/private:

```text
captures/private/phase3/
data/raw/phase3-wire/
```

Allowed private-only examples:

```text
captures/private/phase3/<timestamp>.pcapng
captures/private/phase3/<timestamp>.flow
captures/private/phase3/<timestamp>.har
data/raw/phase3-wire/<timestamp>-headers-redaction-source.txt
```

Do not commit files from those paths.

## Sanitized Outputs

Commit only sanitized summaries under:

```text
reports/
docs/capture/
```

Sanitized reports may include:

- Tool versions.
- Capture timestamps.
- SHA256 hashes of private capture files.
- Redacted endpoint hostnames if they do not include account/session material.
- Message names or IDs only after correlation.
- Redaction status.
- Open questions.

Sanitized reports must not include:

- Tokens.
- Cookies.
- Authorization headers.
- Device IDs.
- Account IDs.
- Raw request or response bodies.
- Raw PCAP/HAR/mitmproxy content.

## Correlation Inputs

Use these Phase 2 artifacts as the decoder ring once capture metadata exists:

- `docs/protocol/phase2c_filetree_protocol_report.md`
  - 954 of 962 protocol candidates matched live handler filenames.
  - High-value rank/group/arena names are listed.
- `docs/protocol/rank_group_arena_data_flow_map.md`
  - Maps target protocols to manager calls and likely `lpc` fields.
- `reports/phase2g-manager-trace-20260427T132529Z.md`
  - Confirms `RankM.setRankInfo` opaque list storage.
  - Confirms `msg_group_war_member_rank` field-flow evidence.

## Capture Session Rules

1. Run `./scripts/phase3_capture_prep_check.sh`.
2. Start proxy/Frida tooling only after preflight passes.
3. Save raw capture artifacts only under ignored private paths.
4. Keep a separate redaction scratch note outside Git if needed.
5. Create a sanitized observation report from `docs/capture/phase3_capture_report_template.md`.
6. Validate the sanitized report before committing:

```bash
python3 ./scripts/validate_capture_report.py <sanitized-report.md>
```

7. Run `./scripts/qa_gate.sh`.
8. Run `./scripts/git_auto_sync.sh` only after QA passes.

## Stop Conditions

Stop and do not autosync if any of these happen:

- A token, cookie, auth header, account ID, or device ID is visible in a report.
- A `.pcap`, `.pcapng`, `.flow`, or `.har` file appears staged.
- `validate_capture_report.py` flags the sanitized report.
- The app is not running or top/resumed.
- Capture tooling requires installing unknown root certificates or hooks without a written note.
- Transport/auth behavior is ambiguous enough that replay could mutate account state.

## Phase 4 Gate

Do not build the API client until Phase 3 proves:

- Transport type.
- Auth flow.
- Session lifetime or refresh behavior.
- Whether requests can be replayed safely.
- Which captured packets correlate to Phase 2C/2G rank/group targets.
