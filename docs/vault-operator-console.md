# Operator Console

Use this page for day-to-day KB operations. Follow the **Next Move** decision tree in order — each step is blocking until resolved.

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
After ingest, run `wiki open-report latest` to review:
```bash
ssh -t work-nuc2 'cd /home/slimy/kb && bash tools/wiki open-report latest'
```

---

### Step 3 — Uncompiled Raw Files?
```bash
ssh work-nuc2 'cd /home/slimy/kb && bash tools/wiki compile-candidates'
```
If candidates are listed, run the compile prompt:
```bash
ssh work-nuc2 'cd /home/slimy/kb && bash tools/wiki prompt-compile'
```
Then execute the resulting prompt file as a harness run.

After compiling, sync the wiki mirror:
```bash
ssh work-nuc2 'cd /home/slimy/kb && bash tools/wiki vault-sync'
```

---

### Step 4 — Nothing Pending?
**Nothing to do?** Either:
- **Capture new material:** add notes/clips to vault `Inbox/` or `Projects/`, then run `wiki vault-ingest`
- **Query the KB:**
```bash
ssh work-nuc2 'cd /home/slimy/kb && bash tools/wiki prompt-query "your question here"'
```
- **Search the wiki directly:**
```bash
ssh work-nuc2 'cd /home/slimy/kb && bash tools/wiki search "search terms"'
```

---

## Command Reference

| Action | Shell Command |
|--------|--------------|
| Check status (all) | `ssh work-nuc2 'cd /home/slimy/kb && bash tools/wiki status'` |
| Daily summary | `ssh work-nuc2 'cd /home/slimy/kb && bash tools/wiki daily'` |
| Vault ingest | `ssh work-nuc2 'cd /home/slimy/kb && bash tools/wiki vault-ingest'` |
| Vault sync | `ssh work-nuc2 'cd /home/slimy/kb && bash tools/wiki vault-sync'` |
| Compile candidates | `ssh work-nuc2 'cd /home/slimy/kb && bash tools/wiki compile-candidates'` |
| Latest report | `ssh -t work-nuc2 'cd /home/slimy/kb && bash tools/wiki open-report latest'` |
| KB search | `ssh work-nuc2 'cd /home/slimy/kb && bash tools/wiki search "terms"` |
| Prompt query | `ssh work-nuc2 'cd /home/slimy/kb && bash tools/wiki prompt-query "question"` |
| Prompt compile | `ssh work-nuc2 'cd /home/slimy/kb && bash tools/wiki prompt-compile'` |
| KB sync (git pull/push) | `ssh work-nuc2 'cd /home/slimy/kb && bash tools/kb-sync.sh pull'` |

## Guardrails
- Run steps in order — conflicts block all else.
- Do not treat mirrored `Wiki/` files as editable source of truth.
- Prompt generators create harness-ready prompts; they do not execute autonomously.
