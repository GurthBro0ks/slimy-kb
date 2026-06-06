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
        expected = {
            "schema_version": 1,
            "generated_at": None,
            "source_root": "/home/slimy/kb/research",
            "ui_theme": "research_farm",
        }
        for key, expected_value in expected.items():
            if index_data.get(key) != expected_value:
                errors.append(
                    f"index.json field {key!r} must equal {expected_value!r} (got {index_data.get(key)!r})"
                )
        items = index_data.get("items")
        if not isinstance(items, list):
            errors.append("index.json field 'items' must be an array")

    schema_paths = [
        os.path.join(RESEARCH_ROOT, "templates", "research-topic.schema.json"),
        os.path.join(RESEARCH_ROOT, "templates", "research-index.schema.json"),
    ]
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
