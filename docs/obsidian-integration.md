# Obsidian Integration for slimy-kb

## Purpose
This integration makes Obsidian the human-facing browse and intake frontend, while `/home/slimy/kb/wiki/` remains the canonical compiled knowledge source.

## Canonical vs Mirror
- Canonical compiled wiki: `/home/slimy/kb/wiki/`
- Obsidian mirror for browsing: `/home/slimy/obsidian/slimyai-vault/Wiki/`

The vault `Wiki/` folder is a mirrored copy and should be treated as browse-only.

## Vault Layout
- `Wiki/`: mirrored KB wiki (read-only target after sync)
- `Inbox/notes/`: quick notes to ingest
- `Inbox/articles/`: longer writeups to ingest
- `Inbox/images/`: screenshots/images to ingest
- `Projects/`: project thinking notes to ingest
- `Attachments/`: optional personal vault attachments

## Writable vs Read-only
- Read-only intent: `Wiki/` (mirrored from canonical KB)
- Writable: `Inbox/*`, `Projects/`, and `Attachments/`

## Commands
- Refresh wiki mirror:
  - `bash /home/slimy/kb/tools/kb-obsidian-sync.sh`
  - or `wiki vault-sync`
- Ingest Obsidian content into KB raw:
  - `bash /home/slimy/kb/tools/kb-obsidian-ingest.sh`
  - or `wiki vault-ingest`
  - Writes ingest report: `/home/slimy/kb/output/obsidian-ingest-report-YYYYMMDD-HHMMSS.md`

## Ingest Mapping
- `Inbox/articles/*` -> `kb/raw/articles/`
- `Inbox/notes/*` -> `kb/raw/research/`
- `Projects/*` -> `kb/raw/research/`
- Image files (`png/jpg/webp/svg/...`) -> `kb/raw/research/attachments/` plus a provenance markdown wrapper in `kb/raw/research/`

Imported filenames include an `obsidian-...` prefix and source-path-derived slug for provenance.

## Duplicate Avoidance
The ingest script keeps a checksum manifest at:
- `/home/slimy/kb/output/.state/obsidian-ingest-manifest.tsv`

If a source file has not changed, ingest skips re-import.

## Ingest Provenance
Markdown ingest preserves source note metadata and adds ingest provenance fields:
- `kb_ingest_source`
- `kb_ingest_folder`
- `kb_ingest_relpath`
- `kb_ingest_timestamp`
- `kb_ingest_hash`
- `kb_ingest_type`

Image and non-markdown intake also records folder/path/hash/timestamp in generated wrapper notes.

## Daily Use (Simple)
1. Write notes in `Inbox/notes/` or `Projects/`.
2. Drop longer references in `Inbox/articles/`.
3. Drop screenshots in `Inbox/images/`.
4. Run `wiki sync`.
5. Run `wiki vault-sync`.
6. Run `wiki vault-ingest`.
7. Check status and report quickly:
   - `wiki status`
   - `wiki open-report latest`
8. Run `wiki compile-candidates` to identify uncompiled raw notes.
   - Candidate detection is strict and based on wiki article `> Sources:` lines.
9. Generate next-step prompt shortcuts when needed:
   - `wiki prompt-query "question"`
   - `wiki prompt-compile`
10. Continue normal KB compile flow from `raw/` to `wiki/`.
11. Run `wiki vault-sync` whenever you want the latest compiled wiki in Obsidian.

## Operator Panel Notes In Vault
- `Home`: `/home/slimy/obsidian/slimyai-vault/Home.md`
- `Operator Console`: `/home/slimy/obsidian/slimyai-vault/Projects/Operator Console.md`
- Shell command wiring:
  - `/home/slimy/obsidian/slimyai-vault/Plugin Setup/Shell Commands - Operator Commands.md`
  - `/home/slimy/obsidian/slimyai-vault/Plugin Setup/Shell Commands - Suggested Additions.md`
