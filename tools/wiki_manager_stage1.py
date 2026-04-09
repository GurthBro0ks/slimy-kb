#!/usr/bin/env python3
"""
wiki_manager_stage1.py — Generate todo_queue.json + todo_queue.md from KB state.

Stage 1 is advisory only: it reads KB state and produces todo queue files.
It does NOT dispatch harness jobs or modify non-kb repos.

Backend: ollama (local) or stub (always-available fallback).
"""
import json
import sys
import os
import argparse
import re
from datetime import datetime, timezone
from pathlib import Path

TIMESTAMP = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
DATE = TIMESTAMP[:10]
HOST = os.uname()[1]
OUTPUT_DIR = Path("/home/slimy/kb/output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TODO_JSON = OUTPUT_DIR / "todo_queue.json"
TODO_MD = OUTPUT_DIR / "todo_queue.md"


def parse_orphans(content: str) -> list[str]:
    """Extract orphan page paths from _orphans.md."""
    if not content:
        return []
    orphans = []
    # Match lines like: - `concepts/some-page.md`
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


def build_todos(orphans, weak_links, nuc1_count, nuc1_content, backend, model):
    """
    Build todo list from KB state.
    Returns list of todo dicts.
    """
    todos = []
    task_id = 1

    def add(kind, severity, title, reason, recommended_action, suggested_prompt_mode="manual", safe=True):
        nonlocal task_id
        todos.append({
            "id": f"todo-{DATE}-{task_id:03d}",
            "created_at": TIMESTAMP,
            "source_host": HOST,
            "project": "kb",
            "title": title,
            "kind": kind,
            "severity": severity,
            "reason": reason,
            "recommended_action": recommended_action,
            "suggested_prompt_mode": suggested_prompt_mode,
            "safe_to_dispatch": safe,
            "evidence_paths": [],
            "notes": ""
        })
        task_id += 1

    # Orphans — wiki gaps
    if orphans:
        add(
            kind="wiki_gap",
            severity="medium",
            title=f"Resolve {len(orphans)} orphaned wiki pages",
            reason=f"Orphaned pages have 0 inbound links and are effectively hidden from navigation.",
            recommended_action="Review each orphan: either add links from related pages, merge into existing articles, or delete if redundant.",
            suggested_prompt_mode="plan-build-qa",
            safe=True
        )
        # Add individual orphan todos for high-value ones
        for orphan in orphans[:5]:  # Limit to first 5 to avoid bloat
            add(
                kind="wiki_gap",
                severity="low",
                title=f"Review orphaned page: {orphan}",
                reason=f"Page '{orphan}' has no inbound links.",
                recommended_action=f"Check if {orphan} should be linked from related articles or removed.",
                suggested_prompt_mode="manual",
                safe=True
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
            safe=True
        )

    # NUC1 inbox items present
    if nuc1_count > 0:
        add(
            kind="doc_drift",
            severity="medium",
            title=f"Process {nuc1_count} NUC1 inbox item(s)",
            reason="NUC1 has sent digests to inbox-nuc1 that have not been processed.",
            recommended_action="Read inbox-nuc1 items, extract key findings, and either file to wiki or acknowledge.",
            suggested_prompt_mode="manual",
            safe=True
        )

    # KB age/staleness check
    # Look for articles with "stale" status or old dates
    stale_match = re.findall(r"(?i)status:\s*stale", (orphans + weak_links).__str__())
    if stale_match:
        add(
            kind="doc_drift",
            severity="low",
            title="Some wiki articles may be stale",
            reason="Stale-status articles detected in KB lint output.",
            recommended_action="Review wiki/_stale.md if present, or run wiki status for staleness signals.",
            suggested_prompt_mode="health",
            safe=True
        )

    # Stub todo if nothing else triggered
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
            "notes": f"Backend used: {backend}. NUC1 inbox: {nuc1_count} items."
        })

    return todos


def generate_markdown(todos, backend, nuc1_count):
    """Generate human-readable todo_queue.md."""
    lines = []
    lines.append(f"# Todo Queue — {TIMESTAMP}")
    lines.append("")
    lines.append(f"**Generated by:** wiki_manager_stage1.py")
    lines.append(f"**Backend:** {backend}")
    lines.append(f"**Host:** {HOST}")
    lines.append(f"**NUC1 inbox items:** {nuc1_count}")
    lines.append("")

    # Group by severity
    by_severity = {}
    for t in todos:
        sev = t["severity"]
        by_severity.setdefault(sev, []).append(t)

    for sev in ["high", "medium", "low"]:
        tasks = by_severity.get(sev, [])
        if not tasks:
            continue
        lines.append(f"## {sev.upper()} ({len(tasks)})")
        lines.append("")
        for t in tasks:
            lines.append(f"### [{t['id']}] {t['title']}")
            lines.append("")
            lines.append(f"- **Kind:** {t['kind']}")
            lines.append(f"- **Severity:** {t['severity']}")
            lines.append(f"- **Reason:** {t['reason']}")
            lines.append(f"- **Recommended Action:** {t['recommended_action']}")
            lines.append(f"- **Prompt Mode:** {t['suggested_prompt_mode']}")
            lines.append(f"- **Safe to Dispatch:** {t['safe_to_dispatch']}")
            if t.get("evidence_paths"):
                lines.append(f"- **Evidence:** {', '.join(t['evidence_paths'])}")
            lines.append("")
            lines.append(f"_Source: {t['source_host']} | Created: {t['created_at']}_")
            lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("*This is advisory output from wiki-manager stage 1. No harness jobs have been dispatched.*")

    return "\n".join(lines)


def call_ollama(model: str, prompt: str) -> str:
    """Call local Ollama API. Returns response text or empty string on failure."""
    import urllib.request
    import urllib.error

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

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


def main():
    parser = argparse.ArgumentParser(description="Wiki Manager Stage 1 — todo queue generator")
    parser.add_argument("--orphans", default="")
    parser.add_argument("--weak-links", default="")
    parser.add_argument("--nuc1-count", type=int, default=0)
    parser.add_argument("--nuc1-content", default="")
    parser.add_argument("--backend", default="stub", choices=["ollama", "stub"])
    parser.add_argument("--model", default="qwen2.5:7b")
    args = parser.parse_args()

    orphans = parse_orphans(args.orphans)
    weak_links = parse_weak_links(args.weak_links)

    # Build todos
    todos = build_todos(orphans, weak_links, args.nuc1_count, args.nuc1_content, args.backend, args.model)

    # Optional Ollama enhancement (stub falls back to base todos)
    if args.backend == "ollama":
        prompt = f"""You are a KB analyst. Based on this KB state:
- Orphaned pages ({len(orphans)}): {orphans[:10]}
- Weak-link pages ({len(weak_links)}): {weak_links[:10]}
- NUC1 inbox items: {args.nuc1_count}

Suggest up to 3 high-priority KB maintenance tasks as a JSON array with fields:
id, title, kind (wiki_gap/doc_drift/repo_gap/harness_task/investigate), severity (low/medium/high), reason, recommended_action.

Return ONLY valid JSON array, no markdown formatting."""

        response = call_ollama(args.model, prompt)
        if response:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\[[\s\S]+\]', response)
            if json_match:
                try:
                    ollama_todos = json.loads(json_match.group())
                    # Merge/replace severity if provided
                    for ot in ollama_todos:
                        ot["id"] = f"todo-{DATE}-{len(todos)+1:03d}"
                        ot["created_at"] = TIMESTAMP
                        ot["source_host"] = HOST
                        ot["safe_to_dispatch"] = False
                    todos.extend(ollama_todos)
                except json.JSONDecodeError:
                    pass  # keep base todos

    # Write JSON
    output = {
        "generated_at": TIMESTAMP,
        "source_host": HOST,
        "backend": args.backend,
        "model": args.model if args.backend == "ollama" else None,
        "task_count": len(todos),
        "nuc1_inbox_count": args.nuc1_count,
        "orphan_count": len(orphans),
        "weak_link_count": len(weak_links),
        "tasks": todos
    }

    with open(TODO_JSON, "w") as f:
        json.dump(output, f, indent=2)

    # Write Markdown
    md = generate_markdown(todos, args.backend, args.nuc1_count)
    with open(TODO_MD, "w") as f:
        f.write(md)

    print(f"todo_queue.json: {TODO_JSON} ({len(todos)} tasks)")
    print(f"todo_queue.md: {TODO_MD}")
    print(f"Backend: {args.backend}")


if __name__ == "__main__":
    main()
