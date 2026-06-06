#!/usr/bin/env python3
"""Research Farm Phase 2: seed-to-run lifecycle planner.

Standard-library-only Python tool that:
  list                          - list queued topic seeds
  plan <topic>                  - validate frontmatter, show planned run
  create-run <topic> [--dry-run] [--allow-nonqueued]
                                - create an immutable run skeleton

Safety:
  - Never overwrites existing runs.
  - Never restarts services.
  - Never touches Habitat code.
  - Never calls external APIs.
  - Never pushes git changes.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import shutil
import sys
import uuid

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
RESEARCH_ROOT = os.path.join(REPO_ROOT, "research")
INDEX_PATH = os.path.join(RESEARCH_ROOT, "indexes", "index.json")
TOPICS_DIR = os.path.join(RESEARCH_ROOT, "topics")
RUNS_DIR = os.path.join(RESEARCH_ROOT, "runs")

REQUIRED_FRONTMATTER_KEYS = [
    "type", "status", "priority", "depth", "output", "title", "slug",
    "created_by", "created_at", "audience", "visibility", "tags",
    "seed_kind", "question", "scope_notes", "constraints",
    "related_projects", "assigned_critter", "campaign",
    "claim_token", "claimed_at",
]

VALID_STATUSES = {"queued", "running", "complete", "failed", "archived"}
VALID_PRIORITIES = {"low", "normal", "high", "urgent"}
VALID_DEPTHS = {"quick", "standard", "deep"}

RUNNER_VERSION = "slimy-research-plan-run@0.1.0"


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


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("---", 3)
    if end == -1:
        return {}, text
    import yaml  # type: ignore[import-not-found]  # stdlib yaml may not exist
    fm_text = text[3:end].strip()
    body = text[end + 3:].strip()
    try:
        data = yaml.safe_load(fm_text)
    except Exception:
        return {}, text
    if not isinstance(data, dict):
        return {}, text
    return data, body


def _parse_frontmatter_no_yaml(text: str) -> tuple[dict, str]:
    """Parse YAML frontmatter using only stdlib (no yaml import)."""
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


def _try_parse_frontmatter(text: str) -> tuple[dict, str]:
    try:
        import yaml
        return _parse_frontmatter(text)
    except ImportError:
        return _parse_frontmatter_no_yaml(text)


def _resolve_topic_path(topic_arg: str) -> str:
    if os.path.isfile(topic_arg):
        return os.path.abspath(topic_arg)
    candidate = os.path.join(TOPICS_DIR, os.path.basename(topic_arg))
    if os.path.isfile(candidate):
        return candidate
    if not topic_arg.endswith(".md"):
        candidate_md = candidate + ".md"
        if os.path.isfile(candidate_md):
            return candidate_md
    raise FileNotFoundError(f"Topic file not found: {topic_arg}")


def _validate_frontmatter(fm: dict) -> list[str]:
    errors: list[str] = []
    for key in REQUIRED_FRONTMATTER_KEYS:
        if key not in fm:
            errors.append(f"missing required frontmatter key: {key}")
    if "type" in fm and fm["type"] != "research_topic":
        errors.append(f"frontmatter 'type' must be 'research_topic', got {fm['type']!r}")
    if "status" in fm and fm["status"] not in VALID_STATUSES:
        errors.append(f"frontmatter 'status' must be one of {VALID_STATUSES}, got {fm['status']!r}")
    if "priority" in fm and fm["priority"] not in VALID_PRIORITIES:
        errors.append(f"frontmatter 'priority' must be one of {VALID_PRIORITIES}, got {fm['priority']!r}")
    if "depth" in fm and fm["depth"] not in VALID_DEPTHS:
        errors.append(f"frontmatter 'depth' must be one of {VALID_DEPTHS}, got {fm['depth']!r}")
    if "visibility" in fm and fm["visibility"] != "owner":
        errors.append(f"frontmatter 'visibility' must be 'owner', got {fm['visibility']!r}")
    return errors


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


def _build_run_id(slug: str) -> str:
    today = datetime.date.today().isoformat()
    return f"{today}-{slug}"


def _build_run_dir(run_id: str) -> str:
    return os.path.join(RUNS_DIR, run_id)


def _topic_rel_path(abs_path: str) -> str:
    return os.path.relpath(abs_path, REPO_ROOT)


def _run_rel_path(abs_path: str) -> str:
    return os.path.relpath(abs_path, REPO_ROOT)


def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _build_run_json(fm: dict, run_id: str, topic_rel: str, run_dir: str) -> dict:
    return {
        "schema_version": 1,
        "immutable_run_id": run_id,
        "slug": fm.get("slug", ""),
        "title": fm.get("title", ""),
        "status": "planned",
        "priority": fm.get("priority", "normal"),
        "depth": fm.get("depth", "standard"),
        "confidence": None,
        "source_count": 0,
        "citation_count": 0,
        "created_at": fm.get("created_at", None),
        "started_at": None,
        "completed_at": None,
        "model_used": None,
        "runner_version": RUNNER_VERSION,
        "pdf_path": None,
        "report_path": _run_rel_path(os.path.join(run_dir, "report.md")),
        "critic_path": _run_rel_path(os.path.join(run_dir, "critic.md")),
        "proof_path": _run_rel_path(run_dir),
        "topic_path": topic_rel,
        "tags": fm.get("tags", []),
        "related_harness_session": None,
        "related_guild_campaign": None,
        "assigned_critter": fm.get("assigned_critter", "") or None,
        "source_topic_path": topic_rel,
    }


def _build_index_entry(run_json: dict) -> dict:
    entry: dict = {}
    for key in [
        "slug", "title", "status", "priority", "depth",
        "confidence", "source_count", "citation_count",
        "created_at", "started_at", "completed_at",
        "model_used", "runner_version",
        "pdf_path", "report_path", "critic_path", "proof_path", "topic_path",
        "tags",
        "related_harness_session", "related_guild_campaign",
        "assigned_critter", "immutable_run_id",
    ]:
        entry[key] = run_json.get(key)
    return entry


def _placeholder_report(slug: str) -> str:
    return f"""# Research Report: {slug}

> This is a placeholder report skeleton.
> No research has been conducted yet.
> Do NOT mark this run as complete.

## Status

PLANNED - awaiting research execution.

## Findings

(No findings yet.)

## Recommendations

(No recommendations yet.)
"""


def _placeholder_plan(slug: str) -> str:
    return f"""# Research Plan: {slug}

> This is a placeholder plan skeleton.
> No research execution has started.

## Objective

(To be filled when research begins.)

## Approach

(To be filled when research begins.)

## Steps

1. Define search queries
2. Fetch and review sources
3. Synthesize findings
4. Write report
5. Write critic notes
"""


def _placeholder_slides(slug: str) -> str:
    return f"""# Presentation Slides: {slug}

> This is a placeholder slides skeleton.
> No research has been conducted yet.

## Slide 1: Title

{slug}

## Slide 2: Key Findings

(No findings yet.)

## Slide 3: Recommendations

(No recommendations yet.)

## Slide 4: Sources

(No sources fetched yet.)
"""


def _placeholder_critic(slug: str) -> str:
    return f"""# Critic Notes: {slug}

> This is a placeholder critic skeleton.
> No research has been conducted yet.

## Strengths

(To be evaluated after research.)

## Weaknesses

(To be evaluated after research.)

## Red-Team Assessment

(To be evaluated after research.)
"""


def _placeholder_result(run_id: str) -> str:
    return f"""# Result

RESULT=PLANNED
RUN_ID={run_id}

## What this means

This is a Phase 2 lifecycle skeleton created by the seed-to-run planner.

- No web research has been run yet.
- No sources fetched yet.
- No report has been written yet.
- No PDF has been generated yet.
- No model was used for research.

This run folder exists only as a skeleton ready for a future research execution phase.

## Lifecycle

- Status: planned
- Created by: {RUNNER_VERSION}
- This RESULT.md will be updated when research is actually executed.
"""


def _placeholder_readme(label: str) -> str:
    return f"""# {label}

This directory is a placeholder created by the Phase 2 seed-to-run planner.

Contents will be populated during future research execution.
"""


def _build_queries_template() -> list[dict]:
    return [
        {"query": "", "purpose": "placeholder", "status": "pending"},
    ]


def _build_sources_template() -> list[str]:
    return [
        '{"url": "", "title": "", "fetched_at": null, "status": "pending"}',
    ]


def cmd_list(args: argparse.Namespace) -> int:
    if not os.path.isdir(TOPICS_DIR):
        print("ERROR: topics directory not found")
        return 1
    topics = sorted(
        f for f in os.listdir(TOPICS_DIR)
        if f.endswith(".md")
        and os.path.isfile(os.path.join(TOPICS_DIR, f))
        and not f.startswith("README")
    )
    if not topics:
        print("No topic seeds found in research/topics/")
        return 0
    print(f"{'Slug':<45} {'Title':<40} {'Status':<10} {'Priority':<10} {'Depth':<10}")
    print("-" * 115)
    for fname in topics:
        path = os.path.join(TOPICS_DIR, fname)
        text = _read_text(path)
        fm, _ = _try_parse_frontmatter(text)
        slug = fm.get("slug", fname.replace(".md", ""))
        title = fm.get("title", "(no title)")
        status = fm.get("status", "(unknown)")
        priority = fm.get("priority", "(unknown)")
        depth = fm.get("depth", "(unknown)")
        print(f"{slug:<45} {title:<40} {status:<10} {priority:<10} {depth:<10}")
    return 0


def cmd_plan(args: argparse.Namespace) -> int:
    try:
        topic_path = _resolve_topic_path(args.topic)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}")
        return 1
    text = _read_text(topic_path)
    fm, _ = _try_parse_frontmatter(text)
    errors = _validate_frontmatter(fm)
    if errors:
        print("Frontmatter validation FAILED:")
        for err in errors:
            print(f"  - {err}")
        return 1
    slug = fm["slug"]
    run_id = _build_run_id(slug)
    run_dir = _build_run_dir(run_id)
    topic_rel = _topic_rel_path(topic_path)
    print(f"Topic: {topic_rel}")
    print(f"Slug:  {slug}")
    print(f"Title: {fm['title']}")
    print(f"Run folder: research/runs/{run_id}/")
    print(f"Full path:  {run_dir}")
    print()
    print("Expected files in run folder:")
    expected = [
        "topic.md",
        "run.json",
        "plan.md",
        "queries.json",
        "sources.jsonl",
        "notes/README.md",
        "fetched/README.md",
        "report.md",
        "slides.md",
        "critic.md",
        "RESULT.md",
    ]
    for f in expected:
        print(f"  {f}")
    print()
    print(f"Index update: add entry for immutable_run_id={run_id}")
    return 0


def cmd_create_run(args: argparse.Namespace) -> int:
    try:
        topic_path = _resolve_topic_path(args.topic)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}")
        return 1
    text = _read_text(topic_path)
    fm, body = _try_parse_frontmatter(text)
    errors = _validate_frontmatter(fm)
    if errors:
        print("Frontmatter validation FAILED:")
        for err in errors:
            print(f"  - {err}")
        return 1
    slug = fm["slug"]
    status = fm.get("status", "")
    if status != "queued" and not args.allow_nonqueued:
        print(f"ERROR: topic status is '{status}', not 'queued'. Use --allow-nonqueued to override.")
        return 1
    run_id = _build_run_id(slug)
    run_dir = _build_run_dir(run_id)
    topic_rel = _topic_rel_path(topic_path)
    if os.path.exists(run_dir):
        print(f"ERROR: run folder already exists: {run_dir}")
        print("Refusing to overwrite an existing run.")
        return 1
    run_json = _build_run_json(fm, run_id, topic_rel, run_dir)
    print(f"Topic:   {topic_rel}")
    print(f"Slug:    {slug}")
    print(f"Title:   {fm['title']}")
    print(f"Run ID:  {run_id}")
    print(f"Run dir: {run_dir}")
    print(f"Status:  {status} -> planned")
    print()
    if args.dry_run:
        print("DRY RUN - no files will be created.")
        print()
        print("Planned changes:")
        print(f"  CREATE {run_dir}/")
        print(f"  CREATE {run_dir}/topic.md")
        print(f"  CREATE {run_dir}/run.json")
        print(f"  CREATE {run_dir}/plan.md")
        print(f"  CREATE {run_dir}/queries.json")
        print(f"  CREATE {run_dir}/sources.jsonl")
        print(f"  CREATE {run_dir}/notes/README.md")
        print(f"  CREATE {run_dir}/fetched/README.md")
        print(f"  CREATE {run_dir}/report.md")
        print(f"  CREATE {run_dir}/slides.md")
        print(f"  CREATE {run_dir}/critic.md")
        print(f"  CREATE {run_dir}/RESULT.md")
        print(f"  UPDATE {INDEX_PATH}")
        return 0
    os.makedirs(run_dir, exist_ok=False)
    shutil.copy2(topic_path, os.path.join(run_dir, "topic.md"))
    _write_json(os.path.join(run_dir, "run.json"), run_json)
    _write_text(os.path.join(run_dir, "plan.md"), _placeholder_plan(slug))
    _write_json(os.path.join(run_dir, "queries.json"), _build_queries_template())
    _write_text(
        os.path.join(run_dir, "sources.jsonl"),
        "\n".join(_build_sources_template()) + "\n",
    )
    _write_text(os.path.join(run_dir, "notes", "README.md"), _placeholder_readme("Notes"))
    _write_text(os.path.join(run_dir, "fetched", "README.md"), _placeholder_readme("Fetched Sources"))
    _write_text(os.path.join(run_dir, "report.md"), _placeholder_report(slug))
    _write_text(os.path.join(run_dir, "slides.md"), _placeholder_slides(slug))
    _write_text(os.path.join(run_dir, "critic.md"), _placeholder_critic(slug))
    _write_text(os.path.join(run_dir, "RESULT.md"), _placeholder_result(run_id))
    index_data = _load_index()
    entry = _build_index_entry(run_json)
    existing_ids = {
        item.get("immutable_run_id")
        for item in index_data.get("items", [])
        if item.get("immutable_run_id")
    }
    if run_id in existing_ids:
        print(f"WARNING: immutable_run_id {run_id} already in index, skipping duplicate")
    else:
        index_data.setdefault("items", []).append(entry)
    index_data["generated_at"] = _now_iso()
    _save_index(index_data)
    print("Run skeleton created successfully.")
    print(f"Files created in: {run_dir}")
    print(f"Index updated: {INDEX_PATH}")
    return 0


def cmd_test(args: argparse.Namespace) -> int:
    """Run self-test: create a temporary run under /tmp and validate skeleton."""
    global RESEARCH_ROOT, INDEX_PATH, TOPICS_DIR, RUNS_DIR

    import tempfile
    tmpdir = tempfile.mkdtemp(prefix="research-plan-run-test-")
    print(f"Test directory: {tmpdir}")

    orig_research_root = RESEARCH_ROOT
    orig_index_path = INDEX_PATH
    orig_topics_dir = TOPICS_DIR
    orig_runs_dir = RUNS_DIR

    test_research = os.path.join(tmpdir, "research")
    test_topics = os.path.join(test_research, "topics")
    test_runs = os.path.join(test_research, "runs")
    test_indexes = os.path.join(test_research, "indexes")
    os.makedirs(test_topics, exist_ok=True)
    os.makedirs(test_runs, exist_ok=True)
    os.makedirs(test_indexes, exist_ok=True)

    topic_path = os.path.join(test_topics, "test-sample-research.md")
    _write_text(topic_path, _SAMPLE_TEST_TOPIC)
    idx_path = os.path.join(test_indexes, "index.json")
    _write_json(idx_path, {
        "schema_version": 1,
        "generated_at": None,
        "source_root": test_research,
        "ui_theme": "research_farm",
        "items": [],
    })

    RESEARCH_ROOT = test_research
    INDEX_PATH = idx_path
    TOPICS_DIR = test_topics
    RUNS_DIR = test_runs

    test_passed = True
    test_errors: list[str] = []

    try:
        text = _read_text(topic_path)
        fm, _ = _try_parse_frontmatter(text)
        errs = _validate_frontmatter(fm)
        if errs:
            test_passed = False
            test_errors.extend([f"frontmatter: {e}" for e in errs])
        else:
            print("  frontmatter validation: OK")

        slug = fm.get("slug", "unknown")
        run_id = _build_run_id(slug)
        run_dir = os.path.join(test_runs, run_id)
        os.makedirs(run_dir)
        run_json = _build_run_json(fm, run_id, "research/topics/test-sample-research.md", run_dir)
        _write_json(os.path.join(run_dir, "run.json"), run_json)
        _write_text(os.path.join(run_dir, "RESULT.md"), _placeholder_result(run_id))

        rj = json.loads(_read_text(os.path.join(run_dir, "run.json")))
        if rj.get("status") != "planned":
            test_passed = False
            test_errors.append(f"run.json status is {rj.get('status')}, expected 'planned'")
        else:
            print("  run.json status=planned: OK")

        result_text = _read_text(os.path.join(run_dir, "RESULT.md"))
        if "RESULT=PLANNED" not in result_text:
            test_passed = False
            test_errors.append("RESULT.md does not contain RESULT=PLANNED")
        else:
            print("  RESULT.md RESULT=PLANNED: OK")

        index_data = _load_index()
        entry = _build_index_entry(run_json)
        index_data["items"].append(entry)
        _save_index(index_data)

        saved_index = json.loads(_read_text(INDEX_PATH))
        if len(saved_index.get("items", [])) != 1:
            test_passed = False
            test_errors.append(f"index has {len(saved_index.get('items', []))} items, expected 1")
        else:
            print("  index update: OK")

        if test_passed:
            print("TEST RESULT: PASS")
        else:
            print("TEST RESULT: FAIL")
            for e in test_errors:
                print(f"  ERROR: {e}")
    finally:
        RESEARCH_ROOT = orig_research_root
        INDEX_PATH = orig_index_path
        TOPICS_DIR = orig_topics_dir
        RUNS_DIR = orig_runs_dir
        shutil.rmtree(tmpdir, ignore_errors=True)

    return 0 if test_passed else 1


_SAMPLE_TEST_TOPIC = """---
type: research_topic
status: queued
priority: normal
depth: quick
output: report_md
title: Test sample research topic
slug: test-sample-research
created_by: test
created_at: 2026-06-06
audience: technical_owner
visibility: owner
tags:
  - test
seed_kind: one_shot
question: "Test question for self-test"
scope_notes: "Test scope notes"
constraints:
  - "Test constraint"
related_projects:
  - "slimy-kb"
assigned_critter: ""
campaign: "test"
claim_token: ""
claimed_at: ""
---

# Test

This is a test topic for the research-plan-run self-test.
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="research-plan-run",
        description="Research Farm Phase 2: seed-to-run lifecycle planner",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list", help="List research topic seeds")

    plan_p = sub.add_parser("plan", help="Validate topic and show planned run")
    plan_p.add_argument("topic", help="Topic file path or slug")

    create_p = sub.add_parser("create-run", help="Create a run skeleton from a topic")
    create_p.add_argument("topic", help="Topic file path or slug")
    create_p.add_argument("--dry-run", action="store_true", help="Show what would be created without creating files")
    create_p.add_argument("--allow-nonqueued", action="store_true", help="Allow creating run from non-queued topic")

    sub.add_parser("test", help="Run self-test with temporary sample run")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "list":
        return cmd_list(args)
    elif args.command == "plan":
        return cmd_plan(args)
    elif args.command == "create-run":
        return cmd_create_run(args)
    elif args.command == "test":
        return cmd_test(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
