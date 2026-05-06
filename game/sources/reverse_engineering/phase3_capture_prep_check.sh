#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERIAL="${ANDROID_SERIAL:-emulator-5554}"
AVD_NAME="${SNAIL_AVD_NAME:-snail-recon}"
PACKAGE="${SNAIL_PACKAGE:-com.qcplay.snail.android.na}"
ACTIVITY="${SNAIL_ACTIVITY:-org.cocos2dx.lua.AppActivity}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
PROOF="/tmp/proof_snail_phase3_capture_prep_${STAMP}"

mkdir -p "$PROOF"
cd "$ROOT"

log() {
  printf '[phase3-prep] %s\n' "$*"
}

run_capture() {
  local name="$1"
  shift
  {
    printf '$'
    printf ' %q' "$@"
    printf '\n'
    "$@"
  } > "$PROOF/${name}.txt" 2>&1
}

wait_for_device() {
  local waited=0
  while [ "$waited" -lt 120 ]; do
    if adb devices | awk 'NR > 1 && $1 == serial && $2 == "device" { found=1 } END { exit found ? 0 : 1 }' serial="$SERIAL"; then
      return 0
    fi
    sleep 2
    waited=$((waited + 2))
  done
  return 1
}

wait_for_boot() {
  local waited=0
  while [ "$waited" -lt 180 ]; do
    if [ "$(adb -s "$SERIAL" shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')" = "1" ]; then
      return 0
    fi
    sleep 2
    waited=$((waited + 2))
  done
  return 1
}

log "proof: $PROOF"

run_capture adb-devices adb devices

if ! adb devices | awk 'NR > 1 && $1 == serial && $2 == "device" { found=1 } END { exit found ? 0 : 1 }' serial="$SERIAL"; then
  log "$SERIAL is not running; attempting to start $AVD_NAME"
  if ! command -v emulator >/dev/null 2>&1; then
    echo "ERROR: emulator command not found and $SERIAL is not connected" | tee "$PROOF/RESULT.txt"
    exit 1
  fi
  nohup emulator -avd "$AVD_NAME" -no-snapshot-save > "$PROOF/emulator-${AVD_NAME}.log" 2>&1 &
  echo "$!" > "$PROOF/emulator.pid"
  wait_for_device
  wait_for_boot
fi

run_capture boot-completed adb -s "$SERIAL" shell getprop sys.boot_completed
run_capture package-list adb -s "$SERIAL" shell pm list packages "$PACKAGE"
run_capture resolve-activity adb -s "$SERIAL" shell cmd package resolve-activity --brief "$PACKAGE"

PID="$(adb -s "$SERIAL" shell pidof -s "$PACKAGE" 2>/dev/null | tr -d '\r' || true)"
if [ -z "$PID" ]; then
  log "$PACKAGE is not running; launching $PACKAGE/$ACTIVITY"
  run_capture app-launch adb -s "$SERIAL" shell am start -n "$PACKAGE/$ACTIVITY"
  sleep 8
  PID="$(adb -s "$SERIAL" shell pidof -s "$PACKAGE" 2>/dev/null | tr -d '\r' || true)"
fi

printf '%s\n' "${PID:-missing}" > "$PROOF/app-pid.txt"
run_capture top-activity bash -lc "adb -s '$SERIAL' shell dumpsys activity activities | rg 'mResumedActivity|topResumedActivity|ResumedActivity' || true"

if [ -z "$PID" ]; then
  echo "FAIL: $PACKAGE did not start; see $PROOF" | tee "$PROOF/RESULT.txt"
  exit 1
fi

mkdir -p "$ROOT/captures/private/phase3"
mkdir -p "$ROOT/data/raw/phase3-wire"
{
  echo "$ROOT/captures/private/phase3"
  echo "$ROOT/data/raw/phase3-wire"
} > "$PROOF/ignored-private-dirs.txt"

cat > "$PROOF/git-ignore-probes.txt" <<'EOF2'
captures/private/phase3/session.pcap
captures/private/phase3/session.pcapng
captures/private/phase3/session.flow
captures/private/phase3/session.har
data/raw/phase3-wire/auth_headers.txt
data/raw/phase3-wire/session_tokens.json
.env.phase3
EOF2

while IFS= read -r path; do
  git check-ignore "$path"
done < "$PROOF/git-ignore-probes.txt" > "$PROOF/git-check-ignore-results.txt"

if [ "$(wc -l < "$PROOF/git-check-ignore-results.txt" | tr -d ' ')" != "$(wc -l < "$PROOF/git-ignore-probes.txt" | tr -d ' ')" ]; then
  echo "FAIL: one or more sensitive probe paths are not ignored" | tee "$PROOF/RESULT.txt"
  exit 1
fi

if ! ./scripts/qa_gate.sh > "$PROOF/qa_gate.txt" 2>&1; then
  echo "FAIL: qa_gate failed; see $PROOF/qa_gate.txt" | tee "$PROOF/RESULT.txt"
  exit 1
fi

cat > "$PROOF/RESULT.txt" <<EOF2
PASS_PHASE3_CAPTURE_PREP_READY
serial=$SERIAL
package=$PACKAGE
pid=$PID
raw_capture_started=false
proof=$PROOF
EOF2

cat "$PROOF/RESULT.txt"
