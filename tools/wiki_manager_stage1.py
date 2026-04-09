#!/usr/bin/env python3
"""
wiki_manager_stage1.py — Stage 1.8 todo queue generator + stable wiki pages.

Stage 1.8 adds:
- Project-page filing: updates matching wiki/projects/*.md pages with machine-managed status blocks
- Project health index: wiki/projects/_project-health-index.md
- Harness candidate promotion rules: wiki/_candidate-promotion-rules.md
- Enhanced harness_candidates.md with richer per-candidate fields
- Promotion fields in todo queue (promotion_status, promotion_reason, dispatch_blocker)
- Noise control: bounded growth, deterministic machine-managed sections
- Stage 1.8 is still advisory only: does NOT dispatch harness jobs.
"""
import json
import sys
import os
import argparse
import re
from datetime import datetime, timezone
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

# History retention
HISTORY_RETENTION_RUNS = 10
HISTORY_RETENTION_DAYS = 30

# Promotion thresholds
PROMOTION_MIN_OCCURRENCES = 3      # task must persist N times before becoming candidate
PROMOTION_CROSS_NUC_BONUS = 2     # cross-NUC evidence counts as extra occurrences


# ── Parsing helpers ──────────────────────────────────────────────────────────

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
        "repos": [], "repo_details": [], "dirty_repos": [], "diverged_repos": [],
        "kb_present": False, "nuc1_host": "unknown", "ts": ""
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
        "nuc1_host": "unknown", "ts": "",
        "dirty_services": [], "active_services": [], "listening_ports": []
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


# ── Project-page matching ─────────────────────────────────────────────────────

def find_project_page(repo_name: str) -> Optional[Path]:
    """
    Find a wiki/projects/*.md page that corresponds to the given repo name.
    Matches by normalized name (lowercase, hyphens/underscores normalized).
    """
    if not repo_name or not WIKI_PROJ_DIR.exists():
        return None

    normalized = re.sub(r"[-_]", "", repo_name.lower())
    for page_path in WIKI_PROJ_DIR.glob("*.md"):
        if page_path.name.startswith("_"):
            continue
        page_normalized = re.sub(r"[-_]", "", page_path.stem.lower())
        if page_normalized == normalized or page_normalized.startswith(normalized) or normalized.startswith(page_normalized):
            return page_path
    return None


def get_project_page_name(repo_name: str) -> str:
    """Get the display name for a repo."""
    return repo_name.replace("-", " ").replace("_", " ").title()


def get_machine_managed_block(content: str) -> tuple[str, str]:
    """
    Extract the existing machine-managed block content and the rest.
    Returns (machine_block_content, rest_of_file).
    If no block found, returns ('', full_content).
    """
    begin_marker = "<!-- BEGIN MACHINE MANAGED"
    end_marker = "<!-- END MACHINE MANAGED -->"

    begin_idx = content.find(begin_marker)
    end_idx = content.find(end_marker)

    if begin_idx == -1 or end_idx == -1:
        return "", content

    block_content = content[begin_idx + len(begin_marker):end_idx]
    before = content[:begin_idx]
    after = content[end_idx + len(end_marker):]
    rest = before + after

    return block_content.strip(), rest


def update_project_page(page_path: Path, repo_name: str, status_block: str, todos: list[dict]) -> bool:
    """
    Update a project page with a machine-managed status block.
    Preserves human-written content outside the MACHINE MANAGED markers.
    Returns True if page was modified, False if skipped (no material change).
    """
    if not page_path.exists():
        return False

    existing = page_path.read_text()

    begin_marker = f"<!-- BEGIN MACHINE MANAGED — Do not edit manually -->"
    end_marker = "<!-- END MACHINE MANAGED -->"

    # Check if block already exists and matches
    existing_block_match = re.search(
        r'<!-- BEGIN MACHINE MANAGED — Do not edit manually -->.*?<!-- END MACHINE MANAGED -->',
        existing, re.DOTALL
    )
    new_block = f"{begin_marker}\n\n{status_block}\n\n{end_marker}"

    if existing_block_match:
        if existing_block_match.group(0) == new_block:
            return False  # no change
        new_content = existing[:existing_block_match.start()] + new_block + existing[existing_block_match.end():]
    else:
        # Append before any "## See Also" or at end
        see_also_match = re.search(r'\n## See Also', existing)
        if see_also_match:
            new_content = existing[:see_also_match.start()] + "\n" + new_block + "\n" + existing[see_also_match.start():]
        else:
            new_content = existing.rstrip() + "\n\n" + new_block + "\n"

    page_path.write_text(new_content)
    return True


def build_project_status_block(repo_name: str, nuc1_json: dict, todos: list[dict], all_repos) -> str:
    """Build the machine-managed status block for a project page."""
    lines = []

    # Find repo data — repos can be list of strings or list of dicts
    repo_data = None
    for r in all_repos:
        if isinstance(r, dict) and r.get("name") == repo_name:
            repo_data = r
            break
        elif isinstance(r, str) and r == repo_name:
            repo_data = {"name": r}
            break

    # Current timestamp
    lines.append(f"**Last updated:** {TIMESTAMP}")

    # Repo health from NUC1 digest
    dirty = repo_name in nuc1_json.get("dirty_repos", [])
    diverged = repo_name in nuc1_json.get("diverged_repos", [])
    nuc1_repos = nuc1_json.get("repos", [])

    if repo_data:
        lines.append(f"**NUC1 status:** {'DIRTY' if dirty else 'clean'}, {'DIVERGED' if diverged else 'synced'}")
        commit = (repo_data.get("commit_hash") or "unknown")[:7]
        subject = repo_data.get("commit_subject", "")
        branch = repo_data.get("branch") or "detached"
        lines.append(f"**NUC1 commit:** `{commit}` — {subject}")
        lines.append(f"**Branch:** {branch}")
    elif nuc1_repos and not repo_data:
        lines.append(f"**NUC1 status:** in digest but no detail available")

    # Find relevant todos for this project
    project_todos = [t for t in todos if t.get("project", "").lower() == repo_name.lower()]
    if project_todos:
        lines.append("")
        lines.append("### Open Issues")
        for t in project_todos[:5]:
            sev = t.get("severity", "?").upper()
            kind = t.get("kind", "?")
            occ = t.get("occurrence_count", 1)
            lines.append(f"- **[{sev}]** {t['title']} ({kind}, {occ}x)")
    else:
        lines.append(f"**Open issues:** none in current queue")

    # Evidence paths
    if project_todos and project_todos[0].get("evidence_paths"):
        lines.append("")
        lines.append("### Evidence")
        for ep in project_todos[0].get("evidence_paths", []):
            lines.append(f"- `{ep}`")

    # Related pages
    lines.append("")
    lines.append("### Related Pages")
    lines.append(f"- [Repo Health Overview](./_project-health-index.md)")
    lines.append(f"- [NUC1 Current State](../architecture/nuc1-current-state.md)")

    return "\n".join(lines)


# ── Project health index ──────────────────────────────────────────────────────

def build_project_health_index(nuc1_json: dict, todos: list[dict], updated_pages: list[str]) -> str:
    """Build the _project-health-index.md content."""
    lines = []
    lines.append("# Project Health Index")
    lines.append("")
    lines.append("> Category: projects")
    lines.append(f"> Updated: {TIMESTAMP}")
    lines.append("> Status: active")
    lines.append("")
    lines.append("<!-- BEGIN MACHINE MANAGED — Do not edit manually -->")
    lines.append("")

    # Which repos appear in NUC1 digest
    # repos can be list of strings (from parse_nuc1_json) or list of dicts (from raw JSON)
    raw_repos = nuc1_json.get("repos", [])
    nuc1_repo_names = []
    for r in raw_repos:
        if isinstance(r, dict):
            nuc1_repo_names.append(r.get("name", ""))
        elif isinstance(r, str):
            nuc1_repo_names.append(r)

    # Which project pages exist
    existing_pages = {}
    if WIKI_PROJ_DIR.exists():
        for p in WIKI_PROJ_DIR.glob("*.md"):
            if not p.name.startswith("_"):
                existing_pages[p.stem.lower()] = p.name

    # Categorize repos
    covered_repos = []
    uncovered_repos = []
    for name in nuc1_repo_names:
        page = find_project_page(name)
        if page:
            covered_repos.append((name, page.name))
        else:
            uncovered_repos.append(name)

    # Counts
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

    # Pages updated this run
    if updated_pages:
        lines.append("## Pages Updated This Run")
        lines.append("")
        for pg in updated_pages:
            lines.append(f"- {pg}")
        lines.append("")

    # Repos with project pages
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

    # Repos without project pages
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

    # Repo health table
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
    lines.append("<!-- Add notes here — this section is preserved on machine-managed runs -->")
    lines.append("")
    lines.append("## See Also")
    lines.append("- [Repo Health Overview](./repo-health-overview.md)")
    lines.append("- [NUC1 Current State](../architecture/nuc1-current-state.md)")
    lines.append("- [NUC2 Current State](../architecture/nuc2-current-state.md)")

    return "\n".join(lines)


# ── Candidate promotion rules ─────────────────────────────────────────────────

PROMOTION_RULES_CONTENT = """# Harness Candidate Promotion Rules

> Category: concepts
> Updated: _TS_PLACEHOLDER_
> Status: active

<!-- BEGIN MACHINE MANAGED — Do not edit manually -->

## Overview

A task becomes a **harness candidate** when it meets explicit, bounded criteria. This page defines those criteria so promotion is deterministic and auditable.

## Promotion Statuses

| Status | Meaning |
|--------|---------|
| `not_candidate` | Default — task is tracked but does not yet qualify |
| `emerging` | Task has some signals but does not yet meet all criteria |
| `candidate` | Task meets all promotion criteria — ready for harness dispatch consideration |

## Bounded Promotion Criteria

A task is promoted to `candidate` when **ALL** of the following are true:

### 1. Persistence Threshold
- Task must have `occurrence_count >= {min_occ}` in the todo history
- Cross-NUC evidence adds a bonus of +{cnc_bonus} to the effective occurrence count for this check

### 2. Evidence Quality
- Task must have at least one `evidence_path` in the todo record
- Evidence must reference a real file or directory in `raw/` or `wiki/`

### 3. Severity Floor
- Task severity must be `medium` or `high` (not `low`)
- OR task must be `persisting` with `occurrence_count >= {min_occ} * 2`

### 4. No Active Dispatch Blocker
- `dispatch_blocker` must be empty OR only `"advisory_only"`
- advisory_only is a system-level blocker indicating Stage 1.x does not dispatch — this does not prevent candidate status

### 5. Kind Allowlist
- Only these kinds are eligible for promotion: `repo_drift`, `wiki_gap`, `doc_drift`
- `investigate` and `harness_candidate` kinds are excluded from promotion

## Promotion Reasons

When a task is promoted, `promotion_reason` is set to one of:

- `persistent_drift` — task is repo/wiki drift that has persisted >= {min_occ} times
- `cross_nuc_conflict` — cross-NUC KB or repo conflict with >= 2 occurrences
- `repeated_gap` — wiki gap persisting >= {min_occ} * 2 times

## Dispatch Blockers

Even candidate tasks may have dispatch blockers:

| Blocker | Meaning | Auto-clear? |
|---------|---------|-------------|
| _(empty)_ | No blocker — go ahead if severity warrants | N/A |
| `advisory_only` | Stage 1.x does not dispatch | Yes — cleared in Stage 2 |
| `needs_review` | Human review required before dispatch | No — manual clear |
| `cross_nuc_coordination` | Needs coordination with other NUC | No — manual clear |

## Stage 1.8 Boundary

Stage 1.8 does NOT dispatch harness jobs. Candidate status is recorded but dispatch is blocked by `advisory_only`. Stage 2 will handle actual dispatch.

<!-- END MACHINE MANAGED -->

## Human Notes

<!-- Add notes here -->
""".format(min_occ=PROMOTION_MIN_OCCURRENCES, cnc_bonus=PROMOTION_CROSS_NUC_BONUS)


# ── History management ───────────────────────────────────────────────────────

def load_history() -> dict:
    if not TODO_HISTORY.exists():
        return {"version": 1, "updated_at": "", "tasks": []}
    try:
        with open(TODO_HISTORY) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"version": 1, "updated_at": "", "tasks": []}


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
    from datetime import timedelta
    cutoff_30d = cutoff - timedelta(days=HISTORY_RETENTION_DAYS)

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
            entry["last_seen"] = now
            entry["occurrence_count"] = entry.get("occurrence_count", 1) + 1
            entry["state"] = "persisting"
            task["first_seen"] = entry.get("first_seen", now)
            task["occurrence_count"] = entry["occurrence_count"]
            task["state"] = "persisting"
            state_map[key] = "persisting"
        else:
            history["tasks"].append({
                "task_key": key,
                "first_seen": now,
                "last_seen": now,
                "occurrence_count": 1,
                "state": "new"
            })
            task["first_seen"] = now
            task["occurrence_count"] = 1
            task["state"] = "new"
            state_map[key] = "new"

    new_keys = {task_key(t) for t in new_tasks}
    for entry in history["tasks"]:
        if entry["task_key"] not in new_keys and entry.get("state") != "resolved":
            entry["state"] = "resolved"

    history["updated_at"] = now
    return history, state_map


# ── Severity heuristics ──────────────────────────────────────────────────────

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

    if source_scope == "cross_nuc" and "kb" in title_lower and "uncommitted" in title_lower:
        return "high"

    if occurrence_count > 1:
        severity += 1

    return ["low", "medium", "high"][min(severity, 2)]


# ── Promotion ────────────────────────────────────────────────────────────────

ALLOWED_PROMOTION_KINDS = {"repo_drift", "wiki_gap", "doc_drift"}
BLOCKED_PROMOTION_KINDS = {"investigate", "harness_candidate"}


def compute_promotion(task: dict, history_entry: dict) -> tuple[str, str]:
    """
    Determine promotion status for a task.
    Returns (promotion_status, promotion_reason).
    """
    kind = task.get("kind", "")
    occurrence_count = task.get("occurrence_count", 1)
    source_scope = task.get("source_scope", "")
    severity = task.get("severity", "low")
    evidence_paths = task.get("evidence_paths", [])
    dispatch_blocker = task.get("dispatch_blocker", "")

    # Kind check
    if kind in BLOCKED_PROMOTION_KINDS:
        return "not_candidate", "kind_excluded"
    if kind not in ALLOWED_PROMOTION_KINDS:
        return "not_candidate", "kind_not_allowed"

    # Evidence check
    if not evidence_paths:
        return "not_candidate", "no_evidence"

    # Dispatch blocker check (only advisory_only is acceptable)
    if dispatch_blocker and dispatch_blocker not in ("advisory_only", ""):
        return "not_candidate", f"dispatch_blocker:{dispatch_blocker}"

    # Cross-NUC bonus
    effective_occ = occurrence_count
    if source_scope == "cross_nuc":
        effective_occ += PROMOTION_CROSS_NUC_BONUS

    # Persistence threshold check
    if effective_occ >= PROMOTION_MIN_OCCURRENCES:
        # Severity floor
        if severity in ("medium", "high"):
            reason = "persistent_drift" if kind == "repo_drift" else "repeated_gap"
            if source_scope == "cross_nuc":
                reason = "cross_nuc_conflict"
            return "candidate", reason
        elif occurrence_count >= PROMOTION_MIN_OCCURRENCES * 2:
            return "candidate", "persistent_drift"

    # Emerging: has evidence and some persistence but not enough for candidate
    if evidence_paths and occurrence_count >= 2:
        return "emerging", "insufficient_persistence"

    return "not_candidate", "does_not_meet_criteria"


# ── Build todos ─────────────────────────────────────────────────────────────

def build_todos(orphans, weak_links, nuc1_json, nuc1_md, backend, model) -> tuple[list[dict], dict]:
    todos = []
    task_id = 1

    def add(kind, severity, title, reason, recommended_action,
            suggested_prompt_mode="manual", safe=True, project="kb",
            evidence_paths=None, notes="", source_host=HOST, source_scope="nuc2"):
        nonlocal task_id
        todos.append({
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
            # Promotion fields — filled in after history merge
            "promotion_status": "not_candidate",
            "promotion_reason": "",
        })
        task_id += 1

    nuc1 = parse_nuc1_json(nuc1_json)
    nuc1_md_parsed = parse_nuc1_markdown(nuc1_md)
    if nuc1_md_parsed.get("nuc1_host") and nuc1_md_parsed["nuc1_host"] != "unknown":
        nuc1["nuc1_host"] = nuc1_md_parsed["nuc1_host"]
    if nuc1_md_parsed.get("ts"):
        nuc1["ts"] = nuc1_md_parsed["ts"]

    nuc1_used = bool(nuc1.get("repos") or nuc1_md_parsed.get("active_services"))

    # NUC1-based tasks
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
                    source_scope="cross_nuc"
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
                    source_scope="cross_nuc"
                )

        active = nuc1_md_parsed.get("active_services", [])
        if active and "openclaw-gateway.service" in str(active):
            services = [s for s in active if "slimy" in s.lower() or "openclaw" in s.lower()]

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
            evidence_paths=[f"wiki/_orphans.md"]
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
                evidence_paths=[f"wiki/{orphan}"]
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
            evidence_paths=[f"wiki/_weak-links.md"]
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
            source_scope="cross_nuc"
        )

    # Stub fallback
    if not todos:
        todos.append({
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
        })

    return todos, nuc1


# ── Markdown generation ────────────────────────────────────────────────────

def generate_markdown(todos, backend, nuc1_used, nuc1_info, state_map) -> str:
    lines = []
    lines.append(f"# Todo Queue — {TIMESTAMP}")
    lines.append("")
    lines.append(f"**Generated by:** wiki_manager_stage1.py (Stage 1.8)")
    lines.append(f"**Backend:** {backend}")
    lines.append(f"**Host:** {HOST}")
    lines.append(f"**NUC1 evidence consumed:** {'YES' if nuc1_used else 'NO'}")
    if nuc1_info.get("nuc1_host"):
        lines.append(f"**NUC1 host:** {nuc1_info['nuc1_host']} ({nuc1_info.get('ts', 'no ts')})")
    lines.append("")

    by_severity = {}
    by_kind = {}
    by_state = {"new": [], "persisting": [], "resolved": []}
    by_promotion = {"candidate": [], "emerging": [], "not_candidate": []}
    for t in todos:
        by_severity.setdefault(t["severity"], []).append(t)
        by_kind.setdefault(t["kind"], []).append(t)
        by_state.setdefault(t.get("state", "new"), []).append(t)
        by_promotion.setdefault(t.get("promotion_status", "not_candidate"), []).append(t)

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Total tasks:** {len(todos)}")
    lines.append(f"- by severity: { {k: len(v) for k, v in by_severity.items()} }")
    lines.append(f"- by kind: { {k: len(v) for k, v in by_kind.items()} }")
    if state_map:
        new_c = sum(1 for s in state_map.values() if s == "new")
        pers_c = sum(1 for s in state_map.values() if s == "persisting")
        lines.append(f"- NEW: {new_c} | PERSISTING: {pers_c}")
    lines.append(f"- by promotion: candidate={len(by_promotion['candidate'])} emerging={len(by_promotion['emerging'])} not_candidate={len(by_promotion['not_candidate'])}")
    lines.append("")

    for state_label, sort_severity in [("NEW", ["high", "medium", "low"]), ("PERSISTING", ["high", "medium", "low"])]:
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
                lines.append(f"- **Promotion:** {t.get('promotion_status', 'unknown')} — {t.get('promotion_reason', '')}")
                lines.append(f"- **Reason:** {t['reason']}")
                lines.append(f"- **Recommended Action:** {t['recommended_action']}")
                lines.append(f"- **Prompt Mode:** {t['suggested_prompt_mode']}")
                lines.append(f"- **Safe to Dispatch:** {t['safe_to_dispatch']}")
                lines.append(f"- **Source:** {t['source_host']} ({t.get('source_scope', 'unknown')})")
                if t.get("occurrence_count", 1) > 1:
                    lines.append(f"- **Occurrences:** {t['occurrence_count']}x")
                if t.get("evidence_paths"):
                    lines.append(f"- **Evidence:** {', '.join(t['evidence_paths'])}")
                if t.get("dispatch_blocker"):
                    lines.append(f"- **Dispatch Blocker:** {t['dispatch_blocker']}")
                if t.get("notes"):
                    lines.append(f"- **Notes:** {t['notes']}")
                lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("*Stage 1.8 — advisory only. No harness jobs dispatched.*")

    return "\n".join(lines)


# ── Stable page writers ─────────────────────────────────────────────────────

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
    lines.append(f"- **Dirty (uncommitted changes):** {', '.join(dirty) if dirty else '_none_'}")
    lines.append(f"- **Diverged (ahead + behind remote):** {', '.join(diverged) if diverged else '_none_'}")
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
    nuc1_tasks = [t for t in todos if t.get("source_scope") == "cross_nuc" and t.get("source_host") in ("nuc1", "nuc1")]
    if nuc1_tasks:
        for t in nuc1_tasks:
            lines.append(f"- **[{t['severity'].upper()}]** {t['title']} — {t['kind']}")
    else:
        lines.append("- _No open NUC1 issues in current queue_")
    lines.append("")
    lines.append("<!-- END MACHINE MANAGED -->")
    lines.append("")
    lines.append("## Human Notes")
    lines.append("")
    lines.append("<!-- Add notes here — this section is preserved on machine-managed runs -->")
    lines.append("")
    lines.append("## See Also")
    lines.append("- [NUC Topology and Services](../architecture/nuc-topology-and-services.md)")
    lines.append("- [NUC2 Current State](nuc2-current-state.md)")
    lines.append("- [Cross-NUC Communication Matrix](../architecture/cross-nuc-communication-matrix.md)")
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
        if any(str(p) in line for p in [3000, 3838, 3850, 18790, 18792, 18793, 5432, 3307]):
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
    nuc2_tasks = [t for t in todos if t.get("source_scope") == "nuc2" or t.get("source_host") == HOST]
    wiki_gaps = [t for t in nuc2_tasks if t.get("kind") == "wiki_gap"]
    if wiki_gaps:
        for t in wiki_gaps:
            lines.append(f"- **[{t['severity'].upper()}]** {t['title']} — {t['kind']}")
    else:
        lines.append("- _No open NUC2 issues in current queue_")
    lines.append("")
    lines.append("<!-- END MACHINE MANAGED -->")
    lines.append("")
    lines.append("## Human Notes")
    lines.append("")
    lines.append("<!-- Add notes here — this section is preserved on machine-managed runs -->")
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
        action_items.append(f"- **Dirty on NUC1:** {', '.join(dirty)} — commit or stash")
    if diverged:
        action_items.append(f"- **Diverged on NUC1:** {', '.join(diverged)} — merge or rebase")
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
    lines.append("<!-- Add notes here — this section is preserved on machine-managed runs -->")
    lines.append("")
    lines.append("## See Also")
    lines.append("- [NUC1 Current State](../architecture/nuc1-current-state.md)")
    lines.append("- [NUC2 Current State](../architecture/nuc2-current-state.md)")
    lines.append("- [Slimy KB](../projects/slimy-kb.md)")
    return "\n".join(lines)


def write_harness_candidates(todos: list[dict]) -> bool:
    """Write output/harness_candidates.md for tasks with candidate or emerging promotion status."""
    candidates = [t for t in todos if t.get("promotion_status") in ("candidate", "emerging")]

    lines = []
    lines.append(f"# Harness Candidates — {TIMESTAMP}")
    lines.append("")
    lines.append(f"_Auto-generated by wiki-manager-stage1. Not dispatched._")
    lines.append("")
    lines.append(f"**Total candidates:** {len([t for t in todos if t.get('promotion_status') == 'candidate'])}")
    lines.append(f"**Total emerging:** {len([t for t in todos if t.get('promotion_status') == 'emerging'])}")
    lines.append("")
    lines.append("## Promotion Rules")
    lines.append("")
    lines.append(f"See [_candidate-promotion-rules.md](../wiki/_candidate-promotion-rules.md) for criteria.")
    lines.append("")
    lines.append("## Candidates (meet all promotion criteria)")
    lines.append("")

    candidate_tasks = [t for t in candidates if t.get("promotion_status") == "candidate"]
    emerging_tasks = [t for t in candidates if t.get("promotion_status") == "emerging"]

    if not candidate_tasks and not emerging_tasks:
        lines.append("_No tasks currently meet harness candidate criteria._")
        lines.append("")
        lines.append("Tasks that are `not_candidate` either lack persistence, evidence, or are of a kind that cannot be promoted.")
    else:
        for t in candidate_tasks:
            lines.append(f"### [{t['id']}] {t['title']}")
            lines.append("")
            lines.append(f"- **Project:** {t.get('project', 'unknown')}")
            lines.append(f"- **Severity:** {t['severity']} ({t.get('kind', '?')})")
            lines.append(f"- **Why it matters:** {t.get('reason', 'N/A')}")
            lines.append(f"- **Promotion reason:** {t.get('promotion_reason', 'N/A')}")
            lines.append(f"- **Persistence:** {t.get('occurrence_count', 1)}x")
            lines.append(f"- **Evidence:** {', '.join(t.get('evidence_paths', []) or ['N/A'])}")
            lines.append(f"- **Suggested prompt mode:** {t.get('suggested_prompt_mode', 'auto')}")
            lines.append(f"- **Dispatch blocker:** {t.get('dispatch_blocker') or 'none'}")
            lines.append(f"- **Source:** {t.get('source_host', '?')} ({t.get('source_scope', 'unknown')})")
            # Related wiki pages
            proj = t.get("project", "")
            if proj:
                page = find_project_page(proj)
                if page:
                    lines.append(f"- **Related wiki page:** {page.name}")
            lines.append("")

        if emerging_tasks:
            lines.append("## Emerging (some signals, not yet promoted)")
            lines.append("")
            for t in emerging_tasks:
                lines.append(f"### [{t['id']}] {t['title']}")
                lines.append("")
                lines.append(f"- **Project:** {t.get('project', 'unknown')}")
                lines.append(f"- **Severity:** {t['severity']} ({t.get('kind', '?')})")
                lines.append(f"- **Why it matters:** {t.get('reason', 'N/A')}")
                lines.append(f"- **Promotion status:** {t.get('promotion_status')} — {t.get('promotion_reason', 'N/A')}")
                lines.append(f"- **Persistence:** {t.get('occurrence_count', 1)}x")
                lines.append(f"- **Evidence:** {', '.join(t.get('evidence_paths', []) or ['N/A'])}")
                lines.append("")

    lines.append("---")
    lines.append("_Stage 1.8 does not dispatch harness jobs. Candidate status is recorded but dispatch is blocked by `advisory_only`._")

    HARNESS_CANDIDATES_MD.parent.mkdir(parents=True, exist_ok=True)
    HARNESS_CANDIDATES_MD.write_text("\n".join(lines))
    return bool(candidates)


def write_manager_status(todos, backend, nuc1_used, nuc1_info, state_map, nuc2_state_md_for_status="", updated_project_pages: list[str] = None):
    by_kind = {}
    by_state = {"new": 0, "persisting": 0, "resolved": 0}
    by_promotion = {"candidate": 0, "emerging": 0, "not_candidate": 0}
    harness_candidates = []
    for t in todos:
        by_kind.setdefault(t["kind"], []).append(t)
        by_state[t.get("state", "new")] = by_state.get(t.get("state", "new"), 0) + 1
        prom = t.get("promotion_status", "not_candidate")
        by_promotion[prom] = by_promotion.get(prom, 0) + 1
        if prom in ("candidate", "emerging"):
            harness_candidates.append(t)

    updated_project_pages = updated_project_pages or []

    lines = []
    lines.append(f"# Wiki Manager Status")
    lines.append("")
    lines.append(f"> Category: concepts")
    lines.append(f"> Updated: {TIMESTAMP}")
    lines.append("")
    lines.append(f"**Last run:** {TIMESTAMP}")
    lines.append(f"**Stage:** 1.8")
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
    lines.append(f"- **not_candidate:** {by_promotion.get('not_candidate', 0)}")
    lines.append("")
    lines.append("## By Kind")
    lines.append("")
    for kind, tasks in sorted(by_kind.items()):
        lines.append(f"- **{kind}:** {len(tasks)}")
    lines.append("")
    lines.append("## Stable Pages Updated")
    lines.append("")
    nuc1_updated = "YES" if nuc1_info.get("repos") else "SKIPPED (no NUC1 evidence)"
    lines.append(f"- [nuc1-current-state.md](architecture/nuc1-current-state.md): {nuc1_updated}")
    nuc2_has_state = bool(nuc2_state_md_for_status)
    lines.append(f"- [nuc2-current-state.md](architecture/nuc2-current-state.md): {'YES' if nuc2_has_state else 'SKIPPED (no NUC2 digest)'}")
    lines.append(f"- [repo-health-overview.md](projects/repo-health-overview.md): {'YES' if nuc1_info.get('repos') or nuc2_has_state else 'SKIPPED'}")
    lines.append(f"- [_project-health-index.md](projects/_project-health-index.md): {'YES' if nuc1_info.get('repos') else 'SKIPPED'}")
    lines.append(f"- [_candidate-promotion-rules.md](../wiki/_candidate-promotion-rules.md): YES (always updated)")
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
            lines.append(f"- **[{t['id']}]** {t['title']} (severity: {t['severity']}, promotion: {t.get('promotion_status')})")
        lines.append("")
    lines.append("## Task List")
    lines.append("")
    for t in todos:
        state_icon = {"new": "✨", "persisting": "🔄", "resolved": "✅"}.get(t.get("state", "new"), "•")
        prom = t.get("promotion_status", "")
        prom_str = f" [{prom}]" if prom else ""
        lines.append(f"{state_icon} [{t['id']}] {t['title']} ({t['severity']}, {t['kind']}){prom_str} — {t.get('source_host', '?')}")
    lines.append("")
    lines.append("---")
    lines.append("*Managed by wiki-manager-stage1.timer (every 12h). Do not edit directly.*")

    MANAGER_STATUS.parent.mkdir(parents=True, exist_ok=True)
    with open(MANAGER_STATUS, "w") as f:
        f.write("\n".join(lines))


def write_candidate_rules() -> bool:
    """Write candidate promotion rules page. Always updates (text includes TIMESTAMP)."""
    content = PROMOTION_RULES_CONTENT.replace("_TS_PLACEHOLDER_", TIMESTAMP)
    CANDIDATE_RULES_PAGE.parent.mkdir(parents=True, exist_ok=True)
    existing = CANDIDATE_RULES_PAGE.read_text() if CANDIDATE_RULES_PAGE.exists() else ""
    if existing == content:
        return False
    CANDIDATE_RULES_PAGE.write_text(content)
    return True


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Wiki Manager Stage 1.8 — todo queue + stable wiki pages + project health")
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

    todos, nuc1_info = build_todos(orphans, weak_links, args.nuc1_json, args.nuc1_md, args.backend, args.model)

    history, state_map = update_history(todos)

    # Apply severity and promotion corrections
    for t in todos:
        key = t.get("task_key", task_key(t))
        entry = next((e for e in history["tasks"] if e["task_key"] == key), None)
        occ = entry["occurrence_count"] if entry else 1
        new_sev = compute_severity(t, nuc1_info, occ)
        t["severity"] = new_sev
        t["occurrence_count"] = occ

        # Compute promotion
        prom_status, prom_reason = compute_promotion(t, entry or {})
        t["promotion_status"] = prom_status
        t["promotion_reason"] = prom_reason

        # Set dispatch blocker for candidates if not already set
        if prom_status == "candidate" and not t.get("dispatch_blocker"):
            t["dispatch_blocker"] = "advisory_only"

    with open(TODO_HISTORY, "w") as f:
        json.dump(history, f, indent=2)

    nuc1_used = bool(nuc1_info.get("repos") or nuc1_info.get("dirty_repos"))

    # Write stable wiki pages
    nuc1_written = write_stable_page(NUC1_STATE_PAGE, build_nuc1_state_content(nuc1_info, {}, todos))
    nuc2_written = write_stable_page(NUC2_STATE_PAGE, build_nuc2_state_content(args.nuc2_md, todos))
    repo_written = write_stable_page(REPO_HEALTH_PAGE, build_repo_health_content(nuc1_info, args.nuc2_md))

    # Project health index
    nuc1_repos = nuc1_info.get("repos", [])
    project_health_written = False
    if nuc1_used and nuc1_repos:
        project_health_written = write_stable_page(PROJECT_HEALTH_INDEX, build_project_health_index(nuc1_info, todos, []))

    # Candidate promotion rules
    candidate_rules_written = write_candidate_rules()

    # Project page filing — update project pages that have matching evidence
    updated_project_pages = []
    all_repos_data = nuc1_info.get("repo_details", [])
    if nuc1_used:
        for t in todos:
            proj = t.get("project", "")
            if not proj or proj == "kb":
                continue
            page = find_project_page(proj)
            if page:
                status_block = build_project_status_block(proj, nuc1_info, todos, all_repos_data)
                if update_project_page(page, proj, status_block, todos):
                    updated_project_pages.append(page.name)

    # Build project health index with updated pages list
    if nuc1_used and nuc1_repos:
        health_content = build_project_health_index(nuc1_info, todos, updated_project_pages)
        write_stable_page(PROJECT_HEALTH_INDEX, health_content)

    # Write harness candidates
    harness_written = write_harness_candidates(todos)

    # Write JSON output
    candidate_count = sum(1 for t in todos if t.get("promotion_status") == "candidate")
    emerging_count = sum(1 for t in todos if t.get("promotion_status") == "emerging")
    output = {
        "generated_at": TIMESTAMP,
        "source_host": HOST,
        "backend": args.backend,
        "model": args.model if args.backend == "ollama" else None,
        "stage": "1.8",
        "task_count": len(todos),
        "nuc1_evidence_used": nuc1_used,
        "nuc1_host": nuc1_info.get("nuc1_host", "unknown"),
        "orphan_count": len(orphans),
        "weak_link_count": len(weak_links),
        "promotion_counts": {
            "candidate": candidate_count,
            "emerging": emerging_count,
            "not_candidate": len(todos) - candidate_count - emerging_count
        },
        "stable_pages_written": {
            "nuc1_current_state": nuc1_written,
            "nuc2_current_state": nuc2_written,
            "repo_health_overview": repo_written,
            "project_health_index": project_health_written,
            "candidate_promotion_rules": candidate_rules_written
        },
        "project_pages_updated": updated_project_pages,
        "harness_candidates_written": harness_written,
        "tasks": todos
    }
    with open(TODO_JSON, "w") as f:
        json.dump(output, f, indent=2)

    md = generate_markdown(todos, args.backend, nuc1_used, nuc1_info, state_map)
    with open(TODO_MD, "w") as f:
        f.write(md)

    write_manager_status(todos, args.backend, nuc1_used, nuc1_info, state_map, nuc2_state_md_for_status=args.nuc2_md, updated_project_pages=updated_project_pages)

    print(f"todo_queue.json: {TODO_JSON} ({len(todos)} tasks)")
    print(f"todo_queue.md: {TODO_MD}")
    print(f"todo_history.json: {TODO_HISTORY}")
    print(f"nuc1_evidence_used: {nuc1_used}")
    print(f"Stable pages: nuc1={nuc1_written} nuc2={nuc2_written} repo={repo_written} health={project_health_written} rules={candidate_rules_written}")
    print(f"Project pages updated: {updated_project_pages}")
    print(f"Promotion: candidate={candidate_count} emerging={emerging_count}")
    print(f"Harness candidates: {'YES' if harness_written else 'none'}")
    print(f"Backend: {args.backend}")


if __name__ == "__main__":
    main()
