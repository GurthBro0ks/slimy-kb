#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT/init.sh" >/dev/null
PROOF="$($ROOT/scripts/proof_pack.sh)"
LOG="$PROOF/qa.log"
RESULT="$PROOF/RESULT.txt"
FAIL=0

log(){ echo "$*" | tee -a "$LOG"; }
pass(){ log "PASS: $*"; }
fail(){ log "FAIL: $*"; FAIL=1; }
warn(){ log "WARN: $*"; }

log "QA proof: $PROOF"

# Required files
for f in AGENTS.md PROJECT_INSTRUCTIONS.md QUALITY_CRITERIA.md feature_list.json claude-progress.md init.sh snail-run scripts/git_auto_sync.sh scripts/inventory.py scripts/proof_pack.sh; do
  [[ -e "$ROOT/$f" ]] && pass "required file exists: $f" || fail "missing required file: $f"
done

# Syntax checks
bash -n "$ROOT/init.sh" && pass "init.sh syntax" || fail "init.sh syntax"
bash -n "$ROOT/snail-run" && pass "snail-run syntax" || fail "snail-run syntax"
for sh in "$ROOT"/scripts/*.sh; do
  bash -n "$sh" && pass "$(basename "$sh") syntax" || fail "$(basename "$sh") syntax"
done
PYTHONNOUSERSITE=1 python3 -S -m py_compile "$ROOT/scripts/inventory.py" && pass "inventory.py compiles" || fail "inventory.py compile"
if [[ -f "$ROOT/scripts/validate_capture_report.py" ]]; then
  PYTHONNOUSERSITE=1 python3 -S -m py_compile "$ROOT/scripts/validate_capture_report.py" && pass "validate_capture_report.py compiles" || fail "validate_capture_report.py compile"
fi
PYTHONNOUSERSITE=1 python3 -S -m json.tool "$ROOT/feature_list.json" >/dev/null && pass "feature_list.json valid JSON" || fail "feature_list.json invalid JSON"

# Git ignore safety checks
for pat in "*.luac" "*.apk" "*.xapk" "*.so" "*.pcap" "*.flow" "originals/" "quarantine/" ".env"; do
  grep -Fq "$pat" "$ROOT/.gitignore" && pass ".gitignore blocks $pat" || fail ".gitignore missing $pat"
done

# Search for scripts that overwrite luac evidence
if grep -RIn --include='*.py' --include='*.sh' --exclude='qa_gate.sh' --exclude='import_tmp_project_files.py' -E "open\([^)]*\.luac[^)]*['\"]w|> *.*\.luac|cat .* > .*\.luac" "$ROOT" \
  --exclude-dir=.git --exclude-dir=.harness --exclude-dir=quarantine --exclude-dir=originals > "$PROOF/luac-write-scan.txt" 2>/dev/null; then
  # Allow the scan file itself to exist, but fail on matches.
  if [[ -s "$PROOF/luac-write-scan.txt" ]]; then
    fail "potential .luac overwrite logic found; see $PROOF/luac-write-scan.txt"
  else
    pass "no .luac overwrite patterns found"
  fi
else
  pass "no .luac overwrite patterns found"
fi

# Ensure git autosync does not use git add .
if grep "git add \." "$ROOT/scripts/git_auto_sync.sh" | grep -v '#' > "$PROOF/git-add-dot-scan.txt" 2>/dev/null; then
  fail "git_auto_sync.sh uses git add ."
else
  pass "git_auto_sync.sh avoids git add ."
fi

# Check staged files for forbidden artifacts
if git -C "$ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git -C "$ROOT" diff --cached --name-status > "$PROOF/staged-files.txt" || true
  awk '$1 !~ /^D/ {print $NF}' "$PROOF/staged-files.txt" > "$PROOF/staged-nondeleted-files.txt"
  if grep -E '\.(luac|apk|xapk|apks|aab|so|pcap|pcapng|flow|har)$|(^|/)originals/|(^|/)quarantine/|(^|/)captures/|(^|/)\.env' "$PROOF/staged-nondeleted-files.txt" >/dev/null 2>&1; then
    fail "forbidden artifacts are staged; see $PROOF/staged-files.txt"
  else
    pass "no forbidden artifacts staged for add/modify"
  fi
else
  warn "not a git repo; staged-file check skipped"
fi

# Capture report secret guard. This intentionally scans only capture docs and
# reports, so general policy docs can keep using literal warning terms.
CAPTURE_REPORTS=()
while IFS= read -r -d '' f; do
  CAPTURE_REPORTS+=("$f")
done < <(find "$ROOT/docs/capture" "$ROOT/reports" -type f \( -name '*capture*.md' -o -name '*wire*.md' \) -print0 2>/dev/null)
if [[ "${#CAPTURE_REPORTS[@]}" -gt 0 && -f "$ROOT/scripts/validate_capture_report.py" ]]; then
  if PYTHONNOUSERSITE=1 python3 -S "$ROOT/scripts/validate_capture_report.py" "${CAPTURE_REPORTS[@]}" > "$PROOF/capture-report-validation.txt" 2>&1; then
    pass "capture docs/reports sanitized"
  else
    fail "capture docs/reports may contain sensitive material; see $PROOF/capture-report-validation.txt"
  fi
fi

if [[ "$FAIL" -eq 0 ]]; then
  echo "PASS" > "$RESULT"
  log "RESULT: PASS"
else
  echo "FAIL" > "$RESULT"
  log "RESULT: FAIL"
fi

log "Proof directory: $PROOF"
[[ "$FAIL" -eq 0 ]]
