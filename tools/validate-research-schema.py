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

PHASE3_FILES = [
    os.path.join(REPO_ROOT, "tools", "research-render-almanac.py"),
    os.path.join(REPO_ROOT, "tools", "research-render-almanac.sh"),
    os.path.join(RESEARCH_ROOT, "templates", "almanac.css"),
    os.path.join(RESEARCH_ROOT, "templates", "almanac-render.schema.json"),
    os.path.join(RESEARCH_ROOT, "planning", "phase-3-pdf-almanac-output.md"),
]

PHASE3_SCHEMA_PATHS = [
    os.path.join(RESEARCH_ROOT, "templates", "almanac-render.schema.json"),
]

PHASE6A_DIRS = [
    os.path.join(RESEARCH_ROOT, "policies"),
]

PHASE6A_FILES = [
    os.path.join(RESEARCH_ROOT, "policies", "source-quality-policy.md"),
    os.path.join(RESEARCH_ROOT, "policies", "citation-policy.md"),
    os.path.join(RESEARCH_ROOT, "policies", "execution-safety-policy.md"),
    os.path.join(RESEARCH_ROOT, "planning", "phase-6a-research-execution-contract.md"),
    os.path.join(RESEARCH_ROOT, "templates", "source-record.schema.json"),
    os.path.join(RESEARCH_ROOT, "templates", "citation-record.schema.json"),
    os.path.join(RESEARCH_ROOT, "templates", "claim-record.schema.json"),
    os.path.join(RESEARCH_ROOT, "templates", "execution-timeline.schema.json"),
    os.path.join(RESEARCH_ROOT, "templates", "execution-plan.template.md"),
    os.path.join(RESEARCH_ROOT, "templates", "source-notes.template.md"),
    os.path.join(REPO_ROOT, "tools", "research-execute-run.py"),
    os.path.join(REPO_ROOT, "tools", "research-execute-run.sh"),
]

PHASE6A_SCHEMA_PATHS = [
    os.path.join(RESEARCH_ROOT, "templates", "source-record.schema.json"),
    os.path.join(RESEARCH_ROOT, "templates", "citation-record.schema.json"),
    os.path.join(RESEARCH_ROOT, "templates", "claim-record.schema.json"),
    os.path.join(RESEARCH_ROOT, "templates", "execution-timeline.schema.json"),
]

PHASE6B_DIRS = [
    # No new directories introduced by Phase 6B; lives under research/policies/
    # and research/planning/, both created in earlier phases.
]

PHASE6B_FILES = [
    os.path.join(RESEARCH_ROOT, "policies", "fetching-policy.md"),
    os.path.join(RESEARCH_ROOT, "planning", "phase-6b-owner-approved-source-fetching.md"),
    os.path.join(RESEARCH_ROOT, "templates", "pending-sources.schema.json"),
    os.path.join(RESEARCH_ROOT, "templates", "pending-sources.template.json"),
    os.path.join(RESEARCH_ROOT, "templates", "source-fetch-record.schema.json"),
    os.path.join(RESEARCH_ROOT, "templates", "fetch-result.schema.json"),
    os.path.join(REPO_ROOT, "tools", "research-fetch-sources.py"),
    os.path.join(REPO_ROOT, "tools", "research-fetch-sources.sh"),
]

PHASE6B_SCHEMA_PATHS = [
    os.path.join(RESEARCH_ROOT, "templates", "pending-sources.schema.json"),
    os.path.join(RESEARCH_ROOT, "templates", "source-fetch-record.schema.json"),
    os.path.join(RESEARCH_ROOT, "templates", "fetch-result.schema.json"),
    os.path.join(RESEARCH_ROOT, "templates", "source-record.schema.json"),
    os.path.join(RESEARCH_ROOT, "templates", "run-metadata.schema.json"),
]

PHASE6C_FILES = [
    os.path.join(RESEARCH_ROOT, "policies", "source-notes-policy.md"),
    os.path.join(RESEARCH_ROOT, "planning", "phase-6c-source-note-extraction.md"),
    os.path.join(RESEARCH_ROOT, "templates", "extracted-text.schema.json"),
    os.path.join(RESEARCH_ROOT, "templates", "source-note-record.schema.json"),
    os.path.join(RESEARCH_ROOT, "templates", "source-note.template.md"),
    os.path.join(REPO_ROOT, "tools", "research-extract-source-notes.py"),
    os.path.join(REPO_ROOT, "tools", "research-extract-source-notes.sh"),
]

PHASE6C_SCHEMA_PATHS = [
    os.path.join(RESEARCH_ROOT, "templates", "extracted-text.schema.json"),
    os.path.join(RESEARCH_ROOT, "templates", "source-note-record.schema.json"),
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

    for file_path in PHASE3_FILES:
        if not os.path.isfile(file_path):
            errors.append(f"missing Phase 3 file: {file_path}")

    for directory in PHASE6A_DIRS:
        if not os.path.isdir(directory):
            errors.append(f"missing Phase 6A directory: {directory}")

    for file_path in PHASE6A_FILES:
        if not os.path.isfile(file_path):
            errors.append(f"missing Phase 6A file: {file_path}")

    for file_path in PHASE6B_FILES:
        if not os.path.isfile(file_path):
            errors.append(f"missing Phase 6B file: {file_path}")

    for file_path in PHASE6C_FILES:
        if not os.path.isfile(file_path):
            errors.append(f"missing Phase 6C file: {file_path}")

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

    for phase3_file in PHASE3_FILES:
        if os.path.isfile(phase3_file):
            content = read_text(phase3_file)
            for line_no, line in enumerate(content.split("\n"), 1):
                if "/home/slimy/slimy-kb" in line:
                    stripped = line.strip()
                    if stripped.startswith("#") or stripped.startswith(">"):
                        continue
                    if "must not" in line.lower() or "forbidden" in line.lower() or "do not" in line.lower():
                        continue
                    rel = os.path.relpath(phase3_file, REPO_ROOT)
                    errors.append(f"Phase 3 file {rel}:{line_no} must not reference /home/slimy/slimy-kb")

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

    for schema_path in PHASE3_SCHEMA_PATHS:
        if os.path.isfile(schema_path):
            try:
                schema = json.loads(read_text(schema_path))
                if not isinstance(schema, dict):
                    rel = os.path.relpath(schema_path, REPO_ROOT)
                    errors.append(f"{rel} root must be a JSON object")
            except json.JSONDecodeError as exc:
                errors.append(f"Phase 3 schema not valid JSON: {schema_path}: {exc}")

    for phase6a_file in PHASE6A_FILES:
        if os.path.isfile(phase6a_file):
            content = read_text(phase6a_file)
            for line_no, line in enumerate(content.split("\n"), 1):
                if "/home/slimy/slimy-kb" in line:
                    stripped = line.strip()
                    if stripped.startswith("#") or stripped.startswith(">"):
                        continue
                    if "must not" in line.lower() or "forbidden" in line.lower() or "do not" in line.lower():
                        continue
                    rel = os.path.relpath(phase6a_file, REPO_ROOT)
                    errors.append(f"Phase 6A file {rel}:{line_no} must not reference /home/slimy/slimy-kb")

    for schema_path in PHASE6A_SCHEMA_PATHS:
        if os.path.isfile(schema_path):
            try:
                schema = json.loads(read_text(schema_path))
                if not isinstance(schema, dict):
                    rel = os.path.relpath(schema_path, REPO_ROOT)
                    errors.append(f"{rel} root must be a JSON object")
            except json.JSONDecodeError as exc:
                errors.append(f"Phase 6A schema not valid JSON: {schema_path}: {exc}")

    for phase6b_file in PHASE6B_FILES:
        if os.path.isfile(phase6b_file):
            content = read_text(phase6b_file)
            for line_no, line in enumerate(content.split("\n"), 1):
                if "/home/slimy/slimy-kb" in line:
                    stripped = line.strip()
                    if stripped.startswith("#") or stripped.startswith(">"):
                        continue
                    if "must not" in line.lower() or "forbidden" in line.lower() or "do not" in line.lower():
                        continue
                    rel = os.path.relpath(phase6b_file, REPO_ROOT)
                    errors.append(f"Phase 6B file {rel}:{line_no} must not reference /home/slimy/slimy-kb")

    for schema_path in PHASE6B_SCHEMA_PATHS:
        if os.path.isfile(schema_path):
            try:
                schema = json.loads(read_text(schema_path))
                if not isinstance(schema, dict):
                    rel = os.path.relpath(schema_path, REPO_ROOT)
                    errors.append(f"{rel} root must be a JSON object")
            except json.JSONDecodeError as exc:
                errors.append(f"Phase 6B schema not valid JSON: {schema_path}: {exc}")

    for phase6c_file in PHASE6C_FILES:
        if os.path.isfile(phase6c_file):
            content = read_text(phase6c_file)
            for line_no, line in enumerate(content.split("\n"), 1):
                if "/home/slimy/slimy-kb" in line:
                    stripped = line.strip()
                    if stripped.startswith("#") or stripped.startswith(">"):
                        continue
                    if "must not" in line.lower() or "forbidden" in line.lower() or "do not" in line.lower():
                        continue
                    rel = os.path.relpath(phase6c_file, REPO_ROOT)
                    errors.append(f"Phase 6C file {rel}:{line_no} must not reference /home/slimy/slimy-kb")

    for schema_path in PHASE6C_SCHEMA_PATHS:
        if os.path.isfile(schema_path):
            try:
                schema = json.loads(read_text(schema_path))
                if not isinstance(schema, dict):
                    rel = os.path.relpath(schema_path, REPO_ROOT)
                    errors.append(f"{rel} root must be a JSON object")
            except json.JSONDecodeError as exc:
                errors.append(f"Phase 6C schema not valid JSON: {schema_path}: {exc}")

    # Phase 6B tool self-checks.
    fetcher = os.path.join(REPO_ROOT, "tools", "research-fetch-sources.py")
    if os.path.isfile(fetcher):
        try:
            import py_compile
            py_compile.compile(fetcher, doraise=True)
        except py_compile.PyCompileError as exc:
            errors.append(f"Phase 6B fetcher does not compile: {exc}")

    extractor = os.path.join(REPO_ROOT, "tools", "research-extract-source-notes.py")
    if os.path.isfile(extractor):
        try:
            import py_compile
            py_compile.compile(extractor, doraise=True)
        except py_compile.PyCompileError as exc:
            errors.append(f"Phase 6C extractor does not compile: {exc}")

    # Validate run-metadata schema is also valid JSON.
    rm_schema = os.path.join(RESEARCH_ROOT, "templates", "run-metadata.schema.json")
    if os.path.isfile(rm_schema):
        try:
            json.loads(read_text(rm_schema))
        except json.JSONDecodeError as exc:
            errors.append(f"run-metadata.schema.json is not valid JSON: {exc}")

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
