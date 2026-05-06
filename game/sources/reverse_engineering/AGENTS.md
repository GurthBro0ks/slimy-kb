# Super Snail Extraction — Agent Operating Manual

You are operating inside the Super Snail extraction project folder.

## Mission

Build a repeatable, proof-driven analysis workflow for Super Snail protocol/reverse-product research.

This project currently contains a mix of:
- Original or reacquired `.luac` evidence.
- Decompiled/decoded/generated Lua and protocol text.
- Decode scripts.
- Prior model responses.
- Suspect rewrite/fake scripts that must not be treated as evidence.
- Harness and PM reports from SlimyAI.

Your priority is **truth preservation** before new extraction work.

## Startup Sequence

Run at the start of every session:

```bash
cat ./AGENTS.md
cat ./claude-progress.md
source ./init.sh
```

Then inspect:

```bash
cat ./PROJECT_INSTRUCTIONS.md
cat ./QUALITY_CRITERIA.md
cat ./feature_list.json
```

## Hard Rules

- **Never overwrite original evidence.**
- **Never normalize protocol strings and present them as exact originals.**
- **Never use rewritten/fake `.luac` files as source-of-truth.**
- **Never commit raw proprietary files or sensitive captures to public GitHub.**
- **Never mark a feature complete without a proof directory.**
- **No Discord/webhook interaction in this lite harness.**
- **GitHub sync is allowlist-based only.**

## Evidence Rules

Evidence tiers:

1. **Tier 0 — Fresh originals**
   - Pulled from device/APK/capture source.
   - Stored under `originals/` or external private storage.
   - Read-only if possible.
   - Has SHA256 recorded in proof pack.

2. **Tier 1 — Derived outputs**
   - Decoded Lua/text, protocol lists, markdown specs.
   - Must cite the exact input hash and script used.

3. **Tier 2 — Hypotheses**
   - Model-generated explanations, guessed mappings, inferred API behavior.
   - Must be labeled as hypothesis until verified.

4. **Tier X — Suspect/quarantined**
   - Any script that rewrites originals.
   - Any generated `.luac` presented as original.
   - Any output created from normalized strings instead of raw evidence.

## Project Layout

Recommended layout:

```text
./AGENTS.md
./PROJECT_INSTRUCTIONS.md
./QUALITY_CRITERIA.md
./feature_list.json
./claude-progress.md
./init.sh
./snail-run
./scripts/
  qa_gate.sh
  proof_pack.sh
  git_auto_sync.sh
  inventory.py
  make_prompt.sh
./reports/
./originals/        # ignored by git; raw evidence only
./quarantine/       # ignored by git; suspect/rewrite artifacts
./.harness/
  logs/
  proofs/
```

## End-of-Session Checklist

At the end of every agent session:

1. Run the project QA gate:

```bash
./scripts/qa_gate.sh
```

2. Update `claude-progress.md` with:
   - Date/time.
   - Task.
   - Files changed.
   - Commands run.
   - Proof directory path.
   - What passed.
   - What remains unknown.

3. Update `feature_list.json` if the task status changed.

4. If QA passed, run:

```bash
./scripts/git_auto_sync.sh
```

5. Do not manually `git add .`.

## Preferred Commit Style

Use precise commits:

```text
feat: add proof-backed protocol inventory gate
fix: prevent luac originals from git autosync
docs: document cipher reset evidence policy
chore: update harness progress log
```

## Current High-Priority Work

1. Stabilize folder structure and quarantine suspect artifacts.
2. Ensure `.gitignore` prevents raw game artifacts/captures from public GitHub.
3. Build repeatable proof pack workflow.
4. Re-run decoding only from read-only originals.
5. Produce sanitized protocol reports that include input hashes and caveats.
