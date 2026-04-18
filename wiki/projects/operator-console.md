# Operator Console
> Category: projects
> Sources: /home/slimy/kb/raw/research/obsidian-projects-operator-console.md
> Created: 2026-04-05
> Updated: 2026-04-05
> Status: draft

<!-- KB METADATA
> Last edited: 2026-04-18 00:24 UTC (git)
> Version: r10 / 757d387
KB METADATA -->

Operator Console is the NUC2 KB operations decision tree. Run steps in order — each step is blocking until resolved.

## Next Move Decision Tree

### Step 1 — Conflicts?
Check for merge conflicts in the KB:
```bash
ssh work-nuc2 'cd /home/slimy/kb && bash tools/kb-sync.sh pull 2>&1 | grep -i conflict'
```
**If conflicts found:** resolve them before any other operation. Run `wiki sync` to pull latest, then manually resolve conflict markers in affected `.md` files.

---

### Step 2 — Inbox Items?
```bash
ssh work-nuc2 'cd /home/slimy/kb && bash tools/wiki daily'
```
Look for `Inbox Pending Count: N` — if N > 0, **vault-ingest first**.

**Ingest command:**
```bash
ssh work-nuc2 'cd /home/slimy/kb && bash tools/wiki vault-ingest'
```
After ingest, run `wiki open-report latest` to review.

---

### Step 3 — Uncompiled Raw Files?
```bash
ssh work-nuc2 'cd /home/slimy/kb && bash tools/wiki compile-candidates'
```
If candidates are listed, run: `wiki prompt-compile` then execute the resulting prompt file as a harness run. After compiling, sync: `wiki vault-sync`.

---

### Step 4 — Nothing Pending?
- **Capture new material:** add notes/clips to vault `Inbox/` or `Projects/`, then run `wiki vault-ingest`
- **Query the KB:** `wiki prompt-query "your question here"`
- **Search the wiki:** `wiki search "terms"`

## Command Reference

| Action | Shell Command |
|--------|--------------|
| Check status (all) | `ssh work-nuc2 'cd /home/slimy/kb && bash tools/wiki status'` |
| Daily summary | `ssh work-nuc2 'cd /home/slimy/kb && bash tools/wiki daily'` |
| Vault ingest | `ssh work-nuc2 'cd /home/slimy/kb && bash tools/wiki vault-ingest'` |
| Vault sync | `ssh work-nuc2 'cd /home/slimy/kb && bash tools/wiki vault-sync'` |
| Compile candidates | `ssh work-nuc2 'cd /home/slimy/kb && bash tools/wiki compile-candidates'` |
| KB sync (git pull/push) | `ssh work-nuc2 'cd /home/slimy/kb && bash tools/kb-sync.sh pull'` |

## Guardrails
- Run steps in order — conflicts block all else.
- Do not treat mirrored `Wiki/` files as editable source of truth.
- Prompt generators create harness-ready prompts; they do not execute autonomously.

## See Also
- [Knowledge Base Build Pipeline](../architecture/knowledge-base-build-pipeline.md) — end-to-end lifecycle
- [Capture Dashboard](capture-dashboard.md) — intake surface