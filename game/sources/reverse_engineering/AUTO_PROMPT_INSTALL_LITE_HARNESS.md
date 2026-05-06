# Auto-Prompt — Install Super Snail Lite Harness

Copy this into Claude Code, Codex, OpenCode, or OpenClaw from the real project root.

```bash
cat ./AGENTS.md 2>/dev/null || true
cat ./claude-progress.md 2>/dev/null || true
source ./init.sh 2>/dev/null || true

# TASK: Install a stripped-down Slimy-style harness for this Super Snail extraction project

## Goal
Create a local project harness based on SlimyAI, but stripped down:
- no Discord
- no multi-NUC dependency
- no broad repo sweeps
- automatic GitHub sync only after QA passes
- fail-closed protection against committing raw game artifacts/captures/secrets

## Required files to create or update
- PROJECT_INSTRUCTIONS.md
- AGENTS.md
- QUALITY_CRITERIA.md
- feature_list.json
- claude-progress.md
- init.sh
- snail-run
- .gitignore
- scripts/inventory.py
- scripts/proof_pack.sh
- scripts/qa_gate.sh
- scripts/git_auto_sync.sh
- scripts/make_prompt.sh
- docs/INSTALL.md
- reports/HARNESS_DESIGN_NOTES.md

## Safety requirements
- Do not overwrite original .luac files.
- Do not move/delete raw evidence unless placing a copy into quarantine with hashes.
- Do not run `git add .`.
- .gitignore must block: *.luac, *.apk, *.xapk, *.so, *.pcap, *.pcapng, *.flow, *.har, originals/, quarantine/, captures/, .env.
- Git autosync must stage only allowlisted safe files.
- QA must fail if forbidden artifacts are staged.

## Verification
Run:
./scripts/qa_gate.sh

Then update claude-progress.md with:
- files created/changed
- commands run
- proof directory
- any caveats

When done:
1. Update ./claude-progress.md with commands run, files changed, proof directory, and remaining unknowns.
2. Update ./feature_list.json if relevant.
3. Run ./scripts/qa_gate.sh and save the proof path.
4. Run ./scripts/git_auto_sync.sh only after QA passes.
5. Do not commit originals, captures, APK/XAPK, .so, .luac, secrets, or account/session data.
```
