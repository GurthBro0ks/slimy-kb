#!/usr/bin/env python3
"""
wiki_manager_stage1.py — Stage 1.86 todo queue generator + stable wiki pages.

Stage 1.86 changes (from 1.85):
- Freshness-weighted promotion: recent evidence counts more than lifetime count
- Rolling window fields: run_timestamps, recent_occurrence_count (last 5 runs)
- Freshness bands: fresh / aging / stale
- cooling_down status for items with stale/weak recent evidence
- Candidate requires recency AND persistence — lifetime count alone is not enough
- History stores per-run timestamps (run_timestamps array)
- Stage 1.86 is still advisory only: does NOT dispatch harness jobs.
"""

import json
import sys
import os
import argparse
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

TIMESTAMP = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
DATE = TIMESTAMP[:10]
HOST = os.uname()[1]
OUTPUT_DIR = Path("/home/slimy/kb/output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TODO_JSON = OUTPUT_DIR / "todo_queue.json"
TODO_MD = OUTPUT_DIR / "todo_queue.md"
TODO_HISTORY = OUTPUT_DIR / "todo_history.json"
MANAGER_STATUS = Path("/home/slimy/kb/wiki/_manager-status.md")
WIKI_PROJ_DIR = Path("/home/slimy/kb/wiki/projects")
WIKI_ARCH_DIR = Path("/home/slimy/kb/wiki/architecture")
CANDIDATE_RULES_PAGE = Path("/home/slimy/kb/wiki/_candidate-promotion-rules.md")
PROJECT_HEALTH_INDEX = WIKI_PROJ_DIR / "_project-health-index.md"
HARNESS_CANDIDATES_MD = OUTPUT_DIR / "harness_candidates.md"
CANDIDATE_REVIEW_PACK = OUTPUT_DIR / "candidate_review_pack.md"

# History retention
HISTORY_RETENTION_RUNS = 10
HISTORY_RETENTION_DAYS = 30

# ── Stage 1.86 Freshness Constants ─────────────────────────────────────────
# Rolling window: last N runs count as "recent"
RECENT_WINDOW_RUNS = 5
# Hours to consider evidence "fresh" (no penalty)
FRESH_HOURS = 24
# Hours after which evidence starts aging
AGING_HOURS = 72
# Items not seen in this many hours are "stale"
STALE_HOURS = 168  # 7 days
# Candidate: needs at least this many RECENT occurrences (within window)
CANDIDATE_RECENT_MIN = 3
# Emerging: needs at least this many recent occurrences
EMERGING_RECENT_MIN = 2
# Lifetime occurrences needed for cross-NUC bonus to apply
CROSS_NUC_BONUS_IF_LIFETIME_AT_LEAST = 3
PROMOTION_CROSS_NUC_BONUS = 2
# Must have severity >= medium for candidate
# Must have a real evidence path

ALLOWED_PROMOTION_KINDS = {"repo_drift", "wiki_gap", "doc_drift"}
BLOCKED_PROMOTION_KINDS = {"investigate", "harness_candidate"}


# ── Parsing helpers ───────────────────────────────────────────────────────────


def parse_orphans(content: str) -> list[str]:
    if not content:
        return []
    orphans = []
    for line in content.splitlines():
        m = re.match(r"^\- \`(.+?\.md)\`", line.strip())
        if m:
            orphans.append(m.group(1))
    return orphans


def parse_weak_links(content: str) -> list[str]:
    if not content:
        return []
    weak = []
    for line in content.splitlines():
        m = re.match(r"^\- \`(.+?\.md)\`", line.strip())
        if m:
            weak.append(m.group(1))
    return weak


def parse_nuc1_json(content: str) -> dict:
    result = {
        "repos": [],
        "repo_details": [],
        "dirty_repos": [],
        "diverged_repos": [],
        "kb_present": False,
        "nuc1_host": "unknown",
        "ts": "",
    }
    if not content:
        return result
    try:
        data = json.loads(content)
    except (json.JSONDecodeError, ValueError):
        return result

    result["nuc1_host"] = data.get("hostname", "unknown")
    result["ts"] = data.get("ts", "")

    for repo in data.get("repos", []):
        result["repos"].append(repo["name"])
        result["repo_details"].append(repo)
        if repo.get("dirty"):
            result["dirty_repos"].append(repo["name"])
        ab = repo.get("ahead_behind") or {}
        if ab.get("ahead", 0) > 0 and ab.get("behind", 0) > 0:
            result["diverged_repos"].append(repo["name"])

    return result


def parse_nuc1_markdown(content: str) -> dict:
    result = {
        "nuc1_host": "unknown",
        "ts": "",
        "dirty_services": [],
        "active_services": [],
        "listening_ports": [],
    }
    if not content:
        return result

    m = re.search(r"NUC1 State Digest.*?(\d{8}T\d{6}Z)", content)
    if m:
        result["ts"] = m.group(1)

    hm = re.search(r"hostname:\s*(\S+)", content)
    if hm:
        result["nuc1_host"] = hm.group(1)

    for line in content.splitlines():
        if "⚠️" in line or "dirty" in line.lower():
            result["dirty_services"].append(line.strip())

    in_services = False
    for line in content.splitlines():
        if "## Active Services" in line or "## Systemd" in line:
            in_services = True
            continue
        if in_services and line.startswith("## "):
            in_services = False
        if in_services and line.strip() and not line.startswith("-"):
            result["active_services"].append(line.strip())

    for line in content.splitlines():
        pm = re.findall(r":(\d{4,5})", line)
        for p in pm:
            if 1024 <= int(p) <= 65535:
                result["listening_ports"].append(int(p))

    return result


# ── Evidence verification ────────────────────────────────────────────────────


def evidence_path_is_real(path: str) -> bool:
    """Check if an evidence path actually exists in the KB."""
    if not path:
        return False
    rel_path = path
    for prefix in ("/home/slimy/kb/", "/home/slimy/kb"):
        if rel_path.startswith(prefix):
            rel_path = rel_path[len(prefix) :]
            break
    return Path(f"/home/slimy/kb/{rel_path}").exists()


def has_real_evidence(task: dict) -> bool:
    """Task has at least one evidence path that points to a real file/dir."""
    for ep in task.get("evidence_paths", []):
        if evidence_path_is_real(ep):
            return True
    return False


def evidence_age_hours(task: dict) -> float:
    """
    How many hours old is the best evidence path?
    We check the file modification time of the evidence path.
    Returns inf if no evidence path exists.
    """
    now = datetime.now(timezone.utc)
    for ep in task.get("evidence_paths", []):
        # Strip KB root or relative prefix and resolve
        rel = ep
        for root_prefix in ("/home/slimy/kb/", "/home/slimy/kb"):
            if rel.startswith(root_prefix):
                rel = rel[len(root_prefix) :]
                break
        # rel is now a relative path like "raw/inbox-nuc1" or "wiki/_orphans.md"
        full = Path(f"/home/slimy/kb/{rel}")
        # Ensure we check the directory/file without trailing slash artifacts
        if full.exists():
            mtime = datetime.fromtimestamp(full.stat().st_mtime, tz=timezone.utc)
            return (now - mtime).total_seconds() / 3600
    return float("inf")


def compute_freshness_band(task: dict, now_ts: str) -> str:
    """
    Compute freshness band based on evidence age.
    - fresh: evidence < FRESH_HOURS old
    - aging: evidence >= FRESH_HOURS but < AGING_HOURS
    - stale: evidence >= AGING_HOURS
    """
    age_h = evidence_age_hours(task)
    if age_h == float("inf"):
        # No real evidence — treat as stale
        return "stale"
    if age_h < FRESH_HOURS:
        return "fresh"
    elif age_h < AGING_HOURS:
        return "aging"
    else:
        return "stale"


# ── Project-page matching ─────────────────────────────────────────────────────


def find_project_page(repo_name: str) -> Optional[Path]:
    if not repo_name or not WIKI_PROJ_DIR.exists():
        return None
    normalized = re.sub(r"[-_]", "", repo_name.lower())
    for page_path in WIKI_PROJ_DIR.glob("*.md"):
        if page_path.name.startswith("_"):
            continue
        page_normalized = re.sub(r"[-_]", "", page_path.stem.lower())
        if (
            page_normalized == normalized
            or page_normalized.startswith(normalized)
            or normalized.startswith(page_normalized)
        ):
            return page_path
    return None


def update_project_page(
    page_path: Path, repo_name: str, status_block: str, todos: list[dict]
) -> bool:
    if not page_path.exists():
        return False
    existing = page_path.read_text()
    begin_marker = f"<!-- BEGIN MACHINE MANAGED — Do not edit manually -->"
    end_marker = "<!-- END MACHINE MANAGED -->"
    existing_block_match = re.search(
        r"<!-- BEGIN MACHINE MANAGED — Do not edit manually -->.*?<!-- END MACHINE MANAGED -->",
        existing,
        re.DOTALL,
    )
    new_block = f"{begin_marker}\n\n{status_block}\n\n{end_marker}"
    if existing_block_match:
        if existing_block_match.group(0) == new_block:
            return False
        new_content = (
            existing[: existing_block_match.start()]
            + new_block
            + existing[existing_block_match.end() :]
        )
    else:
        see_also_match = re.search(r"\n## See Also", existing)
        if see_also_match:
            new_content = (
                existing[: see_also_match.start()]
                + "\n"
                + new_block
                + "\n"
                + existing[see_also_match.start() :]
            )
        else:
            new_content = existing.rstrip() + "\n\n" + new_block + "\n"
    page_path.write_text(new_content)
    return True


def build_project_status_block(
    repo_name: str, nuc1_json: dict, todos: list[dict], all_repos
) -> str:
    lines = []
    repo_data = None
    for r in all_repos:
        if isinstance(r, dict) and r.get("name") == repo_name:
            repo_data = r
            break
        elif isinstance(r, str) and r == repo_name:
            repo_data = {"name": r}
            break
    lines.append(f"**Last updated:** {TIMESTAMP}")
    dirty = repo_name in nuc1_json.get("dirty_repos", [])
    diverged = repo_name in nuc1_json.get("diverged_repos", [])
    nuc1_repos = nuc1_json.get("repos", [])
    if repo_data:
        lines.append(
            f"**NUC1 status:** {'DIRTY' if dirty else 'clean'}, {'DIVERGED' if diverged else 'synced'}"
        )
        commit = (repo_data.get("commit_hash") or "unknown")[:7]
        subject = repo_data.get("commit_subject", "")
        branch = repo_data.get("branch") or "detached"
        lines.append(f"**NUC1 commit:** `{commit}` — {subject}")
        lines.append(f"**Branch:** {branch}")
    elif nuc1_repos and not repo_data:
        lines.append(f"**NUC1 status:** in digest but no detail available")
    project_todos = [
        t for t in todos if t.get("project", "").lower() == repo_name.lower()
    ]
    if project_todos:
        lines.append("")
        lines.append("### Open Issues")
        for t in project_todos[:5]:
            sev = t.get("severity", "?").upper()
            kind = t.get("kind", "?")
            occ = t.get("occurrence_count", 1)
            prom = t.get("promotion_status", "?")
            fresh = t.get("freshness_band", "?")
            lines.append(f"- **[{sev}/{prom}]** {t['title']} ({kind}, {occ}x, {fresh})")
    else:
        lines.append(f"**Open issues:** none in current queue")
    if project_todos and project_todos[0].get("evidence_paths"):
        lines.append("")
        lines.append("### Evidence")
        for ep in project_todos[0].get("evidence_paths", []):
            lines.append(f"- `{ep}`")
    lines.append("")
    lines.append("### Related Pages")
    lines.append(f"- [Repo Health Overview](./_project-health-index.md)")
    lines.append(f"- [NUC1 Current State](../architecture/nuc1-current-state.md)")
    return "\n".join(lines)


# ── Project health index ──────────────────────────────────────────────────────


def build_project_health_index(
    nuc1_json: dict, todos: list[dict], updated_pages: list[str]
) -> str:
    lines = []
    lines.append("# Project Health Index")
    lines.append("")
    lines.append("> Category: projects")
    lines.append(f"> Updated: {TIMESTAMP}")
    lines.append("> Status: active")
    lines.append("")
    lines.append("<!-- BEGIN MACHINE MANAGED — Do not edit manually -->")
    lines.append("")
    raw_repos = nuc1_json.get("repos", [])
    nuc1_repo_names = []
    for r in raw_repos:
        if isinstance(r, dict):
            nuc1_repo_names.append(r.get("name", ""))
        elif isinstance(r, str):
            nuc1_repo_names.append(r)
    existing_pages = {}
    if WIKI_PROJ_DIR.exists():
        for p in WIKI_PROJ_DIR.glob("*.md"):
            if not p.name.startswith("_"):
                existing_pages[p.stem.lower()] = p.name
    covered_repos = []
    uncovered_repos = []
    for name in nuc1_repo_names:
        page = find_project_page(name)
        if page:
            covered_repos.append((name, page.name))
        else:
            uncovered_repos.append(name)
    dirty = nuc1_json.get("dirty_repos", [])
    diverged = nuc1_json.get("diverged_repos", [])
    dirty_count = len(dirty)
    diverged_count = len(diverged)
    clean_count = len(nuc1_repo_names) - dirty_count - diverged_count
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- NUC1 repos tracked: {len(nuc1_repo_names)}")
    lines.append(f"- With project page: {len(covered_repos)}")
    lines.append(f"- Without project page: {len(uncovered_repos)}")
    lines.append(f"- Dirty (uncommitted): {dirty_count}")
    lines.append(f"- Diverged (ahead + behind): {diverged_count}")
    lines.append(f"- Clean: {clean_count}")
    lines.append("")
    if updated_pages:
        lines.append("## Pages Updated This Run")
        lines.append("")
        for pg in updated_pages:
            lines.append(f"- {pg}")
        lines.append("")
    if covered_repos:
        lines.append("## Covered Repos (have project pages)")
        lines.append("")
        for name, page_name in sorted(covered_repos):
            status_parts = []
            if name in dirty:
                status_parts.append("DIRTY")
            if name in diverged:
                status_parts.append("DIVERGED")
            status_str = ", ".join(status_parts) if status_parts else "clean"
            lines.append(f"- **{name}** → `{page_name}` — {status_str}")
        lines.append("")
    if uncovered_repos:
        lines.append("## Uncovered Repos (no matching project page)")
        lines.append("")
        for name in sorted(uncovered_repos):
            status_parts = []
            if name in dirty:
                status_parts.append("DIRTY")
            if name in diverged:
                status_parts.append("DIVERGED")
            status_str = ", ".join(status_parts) if status_parts else "clean"
            lines.append(f"- **{name}** — {status_str}")
        lines.append("")
    if nuc1_repo_names:
        lines.append("## NUC1 Repo Health Table")
        lines.append("")
        lines.append("| Repo | Status | Diverged |")
        lines.append("|------|--------|----------|")
        for name in sorted(nuc1_repo_names)[:30]:
            is_dirty = "⚠️ DIRTY" if name in dirty else "—"
            is_diverged = "⚠️ DIVERGED" if name in diverged else "—"
            lines.append(f"| {name} | {is_dirty} | {is_diverged} |")
        lines.append("")
    lines.append("<!-- END MACHINE MANAGED -->")
    lines.append("")
    lines.append("## Human Notes")
    lines.append("")
    lines.append(
        "<!-- Add notes here — this section is preserved on machine-managed runs -->"
    )
    lines.append("")
    lines.append("## See Also")
    lines.append("- [Repo Health Overview](./repo-health-overview.md)")
    lines.append("- [NUC1 Current State](../architecture/nuc1-current-state.md)")
    lines.append("- [NUC2 Current State](../architecture/nuc2-current-state.md)")
    return "\n".join(lines)


# ── Promotion rules content (Stage 1.86) ─────────────────────────────────────

CANDIDATE_RULES_CONTENT_186 = """# Harness Candidate Promotion Rules

> Category: concepts
> Updated: _TS_PLACEHOLDER_
> Status: active

<!-- BEGIN MACHINE MANAGED — Do not edit manually -->

## Overview

Stage 1.86 adds **freshness-weighted promotion** to Stage 1.85's stricter criteria.
Recent evidence matters more than lifetime occurrence count.
Tasks can also enter `cooling_down` when recent evidence weakens.

## Promotion Statuses

| Status | Meaning |
|--------|---------|
| `not_candidate` | Default — tracked but does not yet qualify |
| `emerging` | Has some signals but not all criteria met |
| `candidate` | Meets all criteria — ready for harness dispatch consideration |
| `cooling_down` | Was candidate/emerging but recent evidence has weakened |
| `resolved` | No longer present in current queue |

## Freshness Bands

| Band | Meaning | Evidence Age |
|------|---------|--------------|
| `fresh` | Evidence seen or file modified < 24h ago | < {FRESH_HOURS}h |
| `aging` | Evidence 1-3 days old | {FRESH_HOURS}h–{AGING_HOURS}h |
| `stale` | Evidence older than 3 days | >= {AGING_HOURS}h |

Evidence age is measured by file modification time of the primary evidence path.

## State Transitions

```
not_candidate → emerging → candidate → cooling_down → resolved
     ↑            ↑           ↑            ↓
     └─────────────┴───────────┴────────────┘  (demotion paths)
```

## Freshness-Weighted Promotion Criteria (Stage 1.86)

A task is promoted to `candidate` when **ALL** of the following are true:

### 1. Recent Occurrence Score
- Must have `recent_occurrence_count >= {CANDIDATE_RECENT_MIN}` within the last {RECENT_WINDOW_RUNS} runs
- Lifetime `occurrence_count` is tracked for audit only — it does NOT force candidate status

### 2. Evidence Quality + Recency
- Task must have at least one **real existing** `evidence_path`
- Evidence file must have been modified within `{AGING_HOURS}h` (not stale)
- OR task must have `freshness_band = "fresh"` or `"aging"` AND evidence is real

### 3. Severity Floor
- Severity must be `medium` or `high`

### 4. No Hard Dispatch Blocker
- `dispatch_blocker` must be empty OR only `"advisory_only"`

### 5. Kind Allowlist
- Only `repo_drift`, `wiki_gap`, `doc_drift` are eligible

## Emerging

`emerging` when:
- `recent_occurrence_count >= {EMERGING_RECENT_MIN}` AND < `{CANDIDATE_RECENT_MIN}`
- Evidence is real and freshness_band is `fresh` or `aging`
- Severity is `medium` or `high`

OR:
- Has real evidence, but `freshness_band = "stale"` with some recency signal

## Cooling Down

`cooling_down` when:
- Was previously `candidate` or `emerging`
- But `freshness_band = "stale"` OR evidence no longer exists
- Recent evidence has weakened even if lifetime count is high

## Not Candidate

`not_candidate` when:
- No real evidence path
- Evidence is stale AND no recent occurrences
- Kind is excluded
- Hard dispatch blocker present

## Stage 1.86 Boundary

Stage 1.86 does NOT dispatch harness jobs. Candidate status is advisory only.

<!-- END MACHINE MANAGED -->

## Human Notes

<!-- Add notes here -->
""".format(
    FRESH_HOURS=FRESH_HOURS,
    AGING_HOURS=AGING_HOURS,
    CANDIDATE_RECENT_MIN=CANDIDATE_RECENT_MIN,
    EMERGING_RECENT_MIN=EMERGING_RECENT_MIN,
    RECENT_WINDOW_RUNS=RECENT_WINDOW_RUNS,
)


# ── History management ───────────────────────────────────────────────────────


def load_history() -> dict:
    if not TODO_HISTORY.exists():
        return {"version": 2, "updated_at": "", "tasks": []}
    try:
        with open(TODO_HISTORY) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"version": 2, "updated_at": "", "tasks": []}


def task_key(task: dict) -> str:
    parts = [
        task.get("source_host", ""),
        task.get("project", ""),
        task.get("kind", ""),
    ]
    title = re.sub(r"\d{4}-\d{2}-\d{2}[-T]\d+", "", task.get("title", "")).lower()
    title = re.sub(r"^\[\S+\]\s*", "", title)
    title = re.sub(r"\s+", " ", title).strip()
    parts.append(title)
    return "|".join(parts)


def prune_history(history: dict) -> dict:
    now = datetime.now(timezone.utc)
    cutoff = datetime.strptime(TIMESTAMP[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
    cutoff_30d = cutoff - timedelta(days=HISTORY_RETENTION_DAYS)
    from datetime import timedelta as td

    cutoff_30d = cutoff - td(days=HISTORY_RETENTION_DAYS)
    kept = []
    for entry in history.get("tasks", []):
        last_seen = entry.get("last_seen", "")
        if not last_seen:
            continue
        try:
            ls = datetime.fromisoformat(last_seen.replace("Z", "+00:00"))
        except ValueError:
            continue
        runs = entry.get("occurrence_count", 1)
        if ls >= cutoff_30d or runs >= max(1, HISTORY_RETENTION_RUNS - 3):
            kept.append(entry)
    history["tasks"] = kept
    return history


def update_history(new_tasks: list[dict]) -> tuple[dict, dict]:
    """
    Update history with new run timestamps.
    For each task: append current run timestamp to run_timestamps array,
    trim to last RECENT_WINDOW_RUNS entries, compute recent_occurrence_count.
    """
    history = load_history()
    history = prune_history(history)
    state_map = {}
    now = TIMESTAMP

    existing = {e["task_key"]: e for e in history["tasks"]}

    for task in new_tasks:
        key = task_key(task)
        task["task_key"] = key
        if key in existing:
            entry = existing[key]
            # Append current run to run_timestamps, keep last N
            rts = entry.get("run_timestamps", [])
            rts.append(now)
            rts = rts[-RECENT_WINDOW_RUNS:]
            entry["run_timestamps"] = rts
            entry["last_seen"] = now
            entry["occurrence_count"] = entry.get("occurrence_count", 1) + 1
            entry["state"] = "persisting"
            task["first_seen"] = entry.get("first_seen", now)
            task["occurrence_count"] = entry["occurrence_count"]
            task["state"] = "persisting"
            task["run_timestamps"] = rts
            task["recent_occurrence_count"] = len(rts)
            # Promotion tracking
            task["promotion_first_seen"] = entry.get("promotion_first_seen", now)
            task["promotion_last_seen"] = entry.get("promotion_last_seen", now)
            task["promotion_occurrence_count"] = (
                entry.get("promotion_occurrence_count", 0) + 1
            )
            task["last_promotion_status_change"] = entry.get(
                "last_promotion_status_change", now
            )
            task["prior_promotion_status"] = entry.get(
                "last_known_promotion_status", "not_candidate"
            )
            state_map[key] = "persisting"
        else:
            hist_entry = {
                "task_key": key,
                "first_seen": now,
                "last_seen": now,
                "occurrence_count": 1,
                "state": "new",
                "run_timestamps": [now],
                "promotion_first_seen": None,
                "promotion_last_seen": None,
                "promotion_occurrence_count": 0,
                "last_promotion_status_change": now,
                "last_known_promotion_status": "not_candidate",
            }
            history["tasks"].append(hist_entry)
            task["first_seen"] = now
            task["occurrence_count"] = 1
            task["state"] = "new"
            task["run_timestamps"] = [now]
            task["recent_occurrence_count"] = 1
            task["promotion_first_seen"] = None
            task["promotion_last_seen"] = None
            task["promotion_occurrence_count"] = 0
            task["last_promotion_status_change"] = now
            task["prior_promotion_status"] = "not_candidate"
            state_map[key] = "new"

    new_keys = {task_key(t) for t in new_tasks}
    for entry in history["tasks"]:
        if entry["task_key"] not in new_keys and entry.get("state") != "resolved":
            entry["state"] = "resolved"

    history["updated_at"] = now
    return history, state_map


# ── Severity heuristics ─────────────────────────────────────────────────────────


def compute_severity(task: dict, nuc1_evidence: dict, occurrence_count: int = 1) -> str:
    kind = task.get("kind", "")
    source_scope = task.get("source_scope", "")
    title_lower = task.get("title", "").lower()

    if kind in ("wiki_gap", "doc_drift"):
        severity = 1
    elif kind == "repo_drift":
        severity = 1
    else:
        severity = 0

    if (
        source_scope == "cross_nuc"
        and "kb" in title_lower
        and "uncommitted" in title_lower
    ):
        return "high"

    if occurrence_count > 1:
        severity += 1

    return ["low", "medium", "high"][min(severity, 2)]


# ── Promotion (Stage 1.86 — freshness-weighted) ────────────────────────────────


def compute_promotion_186(task: dict, history_entry: dict) -> tuple[str, str, bool]:
    """
    Stage 1.86 freshness-weighted promotion logic.
    Returns (promotion_status, promotion_reason, demoted_this_run).
    Demoted if prior was candidate/emerging but now lower.
    Key insight: lifetime count is audit-only. Recent evidence drives promotion.
    """
    kind = task.get("kind", "")
    # Use history run_timestamps for recent count
    run_ts = task.get("run_timestamps", [])
    recent_occ = len(run_ts) if run_ts else task.get("recent_occurrence_count", 1)
    occurrence_count = task.get("occurrence_count", 1)
    source_scope = task.get("source_scope", "")
    severity = task.get("severity", "low")
    evidence_paths = task.get("evidence_paths", [])
    dispatch_blocker = task.get("dispatch_blocker", "")
    prior_status = task.get("prior_promotion_status", "not_candidate")

    real_evidence = has_real_evidence(task)
    freshness_band = compute_freshness_band(task, TIMESTAMP)
    evidence_age_h = evidence_age_hours(task)

    # ── Kind check ──
    if kind in BLOCKED_PROMOTION_KINDS:
        reason = "kind_excluded"
        new_status = "not_candidate"
        demoted = (
            prior_status in ("candidate", "emerging") and new_status != prior_status
        )
        return new_status, reason, demoted

    if kind not in ALLOWED_PROMOTION_KINDS:
        reason = "kind_not_allowed"
        new_status = "not_candidate"
        demoted = (
            prior_status in ("candidate", "emerging") and new_status != prior_status
        )
        return new_status, reason, demoted

    # ── Evidence check ──
    if not evidence_paths or not real_evidence:
        reason = "no_evidence" if not evidence_paths else "stale_evidence"
        new_status = "not_candidate"
        demoted = (
            prior_status in ("candidate", "emerging") and new_status != prior_status
        )
        return new_status, reason, demoted

    # ── Stale evidence + no recent run → cooling_down ──
    if freshness_band == "stale":
        if prior_status in ("candidate", "emerging"):
            reason = "evidence_stale_cooling"
            new_status = "cooling_down"
            demoted = True
            return new_status, reason, demoted
        else:
            reason = "evidence_stale"
            new_status = "not_candidate"
            demoted = False
            return new_status, reason, demoted

    # ── Hard dispatch blocker check ──
    if dispatch_blocker and dispatch_blocker not in ("advisory_only", ""):
        reason = f"dispatch_blocker:{dispatch_blocker}"
        new_status = "not_candidate"
        demoted = (
            prior_status in ("candidate", "emerging") and new_status != prior_status
        )
        return new_status, reason, demoted

    # ── CANDIDATE check ──
    # Requirements:
    #   - recent_occurrence_count >= CANDIDATE_RECENT_MIN (3 within last 5 runs)
    #   - severity >= medium
    #   - freshness_band != stale (fresh or aging)
    #   - evidence is real
    if (
        recent_occ >= CANDIDATE_RECENT_MIN
        and severity in ("medium", "high")
        and freshness_band != "stale"
    ):
        if source_scope == "cross_nuc":
            reason = "cross_nuc_conflict"
        elif kind == "repo_drift":
            reason = "persistent_drift"
        else:
            reason = "repeated_gap"
        new_status = "candidate"
        demoted = False
        return new_status, reason, demoted

    # ── EMERGING check ──
    # Has real evidence + freshness + some recency signal
    if (
        real_evidence
        and freshness_band != "stale"
        and recent_occ >= EMERGING_RECENT_MIN
    ):
        reason = "insufficient_persistence"
        new_status = "emerging"
        demoted = False
        return new_status, reason, demoted

    # ── COOLING_DOWN check ──
    # Was candidate/emerging, evidence is aging, but not fresh
    if prior_status in ("candidate", "emerging") and freshness_band == "aging":
        reason = "evidence_aging"
        new_status = "cooling_down"
        demoted = True
        return new_status, reason, demoted

    # ── NOT_CANDIDATE fallback ──
    reason = "insufficient_recency"
    new_status = "not_candidate"
    demoted = prior_status in ("candidate", "emerging") and new_status != prior_status
    return new_status, reason, demoted


# ── Build todos ─────────────────────────────────────────────────────────────


def build_todos(
    orphans, weak_links, nuc1_json, nuc1_md, backend, model
) -> tuple[list[dict], dict]:
    todos = []
    task_id = 1

    def add(
        kind,
        severity,
        title,
        reason,
        recommended_action,
        suggested_prompt_mode="manual",
        safe=True,
        project="kb",
        evidence_paths=None,
        notes="",
        source_host=HOST,
        source_scope="nuc2",
    ):
        nonlocal task_id
        todos.append(
            {
                "id": f"todo-{DATE}-{task_id:03d}",
                "created_at": TIMESTAMP,
                "source_host": source_host,
                "project": project,
                "title": title,
                "kind": kind,
                "severity": severity,
                "reason": reason,
                "recommended_action": recommended_action,
                "suggested_prompt_mode": suggested_prompt_mode,
                "safe_to_dispatch": safe,
                "evidence_paths": evidence_paths or [],
                "notes": notes,
                "source_scope": source_scope,
                "dispatch_blocker": "" if safe else "advisory_only",
                "promotion_status": "not_candidate",
                "promotion_reason": "",
                "demoted_this_run": False,
            }
        )
        task_id += 1

    nuc1 = parse_nuc1_json(nuc1_json)
    nuc1_md_parsed = parse_nuc1_markdown(nuc1_md)
    if nuc1_md_parsed.get("nuc1_host") and nuc1_md_parsed["nuc1_host"] != "unknown":
        nuc1["nuc1_host"] = nuc1_md_parsed["nuc1_host"]
    if nuc1_md_parsed.get("ts"):
        nuc1["ts"] = nuc1_md_parsed["ts"]

    nuc1_used = bool(nuc1.get("repos") or nuc1_md_parsed.get("active_services"))

    if nuc1_used:
        dirty = nuc1.get("dirty_repos", [])
        if dirty:
            for repo in dirty:
                project_name = repo
                add(
                    kind="repo_drift",
                    severity="medium",
                    title=f"NUC1 repo has uncommitted changes: {repo}",
                    reason=f"Repo '{repo}' on NUC1 has uncommitted changes (dirty=true). Risk of work loss or drift.",
                    recommended_action=f"Review {repo} on NUC1, commit or stash uncommitted work, push if appropriate.",
                    suggested_prompt_mode="manual",
                    safe=True,
                    project=project_name,
                    evidence_paths=[f"raw/inbox-nuc1/"],
                    notes=f"Dirty repo detected via NUC1 digest.",
                    source_host="nuc1",
                    source_scope="cross_nuc",
                )

        diverged = nuc1.get("diverged_repos", [])
        if diverged:
            for repo in diverged:
                add(
                    kind="repo_drift",
                    severity="low",
                    title=f"NUC1 repo diverged from remote: {repo}",
                    reason=f"Repo '{repo}' on NUC1 is both ahead and behind remote — unmerged commits present.",
                    recommended_action=f"Review {repo} on NUC1, merge or rebase remote changes, resolve any conflicts.",
                    suggested_prompt_mode="manual",
                    safe=True,
                    project=repo,
                    evidence_paths=[f"raw/inbox-nuc1/"],
                    notes=f"Diverged repo detected via NUC1 digest.",
                    source_host="nuc1",
                    source_scope="cross_nuc",
                )

    # Orphans
    if orphans:
        add(
            kind="wiki_gap",
            severity="medium",
            title=f"Resolve {len(orphans)} orphaned wiki pages",
            reason=f"Orphaned pages have 0 inbound links and are effectively hidden from navigation.",
            recommended_action="Review each orphan: add links from related pages, merge into existing articles, or delete if redundant.",
            suggested_prompt_mode="plan-build-qa",
            safe=True,
            evidence_paths=[f"wiki/_orphans.md"],
        )
        for orphan in orphans[:5]:
            add(
                kind="wiki_gap",
                severity="low",
                title=f"Review orphaned page: {orphan}",
                reason=f"Page '{orphan}' has no inbound links.",
                recommended_action=f"Check if {orphan} should be linked from related articles or removed.",
                suggested_prompt_mode="manual",
                safe=True,
                evidence_paths=[f"wiki/{orphan}"],
            )

    # Weak links
    if weak_links:
        add(
            kind="wiki_gap",
            severity="low",
            title=f"Strengthen {len(weak_links)} weak-linked pages",
            reason="Weakly-linked pages have only 1 inbound link — vulnerable to becoming orphans.",
            recommended_action="Find additional contexts where these pages should be referenced.",
            suggested_prompt_mode="manual",
            safe=True,
            evidence_paths=[f"wiki/_weak-links.md"],
        )

    # Cross-NUC KB dirty
    if nuc1.get("dirty_repos") and "kb" in nuc1.get("dirty_repos", []):
        add(
            kind="repo_drift",
            severity="high",
            title="NUC1 KB has uncommitted changes",
            reason="The kb repo on NUC1 is dirty — there are uncommitted changes that may need to be merged.",
            recommended_action="Coordinate with NUC1 to push or transfer the uncommitted KB changes, then reconcile.",
            suggested_prompt_mode="manual",
            safe=True,
            project="kb",
            evidence_paths=[f"raw/inbox-nuc1/"],
            notes="Cross-NUC KB drift signal — NUC1 has uncommitted work in shared KB.",
            source_host="nuc1",
            source_scope="cross_nuc",
        )

    if not todos:
        todos.append(
            {
                "id": f"todo-{DATE}-001",
                "created_at": TIMESTAMP,
                "source_host": HOST,
                "project": "kb",
                "title": "KB state nominal",
                "kind": "investigate",
                "severity": "low",
                "reason": "No obvious gaps detected in this run.",
                "recommended_action": "No immediate action — continue normal KB maintenance.",
                "suggested_prompt_mode": "manual",
                "safe_to_dispatch": False,
                "evidence_paths": [],
                "notes": f"NUC1 intake consumed: {nuc1_used}",
                "source_scope": "nuc2",
                "dispatch_blocker": "advisory_only",
                "promotion_status": "not_candidate",
                "promotion_reason": "investigate_kind_excluded",
                "demoted_this_run": False,
            }
        )

    return todos, nuc1, nuc1_md_parsed


# ── Markdown generation ──────────────────────────────────────────────────────


def generate_markdown(todos, backend, nuc1_used, nuc1_info, state_map) -> str:
    lines = []
    lines.append(f"# Todo Queue — {TIMESTAMP}")
    lines.append("")
    lines.append(f"**Generated by:** wiki_manager_stage1.py (Stage 1.86)")
    lines.append(f"**Backend:** {backend}")
    lines.append(f"**Host:** {HOST}")
    lines.append(f"**NUC1 evidence consumed:** {'YES' if nuc1_used else 'NO'}")
    if nuc1_info.get("nuc1_host"):
        lines.append(
            f"**NUC1 host:** {nuc1_info['nuc1_host']} ({nuc1_info.get('ts', 'no ts')})"
        )
    lines.append("")

    by_severity = {}
    by_kind = {}
    by_state = {"new": [], "persisting": [], "resolved": []}
    by_promotion = {
        "candidate": [],
        "emerging": [],
        "not_candidate": [],
        "cooling_down": [],
    }
    by_freshness = {"fresh": [], "aging": [], "stale": []}
    for t in todos:
        by_severity.setdefault(t["severity"], []).append(t)
        by_kind.setdefault(t["kind"], []).append(t)
        by_state.setdefault(t.get("state", "new"), []).append(t)
        by_promotion.setdefault(t.get("promotion_status", "not_candidate"), []).append(
            t
        )
        by_freshness.setdefault(t.get("freshness_band", "unknown"), []).append(t)

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Total tasks:** {len(todos)}")
    lines.append(f"- by severity: { {k: len(v) for k, v in by_severity.items()} }")
    lines.append(f"- by kind: { {k: len(v) for k, v in by_kind.items()} }")
    if state_map:
        new_c = sum(1 for s in state_map.values() if s == "new")
        pers_c = sum(1 for s in state_map.values() if s == "persisting")
        lines.append(f"- NEW: {new_c} | PERSISTING: {pers_c}")
    lines.append(
        f"- by promotion: candidate={len(by_promotion.get('candidate', []))} emerging={len(by_promotion.get('emerging', []))} cooling_down={len(by_promotion.get('cooling_down', []))} not_candidate={len(by_promotion.get('not_candidate', []))}"
    )
    lines.append(
        f"- by freshness: fresh={len(by_freshness.get('fresh', []))} aging={len(by_freshness.get('aging', []))} stale={len(by_freshness.get('stale', []))}"
    )
    lines.append("")

    for state_label, sort_severity in [
        ("NEW", ["high", "medium", "low"]),
        ("PERSISTING", ["high", "medium", "low"]),
    ]:
        state_tasks = by_state.get(state_label.lower(), [])
        if not state_tasks:
            continue
        lines.append(f"## {state_label} ({len(state_tasks)})")
        lines.append("")
        for sev in sort_severity:
            tasks = [t for t in state_tasks if t["severity"] == sev]
            if not tasks:
                continue
            lines.append(f"### {sev.upper()} ({len(tasks)})")
            lines.append("")
            for t in tasks:
                lines.append(f"#### [{t['id']}] {t['title']}")
                lines.append("")
                lines.append(f"- **Kind:** {t['kind']}")
                lines.append(f"- **Severity:** {t['severity']}")
                lines.append(
                    f"- **Promotion:** {t.get('promotion_status', 'unknown')} — {t.get('promotion_reason', '')}"
                )
                lines.append(
                    f"- **Freshness:** {t.get('freshness_band', 'unknown')} (recency: {t.get('recent_occurrence_count', '?')}x)"
                )
                lines.append(f"- **Reason:** {t['reason']}")
                lines.append(f"- **Recommended Action:** {t['recommended_action']}")
                lines.append(f"- **Prompt Mode:** {t['suggested_prompt_mode']}")
                lines.append(f"- **Safe to Dispatch:** {t['safe_to_dispatch']}")
                lines.append(
                    f"- **Source:** {t['source_host']} ({t.get('source_scope', 'unknown')})"
                )
                if t.get("occurrence_count", 1) > 1:
                    lines.append(
                        f"- **Occurrences:** {t['occurrence_count']}x (lifetime) / {t.get('recent_occurrence_count', '?')}x (recent)"
                    )
                if t.get("evidence_paths"):
                    lines.append(f"- **Evidence:** {', '.join(t['evidence_paths'])}")
                if t.get("dispatch_blocker"):
                    lines.append(f"- **Dispatch Blocker:** {t['dispatch_blocker']}")
                if t.get("notes"):
                    lines.append(f"- **Notes:** {t['notes']}")
                lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("*Stage 1.86 — advisory only. No harness jobs dispatched.*")
    return "\n".join(lines)


# ── Stable page writers ──────────────────────────────────────────────────────

NUC1_STATE_PAGE = WIKI_ARCH_DIR / "nuc1-current-state.md"
NUC2_STATE_PAGE = WIKI_ARCH_DIR / "nuc2-current-state.md"
REPO_HEALTH_PAGE = WIKI_PROJ_DIR / "repo-health-overview.md"


def write_stable_page(path: Path, content: str) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        existing = path.read_text()
        if existing == content:
            return False
    path.write_text(content)
    return True


def build_nuc1_state_content(nuc1_json: dict, nuc1_md: dict, todos: list[dict]) -> str:
    lines = []
    lines.append("# NUC1 Current State")
    lines.append("")
    lines.append("> Category: architecture")
    lines.append(f"> Updated: {TIMESTAMP}")
    lines.append(f"> Sources: raw/inbox-nuc1/")
    lines.append("> Status: active")
    lines.append("")
    lines.append("<!-- BEGIN MACHINE MANAGED — Do not edit manually -->")
    lines.append("")
    lines.append("## Host")
    lines.append(f"- **Hostname:** {nuc1_json.get('nuc1_host', 'unknown')}")
    lines.append(f"- **Last seen:** {nuc1_json.get('ts', 'unknown')}")
    lines.append("")
    lines.append("## Repository Status")
    dirty = nuc1_json.get("dirty_repos", [])
    diverged = nuc1_json.get("diverged_repos", [])
    all_repos = nuc1_json.get("repos", [])
    lines.append(f"- **Total repos tracked:** {len(all_repos)}")
    lines.append(
        f"- **Dirty (uncommitted changes):** {', '.join(dirty) if dirty else '_none_'}"
    )
    lines.append(
        f"- **Diverged (ahead + behind remote):** {', '.join(diverged) if diverged else '_none_'}"
    )
    lines.append("")
    lines.append("## Active Services (from digest)")
    services = nuc1_md.get("active_services", [])
    if services:
        for s in services[:10]:
            lines.append(f"- {s}")
    else:
        lines.append("- _(none detected in this digest)_")
    lines.append("")
    lines.append("## Open Issues (from todo queue)")
    nuc1_tasks = [
        t
        for t in todos
        if t.get("source_scope") == "cross_nuc"
        and t.get("source_host") in ("nuc1", "nuc1")
    ]
    if nuc1_tasks:
        for t in nuc1_tasks:
            prom = t.get("promotion_status", "")
            fresh = t.get("freshness_band", "")
            lines.append(
                f"- **[{t['severity'].upper()}/{prom}]** {t['title']} — {t['kind']} ({fresh})"
            )
    else:
        lines.append("- _No open NUC1 issues in current queue_")
    lines.append("")
    lines.append("<!-- END MACHINE MANAGED -->")
    lines.append("")
    lines.append("## Human Notes")
    lines.append("")
    lines.append(
        "<!-- Add notes here — this section is preserved on machine-managed runs -->"
    )
    lines.append("")
    lines.append("## See Also")
    lines.append(
        "- [NUC Topology and Services](../architecture/nuc-topology-and-services.md)"
    )
    lines.append("- [NUC2 Current State](nuc2-current-state.md)")
    lines.append(
        "- [Cross-NUC Communication Matrix](../architecture/cross-nuc-communication-matrix.md)"
    )
    return "\n".join(lines)


def build_nuc2_state_content(nuc2_state_md: str, todos: list[dict]) -> str:
    lines = []
    lines.append("# NUC2 Current State")
    lines.append("")
    lines.append("> Category: architecture")
    lines.append(f"> Updated: {TIMESTAMP}")
    lines.append("> Status: active")
    lines.append("")
    lines.append("<!-- BEGIN MACHINE MANAGED — Do not edit manually -->")
    lines.append("")
    lines.append("## Host")
    lines.append(f"- **Hostname:** {HOST}")
    lines.append(f"- **Last updated:** {TIMESTAMP}")
    lines.append("")
    lines.append("## Active Services")
    in_services = False
    service_lines = []
    for line in nuc2_state_md.splitlines():
        if "## Active PM2" in line or "PM2 Processes" in line:
            in_services = True
            continue
        if in_services and line.startswith("## "):
            in_services = False
        if in_services and line.strip():
            service_lines.append(line.strip())
    if service_lines:
        for s in service_lines[:10]:
            lines.append(f"- {s}")
    else:
        lines.append("- _(parsing unavailable)_")
    lines.append("")
    lines.append("## Network Ports")
    for line in nuc2_state_md.splitlines():
        if any(
            str(p) in line for p in [3000, 3838, 3850, 18790, 18792, 18793, 5432, 3307]
        ):
            lines.append(f"- `{line.strip()}`")
    lines.append("")
    lines.append("## KB Health")
    orphan_m = re.search(r"orphans.*?(\d+)", nuc2_state_md)
    weak_m = re.search(r"weak-links.*?(\d+)", nuc2_state_md)
    if orphan_m:
        lines.append(f"- **Orphaned pages:** {orphan_m.group(1)}")
    if weak_m:
        lines.append(f"- **Weak-linked pages:** {weak_m.group(1)}")
    lines.append("")
    lines.append("## Open Issues (from todo queue)")
    nuc2_tasks = [
        t
        for t in todos
        if t.get("source_scope") == "nuc2" or t.get("source_host") == HOST
    ]
    wiki_gaps = [t for t in nuc2_tasks if t.get("kind") == "wiki_gap"]
    if wiki_gaps:
        for t in wiki_gaps:
            prom = t.get("promotion_status", "")
            fresh = t.get("freshness_band", "")
            lines.append(
                f"- **[{t['severity'].upper()}/{prom}]** {t['title']} — {t['kind']} ({fresh})"
            )
    else:
        lines.append("- _No open NUC2 issues in current queue_")
    lines.append("")
    lines.append("<!-- END MACHINE MANAGED -->")
    lines.append("")
    lines.append("## Human Notes")
    lines.append("")
    lines.append(
        "<!-- Add notes here — this section is preserved on machine-managed runs -->"
    )
    lines.append("")
    lines.append("## See Also")
    lines.append("- [NUC Topology and Services](nuc-topology-and-services.md)")
    lines.append("- [NUC1 Current State](nuc1-current-state.md)")
    lines.append("- [Slimy KB](../projects/slimy-kb.md)")
    return "\n".join(lines)


def build_repo_health_content(nuc1_json: dict, nuc2_state_md: str) -> str:
    lines = []
    lines.append("# Repo Health Overview")
    lines.append("")
    lines.append("> Category: projects")
    lines.append(f"> Updated: {TIMESTAMP}")
    lines.append("> Status: active")
    lines.append("")
    lines.append("<!-- BEGIN MACHINE MANAGED — Do not edit manually -->")
    lines.append("")
    lines.append("## Cross-NUC Repo Summary")
    lines.append("")
    lines.append("### NUC1 Repos")
    nuc1_repos = nuc1_json.get("repos", [])
    dirty = nuc1_json.get("dirty_repos", [])
    diverged = nuc1_json.get("diverged_repos", [])
    if nuc1_repos:
        lines.append("| Repo | Dirty | Diverged |")
        lines.append("|------|--------|----------|")
        for name in nuc1_repos[:20]:
            is_dirty = "⚠️ YES" if name in dirty else "—"
            is_diverged = "⚠️ YES" if name in diverged else "—"
            lines.append(f"| {name} | {is_dirty} | {is_diverged} |")
    else:
        lines.append("_No NUC1 repo data available in this digest._")
    lines.append("")
    lines.append("### NUC2 Repos")
    lines.append("- _NUC2 repo state parsed from local git status_")
    lines.append("")
    lines.append("## Action Required")
    action_items = []
    if dirty:
        action_items.append(
            f"- **Dirty on NUC1:** {', '.join(dirty)} — commit or stash"
        )
    if diverged:
        action_items.append(
            f"- **Diverged on NUC1:** {', '.join(diverged)} — merge or rebase"
        )
    if not action_items:
        lines.append("- _No repo drift detected in this run_")
    else:
        for a in action_items:
            lines.append(a)
    lines.append("")
    lines.append("<!-- END MACHINE MANAGED -->")
    lines.append("")
    lines.append("## Human Notes")
    lines.append("")
    lines.append(
        "<!-- Add notes here — this section is preserved on machine-managed runs -->"
    )
    lines.append("")
    lines.append("## See Also")
    lines.append("- [NUC1 Current State](../architecture/nuc1-current-state.md)")
    lines.append("- [NUC2 Current State](../architecture/nuc2-current-state.md)")
    lines.append("- [Slimy KB](../projects/slimy-kb.md)")
    return "\n".join(lines)


def write_harness_candidates(todos: list[dict]) -> bool:
    """Write output/harness_candidates.md."""
    candidate_tasks = [t for t in todos if t.get("promotion_status") == "candidate"]
    emerging_tasks = [t for t in todos if t.get("promotion_status") == "emerging"]
    cooling_tasks = [t for t in todos if t.get("promotion_status") == "cooling_down"]

    lines = []
    lines.append(f"# Harness Candidates — {TIMESTAMP}")
    lines.append("")
    lines.append(f"_Auto-generated by wiki-manager-stage1 (1.86). Not dispatched._")
    lines.append("")
    lines.append(f"**Total candidates:** {len(candidate_tasks)}")
    lines.append(f"**Total emerging:** {len(emerging_tasks)}")
    lines.append(f"**Total cooling_down:** {len(cooling_tasks)}")
    lines.append("")
    lines.append(
        f"See [_candidate-promotion-rules.md](../wiki/_candidate-promotion-rules.md) for Stage 1.86 criteria."
    )
    lines.append("")
    lines.append("## Candidates (meet all 1.86 criteria)")
    lines.append("")

    if not candidate_tasks:
        lines.append("_No tasks currently meet harness candidate criteria._")
    else:
        for t in candidate_tasks:
            lines.append(f"### [{t['id']}] {t['title']}")
            lines.append("")
            lines.append(f"- **Project:** {t.get('project', 'unknown')}")
            lines.append(f"- **Severity:** {t['severity']} ({t.get('kind', '?')})")
            lines.append(f"- **Why it matters:** {t.get('reason', 'N/A')}")
            lines.append(f"- **Promotion reason:** {t.get('promotion_reason', 'N/A')}")
            lines.append(
                f"- **Persistence:** {t.get('occurrence_count', 1)}x lifetime / {t.get('recent_occurrence_count', '?')}x recent"
            )
            lines.append(
                f"- **Freshness:** {t.get('freshness_band', '?')} (evidence age: {t.get('evidence_age_h', '?')}h)"
            )
            lines.append(
                f"- **Evidence:** {', '.join(t.get('evidence_paths', []) or ['N/A'])}"
            )
            lines.append(
                f"- **Suggested prompt mode:** {t.get('suggested_prompt_mode', 'auto')}"
            )
            lines.append(
                f"- **Dispatch blocker:** {t.get('dispatch_blocker') or 'none'}"
            )
            lines.append(
                f"- **Source:** {t.get('source_host', '?')} ({t.get('source_scope', 'unknown')})"
            )
            proj = t.get("project", "")
            if proj:
                page = find_project_page(proj)
                if page:
                    lines.append(f"- **Related wiki page:** {page.name}")
            lines.append("")

    if emerging_tasks:
        lines.append("## Emerging (not yet candidate — needs more recency or evidence)")
        lines.append("")
        for t in emerging_tasks:
            lines.append(f"### [{t['id']}] {t['title']}")
            lines.append("")
            lines.append(
                f"- **Project:** {t.get('project', 'unknown')} | **Severity:** {t['severity']}"
            )
            lines.append(
                f"- **Persistence:** {t.get('recent_occurrence_count', '?')}x recent / {t.get('occurrence_count', '?')}x lifetime"
            )
            lines.append(f"- **Freshness:** {t.get('freshness_band', '?')}")
            lines.append(f"- **Why it matters:** {t.get('reason', 'N/A')}")
            lines.append(
                f"- **What would promote:** more recent evidence or fresher evidence files"
            )
            lines.append("")

    if cooling_tasks:
        lines.append("## Cooling Down (was candidate/emerging — evidence weakened)")
        lines.append("")
        for t in cooling_tasks:
            lines.append(f"### [{t['id']}] {t['title']}")
            lines.append("")
            lines.append(
                f"- **Project:** {t.get('project', 'unknown')} | **Severity:** {t['severity']}"
            )
            lines.append(
                f"- **Persistence:** {t.get('recent_occurrence_count', '?')}x recent / {t.get('occurrence_count', '?')}x lifetime"
            )
            lines.append(f"- **Freshness:** {t.get('freshness_band', '?')} (demoted)")
            lines.append(f"- **Why it matters:** {t.get('reason', 'N/A')}")
            lines.append(
                f"- **What would restore:** newer evidence or fresher source files"
            )
            lines.append("")

    lines.append("---")
    lines.append(
        "_Stage 1.86 does not dispatch. Candidate status is advisory only, dispatch blocked by `advisory_only`._"
    )

    HARNESS_CANDIDATES_MD.parent.mkdir(parents=True, exist_ok=True)
    HARNESS_CANDIDATES_MD.write_text("\n".join(lines))
    return bool(candidate_tasks) or bool(emerging_tasks) or bool(cooling_tasks)


def write_candidate_review_pack(todos: list[dict]) -> None:
    """
    Write output/candidate_review_pack.md — human-oriented compact review digest.
    Stage 1.86 version with freshness bands, cooling_down, and bucket grouping.
    """
    candidate_tasks = [t for t in todos if t.get("promotion_status") == "candidate"]
    emerging_tasks = [t for t in todos if t.get("promotion_status") == "emerging"]
    cooling_tasks = [t for t in todos if t.get("promotion_status") == "cooling_down"]
    not_cand_tasks = [t for t in todos if t.get("promotion_status") == "not_candidate"]

    lines = []
    lines.append(f"# Candidate Review Pack — {TIMESTAMP}")
    lines.append("")
    lines.append("> Stage: 1.86")
    lines.append(f"> Generated: {TIMESTAMP}")
    lines.append("> Purpose: Human review digest for future harness dispatch")
    lines.append("")
    lines.append("**This file does NOT dispatch. It is a review aid.**")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Candidates:** {len(candidate_tasks)}")
    lines.append(f"- **Emerging:** {len(emerging_tasks)}")
    lines.append(f"- **Cooling down:** {len(cooling_tasks)}")
    lines.append(f"- **Not candidate:** {len(not_cand_tasks)}")
    lines.append(f"- **Total in queue:** {len(todos)}")
    lines.append("")
    lines.append("## Freshness Bands")
    fresh = sum(1 for t in todos if t.get("freshness_band") == "fresh")
    aging = sum(1 for t in todos if t.get("freshness_band") == "aging")
    stale = sum(1 for t in todos if t.get("freshness_band") == "stale")
    lines.append(f"- **fresh** (< 24h): {fresh}")
    lines.append(f"- **aging** (24-72h): {aging}")
    lines.append(f"- **stale** (> 72h): {stale}")
    lines.append("")

    # ── True Candidates ──
    if candidate_tasks:
        lines.append("## Candidates — Ready for Harness Dispatch Review")
        lines.append("")
        lines.append("These tasks meet all Stage 1.86 promotion criteria:")
        lines.append(
            "recent evidence (3+ in last 5 runs), fresh/aging evidence, medium+ severity."
        )
        lines.append("")
        for t in candidate_tasks:
            proj = t.get("project", "")
            page = find_project_page(proj) if proj else None
            sev = t.get("severity", "?").upper()
            kind = t.get("kind", "?")
            recent = t.get("recent_occurrence_count", "?")
            lifetime = t.get("occurrence_count", "?")
            fresh = t.get("freshness_band", "?")
            evidence = t.get("evidence_paths", [])
            blocker = t.get("dispatch_blocker") or "none"
            actionability = (
                "actionable"
                if blocker == "advisory_only" and sev in ("HIGH", "MEDIUM")
                else "review_required"
            )

            lines.append(f"### [{t['id']}] {t['title']}")
            lines.append("")
            lines.append(f"| Field | Value |")
            lines.append(f"|-------|-------|")
            lines.append(f"| Project | {proj} |")
            lines.append(f"| Severity | {sev} ({kind}) |")
            lines.append(f"| Persistence | {recent}x recent / {lifetime}x lifetime |")
            lines.append(f"| Freshness | {fresh} |")
            lines.append(
                f"| Evidence | {', '.join(evidence) if evidence else 'none'} |"
            )
            lines.append(f"| Dispatch blocker | {blocker} |")
            lines.append(f"| Actionability | {actionability} |")
            lines.append(
                f"| Source | {t.get('source_host', '?')} ({t.get('source_scope', '?')}) |"
            )
            if page:
                lines.append(f"| Related wiki page | {page.name} |")
            lines.append("")
            lines.append(f"**Why it matters:** {t.get('reason', 'N/A')}")
            lines.append("")
            lines.append(
                f"**Recommended action:** {t.get('recommended_action', 'N/A')}"
            )
            lines.append("")
    else:
        lines.append("## Candidates — Ready for Harness Dispatch Review")
        lines.append("")
        lines.append("_No tasks currently qualify as candidates._")
        lines.append("")
        lines.append(
            "This may be correct — Stage 1.86 requires recent evidence (3+ in 5 runs),"
        )
        lines.append("fresh/aging evidence files, and medium+ severity.")
        lines.append("")

    # ── Emerging ──
    if emerging_tasks:
        lines.append("## Emerging — Close but Not Ready")
        lines.append("")
        for t in emerging_tasks:
            proj = t.get("project", "")
            sev = t.get("severity", "?").upper()
            recent = t.get("recent_occurrence_count", "?")
            fresh = t.get("freshness_band", "?")
            lines.append(f"### [{t['id']}] {t['title']}")
            lines.append("")
            lines.append(
                f"- **Project:** {proj} | **Severity:** {sev} | **Freshness:** {fresh}"
            )
            lines.append(
                f"- **Persistence:** {recent}x recent / {t.get('occurrence_count', '?')}x lifetime"
            )
            lines.append(
                f"- **What would promote:** more recent runs OR fresher evidence files"
            )
            lines.append(f"- **Why it matters:** {t.get('reason', 'N/A')}")
            lines.append("")

    # ── Cooling Down ──
    if cooling_tasks:
        lines.append(f"## Cooling Down ({len(cooling_tasks)} tasks)")
        lines.append("")
        lines.append(
            "These tasks were previously candidate/emerging but recent evidence has weakened."
        )
        lines.append(
            "They are tracked but require fresh evidence before they can be restored to candidate."
        )
        lines.append("")
        for t in cooling_tasks:
            sev = t.get("severity", "?").upper()
            fresh = t.get("freshness_band", "?")
            lines.append(
                f"- **[{t['id']}]** {t['title']} — {sev} ({fresh}) — {t.get('promotion_reason', '')}"
            )
        lines.append("")

    # ── Not Candidate ──
    if not_cand_tasks:
        lines.append(f"## Not Candidate ({len(not_cand_tasks)} tasks)")
        lines.append("")
        lines.append(
            "These tasks are tracked but lack sufficient recent evidence, have stale evidence,"
        )
        lines.append("or are excluded kinds. Lifetime history is preserved for audit.")
        lines.append("")
        for t in not_cand_tasks[:8]:
            fresh = t.get("freshness_band", "?")
            lines.append(
                f"- **[{t['id']}]** {t['title']} — {t.get('promotion_reason', '?')} ({fresh})"
            )
        if len(not_cand_tasks) > 8:
            lines.append(f"- _...and {len(not_cand_tasks) - 8} more_")
        lines.append("")

    lines.append("---")
    lines.append(
        "_Stage 1.86 — advisory only. Candidate status is advisory only, dispatch blocked by `advisory_only`._"
    )

    CANDIDATE_REVIEW_PACK.parent.mkdir(parents=True, exist_ok=True)
    CANDIDATE_REVIEW_PACK.write_text("\n".join(lines))


def write_manager_status(
    todos,
    backend,
    nuc1_used,
    nuc1_info,
    state_map,
    nuc2_state_md_for_status="",
    updated_project_pages: list[str] = None,
    demotion_count: int = 0,
    promotion_counts: dict = None,
    freshness_counts: dict = None,
):
    by_kind = {}
    by_state = {"new": 0, "persisting": 0, "resolved": 0}
    by_promotion = {
        "candidate": 0,
        "emerging": 0,
        "not_candidate": 0,
        "cooling_down": 0,
    }
    by_freshness = {"fresh": 0, "aging": 0, "stale": 0}
    harness_candidates = []
    for t in todos:
        by_kind.setdefault(t["kind"], []).append(t)
        by_state[t.get("state", "new")] = by_state.get(t.get("state", "new"), 0) + 1
        prom = t.get("promotion_status", "not_candidate")
        by_promotion[prom] = by_promotion.get(prom, 0) + 1
        by_freshness[t.get("freshness_band", "unknown")] = (
            by_freshness.get(t.get("freshness_band", "unknown"), 0) + 1
        )
        if prom in ("candidate", "emerging"):
            harness_candidates.append(t)

    updated_project_pages = updated_project_pages or []
    promotion_counts = promotion_counts or {}
    freshness_counts = freshness_counts or {}
    demotion_count = demotion_count or 0

    lines = []
    lines.append(f"# Wiki Manager Status")
    lines.append("")
    lines.append(f"> Category: concepts")
    lines.append(f"> Updated: {TIMESTAMP}")
    lines.append("")
    lines.append(f"**Last run:** {TIMESTAMP}")
    lines.append(f"**Stage:** 1.86")
    lines.append(f"**Backend:** {backend}")
    lines.append(f"**NUC1 evidence:** {'consumed' if nuc1_used else 'none'}")
    if nuc1_info.get("nuc1_host"):
        lines.append(f"**NUC1 host:** {nuc1_info['nuc1_host']}")
    lines.append("")
    lines.append("## Queue Summary")
    lines.append("")
    lines.append(f"- Total tasks: {len(todos)}")
    lines.append(f"- NEW: {by_state.get('new', 0)}")
    lines.append(f"- PERSISTING: {by_state.get('persisting', 0)}")
    lines.append(f"- RESOLVED (this run): {by_state.get('resolved', 0)}")
    lines.append("")
    lines.append("## Promotion Counts")
    lines.append("")
    lines.append(f"- **candidate:** {by_promotion.get('candidate', 0)}")
    lines.append(f"- **emerging:** {by_promotion.get('emerging', 0)}")
    lines.append(f"- **cooling_down:** {by_promotion.get('cooling_down', 0)}")
    lines.append(f"- **not_candidate:** {by_promotion.get('not_candidate', 0)}")
    if demotion_count > 0:
        lines.append(f"- **demoted this run:** {demotion_count}")
    lines.append("")
    lines.append("## Freshness Bands")
    lines.append("")
    lines.append(f"- **fresh** (< 24h): {by_freshness.get('fresh', 0)}")
    lines.append(f"- **aging** (24-72h): {by_freshness.get('aging', 0)}")
    lines.append(f"- **stale** (> 72h): {by_freshness.get('stale', 0)}")
    lines.append("")
    lines.append("## By Kind")
    lines.append("")
    for kind, tasks in sorted(by_kind.items()):
        lines.append(f"- **{kind}:** {len(tasks)}")
    lines.append("")
    lines.append("## Stable Pages Updated")
    lines.append("")
    nuc1_updated = "YES" if nuc1_info.get("repos") else "SKIPPED (no NUC1 evidence)"
    lines.append(
        f"- [nuc1-current-state.md](architecture/nuc1-current-state.md): {nuc1_updated}"
    )
    nuc2_has_state = bool(nuc2_state_md_for_status)
    lines.append(
        f"- [nuc2-current-state.md](architecture/nuc2-current-state.md): {'YES' if nuc2_has_state else 'SKIPPED (no NUC2 digest)'}"
    )
    lines.append(
        f"- [repo-health-overview.md](projects/repo-health-overview.md): {'YES' if nuc1_info.get('repos') or nuc2_has_state else 'SKIPPED'}"
    )
    lines.append(
        f"- [_project-health-index.md](projects/_project-health-index.md): {'YES' if nuc1_info.get('repos') else 'SKIPPED'}"
    )
    lines.append(
        f"- [_candidate-promotion-rules.md](../wiki/_candidate-promotion-rules.md): YES (always updated)"
    )
    lines.append("")
    if updated_project_pages:
        lines.append("## Project Pages Updated This Run")
        lines.append("")
        for pg in updated_project_pages:
            lines.append(f"- {pg}")
        lines.append("")
    if harness_candidates:
        lines.append("## Harness Candidates")
        lines.append("")
        for t in harness_candidates:
            prom = t.get("promotion_status", "")
            fresh = t.get("freshness_band", "")
            lines.append(
                f"- **[{t['id']}]** {t['title']} (severity: {t['severity']}, promotion: {prom}, {fresh})"
            )
        lines.append("")
    lines.append("## Task List")
    lines.append("")
    for t in todos:
        state_icon = {"new": "✨", "persisting": "🔄", "resolved": "✅"}.get(
            t.get("state", "new"), "•"
        )
        prom = t.get("promotion_status", "")
        prom_str = f" [{prom}]" if prom else ""
        demoted = " ⚠️" if t.get("demoted_this_run") else ""
        fresh = t.get("freshness_band", "")
        lines.append(
            f"{state_icon} [{t['id']}] {t['title']} ({t['severity']}, {t['kind']}){prom_str} ({fresh}){demoted} — {t.get('source_host', '?')}"
        )
    lines.append("")
    lines.append("---")
    lines.append(
        "*Managed by wiki-manager-stage1.timer (every 12h). Do not edit directly.*"
    )

    MANAGER_STATUS.parent.mkdir(parents=True, exist_ok=True)
    with open(MANAGER_STATUS, "w") as f:
        f.write("\n".join(lines))


def write_candidate_rules() -> bool:
    """Write candidate promotion rules page (Stage 1.86)."""
    content = CANDIDATE_RULES_CONTENT_186.replace("_TS_PLACEHOLDER_", TIMESTAMP)
    CANDIDATE_RULES_PAGE.parent.mkdir(parents=True, exist_ok=True)
    existing = CANDIDATE_RULES_PAGE.read_text() if CANDIDATE_RULES_PAGE.exists() else ""
    if existing == content:
        return False
    CANDIDATE_RULES_PAGE.write_text(content)
    return True


# ── Main ─────────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Wiki Manager Stage 1.86 — freshness-weighted promotion + cooling_down"
    )
    parser.add_argument("--orphans", default="")
    parser.add_argument("--weak-links", default="")
    parser.add_argument("--nuc1-json", default="")
    parser.add_argument("--nuc1-md", default="")
    parser.add_argument("--nuc2-md", default="")
    parser.add_argument("--backend", default="stub", choices=["ollama", "stub"])
    parser.add_argument("--model", default="qwen2.5:7b")
    args = parser.parse_args()

    orphans = parse_orphans(args.orphans)
    weak_links = parse_weak_links(args.weak_links)

    todos, nuc1_info, nuc1_md_parsed = build_todos(
        orphans, weak_links, args.nuc1_json, args.nuc1_md, args.backend, args.model
    )

    history, state_map = update_history(todos)

    demotion_count = 0
    for t in todos:
        key = t.get("task_key", task_key(t))
        entry = next((e for e in history["tasks"] if e["task_key"] == key), None)
        occ = entry["occurrence_count"] if entry else 1
        new_sev = compute_severity(t, nuc1_info, occ)
        t["severity"] = new_sev
        t["occurrence_count"] = occ

        # Freshness band
        t["freshness_band"] = compute_freshness_band(t, TIMESTAMP)
        age_h = evidence_age_hours(t)
        t["evidence_age_h"] = round(age_h, 1) if age_h != float("inf") else -1

        # Stage 1.86 promotion
        prom_status, prom_reason, demoted = compute_promotion_186(t, entry or {})
        t["promotion_status"] = prom_status
        t["promotion_reason"] = prom_reason
        t["demoted_this_run"] = demoted
        if demoted:
            demotion_count += 1

        # Update promotion tracking in history entry
        if entry:
            if prom_status != entry.get("last_known_promotion_status"):
                entry["last_promotion_status_change"] = TIMESTAMP
            entry["last_known_promotion_status"] = prom_status
            if prom_status != "not_candidate":
                if not entry.get("promotion_first_seen"):
                    entry["promotion_first_seen"] = TIMESTAMP
                entry["promotion_last_seen"] = TIMESTAMP
                entry["promotion_occurrence_count"] = (
                    entry.get("promotion_occurrence_count", 0) + 1
                )

        if prom_status == "candidate" and not t.get("dispatch_blocker"):
            t["dispatch_blocker"] = "advisory_only"

    with open(TODO_HISTORY, "w") as f:
        json.dump(history, f, indent=2)

    nuc1_used = bool(nuc1_info.get("repos") or nuc1_info.get("dirty_repos"))

    nuc1_written = write_stable_page(
        NUC1_STATE_PAGE, build_nuc1_state_content(nuc1_info, nuc1_md_parsed, todos)
    )
    nuc2_written = write_stable_page(
        NUC2_STATE_PAGE, build_nuc2_state_content(args.nuc2_md, todos)
    )
    repo_written = write_stable_page(
        REPO_HEALTH_PAGE, build_repo_health_content(nuc1_info, args.nuc2_md)
    )

    nuc1_repos = nuc1_info.get("repos", [])
    project_health_written = False
    if nuc1_used and nuc1_repos:
        project_health_written = write_stable_page(
            PROJECT_HEALTH_INDEX, build_project_health_index(nuc1_info, todos, [])
        )

    candidate_rules_written = write_candidate_rules()

    updated_project_pages = []
    all_repos_data = nuc1_info.get("repo_details", [])
    if nuc1_used:
        for t in todos:
            proj = t.get("project", "")
            if not proj or proj == "kb":
                continue
            page = find_project_page(proj)
            if page:
                status_block = build_project_status_block(
                    proj, nuc1_info, todos, all_repos_data
                )
                if update_project_page(page, proj, status_block, todos):
                    updated_project_pages.append(page.name)

    if nuc1_used and nuc1_repos:
        health_content = build_project_health_index(
            nuc1_info, todos, updated_project_pages
        )
        write_stable_page(PROJECT_HEALTH_INDEX, health_content)

    harness_written = write_harness_candidates(todos)
    write_candidate_review_pack(todos)

    promotion_counts = {
        "candidate": sum(1 for t in todos if t.get("promotion_status") == "candidate"),
        "emerging": sum(1 for t in todos if t.get("promotion_status") == "emerging"),
        "cooling_down": sum(
            1 for t in todos if t.get("promotion_status") == "cooling_down"
        ),
        "not_candidate": sum(
            1 for t in todos if t.get("promotion_status") == "not_candidate"
        ),
    }
    freshness_counts = {
        "fresh": sum(1 for t in todos if t.get("freshness_band") == "fresh"),
        "aging": sum(1 for t in todos if t.get("freshness_band") == "aging"),
        "stale": sum(1 for t in todos if t.get("freshness_band") == "stale"),
    }

    output = {
        "generated_at": TIMESTAMP,
        "source_host": HOST,
        "backend": args.backend,
        "model": args.model if args.backend == "ollama" else None,
        "stage": "1.86",
        "task_count": len(todos),
        "nuc1_evidence_used": nuc1_used,
        "nuc1_host": nuc1_info.get("nuc1_host", "unknown"),
        "orphan_count": len(orphans),
        "weak_link_count": len(weak_links),
        "promotion_counts": promotion_counts,
        "freshness_counts": freshness_counts,
        "demotion_count": demotion_count,
        "stable_pages_written": {
            "nuc1_current_state": nuc1_written,
            "nuc2_current_state": nuc2_written,
            "repo_health_overview": repo_written,
            "project_health_index": project_health_written,
            "candidate_promotion_rules": candidate_rules_written,
        },
        "project_pages_updated": updated_project_pages,
        "harness_candidates_written": harness_written,
        "tasks": todos,
    }
    with open(TODO_JSON, "w") as f:
        json.dump(output, f, indent=2)

    md = generate_markdown(todos, args.backend, nuc1_used, nuc1_info, state_map)
    with open(TODO_MD, "w") as f:
        f.write(md)

    write_manager_status(
        todos,
        args.backend,
        nuc1_used,
        nuc1_info,
        state_map,
        nuc2_state_md_for_status=args.nuc2_md,
        updated_project_pages=updated_project_pages,
        demotion_count=demotion_count,
        promotion_counts=promotion_counts,
        freshness_counts=freshness_counts,
    )

    print(f"todo_queue.json: {TODO_JSON} ({len(todos)} tasks)")
    print(f"todo_queue.md: {TODO_MD}")
    print(f"todo_history.json: {TODO_HISTORY}")
    print(f"nuc1_evidence_used: {nuc1_used}")
    print(
        f"Stable pages: nuc1={nuc1_written} nuc2={nuc2_written} repo={repo_written} health={project_health_written} rules={candidate_rules_written}"
    )
    print(f"Project pages updated: {updated_project_pages}")
    print(
        f"Promotion: candidate={promotion_counts['candidate']} emerging={promotion_counts['emerging']} cooling_down={promotion_counts['cooling_down']} not_candidate={promotion_counts['not_candidate']}"
    )
    print(
        f"Freshness: fresh={freshness_counts['fresh']} aging={freshness_counts['aging']} stale={freshness_counts['stale']}"
    )
    print(f"Demotions this run: {demotion_count}")
    print(f"Harness candidates: {'YES' if harness_written else 'none'}")
    print(f"Candidate review pack: {CANDIDATE_REVIEW_PACK}")
    print(f"Backend: {args.backend}")

    # Refresh git-backed metadata on all wiki pages
    import subprocess as _sp

    try:
        _result = _sp.run(
            ["python3", str(Path("/home/slimy/kb/tools/kb-apply-metadata.py"))],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if _result.returncode == 0:
            print(f"Metadata refresh: {_result.stdout.strip()}")
        else:
            print(f"Metadata refresh warning: {_result.stderr.strip()[:200]}")
    except Exception as _e:
        print(f"Metadata refresh skipped: {_e}")


if __name__ == "__main__":
    main()
