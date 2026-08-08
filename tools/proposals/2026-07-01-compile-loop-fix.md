# Proposal: fix `kb-compile-if-needed.sh` dispatch loop
> Status: PROPOSED — not shipped. Requires operator approval before applying.
> Raised: 2026-07-01, after 35 consecutive no-op re-dispatches of priority batch `20260611-230008`.
> Root cause found: wiki/log.md 2026-06-30T22:25Z entry (child-compile run 32).

## Problem
`tools/kb-compile-if-needed.sh:collect_compile_candidates()` has two bugs the
canonical `tools/wiki:collect_compile_candidates()` does not:

1. `set -euo pipefail` is active script-wide. The per-line
   `grep -oE 'raw/...\.md' <<< "$ref"` inside the Sources-line loop is
   unguarded, so the first `> Sources:` line citing zero `raw/` paths
   (e.g. `wiki/architecture/slimyai-login-and-session-flow.md`, which only
   cites other wiki pages / non-`raw/` source files) makes `grep` exit 1 and
   `set -e` kills the function immediately.
2. Even if reached, the second loop never populates `referenced[x]=1` before
   testing `${referenced[$raw_rel]:-}` — the dedup array is permanently empty.

Effect: the function always dies at the same point in traversal order and
returns the same ~14-20 stale paths regardless of true KB state. This is why
child-compile has re-dispatched the same already-compiled batch 35+ times
(see wiki/log.md entries 2026-06-27 through 2026-07-01).

**Caveat carried over from run 32/33 (not re-derived, still open):** run 31
found no cron/systemd/sequencer entry anywhere under `/home/slimy` that
references batch ID `20260611-230008` — the dispatch source itself may be
external to this host. If so, fixing this script stops the *symptom*
(always-stale candidate list) but may not stop the *dispatcher* from firing.
Worth checking dispatcher-side before/alongside applying this patch.

## Why not shipped automatically
Run 32 tested the naive fix in isolation: candidate count jumps from 14 to
359 (verified against the canonical `tools/wiki compile-candidates`, which
independently returns the same 359). Almost all of the 359 are auto-generated
daily snapshots never intended as standalone articles (`raw/research/*-state.md`,
`*-kb-health.md`, `*-repo-digests.md`, `raw/inbox-nuc1/*`, `raw/changelogs/*`,
`raw/agent-learnings/*-codex-summary.md`, `*-claude-summary.md`), but
`raw/discord-exports/**` is a mixed bag — some threads do become real
`wiki/game/*` articles, so a blanket exclusion risks silently dropping real
candidates. This script is called by `slimy-agent-finish.sh` on both NUCs
after every agent session, so shipping detection-only (without exclusions)
would turn a cheap 14-item no-op loop into an expensive 359-item child-compile
prompt on every session end, forever, with no convergence mechanism. That is
strictly worse than the current state, hence: staged, not shipped.

## Proposed patch (script bug fix — low risk, mirrors already-working `tools/wiki` logic)

```diff
--- a/tools/kb-compile-if-needed.sh
+++ b/tools/kb-compile-if-needed.sh
@@ collect_compile_candidates() {
     local -A referenced=()
-    local wiki_file ref
+    local wiki_file ref raw_rel
     local -a source_lines=()

     while IFS= read -r wiki_file; do
         [[ -f "$wiki_file" ]] || continue
-        mapfile -t source_lines < <(grep -hE '^> Sources:' "$wiki_file" 2>/dev/null || true)
-        for ref in "${source_lines[@]}"; do
-            grep -oE 'raw/[A-Za-z0-9._/-]+\.md' <<< "$ref" 2>/dev/null
-        done
+        mapfile -t source_lines < <(grep -hE '^> Sources:' "$wiki_file" 2>/dev/null || true)
+        [[ ${#source_lines[@]} -eq 0 ]] && continue
+        while IFS= read -r ref; do
+            [[ -n "$ref" ]] || continue
+            referenced["$ref"]=1
+        done < <(printf '%s\n' "${source_lines[@]}" | grep -hoE 'raw/[A-Za-z0-9._/-]+\.md' 2>/dev/null || true)
     done < <(find "$KB_ROOT/wiki" -type f -name '*.md' ! -name '_*.md' 2>/dev/null)

     find "$KB_ROOT/raw" -type f -name '*.md' -printf '%P\n' 2>/dev/null | sort | while IFS= read -r raw_rel; do
         if [[ -z "${referenced[$raw_rel]:-}" ]]; then
             printf '%s\n' "$raw_rel"
         fi
     done
 }
```

This patch alone fixes the correctness bug but exposes the full 359-item
backlog. **Do not apply this patch without also deciding on exclusions
below**, or every session-end hook will trigger an expensive child-compile.

## Proposed exclusion/deferral mechanism (policy decision — needs operator sign-off)

Add `wiki/_compile-exclusions.md` as a glob allowlist-of-exclusions, e.g.:

```
raw/research/*-state.md
raw/research/*-kb-health.md
raw/research/*-repo-digests.md
raw/inbox-nuc1/*
raw/changelogs/*
raw/agent-learnings/*-codex-summary.md
raw/agent-learnings/*-claude-summary.md
raw/discord-exports/**   # ONLY if operator confirms none of the remaining
                          # un-compiled threads are wanted as game/ articles —
                          # otherwise exclude per-thread, not the whole tree
```

Both `tools/wiki:collect_compile_candidates()` and
`tools/kb-compile-if-needed.sh:collect_compile_candidates()` would need to
filter against this list identically, to keep `wiki compile-candidates` and
the auto-dispatcher in agreement.

**Open question for operator:** should `raw/discord-exports/**` game-content
threads be excluded wholesale, or reviewed individually before exclusion?
(14 of ~50 exported threads already have corresponding `wiki/game/*` articles
per current `wiki compile-candidates` output; the rest are undecided.)

## What happens if this proposal is approved
1. Apply the script diff above to `tools/kb-compile-if-needed.sh`.
2. Create `wiki/_compile-exclusions.md` with the agreed glob list.
3. Update both `collect_compile_candidates()` implementations to skip
   raw files matching any exclusion glob.
4. Re-run `wiki compile-candidates` and `kb-compile-if-needed.sh --dry-run`
   to confirm they agree and the candidate count is the intended
   (non-excluded) remainder, not 359 and not 0.
5. Batch-triage the true remaining candidates into real wiki articles or
   explicit per-file deferral notes, so future dispatches never re-fire an
   already-settled batch again.

## Sources
- wiki/log.md — 2026-06-30 22:25Z entry (root cause discovery, run 32)
- wiki/log.md — 2026-07-01 09:01Z entry (re-confirmation, run 33)
- wiki/log.md — 2026-07-01 09:42Z entry (escalation, run 34)
- tools/kb-compile-if-needed.sh (buggy version)
- tools/wiki (canonical, working version)
