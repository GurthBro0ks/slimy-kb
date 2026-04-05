# Knowledge Base Agent Rules

## Directory Ownership
- raw/ — Humans and agents both write here. Never delete raw files.
- wiki/ — AGENTS OWN THIS. Humans should not edit wiki/ directly.
- output/ — Query results land here. Can be filed back into wiki/.

## Writing Wiki Articles
Every wiki article MUST have this structure at the top:

# [Title]
> Category: [concepts|projects|patterns|troubleshooting|architecture]
> Sources: [list of raw/ files or URLs this was compiled from]
> Created: YYYY-MM-DD
> Updated: YYYY-MM-DD
> Status: [draft|reviewed|stale]

## Article Quality Rules
1. Each article covers ONE topic — split if it covers multiple
2. Link to related articles using relative paths: [see also](../patterns/foo.md)
3. Include a "See Also" section at the bottom with backlinks
4. Code examples must be real (from actual repos), not hypothetical
5. Troubleshooting articles must include: symptom, cause, fix, prevention

## Compiling raw → wiki
When processing a raw/ document:
1. Read it fully
2. Identify which wiki category it belongs to
3. Check if a related article already exists — UPDATE it, don't duplicate
4. If new, create the article with proper frontmatter
5. Update _index.md with a one-line summary
6. Update _concepts.md if it introduces a new concept
7. Add backlinks from/to related existing articles

## Index Maintenance
After ANY wiki change:
- _index.md must list every article with a one-line summary
- _concepts.md must list every concept
- _stale.md should flag articles older than 30 days without updates

## Cross-NUC Coordination

The KB is a shared git repo (GurthBro0ks/slimy-kb) cloned on both NUC1 and NUC2.

### Before ANY KB read operation (query, search, compile, lint):
Run: bash /home/slimy/kb/tools/kb-sync.sh pull

### After ANY KB write operation (compile, ingest, file-back, gap-fill):
Run: bash /home/slimy/kb/tools/kb-sync.sh push

### Filing learnings from either NUC:
Use kb-write.sh for atomic file+sync:
  echo "content" | bash /home/slimy/kb/tools/kb-write.sh raw/agent-learnings/YYYY-MM-DD-slug.md

### Conflict resolution:
Git rebase is used. If rebase fails (rare with .md files), the sync tool
warns but does not block. Resolve manually or re-run sync after the other
NUC finishes its current session.

### Detecting conflict files:
Run `wiki lint` or `wiki conflicts` to scan the KB and vault for `*conflict*` files.
Conflict files are also flagged in `wiki daily` output.

## Conflict Resolution

When a conflict file is detected (e.g. `file (2026-04-05 10-30-22).md` from Obsidian
Sync, or a git-originated conflict marker file):

1. **Read both versions** — open the original file and the conflict file side-by-side.
2. **Classify the conflict:**
   - **Complementary changes** — edits to different sections or paragraphs.
     Merge both sets of changes into the original file.
   - **Contradicting changes** — both versions modified the same line differently.
     Keep the **NUC2 version**, then add a note at the top of the file:
     `> Conflict resolved: NUC2 version kept. NUC1 change noted: <one-line summary of loss.>`
3. **Delete the conflict file** after resolving into the original.
4. **Commit** with the message: `kb: resolve conflict - <filename>`
5. **Push** with `bash /home/slimy/kb/tools/kb-sync.sh push`

Note: Obsidian Sync conflict filenames embed the remote device's timestamp in
parens `(YYYY-MM-DD HH-mm-ss)`. This identifies the other NUC but does not
determine which version is "correct" — use the guidance above.

### Naming convention for NUC-sourced content:
Raw files from agent sessions should include the hostname:
  YYYY-MM-DD-nuc1-slug.md or YYYY-MM-DD-nuc2-slug.md
This is for provenance only — wiki articles are NOT split by NUC.

## Wiki CLI (Terminal)

A lightweight operator CLI is available at:
- `/home/slimy/kb/tools/wiki`
- `wiki` (wrapper in `~/.local/bin/wiki`)

Commands:
- `wiki search "terms"` — pulls latest KB first, then searches wiki article path/title first and content second
- `wiki search --raw "terms"` — searches only `raw/`
- `wiki search --all "terms"` — searches `wiki/`, `raw/`, and `output/`
- `wiki open 1` — opens a numbered result from the last search set
- `wiki open architecture/some-article.md` — opens by direct path
- `wiki status` — compact KB/vault/report counts and next-step hints
- `wiki compile-candidates` — lists raw markdown not referenced by wiki `Sources` links
- `wiki open-report latest` — opens newest ingest/query/output report markdown
- `wiki prompt-query "question"` — writes and prints a harness-ready KB Query prompt to `output/prompts/`
- `wiki prompt-compile` — writes and prints a harness-ready KB Compile prompt, including compile candidates when present
- `wiki sync` — pulls latest KB state
- `wiki vault-sync` — mirror canonical wiki into Obsidian vault `Wiki/`
- `wiki vault-ingest` — ingest writable Obsidian vault content into `raw/` and write an ingest report in `output/`
- `wiki help` — prints command usage

Result cache:
- Last search results are saved to `/tmp/wiki-last-results-$USER.tsv` for `wiki open <number>`.
- Last compile candidate set is saved to `/tmp/wiki-last-compile-candidates-$USER.tsv`.
