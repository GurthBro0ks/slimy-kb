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
- Laptop -> NUC2 SSH pattern for operator commands:
  - `ssh work-nuc2 'cd /home/slimy/kb && /home/slimy/kb/tools/wiki <subcommand>'`

## Recommended Plugin Setup
- Shell Commands plugin:
  - Command 1 label: `Slimy: Vault Ingest`
  - Command 1 script: `bash /home/slimy/kb/tools/kb-obsidian-ingest.sh`
  - Command 2 label: `Slimy: Vault Sync`
  - Command 2 script: `bash /home/slimy/kb/tools/kb-obsidian-sync.sh`
  - Additional operator labels:
    - `Slimy: Wiki Status`
    - `Slimy: Compile Candidates`
    - `Slimy: Open Latest Report`
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
- `wiki compile-candidates` — raw markdown not yet cited in wiki `> Sources:` lines
- `wiki prompt-query "question"` — generate a query prompt file in `output/prompts/`
- `wiki prompt-compile` — generate a compile prompt file in `output/prompts/`

## Obsidian Notes To Create/Use
- `Home` — `/home/slimy/obsidian/slimyai-vault/Home.md`
- `First 5 Minutes` — `/home/slimy/obsidian/slimyai-vault/Plugin Setup/First 5 Minutes.md`
- `Operator Console` — `/home/slimy/obsidian/slimyai-vault/Projects/Operator Console.md`
- `Shell Commands - Operator Commands` — `/home/slimy/obsidian/slimyai-vault/Plugin Setup/Shell Commands - Operator Commands.md`
- `Shell Commands - Suggested Additions` — `/home/slimy/obsidian/slimyai-vault/Plugin Setup/Shell Commands - Suggested Additions.md`
