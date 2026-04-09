# Slimyai Setup
> Category: projects
> Sources: raw/decisions/2026-04-05-project-slimyai-setup-nuc1-state.md, raw/decisions/2026-04-05-project-slimyai-setup-nuc2-state.md, raw/research/2026-04-09-nuc2-project-inventory.md, raw/agent-learnings/2026-04-09-nuc2-slimyai-setup-update.md
> Created: 2026-04-05
> Updated: 2026-04-09
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

## NUC2 App (Discord Bot — Active)
- **Path:** `/opt/slimy/app`
- **Remote:** `git@github.com:GurthBro0ks/slimyai_setup.git`, branch `main`
- **Last 3 commits:**
  - `c1fbf1b` — docs: auto-sync project docs from slimy-nuc2 2026-04-05
  - `62efd54` — docs: auto-sync project docs from slimy-nuc2 2026-04-05
  - `8de37f4` — docs: auto-sync project docs from slimy-nuc2 2026-04-05
- **AGENTS.md:** YES — Node.js bot project agent rules
- **README.md:** YES — Super Snail Discord bot with club analytics, GPT-4 vision, DALL-E image gen, sheet sync
- **Status:** ACTIVE — Node.js Discord bot (PM2 managed), SSH tunnel for MySQL
- **Key scripts:** `scripts/ingest-club-screenshots.js`, bot deployment via `ecosystem.config.js`
- **Dependencies:** MySQL (slimyai_prod), Google Sheets API, OpenAI GPT-4 Vision
- **Ports:** 3307 (MySQL tunnel to NUC1)
- **Truth gate:** `node -e "require('./index.js')"` smoke test

## See Also
- [Slimy Monorepo](slimy-monorepo.md)
- [Slimy Discord Bot](slimy-discord-bot.md)
