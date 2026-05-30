# Gear Bridge Design: NUC1 Evidence → NUC2 Web Display

**Date:** 2026-05-30
**Status:** Design (not yet implemented)
**Author:** Agent session

## 1. Architecture Discovery

### Key Finding: Everything is on NUC1 already

Both `snail_gear_evidence` (bot OCR output) and `snail_gear` (web gear editor) tables live in the **same MySQL database** (`slimy`) on **NUC1** (`slimy-mysql` Docker container, port 3306, user `root`/`password`).

NUC2's web app accesses this database through a **MySQL tunnel**:
- NUC2 `CLUB_MYSQL_HOST=127.0.0.1 PORT=3307` → tunnels to NUC1 port 3306
- NUC2 Prisma: `DATABASE_URL=mysql://slimy:...@127.0.0.1:3306/slimyai_prod` (separate local DB for users/sessions/settings)

The "bridge" is not NUC1→NUC2 in the traditional sense. It's **same-database, two tables** on NUC1, with NUC2 web app already having access via the club pool tunnel.

### Network Topology

```
Discord User
    │
    ▼
NUC1: Bot (/gear-donate)
    │  ├── gearScreenshotIntake.ts → saves raw + metadata to /home/slimy/gear-submissions/
    │  ├── gearScreenshotVisionScan.ts → Gemini OCR → writes scan JSON
    │  └── gearDonationEvidence.ts → INSERT INTO snail_gear_evidence (NUC1 MySQL slimy DB)
    │
    ▼
NUC1 MySQL (slimy DB)
    ├── snail_gear_evidence  (OCR results, 50 rows, 1 donor, detailed JSON)
    ├── snail_gear           (web gear editor, 5 rows, member_id + slot + rarity)
    ├── snail_profiles       (snail stats, 2 rows)
    ├── club_members         (Discord→member mapping, 55 members)
    │
    ▼ (MySQL tunnel port 3307)
NUC2: Web App (Next.js)
    ├── lib/club-db.ts → getClubPool("CLUB_MYSQL") → tunnel to NUC1
    ├── /api/snail/personal/[memberId]/gear (PUT) → writes snail_gear
    ├── /api/snail/personal/gear-loadout (GET/PUT) → UserSettings JSON
    └── /app/snail/personal/gear-editor.tsx → UI component
```

## 2. Schema Comparison

### snail_gear_evidence (bot OCR output — 50 rows)

| Column | Type | Purpose |
|--------|------|---------|
| id | bigint PK | Auto-increment |
| guild_id | varchar(20) | Discord guild |
| member_id | int FK → club_members.id | Resolved member |
| discord_user_id | varchar(20) | Discord user |
| source | varchar(64) | "discord_gear_donate" |
| specimen_id | varchar(80) | Unique per raw screenshot |
| image_type | varchar(40) | "gear_card" / "soul_screen" / "unknown_image" |
| gear_name | varchar(120) | e.g. "Norris-chuck", "Big Bounce" |
| gear_stage_text | varchar(30) | e.g. "+5", "+7" |
| tier_color | varchar(30) | From OCR (often null) |
| confidence | tinyint | 0-100 |
| scan_status | varchar(60) | "completed" / "failed" |
| extracted_stats | JSON | HP/ATK/DEF/RUSH, raw_notes |
| effect_lines | JSON | ["Fire DMG +600", ...] |
| soul_context | JSON | Soul tier, buffs, contracts |
| detected_at | datetime | When OCR ran |

### snail_gear (web gear editor — 5 rows)

| Column | Type | Purpose |
|--------|------|---------|
| id | int PK | Auto-increment |
| member_id | int FK → club_members.id | Which member's gear |
| slot_type | enum('snail','war') | Snail or war gear slot |
| slot_number | tinyint | Slot index (0-5) |
| gear_name | varchar(100) | Gear name |
| rarity | enum('green','blue','purple','orange','red') | Rarity tier |
| enhancement | tinyint | Enhancement level (0-?) |
| effects | JSON | Not yet populated |
| updated_at | timestamp | Last update |

### Mapping: Evidence → snail_gear

| evidence field | snail_gear field | Transform |
|----------------|-----------------|-----------|
| member_id | member_id | Direct |
| gear_name | gear_name | Direct |
| gear_stage_text "+5" | enhancement | Parse: strip "+", convert to int |
| tier_color | rarity | Map: "red"→"red", etc. (often null) |
| effect_lines | effects | Direct JSON |
| — | slot_type | Default "snail" (no slot info in OCR) |
| — | slot_number | Must be inferred/assigned (0-5) |

## 3. Bridge Approach Options

### Option A: Bot writes directly to snail_gear (REJECTED)

The bot on NUC1 already has a MySQL connection to the `slimy` DB. It could INSERT into `snail_gear` alongside `snail_gear_evidence`.

**Rejected because:**
- Violates separation of concerns: bot should capture evidence, not manage user gear loadouts
- `snail_gear` has a slot model (slot_type + slot_number) that requires user decisions
- OCR can detect gear but cannot determine which slot it goes in
- Would conflict with web editor upserts

### Option B: Web API endpoint for evidence→gear conversion (RECOMMENDED)

Create a new API endpoint on NUC2 web that:
1. Reads `snail_gear_evidence` rows for a given member
2. Presents detected gear to the user for confirmation
3. User selects slot assignment and confirms rarity
4. API writes to `snail_gear`

**New endpoint:** `POST /api/snail/personal/[memberId]/gear/from-evidence`

**Flow:**
```
Bot OCR → snail_gear_evidence
                    │
                    ▼
User opens gear editor on web
    │
    ▼
GET /api/snail/personal/[memberId]/gear/evidence
    → Returns unprocessed evidence rows (gear_name, stage, rarity hint)
    │
    ▼
User selects gear → assigns to slot → confirms
    │
    ▼
POST /api/snail/personal/[memberId]/gear
    → Existing upsert endpoint writes to snail_gear
```

**Pros:**
- Clean separation: bot captures, web displays, user decides
- Reuses existing snail_gear upsert endpoint
- User has final say on slot assignment and rarity confirmation
- No cross-NUC API calls (both tables on same DB)

**Cons:**
- Requires UI changes in gear-editor.tsx
- User must manually review each piece of evidence
- No automatic sync

### Option C: Cron sync script (FUTURE)

A background job that periodically scans `snail_gear_evidence` for high-confidence gear_card entries and auto-populates `snail_gear` for members with empty slots.

**Pros:**
- Fully automated
- No UI changes needed

**Cons:**
- Cannot determine slot assignment automatically
- May overwrite user's intentional gear setup
- No user confirmation step
- Risk of incorrect auto-placement

## 4. Discord user_id → Web User Mapping

The linkage chain is:

```
Discord user_id (e.g. "427999592986968074")
    │
    ▼ club_members.discord_user_id
club_members.id (e.g. 55)
    │
    ▼ snail_gear.member_id / snail_gear_evidence.member_id
Gear data
```

NUC2 web authentication uses a different system:
- Prisma `SlimyUser` table in `slimyai_prod` DB
- Users have `discordId` field linking to Discord user ID
- `UserSettings` stores gear loadout preferences (gearLoadoutIds in JSON)

The web gear editor uses `member_id` (club_members.id), NOT the SlimyUser.id. This means:
- A club member can have gear data even without a web account
- Web login resolves member_id via `discordId → club_members.discord_user_id`
- No data loss if user has Discord but no web account

## 5. Edge Cases

### Duplicate submissions
- `snail_gear_evidence` uses ON DUPLICATE KEY UPDATE on specimen_id + image_index
- Multiple screenshots of same gear from same user will create multiple evidence rows
- Bridge should show latest evidence per gear_name, deduped

### Failed scans
- 4 scan groups (16 specimens) failed due to glm-4.6v model 404
- 2 true orphans (raw files with no scan JSON at all)
- Failed scans have scan_status="failed", confidence=0, image_type="unknown_image"
- Evidence table still has 50 rows because some failed-scan specimens had useful data in the partial scan

### Users not in club_members
- `resolveLinkedClubMember()` returns null if no discord_user_id match
- Evidence persist returns `{status: "skipped", reason: "no_member_link"}`
- These screenshots are captured in raw/ and scans/ but NOT in snail_gear_evidence

### Rarity inference
- OCR often returns null for tier_color
- Rarity can sometimes be inferred from effect count/strength
- Best approach: default to "green" (lowest), let user upgrade

### Slot assignment ambiguity
- OCR cannot determine which gear slot (0-5 snail, 0-5 war) a piece goes in
- Must be user-assigned

## 6. Rescan Inventory

### Files needing rescan

| Category | Count | Reason |
|----------|-------|--------|
| True orphans (no scan JSON) | 2 raw files | Never scanned |
| Failed scans (glm-4.6v 404) | 4 scan groups / 16 raw files | Model not found |
| Failed scans (gemini) | 2 scan groups / 8 raw files | Various errors |
| **Total rescan candidates** | **26 raw files** | |
| Completed scans | 9 scan groups | No action needed |
| Completed with warnings | 1 scan group | May want to review |

### Rescan cost estimate
- 26 images × Gemini 2.5 Flash pricing ≈ $0.01-0.05 total
- Recommended: batch rescan in single session

## 7. Recommended Implementation Plan

### Phase 1: Rescan orphans (separate prompt)
- Rescan 26 failed/orphan raw screenshots using Gemini 2.5 Flash
- Write new scan JSONs, update snail_gear_evidence

### Phase 2: Evidence → Gear bridge API
- Add `GET /api/snail/personal/[memberId]/gear/evidence` endpoint on NUC2 web
- Returns deduped latest evidence per gear_name for the member
- Frontend: add "Import from Evidence" button in gear-editor.tsx
- User selects evidence items and assigns to slots

### Phase 3: Auto-suggest (optional future)
- When member has empty gear slots but has evidence, show suggestion badges
- One-click fill empty slots with highest-confidence evidence

## 8. Database Principle Compliance

- NUC1 `slimy` DB (bot + club data) — accessed via bot (local) and web (tunnel)
- NUC2 `slimyai_prod` DB (web users/sessions) — accessed via Prisma only
- **Never collapse**: both DBs serve distinct purposes
- Bridge reads from `slimy.snail_gear_evidence` and writes to `slimy.snail_gear` — same DB, different tables
- No cross-database queries needed
