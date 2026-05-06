# Stripped-Down Harness Design Notes

## What was kept from SlimyAI

- Agent operating manual (`AGENTS.md`).
- Local init script.
- Quality criteria.
- Feature tracker.
- Progress log.
- Builder/QA separation as a rule.
- Proof-pack mindset.
- Commit/push discipline.

## What was removed

- Discord notifications.
- Multi-NUC discovery.
- Global `/home/slimy` dependency.
- Qwen auto-dispatch.
- Broad multi-repo sweeps.
- Cron automation by default.

## What was added for this project

- Strong raw-artifact GitHub guardrails.
- `.luac` overwrite detection.
- Inventory classification.
- Proof packs with SHA256 hashes.
- Allowlist-based GitHub autosync.
- Quarantine/originals folder convention.

## Why

This project is evidence-sensitive. The biggest risk is not a failed script; it is accidentally treating generated/rewritten data as original evidence or pushing raw game/account artifacts to a public repo.
