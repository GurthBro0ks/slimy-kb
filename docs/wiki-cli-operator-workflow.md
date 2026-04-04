# Wiki CLI Operator Workflow

This document describes the `wiki` CLI shortcut layer for KB and Obsidian operations.

## Purpose
The CLI shortcuts reduce friction after capture and ingest.
They do not replace KB rules in `/home/slimy/kb/KB_AGENTS.md`.

## Core Operator Commands
- `wiki status`
  - Shows KB root, vault path, latest ingest/query reports, compile signal, markdown counts, and next-step hints.
- `wiki compile-candidates`
  - Lists raw markdown files not referenced in wiki article `> Sources:` lines.
  - Saves the last list to `/tmp/wiki-last-compile-candidates-$USER.tsv`.
- `wiki open-report latest`
  - Opens the newest report markdown in `output/`.
  - Preference order: ingest report, query report, then other output markdown.

## Prompt Generators
- `wiki prompt-query "question"`
  - Generates a harness-ready KB Query prompt.
  - Saves prompt to `/home/slimy/kb/output/prompts/query-prompt-YYYYMMDD-HHMMSS.md`.
  - Prints the prompt to stdout.
- `wiki prompt-compile`
  - Generates a harness-ready KB Compile prompt.
  - Includes detected compile candidates when available.
  - Saves prompt to `/home/slimy/kb/output/prompts/compile-prompt-YYYYMMDD-HHMMSS.md`.
  - Prints the prompt to stdout.

## Typical Flow
1. Capture content in Obsidian inbox/project folders.
2. Run `wiki sync`.
3. Run `wiki vault-sync`.
4. Run `wiki vault-ingest`.
5. Run `wiki status`.
6. Review the latest report with `wiki open-report latest`.
7. Review uncompiled material with `wiki compile-candidates`.
8. Generate the next prompt with `wiki prompt-query` or `wiki prompt-compile`.
9. Continue KB compile/update workflow per KB_AGENTS rules.

## Obsidian Operator Notes
- `/home/slimy/obsidian/slimyai-vault/Home.md`
- `/home/slimy/obsidian/slimyai-vault/Projects/Operator Console.md`
- `/home/slimy/obsidian/slimyai-vault/Plugin Setup/Shell Commands - Operator Commands.md`
- `/home/slimy/obsidian/slimyai-vault/Plugin Setup/Shell Commands - Suggested Additions.md`

## Guardrails
- No direct LLM execution from shell in this workflow.
- No background daemons or watchers.
- Canonical wiki remains `/home/slimy/kb/wiki`.
