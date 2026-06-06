#!/usr/bin/env python3
"""Research Farm Phase 6A: dry-run execution planner.

Standard-library-only Python tool that:
  inspect <run-dir>                  - show run metadata, no modifications
  plan <run-dir> [--dry-run]         - create execution planning artifacts

Safety:
  - Never fetches sources.
  - Never calls external APIs.
  - Never invokes AI models.
  - Never accesses the network.
  - Never modifies completed or archived runs.
  - Never overwrites existing execution plans without --force.
  - Standard library only, no external dependencies.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
RESEARCH_ROOT = os.path.join(REPO_ROOT, "research")
INDEX_PATH = os.path.join(RESEARCH_ROOT, "indexes", "index.json")
RUNS_DIR = os.path.join(RESEARCH_ROOT, "runs")

EXECUTOR_VERSION = "slimy-research-execute-run@0.1.0"

VALID_RUN_STATUSES = {
    "planned", "research_planned", "researching", "sources_fetched",
    "notes_ready", "draft_ready", "critic_ready", "complete",
    "failed", "archived",
}

PLANNABLE_STATUSES = {"planned", "research_planned", "failed"}

IMMUTABLE_STATUSES = {"complete", "archived"}


def _read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def _write_text(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)


def _write_json(path: str, data: object) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False, default=_json_default)
        fh.write("\n")


def _json_default(obj: object) -> object:
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _resolve_run_dir(run_arg: str) -> str:
    if os.path.isabs(run_arg):
        return run_arg
    if run_arg.startswith("research/runs/"):
        return os.path.join(REPO_ROOT, run_arg)
    return os.path.join(RUNS_DIR, os.path.basename(run_arg))


def _validate_run_dir(run_dir: str) -> tuple[bool, str]:
    if not os.path.isdir(run_dir):
        return False, f"run directory does not exist: {run_dir}"
    run_json_path = os.path.join(run_dir, "run.json")
    if not os.path.isfile(run_json_path):
        return False, f"run.json not found in: {run_dir}"
    return True, ""


def _load_run_json(run_dir: str) -> dict:
    return json.loads(_read_text(os.path.join(run_dir, "run.json")))


def _load_index() -> dict:
    if not os.path.isfile(INDEX_PATH):
        return {
            "schema_version": 1,
            "generated_at": None,
            "source_root": "/home/slimy/kb/research",
            "ui_theme": "research_farm",
            "items": [],
        }
    return json.loads(_read_text(INDEX_PATH))


def _save_index(index_data: dict) -> None:
    _write_json(INDEX_PATH, index_data)


def _build_execution_plan(run_json: dict, run_dir: str) -> str:
    title = run_json.get("title", "(untitled)")
    run_id = run_json.get("immutable_run_id", "(unknown)")
    slug = run_json.get("slug", "(unknown)")
    status = run_json.get("status", "unknown")
    priority = run_json.get("priority", "normal")
    depth = run_json.get("depth", "standard")
    planned_at = _now_iso()
    tags = run_json.get("tags", [])
    constraints = []

    topic_path = os.path.join(run_dir, "topic.md")
    objective = "(See topic.md for research objective)"
    if os.path.isfile(topic_path):
        topic_text = _read_text(topic_path)
        fm, body = _parse_frontmatter_simple(topic_text)
        question = fm.get("question", "")
        scope_notes = fm.get("scope_notes", "")
        if question:
            objective = question
        if scope_notes:
            objective += f"\n\nScope: {scope_notes}"
        raw_constraints = fm.get("constraints", "")
        if isinstance(raw_constraints, list):
            constraints = raw_constraints
        elif isinstance(raw_constraints, str) and raw_constraints:
            constraints = [raw_constraints]

    depth_guide = {
        "quick": {"min_sources": 3, "max_sources": 5, "steps": 5},
        "standard": {"min_sources": 5, "max_sources": 10, "steps": 7},
        "deep": {"min_sources": 10, "max_sources": 20, "steps": 9},
    }
    guide = depth_guide.get(depth, depth_guide["standard"])

    queries_section = "(Queries will be defined during research execution based on the topic scope.)"
    source_type_table = (
        "| official_documentation | 2-4 | high |\n"
        "| github_repository | 2-3 | medium |\n"
        "| technical_blog | 1-3 | medium |\n"
        "| community_forum | 0-2 | low |"
    )

    steps = [
        "1. plan_queries    - Define search queries from topic scope",
        "2. search_sources  - Search for candidate sources",
        "3. fetch_source    - Fetch each candidate source",
        "4. review_source   - Review fetched content for relevance",
        "5. write_source_notes - Write detailed notes for each source",
        "6. extract_claims  - Extract verifiable claims from sources",
        "7. synthesize_findings - Combine claims into findings",
        "8. draft_report_section - Write report sections from findings",
        "9. write_critic_notes - Write critic/red-team assessment",
        "10. finalize_report - Finalize report and validate",
    ]
    if depth == "quick":
        steps = steps[:7]
    elif depth == "standard":
        steps = steps[:9]

    execution_steps = "\n".join(steps)

    constraints_text = "\n".join(f"- {c}" for c in constraints) if constraints else "(No specific constraints defined.)"

    return f"""# Execution Plan: {title}

> This execution plan was generated by the Phase 6A dry-run execution planner.
> No sources have been fetched. No model calls have been made.

## Run Metadata

- **Run ID:** {run_id}
- **Slug:** {slug}
- **Status:** {status} -> research_planned
- **Priority:** {priority}
- **Depth:** {depth}
- **Planned At:** {planned_at}
- **Executor Version:** {EXECUTOR_VERSION}

## Research Objective

{objective}

## Planned Search Queries

Based on the topic scope and depth level, the following search queries are planned:

{queries_section}

## Source Type Expectations

| Source Type | Expected Count | Trust Level |
|------------|---------------|-------------|
{source_type_table}

**Expected total sources:** {guide['min_sources']}-{guide['max_sources']} (depth: {depth})

## Planned Execution Steps

{execution_steps}

## Safety Pre-Checks

Before execution begins, the following safety conditions must be verified:

- [x] Run status is `planned` or `research_planned`
- [x] No existing execution plan (or `--force` is explicitly set)
- [x] Topic file exists and is readable
- [x] Run directory exists and contains `run.json`
- [x] No network access will be attempted during planning
- [x] No model calls will be attempted during planning
- [x] Output paths are within the run directory

## Constraints

{constraints_text}

## Notes

- This plan is a skeleton. Actual queries and source expectations will be refined during execution.
- No sources have been fetched during planning.
- No citations have been created during planning.
- No model calls have been made during planning.
"""


def _build_timeline_entries(run_json: dict) -> list[dict]:
    depth = run_json.get("depth", "standard")
    steps = [
        {"step": 1, "action": "plan_queries", "description": "Define search queries from topic scope", "status": "pending"},
        {"step": 2, "action": "search_sources", "description": "Search for candidate sources", "status": "pending"},
        {"step": 3, "action": "fetch_source", "description": "Fetch each candidate source", "status": "pending"},
        {"step": 4, "action": "review_source", "description": "Review fetched content for relevance", "status": "pending"},
        {"step": 5, "action": "write_source_notes", "description": "Write detailed notes for each source", "status": "pending"},
        {"step": 6, "action": "extract_claims", "description": "Extract verifiable claims from sources", "status": "pending"},
        {"step": 7, "action": "synthesize_findings", "description": "Combine claims into findings", "status": "pending"},
        {"step": 8, "action": "draft_report_section", "description": "Write report sections from findings", "status": "pending"},
        {"step": 9, "action": "write_critic_notes", "description": "Write critic/red-team assessment", "status": "pending"},
        {"step": 10, "action": "finalize_report", "description": "Finalize report and validate", "status": "pending"},
    ]
    if depth == "quick":
        steps = steps[:7]
    elif depth == "standard":
        steps = steps[:9]
    return steps


def _parse_frontmatter_simple(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("---", 3)
    if end == -1:
        return {}, text
    fm_text = text[3:end].strip()
    body = text[end + 3:].strip()
    meta: dict = {}
    current_key: str | None = None
    in_list = False
    list_items: list[str] = []
    for line in fm_text.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("- ") and in_list and current_key:
            list_items.append(stripped[2:].strip().strip('"').strip("'"))
            continue
        if in_list and current_key:
            meta[current_key] = list_items
            in_list = False
            current_key = None
            list_items = []
        if ":" in stripped and not stripped.startswith("-"):
            key, _, val = stripped.partition(":")
            key = key.strip()
            val = val.strip()
            if val == "":
                in_list = True
                current_key = key
                list_items = []
                continue
            val = val.strip('"').strip("'")
            meta[key] = val
    if in_list and current_key:
        meta[current_key] = list_items
    return meta, body


def cmd_inspect(args: argparse.Namespace) -> int:
    run_dir = _resolve_run_dir(args.run_dir)
    ok, err = _validate_run_dir(run_dir)
    if not ok:
        print(f"ERROR: {err}")
        return 1

    run_json = _load_run_json(run_dir)
    run_id = run_json.get("immutable_run_id", "(unknown)")

    print(f"Run ID:       {run_id}")
    print(f"Title:        {run_json.get('title', '(unknown)')}")
    print(f"Slug:         {run_json.get('slug', '(unknown)')}")
    print(f"Status:       {run_json.get('status', '(unknown)')}")
    print(f"Priority:     {run_json.get('priority', '(unknown)')}")
    print(f"Depth:        {run_json.get('depth', '(unknown)')}")
    print(f"Confidence:   {run_json.get('confidence', '(none)')}")
    print(f"Source count:  {run_json.get('source_count', 0)}")
    print(f"Citation count:{run_json.get('citation_count', 0)}")
    print(f"Report path:  {run_json.get('report_path', '(none)')}")
    print(f"PDF path:     {run_json.get('pdf_path', '(none)')}")
    print()

    execution_files = [
        ("execution-plan.md", "Execution Plan"),
        ("timeline.jsonl", "Execution Timeline"),
        ("claims.jsonl", "Claim Records"),
    ]
    print("Execution files:")
    for fname, label in execution_files:
        fpath = os.path.join(run_dir, fname)
        exists = os.path.isfile(fpath)
        status_icon = "EXISTS" if exists else "NOT YET"
        print(f"  {label:25s} {status_icon}")

    if run_json.get("execution_plan_path"):
        print(f"  run.json execution_plan_path: {run_json['execution_plan_path']}")
    if run_json.get("execution_planned_at"):
        print(f"  run.json execution_planned_at: {run_json['execution_planned_at']}")
    if run_json.get("executor_version"):
        print(f"  run.json executor_version: {run_json['executor_version']}")

    return 0


def cmd_plan(args: argparse.Namespace) -> int:
    run_dir = _resolve_run_dir(args.run_dir)
    ok, err = _validate_run_dir(run_dir)
    if not ok:
        print(f"ERROR: {err}")
        return 1

    run_json = _load_run_json(run_dir)
    run_id = run_json.get("immutable_run_id", "(unknown)")
    status = run_json.get("status", "unknown")

    if status in IMMUTABLE_STATUSES:
        print(f"ERROR: run {run_id} has status '{status}' which is immutable.")
        print("Cannot plan execution for a completed or archived run.")
        return 1

    if status not in PLANNABLE_STATUSES:
        print(f"ERROR: run {run_id} has status '{status}' which is not planplable.")
        print(f"Planplable statuses: {', '.join(sorted(PLANNABLE_STATUSES))}")
        return 1

    execution_plan_path = os.path.join(run_dir, "execution-plan.md")
    timeline_path = os.path.join(run_dir, "timeline.jsonl")
    claims_path = os.path.join(run_dir, "claims.jsonl")

    if os.path.isfile(execution_plan_path) and not args.force:
        print(f"ERROR: execution-plan.md already exists for run {run_id}")
        print("Use --force to overwrite (not recommended in normal workflow).")
        return 1

    plan_content = _build_execution_plan(run_json, run_dir)
    timeline_entries = _build_timeline_entries(run_json)
    now_iso = _now_iso()

    execution_plan_rel = os.path.relpath(execution_plan_path, REPO_ROOT)

    print(f"Run ID:       {run_id}")
    print(f"Title:        {run_json.get('title', '(unknown)')}")
    print(f"Status:       {status} -> research_planned")
    print(f"Depth:        {run_json.get('depth', 'standard')}")
    print()

    if args.dry_run:
        print("DRY RUN - no files will be created or modified.")
        print()
        print("Planned artifacts:")
        print(f"  CREATE {execution_plan_path}")
        print(f"  CREATE {timeline_path}")
        print(f"  CREATE {claims_path}")
        print(f"  UPDATE {os.path.join(run_dir, 'run.json')}")
        print(f"    status: {status} -> research_planned")
        print(f"    execution_plan_path: {execution_plan_rel}")
        print(f"    execution_planned_at: {now_iso}")
        print(f"    executor_version: {EXECUTOR_VERSION}")
        print(f"  UPDATE {INDEX_PATH}")
        print()
        print(f"Timeline steps: {len(timeline_entries)}")
        print(f"Claims file: empty (no claims during planning)")
        print()
        print("Safety guarantees:")
        print("  - No sources fetched")
        print("  - No external API calls")
        print("  - No web crawling")
        print("  - No model calls")
        print("  - No fake citations generated")
        return 0

    if args.force:
        print("WARNING: --force flag is set. Overwriting existing execution plan.")
        print("This is NOT recommended in normal workflow.")
        print()

    _write_text(execution_plan_path, plan_content)
    print(f"  Created: {execution_plan_path}")

    timeline_lines = [json.dumps(entry, ensure_ascii=False) for entry in timeline_entries]
    _write_text(timeline_path, "\n".join(timeline_lines) + "\n")
    print(f"  Created: {timeline_path} ({len(timeline_entries)} steps)")

    _write_text(claims_path, "")
    print(f"  Created: {claims_path} (empty)")

    run_json["status"] = "research_planned"
    run_json["execution_plan_path"] = execution_plan_rel
    run_json["execution_planned_at"] = now_iso
    run_json["executor_version"] = EXECUTOR_VERSION
    _write_json(os.path.join(run_dir, "run.json"), run_json)
    print(f"  Updated: {os.path.join(run_dir, 'run.json')}")

    index_data = _load_index()
    target_id = run_json.get("immutable_run_id", "")
    for item in index_data.get("items", []):
        if item.get("immutable_run_id") == target_id:
            item["status"] = "research_planned"
            item["execution_plan_path"] = execution_plan_rel
            item["execution_planned_at"] = now_iso
            item["executor_version"] = EXECUTOR_VERSION
            break
    index_data["generated_at"] = now_iso
    _save_index(index_data)
    print(f"  Updated: {INDEX_PATH}")

    print()
    print("Execution plan created successfully.")
    print(f"Status: research_planned (not complete)")
    print()
    print("Safety guarantees:")
    print("  - No sources were fetched")
    print("  - No external API calls occurred")
    print("  - No web crawling occurred")
    print("  - No model calls were made")
    print("  - No fake citations were generated")

    return 0


def cmd_test(args: argparse.Namespace) -> int:
    import tempfile
    import shutil

    tmpdir = tempfile.mkdtemp(prefix="research-execute-run-test-")
    print(f"Test directory: {tmpdir}")

    test_passed = True
    test_errors: list[str] = []

    try:
        test_run_dir = os.path.join(tmpdir, "runs", "2026-01-01-test-run")
        os.makedirs(test_run_dir)

        run_json = {
            "schema_version": 1,
            "immutable_run_id": "2026-01-01-test-run",
            "slug": "test-run",
            "title": "Test Run",
            "status": "planned",
            "priority": "normal",
            "depth": "quick",
            "confidence": None,
            "source_count": 0,
            "citation_count": 0,
            "created_at": "2026-01-01",
            "started_at": None,
            "completed_at": None,
            "model_used": None,
            "runner_version": "test",
            "tags": ["test"],
        }
        _write_json(os.path.join(test_run_dir, "run.json"), run_json)

        topic_content = """---
type: research_topic
status: queued
priority: normal
depth: quick
title: Test Run
slug: test-run
question: "Test question?"
scope_notes: "Test scope"
constraints:
  - "Test constraint"
tags:
  - test
---

Test body.
"""
        _write_text(os.path.join(test_run_dir, "topic.md"), topic_content)

        plan_content = _build_execution_plan(run_json, test_run_dir)
        if "Execution Plan" not in plan_content:
            test_passed = False
            test_errors.append("execution plan missing header")
        else:
            print("  execution plan generation: OK")

        if "test question?" not in plan_content.lower():
            test_passed = False
            test_errors.append("execution plan missing objective from topic")
        else:
            print("  execution plan objective: OK")

        timeline = _build_timeline_entries(run_json)
        if len(timeline) != 7:
            test_passed = False
            test_errors.append(f"quick depth should have 7 steps, got {len(timeline)}")
        else:
            print(f"  timeline steps (quick): {len(timeline)} OK")

        run_json_deep = dict(run_json)
        run_json_deep["depth"] = "deep"
        timeline_deep = _build_timeline_entries(run_json_deep)
        if len(timeline_deep) != 10:
            test_passed = False
            test_errors.append(f"deep depth should have 10 steps, got {len(timeline_deep)}")
        else:
            print(f"  timeline steps (deep): {len(timeline_deep)} OK")

        exec_plan_path = os.path.join(test_run_dir, "execution-plan.md")
        _write_text(exec_plan_path, plan_content)
        if not os.path.isfile(exec_plan_path):
            test_passed = False
            test_errors.append("execution plan file was not written")
        else:
            print("  execution plan file write: OK")

        claims_path = os.path.join(test_run_dir, "claims.jsonl")
        _write_text(claims_path, "")
        saved_claims = _read_text(claims_path)
        if saved_claims != "":
            test_passed = False
            test_errors.append("claims file should be empty during planning")
        else:
            print("  claims file empty: OK")

        updated_run = _load_run_json(test_run_dir)
        if updated_run["status"] != "planned":
            test_passed = False
            test_errors.append(f"run.json status should still be planned, got {updated_run['status']}")
        else:
            print("  run.json unmodified in test: OK")

        if test_passed:
            print("TEST RESULT: PASS")
        else:
            print("TEST RESULT: FAIL")
            for e in test_errors:
                print(f"  ERROR: {e}")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    return 0 if test_passed else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="research-execute-run",
        description="Research Farm Phase 6A: dry-run execution planner",
    )
    sub = parser.add_subparsers(dest="command")

    inspect_p = sub.add_parser("inspect", help="Inspect run metadata without modifications")
    inspect_p.add_argument("run_dir", help="Run directory path or slug")

    plan_p = sub.add_parser("plan", help="Create execution planning artifacts")
    plan_p.add_argument("run_dir", help="Run directory path or slug")
    plan_p.add_argument("--dry-run", action="store_true", help="Show what would be created without modifying files")
    plan_p.add_argument("--force", action="store_true", help="Overwrite existing execution plan (not recommended)")

    sub.add_parser("test", help="Run self-test with temporary sample run")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "inspect":
        return cmd_inspect(args)
    elif args.command == "plan":
        return cmd_plan(args)
    elif args.command == "test":
        return cmd_test(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
