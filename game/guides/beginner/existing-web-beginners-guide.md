# Existing Web Beginner's Guide

**Source:** `apps/web/app/snail/wiki/page.tsx`
**Type:** Static JSX content (extracted and converted to markdown)

---

## What is Super Snail?

Super Snail is a mobile idle RPG where you progress through increasingly powerful stages, collect resources, and compete with other players through club-based rankings. It combines idle mechanics with active progression — your snail keeps growing even when you're away, but smart decisions accelerate your gains significantly.

## How to Join Cormys Bar

Cormys Bar is our club and the heart of our community. To join:

1. Reach the required level to unlock the Club feature in-game.
2. Open the Club menu and search for **Cormys Bar**.
3. Apply to join — an officer will approve your request.
4. Join our Discord for coordination, tips, and bot commands.

## Linking Your Account

To use SlimyAI bot commands for stats tracking, you'll need to link your Discord account with your in-game profile. Use the `/snail stats` command in Discord to get started. The bot will guide you through linking your game account so your power data and rankings are tracked automatically.

## Power Leveling Basics

### SIM Power

SIM Power represents your snail's core combat strength. It's the primary metric used in club rankings and determines your effectiveness in battles. Higher SIM Power means faster stage clears and better rewards.

### Total Power

Total Power is the combined measure of all your snail's stats, equipment, and bonuses. It provides a more holistic view of your overall progression. Both SIM Power and Total Power contribute to your club's ranking.

### How Power is Calculated

Power is derived from multiple in-game systems working together — your snail's base stats, equipped gear and upgrades, collected companions and their levels, research and technology bonuses, and various multipliers from events and buffs. Each system contributes to your overall power number.

### Tips for Increasing Power Quickly

- Log in daily to collect idle rewards and maintain streaks
- Prioritize upgrades that give the biggest power-per-resource ratio
- Participate in events for limited-time bonuses and exclusive items
- Keep your companions leveled — they provide significant passive bonuses
- Join club activities for group rewards that boost individual power
- Redeem active codes regularly for free resources (see Code Redemption below)

## Club Management

### How Club Rankings Work

Club rankings are determined by the aggregate power of all members. Every member's contribution matters. Clubs are ranked against other clubs in the game, and high rankings unlock exclusive rewards and bonuses for all members. The more powerful your club, the better the perks.

### Weekly Snapshots & WoW Tracking

SlimyAI takes weekly snapshots of club member power data. This allows us to track week-over-week (WoW) changes — who's growing fast, who might need help, and how the club is trending overall. These snapshots are taken when officers run club analysis and the data is committed to our tracking system.

### Reading the /club-stats Command

The `/club-stats` Discord command shows a summary of club performance:

- **Total Members** — current roster count
- **Average Power** — mean power level across all members
- **Top Movers** — members with the biggest WoW power gains
- **Decliners** — members whose power dropped (may need help)

### Reading the Website Stats Pages

For detailed stats, check the web dashboard. The Club Dashboard shows sortable member rankings with SIM Power, Total Power, and WoW change %. The Stats page breaks down top 10 lists, movers, and decliners. All data is owner-authenticated and sourced from our weekly MySQL snapshots.

## Code Redemption

### Where to Find Codes

Redeem codes are distributed through several channels: the in-game mailbox often contains codes from the developers, official social media posts announce limited-time codes, community events may distribute exclusive codes, and our SlimyAI bot aggregates all known active codes for easy access.

### How to Redeem Codes

1. Open Super Snail and navigate to the settings or redemption menu in-game.
2. Enter the code exactly as shown (codes are usually case-sensitive).
3. Confirm the redemption — rewards will appear in your mailbox.

### Using the /snail codes Bot Command

Type `/snail codes` in Discord to browse all currently active codes. The bot pulls from multiple sources and categorizes codes as **Latest** or **Older** so you can prioritize which to redeem first. Codes that have expired are automatically filtered out.

## Bot Commands Reference

All commands run in Discord:

| Command | Category | Description |
|---------|----------|-------------|
| `/club-stats` | CLUB | View club power rankings with WoW changes |
| `/club-analyze` | CLUB | Analyze club roster screenshots and commit data |
| `/snail codes` | SNAIL | Browse all active game redemption codes |
| `/snail analyze` | SNAIL | Analyze game screenshots for power data |
| `/snail stats` | SNAIL | View your personal stats and linked account info |
| `/leaderboard` | RANKING | View club power leaderboard rankings |
| `/farming` | GUIDE | Farming tips, guides, and airdrop tracking |
| `/chat` | AI | Chat with the AI assistant |
| `/dream` | AI | Generate AI images with style presets |

## Useful Links

- SlimyAI Website — Main site & dashboard
- Club Stats — Cormys Bar rankings & data
- Stats Dashboard — Detailed power analysis
- Game Codes — Active redemption codes
