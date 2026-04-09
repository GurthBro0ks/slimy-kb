#!/usr/bin/env python3
"""
wiki_manager_stage1.py — Stage 1.75 todo queue generator + stable wiki pages.

Improvements over Stage 1.5:
- Generates durable wiki state pages from digest evidence:
    architecture/nuc1-current-state.md
    architecture/nuc2-current-state.md
    projects/repo-health-overview.md
- Machine-managed sections use <!-- BEGIN/END MACHINE MANAGED --> markers
- Noise control: skip write if content has not materially changed
- Human notes sections preserved
- Improved _manager-status.md with stable page list + harness candidates
- Harness candidate drafts surfaced in todo_queue.md and output/harness_candidates.md
- Stage 1.75 is still advisory only: does NOT dispatch harness jobs.
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

# History retention: keep tasks seen in last N runs or 30 days, whichever is smaller
HISTORY_RETENTION_RUNS = 10
HISTORY_RETENTION_DAYS = 30


# ── Parsing helpers ──────────────────────────────────────────────────────────

def parse_orphans(content: str) -> list[str]:
    """Extract orphan page paths from _orphans.md."""
    if not content:
        return []
    orphans = []
    for line in content.splitlines():
        m = re.match(r"^\- \`(.+?\.md)\`", line.strip())
        if m:
            orphans.append(m.group(1))
    return orphans


def parse_weak_links(content: str) -> list[str]:
    """Extract weak-link page paths from _weak-links.md."""
    if not content:
        return []
    weak = []
    for line in content.splitlines():
        m = re.match(r"^\- \`(.+?\.md)\`", line.strip())
        if m:
            weak.append(m.group(1))
    return weak


def parse_nuc1_json(content: str) -> dict:
    """
    Parse NUC1 JSON digest (from inbox-nuc1/*.json).
    Returns dict with keys: repos (list), dirty_repos (list), diverged_repos (list),
    kb_present (bool), nuc1_host (str), ts (str).
    """
    result = {
        "repos": [], "dirty_repos": [], "diverged_repos": [],
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
        if repo.get("dirty"):
            result["dirty_repos"].append(repo["name"])
        ab = repo.get("ahead_behind") or {}
        if ab.get("ahead", 0) > 0 and ab.get("behind", 0) > 0:
            result["diverged_repos"].append(repo["name"])

    return result


def parse_nuc1_markdown(content: str) -> dict:
    """
    Parse NUC1 markdown digest (from inbox-nuc1/*.md).
    Extracts host, uptime, dirty repos mentioned, services.
    """
    result = {
        "nuc1_host": "unknown", "ts": "",
        "dirty_services": [], "active_services": [], "listening_ports": []
    }
    if not content:
        return result

    # Extract hostname from first line: # NUC1 State Digest — 20260409T160301Z
    m = re.search(r"NUC1 State Digest.*?(\d{8}T\d{6}Z)", content)
    if m:
        result["ts"] = m.group(1)

    # Extract hostname from ## Host section
    hm = re.search(r"hostname:\s*(\S+)", content)
    if hm:
        result["nuc1_host"] = hm.group(1)

    # Extract dirty repos (grep for "⚠️" or "dirty")
    for line in content.splitlines():
        if "⚠️" in line or "dirty" in line.lower():
            result["dirty_services"].append(line.strip())

    # Extract active services
    in_services = False
    for line in content.splitlines():
        if "## Active Services" in line or "## Systemd" in line:
            in_services = True
            continue
        if in_services and line.startswith("## "):
            in_services = False
        if in_services and line.strip() and not line.startswith("-"):
            result["active_services"].append(line.strip())

    # Extract ports
    for line in content.splitlines():
        pm = re.findall(r":(\d{4,5})", line)
        for p in pm:
            if 1024 <= int(p) <= 65535:
                result["listening_ports"].append(int(p))

    return result


# ── History management ───────────────────────────────────────────────────────

def load_history() -> dict:
    """Load todo_history.json. Returns empty structure if missing or invalid."""
    if not TODO_HISTORY.exists():
        return {"version": 1, "updated_at": "", "tasks": []}
    try:
        with open(TODO_HISTORY) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"version": 1, "updated_at": "", "tasks": []}


def task_key(task: dict) -> str:
    """
    Generate stable identity key for deduplication.
    Uses: source_host + project + kind + normalized title.
    Normalizes title by lowercasing and removing dates/IDs.
    """
    parts = [
        task.get("source_host", ""),
        task.get("project", ""),
        task.get("kind", ""),
    ]
    title = re.sub(r"\d{4}-\d{2}-\d{2}[-T]\d+", "", task.get("title", "")).lower()
    title = re.sub(r"^\[\S+\]\s*", "", title)  # remove leading [todo-xxx]
    title = re.sub(r"\s+", " ", title).strip()
    parts.append(title)
    return "|".join(parts)


def prune_history(history: dict) -> dict:
    """Remove stale entries beyond retention policy."""
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
    """
    Merge new_tasks into history. Returns (updated_history, state_map).
    state_map: task_key -> "new" | "persisting" | "resolved"
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
            entry["last_seen"] = now
            entry["occurrence_count"] = entry.get("occurrence_count", 1) + 1
            entry["state"] = "persisting"
            # Preserve first_seen
            task["first_seen"] = entry.get("first_seen", now)
            task["occurrence_count"] = entry["occurrence_count"]
            task["state"] = "persisting"
            state_map[key] = "persisting"
        else:
            # New task
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

    # Mark previously-seen tasks not in new_tasks as resolved
    new_keys = {task_key(t) for t in new_tasks}
    for entry in history["tasks"]:
        if entry["task_key"] not in new_keys and entry.get("state") != "resolved":
            entry["state"] = "resolved"

    history["updated_at"] = now
    return history, state_map


# ── Severity heuristics ──────────────────────────────────────────────────────

def compute_severity(task: dict, nuc1_evidence: dict, occurrence_count: int = 1) -> str:
    """
    Compute severity: low / medium / high.

    Severity scoring (bounded, interpretable):
    - Base by kind:
        - wiki_gap: medium (2)
        - repo_drift: medium (2)
        - investigate/harness_candidate: low (1)
    - +1 if persisting (occurrence_count > 1)
    - Cap at "high"

    Special cases:
    - Only cross-NUC KB conflict (kb uncommitted changes) goes to HIGH
    - All others stay within their base tier unless persisting

    This produces meaningful triage:
    - Fresh wiki_gap = medium
    - Persisting wiki_gap = high
    - Fresh repo_drift = medium
    - Persisting repo_drift = high
    - Cross-NUC KB conflict = high (always)
    """
    kind = task.get("kind", "")
    source_scope = task.get("source_scope", "")
    title_lower = task.get("title", "").lower()

    # Base by kind: 0=low, 1=medium, 2=high
    if kind in ("wiki_gap", "doc_drift"):
        severity = 1  # medium
    elif kind == "repo_drift":
        severity = 1  # medium
    else:
        severity = 0  # low for investigate/harness_candidate

    # Special case: cross-NUC KB conflict is always HIGH
    if source_scope == "cross_nuc" and "kb" in title_lower and "uncommitted" in title_lower:
        return "high"

    # +1 for persisting issues (stays within tier unless already at high)
    if occurrence_count > 1:
        severity += 1

    return ["low", "medium", "high"][min(severity, 2)]


# ── Build todos ─────────────────────────────────────────────────────────────

def build_todos(orphans, weak_links, nuc1_json, nuc1_md, backend, model) -> tuple[list[dict], dict]:
    """
    Build todo list from KB state + NUC1 evidence.
    Returns (todos, nuc1_evidence_dict).
    """
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
        })
        task_id += 1

    # Parse NUC1 evidence
    nuc1 = parse_nuc1_json(nuc1_json)
    nuc1_md_parsed = parse_nuc1_markdown(nuc1_md)
    if nuc1_md_parsed.get("nuc1_host") and nuc1_md_parsed["nuc1_host"] != "unknown":
        nuc1["nuc1_host"] = nuc1_md_parsed["nuc1_host"]
    if nuc1_md_parsed.get("ts"):
        nuc1["ts"] = nuc1_md_parsed["ts"]

    nuc1_used = bool(nuc1.get("repos") or nuc1_md_parsed.get("active_services"))

    # ── NUC1-based tasks ───────────────────────────────────────────────────
    if nuc1_used:
        # Dirty repos on NUC1
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

        # Diverged repos on NUC1
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

        # Active services on NUC1 (flag if kb not in active services — might mean KB agent not running)
        active = nuc1_md_parsed.get("active_services", [])
        if active and "openclaw-gateway.service" in str(active):
            notes_parts = []
            services = [s for s in active if "slimy" in s.lower() or "openclaw" in s.lower()]
            if services:
                notes_parts.append(f"NUC1 active services: {', '.join(services[:5])}")

    # ── Orphans — wiki gaps ─────────────────────────────────────────────────
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
        # Individual orphan todos — cap at 5
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

    # ── Weak links ──────────────────────────────────────────────────────────
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

    # ── Cross-NUC signal: NUC1 kb is dirty ──────────────────────────────────
    # If NUC1's kb is dirty, there's uncommitted KB work on NUC1
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

    # ── Stub fallback ────────────────────────────────────────────────────────
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
        })

    return todos, nuc1


# ── Markdown generation ────────────────────────────────────────────────────

def generate_markdown(todos, backend, nuc1_used, nuc1_info, state_map) -> str:
    """Generate human-readable todo_queue.md with NEW/PERSISTING/RESOLVED sections."""
    lines = []
    lines.append(f"# Todo Queue — {TIMESTAMP}")
    lines.append("")
    lines.append(f"**Generated by:** wiki_manager_stage1.py (Stage 1.5)")
    lines.append(f"**Backend:** {backend}")
    lines.append(f"**Host:** {HOST}")
    lines.append(f"**NUC1 evidence consumed:** {'YES' if nuc1_used else 'NO'}")
    if nuc1_info.get("nuc1_host"):
        lines.append(f"**NUC1 host:** {nuc1_info['nuc1_host']} ({nuc1_info.get('ts', 'no ts')})")
    lines.append("")

    # Summary counts
    by_severity = {}
    by_kind = {}
    by_state = {"new": [], "persisting": [], "resolved": []}
    for t in todos:
        by_severity.setdefault(t["severity"], []).append(t)
        by_kind.setdefault(t["kind"], []).append(t)
        by_state.setdefault(t.get("state", "new"), []).append(t)

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Total tasks:** {len(todos)}")
    lines.append(f"- by severity: { {k: len(v) for k, v in by_severity.items()} }")
    lines.append(f"- by kind: { {k: len(v) for k, v in by_kind.items()} }")
    if state_map:
        new_c = sum(1 for s in state_map.values() if s == "new")
        pers_c = sum(1 for s in state_map.values() if s == "persisting")
        lines.append(f"- NEW: {new_c} | PERSISTING: {pers_c}")
    lines.append("")

    # State sections — NEW first, then PERSISTING, then RESOLVED (if any shown)
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
                lines.append(f"- **Reason:** {t['reason']}")
                lines.append(f"- **Recommended Action:** {t['recommended_action']}")
                lines.append(f"- **Prompt Mode:** {t['suggested_prompt_mode']}")
                lines.append(f"- **Safe to Dispatch:** {t['safe_to_dispatch']}")
                lines.append(f"- **Source:** {t['source_host']} ({t.get('source_scope', 'unknown')})")
                if t.get("occurrence_count", 1) > 1:
                    lines.append(f"- **Occurrences:** {t['occurrence_count']}x")
                if t.get("evidence_paths"):
                    lines.append(f"- **Evidence:** {', '.join(t['evidence_paths'])}")
                if t.get("notes"):
                    lines.append(f"- **Notes:** {t['notes']}")
                lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("*Stage 1.75 — advisory only. No harness jobs dispatched.*")

    return "\n".join(lines)


WIKI_ARCH_DIR = Path("/home/slimy/kb/wiki/architecture")
WIKI_PROJ_DIR = Path("/home/slimy/kb/wiki/projects")
NUC1_STATE_PAGE = WIKI_ARCH_DIR / "nuc1-current-state.md"
NUC2_STATE_PAGE = WIKI_ARCH_DIR / "nuc2-current-state.md"
REPO_HEALTH_PAGE = WIKI_PROJ_DIR / "repo-health-overview.md"
HARNESS_CANDIDATES_MD = OUTPUT_DIR / "harness_candidates.md"


def write_stable_page(path: Path, content: str) -> bool:
    """
    Write a stable wiki page only if content has materially changed.
    Returns True if written, False if skipped.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        existing = path.read_text()
        if existing == content:
            return False  # no material change
    path.write_text(content)
    return True


def build_nuc1_state_content(nuc1_json: dict, nuc1_md: dict, todos: list[dict]) -> str:
    """Build architecture/nuc1-current-state.md content."""
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
    all_repos = nuc1_json.get("repos", [])  # list of repo name strings
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
    """Build architecture/nuc2-current-state.md content."""
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
    # Parse services from nuc2_state_md
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
    port_lines = []
    for line in nuc2_state_md.splitlines():
        if any(str(p) in line for p in [3000, 3838, 3850, 18790, 18792, 18793, 5432, 3307]):
            port_lines.append(line.strip())
    for pl in port_lines[:10]:
        lines.append(f"- `{pl}`")
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
    """Build projects/repo-health-overview.md content."""
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
    nuc1_repos = nuc1_json.get("repos", [])  # list of repo name strings
    dirty = nuc1_json.get("dirty_repos", [])
    diverged = nuc1_json.get("diverged_repos", [])
    if nuc1_repos:
        lines.append(f"| Repo | Dirty | Diverged |")
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
    """Write output/harness_candidates.md for tasks that are harness_candidate kind.
    Returns True if written, False if no candidates.
    """
    candidates = [t for t in todos if t.get("kind") == "harness_candidate"]
    if not candidates:
        return False

    lines = []
    lines.append(f"# Harness Candidates — {TIMESTAMP}")
    lines.append("")
    lines.append(f"_Auto-generated by wiki-manager-stage1. Not dispatched._")
    lines.append("")
    lines.append(f"**Total candidates:** {len(candidates)}")
    lines.append("")

    for t in candidates:
        lines.append(f"## [{t['id']}] {t['title']}")
        lines.append("")
        lines.append(f"- **Severity:** {t['severity']}")
        lines.append(f"- **Kind:** {t['kind']}")
        lines.append(f"- **Source:** {t.get('source_host', 'unknown')} ({t.get('source_scope', 'unknown')})")
        lines.append(f"- **Why it matters:** {t.get('reason', 'N/A')}")
        lines.append(f"- **Evidence:** {', '.join(t.get('evidence_paths', [])) or 'N/A'}")
        lines.append(f"- **Suggested prompt mode:** {t.get('suggested_prompt_mode', 'auto')}")
        lines.append(f"- **Dispatch blocker:** {t.get('dispatch_blocker', 'advisory_only — Stage 1.75 does not dispatch')}")
        if t.get("recommended_action"):
            lines.append(f"- **Recommended action:** {t['recommended_action']}")
        lines.append("")

    lines.append("---")
    lines.append("_Do not dispatch manually — this output is advisory. Stage 2 will handle actual dispatch._")

    HARNESS_CANDIDATES_MD.parent.mkdir(parents=True, exist_ok=True)
    HARNESS_CANDIDATES_MD.write_text("\n".join(lines))
    return True


def write_manager_status(todos, backend, nuc1_used, nuc1_info, state_map, nuc2_state_md_for_status=""):
    """Write _manager-status.md wiki page with stable pages list and harness candidates."""
    by_kind = {}
    by_state = {"new": 0, "persisting": 0, "resolved": 0}
    harness_candidates = []
    for t in todos:
        by_kind.setdefault(t["kind"], []).append(t)
        by_state[t.get("state", "new")] = by_state.get(t.get("state", "new"), 0) + 1
        if t.get("kind") == "harness_candidate":
            harness_candidates.append(t)

    lines = []
    lines.append(f"# Wiki Manager Status")
    lines.append("")
    lines.append(f"> Category: concepts")
    lines.append(f"> Updated: {TIMESTAMP}")
    lines.append("")
    lines.append(f"**Last run:** {TIMESTAMP}")
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
    lines.append("")
    if harness_candidates:
        lines.append("## Harness Candidates")
        lines.append("")
        for t in harness_candidates:
            lines.append(f"- **[{t['id']}]** {t['title']} (severity: {t['severity']})")
        lines.append("")
    lines.append("## Task List")
    lines.append("")
    for t in todos:
        state_icon = {"new": "✨", "persisting": "🔄", "resolved": "✅"}.get(t.get("state", "new"), "•")
        lines.append(f"{state_icon} [{t['id']}] {t['title']} ({t['severity']}, {t['kind']}) — {t.get('source_host', '?')}")
    lines.append("")
    lines.append("---")
    lines.append("*Managed by wiki-manager-stage1.timer (every 12h). Do not edit directly.*")

    MANAGER_STATUS.parent.mkdir(parents=True, exist_ok=True)
    with open(MANAGER_STATUS, "w") as f:
        f.write("\n".join(lines))


# ── Ollama backend ─────────────────────────────────────────────────────────

def call_ollama(model: str, prompt: str) -> str:
    """Call local Ollama API. Returns response text or empty string on failure."""
    payload = {"model": model, "prompt": prompt, "stream": False}
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            "http://127.0.0.1:11434/api/generate",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result.get("response", "").strip()
    except Exception:
        return ""


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Wiki Manager Stage 1.75 — todo queue + stable wiki pages")
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

    # Build todos from KB state + NUC1 evidence
    todos, nuc1_info = build_todos(orphans, weak_links, args.nuc1_json, args.nuc1_md, args.backend, args.model)

    # Deduplicate against history
    history, state_map = update_history(todos)

    # Apply severity corrections using cross-NUC signals
    for t in todos:
        key = t.get("task_key", task_key(t))
        entry = next((e for e in history["tasks"] if e["task_key"] == key), None)
        occ = entry["occurrence_count"] if entry else 1
        new_sev = compute_severity(t, nuc1_info, occ)
        t["severity"] = new_sev

    # Write history
    with open(TODO_HISTORY, "w") as f:
        json.dump(history, f, indent=2)

    nuc1_used = bool(nuc1_info.get("repos") or nuc1_info.get("dirty_repos"))

    # Write stable wiki pages (with noise control — skip if unchanged)
    nuc1_written = write_stable_page(NUC1_STATE_PAGE, build_nuc1_state_content(nuc1_info, {}, todos))
    nuc2_written = write_stable_page(NUC2_STATE_PAGE, build_nuc2_state_content(args.nuc2_md, todos))
    repo_written = write_stable_page(REPO_HEALTH_PAGE, build_repo_health_content(nuc1_info, args.nuc2_md))

    # Write harness candidates
    harness_written = write_harness_candidates(todos)

    # Write JSON output
    output = {
        "generated_at": TIMESTAMP,
        "source_host": HOST,
        "backend": args.backend,
        "model": args.model if args.backend == "ollama" else None,
        "task_count": len(todos),
        "nuc1_evidence_used": nuc1_used,
        "nuc1_host": nuc1_info.get("nuc1_host", "unknown"),
        "orphan_count": len(orphans),
        "weak_link_count": len(weak_links),
        "stable_pages_written": {
            "nuc1_current_state": nuc1_written,
            "nuc2_current_state": nuc2_written,
            "repo_health_overview": repo_written
        },
        "harness_candidates_written": harness_written,
        "tasks": todos
    }
    with open(TODO_JSON, "w") as f:
        json.dump(output, f, indent=2)

    # Write Markdown
    md = generate_markdown(todos, args.backend, nuc1_used, nuc1_info, state_map)
    with open(TODO_MD, "w") as f:
        f.write(md)

    # Write manager status (pass NUC2 digest for stable page tracking)
    write_manager_status(todos, args.backend, nuc1_used, nuc1_info, state_map, nuc2_state_md_for_status=args.nuc2_md)

    print(f"todo_queue.json: {TODO_JSON} ({len(todos)} tasks)")
    print(f"todo_queue.md: {TODO_MD}")
    print(f"todo_history.json: {TODO_HISTORY}")
    print(f"nuc1_evidence_used: {nuc1_used}")
    print(f"Stable pages: nuc1={nuc1_written} nuc2={nuc2_written} repo={repo_written}")
    print(f"Harness candidates: {'YES' if harness_written else 'none'}")
    print(f"Backend: {args.backend}")


if __name__ == "__main__":
    main()
