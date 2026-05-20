# NUC1 Gear Bridge — Design Recommendation
> Date: 2026-05-20
> Author: OpenCode (SlimyAI NUC1)
> Type: Recon / Design
> Status: Draft

## Context

NUC1 runs a gear donation system (Super Snail game gear screenshots donated via Discord → bot scans via vision AI → scan JSON stored locally at `/home/slimy/gear-submissions/`). NUC2 maintains a KB (Knowledge Base) and there is an existing KB bridge that publishes NUC1 host state digests to NUC2's inbox daily.

The question: how should gear scan results flow from NUC1 to NUC2's KB?

## Current Gear Donation System (NUC1)

### Flow
1. User posts gear screenshot via `/gear-donate` slash command (Discord)
2. `gear-donate.ts` processes attachment via `gearScreenshotIntake.ts`:
   - Downloads image → `/home/slimy/gear-submissions/raw/YYYY-MM-DD/<specimen_id>.png`
   - Writes metadata JSON → `/home/slimy/gear-submissions/metadata/YYYY-MM-DD/<specimen_id>.json`
   - Appends record to `submissions.jsonl`
3. Bot immediately calls `scanGearSubmission()` (synchronous, in same command handler):
   - Vision AI (Gemini via GLM endpoint, or OpenAI-compat via Z.AI) analyzes image
   - Writes scan JSON → `/home/slimy/gear-submissions/scans/YYYY-MM-DD/gear_<stamp>_<sha>.scan.json`
   - Updates metadata JSON and submissions.jsonl with scan status
4. User gets Discord embed with scan results (detected gear/soul names)

### Storage Structure
```
/home/slimy/gear-submissions/
├── submissions.jsonl        # 58 records, JSONL — primary ledger
├── raw/                     # Raw image files (YYYY-MM-DD/)
├── metadata/                # Per-specimen metadata JSON (YYYY-MM-DD/)
├── scans/                   # Scan result JSON files (YYYY-MM-DD/)
│   ├── gear_20260520T090008Z_0c8d28.scan.json  # completed (4 images detected)
│   ├── gear_20260520T091755Z_6f610e.scan.json  # failed (4 images, API 400 error)
│   └── gear_20260520T092709Z_fd86a5.scan.json  # completed_with_warnings (4 images)
└── queue/                   # Empty (sync scan done inline, no async queue)
```

### Scan Result Schema (v1.2.0)
Each scan JSON contains:
- `specimen_ids[]` — array of specimen IDs scanned together
- `scan_status` — completed | completed_with_warnings | failed | provider_unavailable
- `provider_name` — gemini | openai-compat | unavailable
- `model_name` — e.g. gemini-2.5-flash
- `image_results[]` — per-image: image_type (gear_card/soul_screen/unknown_*), confidence, extracted fields
- `warnings[]` — any scan anomalies
- `created_at` — ISO timestamp

### Recent Scan Observations (2026-05-20)
- **0900 scan**: 4 images, all detected (Big Bounce gear, 3 soul screens: Blasphemy/Revelation/Valkyrie) — `completed`
- **0917 scan**: 4 images, all failed with Gemini API 400 "Cannot fetch content from the provided URL" — `failed`
- **0927 scan**: 4 images, 3 detected, 1 unknown_image — `completed_with_warnings` (same 400 error for one image)

The 400 error suggests Discord CDN URLs are not reachable by the Gemini API endpoint (content fetch blocked). This is a known failure mode.

## Current KB Bridge (NUC1→NUC2)

### Architecture
- **Collect**: `collect_nuc1_state.sh` + `collect_repo_digests.py` → `/home/slimy/kb-bridge/outbox/YYYY-MM-DD-nuc1-{state,repos}.{md,json}`
- **Publish**: `publish_to_nuc2.sh` → SCP to `slimy@nuc2:4422:/home/slimy/kb/raw/inbox-nuc1/`
- **Timer**: systemd user unit `nuc1-kb-digest.timer` fires every 12h
- **Fail-soft**: If NUC2 unreachable, outbox files stay local, next cycle retries

### What Gets Published
1. `YYYY-MM-DD-nuc1-state.md` — host state (uptime, disk, memory, docker, PM2, systemd, ports, harness files)
2. `YYYY-MM-DD-nuc1-repos.json` — per-repo digest (name, path, branch, commit, dirty/clean, ahead/behind)
3. `YYYY-MM-DD-nuc1-repos.md` — markdown table summary of repos

## Design: NUC1 Gear Bridge

### Option A: Extend existing kb-bridge (add gear digest collector)

**Concept**: Add a `collect_gear_scan_digests.py` script that runs as part of the existing kb-bridge cycle. It reads scan JSON files from the past 24h, aggregates into a compact markdown digest, writes to outbox, and publishes via existing SCP.

**Pros**:
- Reuses existing infrastructure (timer, SCP channel, fail-soft logic, outbox)
- Simple to implement — one new collector script
- Consistent with existing patterns

**Cons**:
- Adds NUC1 gear data volume to the KB inbox (NUC2 must process it)
- Gear scan data is more dynamic than host state (new submissions throughout the day)

**Design**:
```
# New file: /home/slimy/kb-bridge/collect_gear_scan_digests.py
# Run: daily (or per-scan-event triggered)

OUTBOX = /home/slimy/kb-bridge/outbox
SCAN_ROOT = /home/slimy/gear-submissions

1. Scan submissions.jsonl for scan_status changes in past 24h
2. Read recent scan JSON files (scans/YYYY-MM-DD/*.scan.json)
3. Aggregate: specimen count by status, detected items, provider used
4. Write: YYYY-MM-DD-nuc1-gear-digest.md (and .json for machine consumption)
5. publish_to_nuc2.sh already handles today's files → SCP to NUC2

Digest format:
# NUC1 Gear Scan Digest — 2026-05-20

## Summary
- Total submissions today: 12
- Scan completed: 8 | failed: 2 | completed_with_warnings: 2
- Detected gear cards: 5 (Big Bounce, Iron Shell, ...)
- Detected soul screens: 7 (Blasphemy Soul T5, Revelation Soul T4, ...)

## Notable
- 2 scans failed with Gemini API 400 (Discord CDN URL fetch blocked)
- 1 scan completed with warnings (4th image unrecognized)

## Files
- submissions.jsonl: 58 total records
- scans/2026-05-20/: 3 scan JSON files
```

### Option B: Separate lightweight gear bridge service

**Concept**: A dedicated gear-bridge that watches the `submissions.jsonl` file for changes and immediately pushes gear scan events to NUC2 in real-time (not daily batch).

**Pros**:
- Real-time sync to NUC2 KB
- No daily batch delay

**Cons**:
- More complex (needs persistent daemon or systemd timer with shorter interval)
- Risk of flooding NUC2 with individual events
- Over-engineering for a KB that is updated on 12h cadence anyway

### Option C: Event-driven on scan completion (webhook-style)

**Concept**: When `scanGearSubmission()` completes, the bot writes a compact event record to a gear-bridge outbox that gets published on next digest cycle.

**Pros**:
- No new infrastructure — just write a JSON line to a gear-bridge outbox
- Works with existing kb-bridge mechanism

**Cons**:
- Requires bot code change (minor: add a write to gear-bridge outbox after scan)
- Still eventual consistency (next digest cycle)

## Recommendation: Option A

**Extend the existing kb-bridge** with a `collect_gear_scan_digests.py` collector that runs daily alongside the state/repos collectors. No new infrastructure, reuses fail-soft SCP channel, consistent with the 12h KB update cadence.

The gear scan data is append-only (submissions.jsonl + scan JSONs), so a daily digest is appropriate — NUC2's KB doesn't need real-time gear data, a daily summary is sufficient for KB purposes.

### Implementation Steps (for future session)
1. Create `/home/slimy/kb-bridge/collect_gear_scan_digests.py`
   - Input: scan JSON files from past 24h in `/home/slimy/gear-submissions/scans/`
   - Output: `YYYY-MM-DD-nuc1-gear-digest.{md,json}` in outbox
   - Uses existing fail-soft error handling
2. Update `run_digest_cycle.sh` to call the new collector
3. NUC2's KB ingest picks up from `inbox-nuc1/` — existing channel
4. NUC2 KB maintainer creates wiki page consuming the digest

### Data to Include in Digest
- Submission count by status
- Detected gear names (gear_card image_results)
- Detected soul screens (soul_screen image_results)
- Provider used (gemini vs openai-compat)
- Error summary (Gemini 400 Discord CDN failures)
- Any new specimen IDs for audit trail

### What NUC2 KB Gets
NUC2's `inbox-nuc1/` receives `YYYY-MM-DD-nuc1-gear-digest.md` alongside the existing state/repos digests. A wiki page or KB agent on NUC2 processes it into the knowledge base.

## Observed Issue: Discord CDN Block

Recent scans show Gemini API 400 when trying to fetch Discord CDN image URLs (`https://cdn.discordapp.com/...`). This is a known Discord CDN restriction — external services cannot fetch Discord CDN URLs.

**Impact**: Gear scans for Discord-attached images are failing with `provider_unavailable` or `unknown_error`.

**Current behavior**: Scan falls back to `failed` status, donation still completes (safe failure — scan never blocks donation), user sees "queued for lab review" or "completed with warnings" in Discord reply.

**Fix options** (out of scope for this design doc, noted for future):
1. Bot downloads Discord image to local storage BEFORE scan (already does this via `downloadAttachment`)
2. Vision API receives local file path instead of URL — but most vision APIs expect URL
3. Bot uploads to temporary hosting (Cloudflare R2, Imgur, etc.) before scanning — adds complexity and dependency
4. Use bot's own server as proxy for image fetch (bot has the image already in `/home/slimy/gear-submissions/raw/`)

Option 4 is most promising — the bot already has the image downloaded locally. The `scanSingleImage` function sends `imageUrl` to the vision API. If we could send the local file path through a local HTTP endpoint instead (e.g., `file:///home/slimy/gear-submissions/raw/...`), the vision API could fetch it via localhost. However, most vision APIs only support HTTP(S) URLs.

Alternative: Add a lightweight local HTTP server endpoint (Express/Fastify) that serves local image files, so the vision API can call `http://localhost:PORT/...` to fetch images. This would bypass the Discord CDN block entirely.

## Verification

This session:
- ✅ C1: Documented gear-submissions structure (6 subdirs, raw/metadata/scans/queue)
- ✅ C2: Documented scan JSON files (3 today, statuses: completed/failed/completed_with_warnings)
- ✅ C3: Documented gear-donate flow (intake → download → scan → reply)
- ✅ C4: Bot truth gate passes (tsc clean, 726/726 tests)
- ✅ C5: Documented kb-bridge (collect → outbox → SCP → NUC2 inbox, 12h timer)
- ✅ C6: Documented NUC2 KB inbox (SCP destination: `slimy@nuc2:4422:/home/slimy/kb/raw/inbox-nuc1/`)
- ✅ C7: Design written (this document)