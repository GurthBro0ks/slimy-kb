#!/usr/bin/env python3
"""
wiki_manager_stage1.py — Stage 1.5 todo queue generator.

Improvements over Stage 1:
- NUC1 inbox parsed as first-class evidence (markdown + JSON)
- Task deduplication via todo_history.json (bounded retention)
- Task state tracking: new / persisting / resolved
- Cross-NUC evidence incorporated
- Better severity heuristics
- Clearer task kind distinctions
- Human-readable markdown with NEW/PERSISTING/RESOLVED sections

Stage 1.5 is advisory only: does NOT dispatch harness jobs.
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
    - Base: medium for wiki_gap/doc_drift, low for investigate/harness_candidate
    - +1 if persisting across runs (occurrence_count > 1)
    - +1 if cross-NUC signal (source_scope == "cross_nuc")
    - +1 if it's the shared KB repo with uncommitted changes (specific cross-NUC risk)
    - Cap at "high"

    This produces meaningful triage: fresh wiki gaps=medium, persisting=high;
    diverged repos=medium, dirty shared KB=high.
    """
    kind = task.get("kind", "")
    source_scope = task.get("source_scope", "")
    project = task.get("project", "")
    title_lower = task.get("title", "").lower()

    # Base by kind
    if kind in ("wiki_gap", "doc_drift"):
        severity = 2  # medium
    elif kind == "repo_drift":
        severity = 1  # low-to-medium for repo issues initially
    else:
        severity = 1  # low for investigate/harness_candidate

    # +1 for persisting issues
    if occurrence_count > 1:
        severity += 1

    # +1 for cross-NUC signals
    if source_scope == "cross_nuc":
        severity += 1

    # +1 for the shared KB having uncommitted changes (high-value cross-NUC signal)
    if "kb" in title_lower and "uncommitted" in title_lower:
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
    lines.append("*Stage 1.5 — advisory only. No harness jobs dispatched.*")

    return "\n".join(lines)


def write_manager_status(todos, backend, nuc1_used, nuc1_info, state_map):
    """Write optional _manager-status.md wiki page."""
    by_kind = {}
    by_state = {"new": 0, "persisting": 0, "resolved": 0}
    for t in todos:
        by_kind.setdefault(t["kind"], []).append(t)
        by_state[t.get("state", "new")] = by_state.get(t.get("state", "new"), 0) + 1

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
    parser = argparse.ArgumentParser(description="Wiki Manager Stage 1.5 — todo queue generator")
    parser.add_argument("--orphans", default="")
    parser.add_argument("--weak-links", default="")
    parser.add_argument("--nuc1-json", default="")
    parser.add_argument("--nuc1-md", default="")
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
        base_sev = t.get("severity", "medium")
        # Re-score if we have better info
        new_sev = compute_severity(t, nuc1_info, occ)
        t["severity"] = new_sev

    # Write history (before we add tasks to it — history is source of truth for state)
    with open(TODO_HISTORY, "w") as f:
        json.dump(history, f, indent=2)

    nuc1_used = bool(nuc1_info.get("repos") or nuc1_info.get("dirty_repos"))

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
        "tasks": todos
    }
    with open(TODO_JSON, "w") as f:
        json.dump(output, f, indent=2)

    # Write Markdown
    md = generate_markdown(todos, args.backend, nuc1_used, nuc1_info, state_map)
    with open(TODO_MD, "w") as f:
        f.write(md)

    # Write optional manager status
    write_manager_status(todos, args.backend, nuc1_used, nuc1_info, state_map)

    print(f"todo_queue.json: {TODO_JSON} ({len(todos)} tasks)")
    print(f"todo_queue.md: {TODO_MD}")
    print(f"todo_history.json: {TODO_HISTORY}")
    print(f"nuc1_evidence_used: {nuc1_used}")
    print(f"Backend: {args.backend}")


if __name__ == "__main__":
    main()
