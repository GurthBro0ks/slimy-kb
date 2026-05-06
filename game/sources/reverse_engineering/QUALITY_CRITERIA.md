# Quality Criteria — Super Snail Extraction Lite Harness

## 1. Evidence Safety — weight 3x, hard fail

Pass requires:
- Originals are not modified.
- Raw game artifacts are not committed.
- Every derived output references input hashes and script names.
- Suspect rewrite/fake artifacts are identified or quarantined.

Hard fail:
- Any script overwrites an original `.luac`, APK/XAPK, `.so`, capture, or source evidence file.
- Any public Git commit stages raw proprietary/sensitive artifacts.

## 2. Correctness — weight 3x, hard fail

Pass requires:
- Scripts run without syntax/runtime errors.
- Output claims match the actual files used.
- Exact protocol strings are separated from normalized/sanitized strings.

Hard fail:
- Generated or normalized output is represented as raw truth.
- Evidence chain is broken or unverifiable.

## 3. Reproducibility — weight 2x

Pass requires:
- Commands are documented.
- Proof directory contains hashes, inventory, git status, and command logs.
- Another agent can rerun the step from the same inputs.

## 4. GitHub Hygiene — weight 2x, hard fail

Pass requires:
- `git_auto_sync.sh` only stages allowlisted safe files.
- `.gitignore` blocks APK/XAPK, `.luac`, `.so`, captures, secrets, and proof raw dumps.
- Git status is checked before and after autosync.

Hard fail:
- `git add .` is used by automation.
- Secrets or raw game files are staged.

## 5. Documentation — weight 1x

Pass requires:
- `claude-progress.md` is updated.
- Feature status is updated when relevant.
- Caveats and unverified claims are clearly labeled.

## Pass Threshold

- Weighted pass threshold: **80%**.
- Any hard fail = rejection regardless of score.

## Required QA Command

```bash
./scripts/qa_gate.sh
```
