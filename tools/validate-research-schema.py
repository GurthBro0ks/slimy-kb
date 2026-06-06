#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import sys


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
RESEARCH_ROOT = os.path.join(REPO_ROOT, "research")
INDEX_PATH = os.path.join(RESEARCH_ROOT, "indexes", "index.json")

REQUIRED_DIRS = [
    os.path.join(RESEARCH_ROOT, "topics"),
    os.path.join(RESEARCH_ROOT, "runs"),
    os.path.join(RESEARCH_ROOT, "lore"),
    os.path.join(RESEARCH_ROOT, "templates"),
    os.path.join(RESEARCH_ROOT, "indexes"),
    os.path.join(RESEARCH_ROOT, "planning"),
]

REQUIRED_FILES = [
    os.path.join(RESEARCH_ROOT, "README.md"),
    os.path.join(RESEARCH_ROOT, "templates", "research-topic.template.md"),
    os.path.join(RESEARCH_ROOT, "templates", "research-topic.schema.json"),
    os.path.join(RESEARCH_ROOT, "templates", "research-index.schema.json"),
    os.path.join(RESEARCH_ROOT, "planning", "phase-1-index-contract.md"),
    INDEX_PATH,
]

PHASE2_FILES = [
    os.path.join(REPO_ROOT, "tools", "research-plan-run.py"),
    os.path.join(REPO_ROOT, "tools", "research-plan-run.sh"),
    os.path.join(RESEARCH_ROOT, "templates", "run-metadata.schema.json"),
    os.path.join(RESEARCH_ROOT, "templates", "queries.template.json"),
    os.path.join(RESEARCH_ROOT, "templates", "sources.template.jsonl"),
    os.path.join(RESEARCH_ROOT, "planning", "phase-2-seed-to-run-lifecycle.md"),
]

PHASE2_SCHEMA_PATHS = [
    os.path.join(RESEARCH_ROOT, "templates", "run-metadata.schema.json"),
]


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def validate() -> tuple[bool, list[str]]:
    errors: list[str] = []

    if not os.path.isdir(RESEARCH_ROOT):
        errors.append(f"missing research root: {RESEARCH_ROOT}")
        return False, errors

    for directory in REQUIRED_DIRS:
        if not os.path.isdir(directory):
            errors.append(f"missing directory: {directory}")

    for file_path in REQUIRED_FILES:
        if not os.path.isfile(file_path):
            errors.append(f"missing file: {file_path}")

    for file_path in PHASE2_FILES:
        if not os.path.isfile(file_path):
            errors.append(f"missing Phase 2 file: {file_path}")

    if errors:
        return False, errors

    try:
        index_data = json.loads(read_text(INDEX_PATH))
    except json.JSONDecodeError as exc:
        errors.append(f"index.json is not valid JSON: {exc}")
        return False, errors

    if not isinstance(index_data, dict):
        errors.append("index.json root must be an object")
    else:
        if index_data.get("schema_version") != 1:
            errors.append(
                f"index.json field 'schema_version' must equal 1 (got {index_data.get('schema_version')!r})"
            )
        gen_at = index_data.get("generated_at")
        if gen_at is not None and not isinstance(gen_at, str):
            errors.append(
                f"index.json field 'generated_at' must be null or ISO 8601 string (got {gen_at!r})"
            )
        if index_data.get("source_root") != "/home/slimy/kb/research":
            errors.append(
                f"index.json field 'source_root' must equal '/home/slimy/kb/research' (got {index_data.get('source_root')!r})"
            )
        if index_data.get("ui_theme") != "research_farm":
            errors.append(
                f"index.json field 'ui_theme' must equal 'research_farm' (got {index_data.get('ui_theme')!r})"
            )
        items = index_data.get("items")
        if not isinstance(items, list):
            errors.append("index.json field 'items' must be an array")

    schema_paths = [
        os.path.join(RESEARCH_ROOT, "templates", "research-topic.schema.json"),
        os.path.join(RESEARCH_ROOT, "templates", "research-index.schema.json"),
    ] + PHASE2_SCHEMA_PATHS
    for schema_path in schema_paths:
        try:
            json.loads(read_text(schema_path))
        except json.JSONDecodeError as exc:
            errors.append(f"schema file is not valid JSON: {schema_path}: {exc}")

    template_text = read_text(
        os.path.join(RESEARCH_ROOT, "templates", "research-topic.template.md")
    )
    if "/home/slimy/slimy-kb" in template_text:
        errors.append("topic template must not reference /home/slimy/slimy-kb")

    for phase2_file in PHASE2_FILES:
        if os.path.isfile(phase2_file):
            content = read_text(phase2_file)
            for line_no, line in enumerate(content.split("\n"), 1):
                if "/home/slimy/slimy-kb" in line:
                    stripped = line.strip()
                    if stripped.startswith("#") or stripped.startswith(">"):
                        continue
                    if "must not" in line.lower() or "forbidden" in line.lower() or "do not" in line.lower():
                        continue
                    rel = os.path.relpath(phase2_file, REPO_ROOT)
                    errors.append(f"Phase 2 file {rel}:{line_no} must not reference /home/slimy/slimy-kb")

    sample_topic = os.path.join(RESEARCH_ROOT, "topics", "sample-self-hosted-deep-research-agent.md")
    if os.path.isfile(sample_topic):
        try:
            sample_text = read_text(sample_topic)
            if not sample_text.startswith("---"):
                errors.append("sample topic must start with YAML frontmatter")
        except Exception as exc:
            errors.append(f"cannot read sample topic: {exc}")

    for schema_path in PHASE2_SCHEMA_PATHS:
        if os.path.isfile(schema_path):
            try:
                schema = json.loads(read_text(schema_path))
                if not isinstance(schema, dict):
                    rel = os.path.relpath(schema_path, REPO_ROOT)
                    errors.append(f"{rel} root must be a JSON object")
            except json.JSONDecodeError as exc:
                errors.append(f"Phase 2 schema not valid JSON: {schema_path}: {exc}")

    return not errors, errors


def main() -> int:
    ok, errors = validate()
    print(f"research_root={RESEARCH_ROOT}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
    print(f"RESULT={'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
