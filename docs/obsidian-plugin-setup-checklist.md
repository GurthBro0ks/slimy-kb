# Obsidian Plugin Setup Checklist

Use this to configure the operator vault for clean KB intake.

## Required Vault Paths
- Vault root: `/home/slimy/obsidian/slimyai-vault`
- Intake folders:
  - `Inbox/articles`
  - `Inbox/images`
  - `Inbox/notes`
  - `Projects`
- Browse-only folder:
  - `Wiki`

## Shell Command Wiring
- Remote shell command for ingest:
  - `bash /home/slimy/kb/tools/kb-obsidian-ingest.sh`
- Remote shell command for mirror refresh:
  - `bash /home/slimy/kb/tools/kb-obsidian-sync.sh`

## Recommended Plugin Setup
- Shell Commands plugin:
  - Command 1 label: `Slimy: Vault Ingest`
  - Command 1 script: `bash /home/slimy/kb/tools/kb-obsidian-ingest.sh`
  - Command 2 label: `Slimy: Vault Sync`
  - Command 2 script: `bash /home/slimy/kb/tools/kb-obsidian-sync.sh`
- Templater or core Templates:
  - Point templates folder to `Templates/`
- Dataview:
  - Optional only, dashboard must still be readable without it

## Post-Setup Checks
1. Create a note in `Inbox/notes`.
2. Run `Slimy: Vault Ingest`.
3. Confirm a new raw file appears in `/home/slimy/kb/raw/research`.
4. Confirm ingest report appears in `/home/slimy/kb/output/`.
5. Run `Slimy: Vault Sync` and verify `Wiki/` refreshes.
6. In terminal, run `wiki status` and `wiki open-report latest` to confirm operator visibility.

## Guardrails
- Do not edit `Wiki/` as canonical source.
- Do not run a second KB inside Obsidian.
- Treat clipped notes as intake material.

## Operator Shortcuts After Capture
- `wiki status` — current counts and latest report pointers
- `wiki compile-candidates` — raw markdown likely not yet compiled into wiki sources
- `wiki prompt-query "question"` — generate a query prompt file in `output/prompts/`
- `wiki prompt-compile` — generate a compile prompt file in `output/prompts/`
