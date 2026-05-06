# Existing Web Docs Overview

**Source:** `apps/web/app/snail/docs/page.tsx`
**Type:** Static JSX content (extracted and converted to markdown)

---

## Snail Ops Manual

Current operating notes for the SlimyAI Super Snail tools. This covers the live web surfaces, the owner-only OCR workflow, and the minimum checks to run before trusting imported club data.

## Guide Surfaces

### Club Dashboard

- Use the dashboard for the latest club roster snapshot.
- Use XLSX import when you already have structured roster data.
- Use history to confirm previous imports and pushes.

### Screenshot OCR

- Upload 1 to 10 clear PNG, JPG, or WEBP screenshots.
- Upload one metric type per batch: all Power screenshots, then a separate Sim Power batch.
- Review extracted names and powers before pushing.
- Remove questionable rows instead of pushing uncertain OCR output.

### Codes

- Use active scope for current codes.
- Check metadata when deciding whether a code needs manual review.
- Owner tools can scan and push code updates to Discord.

### Stats

- Use stats after imports to verify aggregate changes.
- Compare club dashboard rows against stats totals after large updates.
- Treat missing values as a data-source gap, not a player result.

## Access Model

| Role | Access |
|------|--------|
| Public | Snail hub, wiki, docs, public codes, public stats links. |
| Member | Guild list and authenticated dashboard areas. |
| Leader | Club dashboard and stats surfaces used for roster review. |
| Owner | Screenshot OCR, import history, pushes, and owner admin tools. |

## Data Trust Rules

- Screenshot OCR is a draft extraction until a human reviews row names and power values.
- Regular Power and Sim Power screenshots must stay in separate batches; do not merge those fields by guess.
- A Power-only batch preserves existing Sim Power, and a Sim Power-only batch preserves existing regular Power.
- XLSX imports are preferred when the source sheet is current and structured.
- Pushes should be treated as live data changes. Confirm guild, roster count, and obvious OCR mistakes first.
- When OCR and sheet data disagree, keep the original import evidence and check import history before overwriting.
