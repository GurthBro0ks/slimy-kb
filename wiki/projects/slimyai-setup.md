# Slimyai Setup
> Category: projects
> Sources: raw/decisions/2026-04-05-project-slimyai-setup-nuc1-state.md, raw/decisions/2026-04-05-project-slimyai-setup-nuc2-state.md
> Created: 2026-04-05
> Status: draft

Slimyai Setup is the original JS Discord bot backend that preceded the TypeScript slimy-bot-v2 in the slimy-monorepo. It is currently not running on either NUC.

## Classification History
| NUC | Classification | Notes |
|-----|----------------|-------|
| NUC1 | LEGACY_CANDIDATE | No PM2, systemd, cron, or Docker; rollback script preserved |
| NUC2 | PRESENT_NOT_RUNNING | Healthcheck systemd service present (FAILED); recent commits suggest cutover work |

## Path
- **GitHub:** GurthBro0ks/slimyai_setup
- **NUC1 path:** `/opt/slimy/app`
- **NUC2 path:** `/opt/slimy/app` (symlink or separate clone)

## Supersession
- **Successor:** `slimy-bot-v2` in slimy-monorepo (`/opt/slimy/slimy-monorepo/apps/bot`)
- Cutover from slimyai_setup to slimy-bot-v2 completed **2026-04-03**
- Rollback script preserved at `/home/slimy/rollback-bot.sh` (NUC1)

## NUC2 State (2026-04-05)
- **Last commit:** `2d7edbc1` 2026-03-31 (4 days ago)
- **Dirty:** YES — untracked `command-test-report.txt`
- **slimy-web-health.service:** FAILED (systemd --user)
  - References `/opt/slimy/ops/healthcheck.sh` which was not found at scan time
  - `ops/` directory may have been cleaned up post-cutover
- **Classification (NUC2):** PRESENT_NOT_RUNNING | Confidence: MEDIUM

## See Also
- [Slimy Monorepo](slimy-monorepo.md)
- [Slimy Discord Bot](slimy-discord-bot.md)
