# NUC1 Intake

> Type: index
> Status: active
> Updated: 2026-04-09

<!-- KB METADATA
> Last edited: 2026-04-16 19:37 UTC (git)
> Version: r4 / 56f8615
KB METADATA -->

## Purpose

`raw/inbox-nuc1/` is the drop-off point for NUC1-sourced digests, reports, and notes that NUC2's wiki manager processes. This keeps inter-NUC intelligence flowing through the KB without building a separate transport system.

## Expected Drop-in Formats

### Markdown Summary
Filename pattern: `YYYY-MM-DD-nuc1-*.md`

Required frontmatter or header:
```markdown
# [Title]
> Type: digest|report|note|inventory
> Source: nuc1
> Date: YYYY-MM-DD
> Host: slimy-nuc1
```

### JSON Digest
Filename pattern: `YYYY-MM-DD-nuc1-*.json`

Required fields:
```json
{
  "title": "string",
  "source": "nuc1",
  "date": "YYYY-MM-DD",
  "host": "slimy-nuc1",
  "type": "digest|report|note|inventory",
  "summary": "string (1-3 sentences)",
  "body": "string or array of findings"
}
```

## How the Manager Treats Missing NUC1 Intake

**Fail-soft.** If `raw/inbox-nuc1/` is empty or absent, the wiki manager stage 1 runner proceeds normally without error. No NUC1 input is not fatal — it simply skips the intake step.

The manager logs in `wiki/log.md` whether NUC1 inbox was present and how many items were found.

## Processing

Stage 1 wiki manager reads any NUC1 inbox items, incorporates key findings into the todo queue generation, and moves processed items to `raw/agent-learnings/` with a note linking to the originating inbox file.

## See Also

- [wiki-manager-stage1](../tools/wiki_manager_stage1.sh)
- [log](../log.md)
