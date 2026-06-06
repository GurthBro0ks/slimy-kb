#!/usr/bin/env python3
"""Phase 6C deterministic source-note extraction.

Reads already-fetched local source artifacts and produces deterministic
extraction artifacts plus reviewer-facing note files. No network, no model,
no search, no crawling, no browser automation.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
from html.parser import HTMLParser
from typing import Any


TOOL_NAME = "research-extract-source-notes"
TOOL_VERSION = "0.1.0"
EXTRACTION_WARNING = (
    "This file was produced by deterministic extraction only. "
    "No model summary, citation, or final claim has been created."
)


def _utcnow_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _repo_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


def _research_root() -> str:
    return os.path.join(_repo_root(), "research")


def _index_path() -> str:
    return os.path.join(_research_root(), "indexes", "index.json")


def _run_json_path(run_dir: str) -> str:
    return os.path.join(run_dir, "run.json")


def _sources_path(run_dir: str) -> str:
    return os.path.join(run_dir, "sources.jsonl")


def _timeline_path(run_dir: str) -> str:
    return os.path.join(run_dir, "timeline.jsonl")


def _notes_dir(run_dir: str) -> str:
    return os.path.join(run_dir, "notes")


def _fetched_dir(run_dir: str) -> str:
    return os.path.join(run_dir, "fetched")


def _resolve_run_dir(run_arg: str) -> str:
    research_runs = os.path.join(_research_root(), "runs")
    if os.path.isabs(run_arg):
        run_dir = run_arg
    elif run_arg.startswith("research" + os.sep) or run_arg.startswith("research/"):
        run_dir = os.path.join(_repo_root(), run_arg)
    else:
        run_dir = os.path.join(research_runs, run_arg)
    run_dir = os.path.abspath(run_dir)
    if not os.path.isdir(run_dir):
        raise SystemExit(f"error: run directory not found: {run_dir}")
    if not run_dir.startswith(research_runs + os.sep):
        raise SystemExit(f"error: run directory must be under research/runs/: {run_dir}")
    return run_dir


def _read_json(path: str) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        raise SystemExit(f"error: required file not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"error: invalid JSON at {path}: {exc}")


def _read_text(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    except FileNotFoundError:
        raise SystemExit(f"error: required file not found: {path}")


def _write_text(path: str, text: str) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as handle:
        handle.write(text)
    os.replace(tmp, path)


def _write_json(path: str, obj: Any) -> None:
    _write_text(path, json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=True) + "\n")


def _read_sources(run_dir: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with open(_sources_path(run_dir), "r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"error: invalid JSON in sources.jsonl line {line_no}: {exc}")
            if isinstance(data, dict):
                records.append(data)
    return records


def _real_fetched_sources(run_dir: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for rec in _read_sources(run_dir):
        if not rec.get("source_id"):
            continue
        if rec.get("status") != "fetched":
            continue
        out.append(rec)
    return out


def _next_timeline_step(run_dir: str) -> int:
    path = _timeline_path(run_dir)
    max_step = 0
    if not os.path.isfile(path):
        return 1
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(data, dict) and isinstance(data.get("step"), int):
                max_step = max(max_step, data["step"])
    return max_step + 1


class DeterministicHTMLExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._ignored_stack: list[str] = []
        self._in_title = False
        self._current_heading_level: int | None = None
        self._current_heading_buffer: list[str] = []
        self.title_parts: list[str] = []
        self.headings: list[dict[str, Any]] = []
        self.text_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in {"script", "style", "noscript", "template"}:
            self._ignored_stack.append(tag)
            return
        if tag == "title":
            self._in_title = True
            return
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self._current_heading_level = int(tag[1])
            self._current_heading_buffer = []
            return
        if tag in {"p", "div", "section", "article", "br", "li", "ul", "ol", "tr", "table"}:
            self.text_parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in {"script", "style", "noscript", "template"}:
            if self._ignored_stack:
                self._ignored_stack.pop()
            return
        if tag == "title":
            self._in_title = False
            return
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"} and self._current_heading_level is not None:
            text = _normalize_whitespace(" ".join(self._current_heading_buffer))
            if text:
                self.headings.append({"level": self._current_heading_level, "text": text})
                self.text_parts.append(text)
                self.text_parts.append("\n")
            self._current_heading_level = None
            self._current_heading_buffer = []

    def handle_comment(self, data: str) -> None:
        return

    def handle_data(self, data: str) -> None:
        if self._ignored_stack:
            return
        if self._in_title:
            self.title_parts.append(data)
            return
        if self._current_heading_level is not None:
            self._current_heading_buffer.append(data)
            return
        self.text_parts.append(data)


def _normalize_whitespace(text: str) -> str:
    text = text.replace("\r", "\n")
    text = re.sub(r"[ \t\f\v]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    text = re.sub(r" ?\n ?", "\n", text)
    return text.strip()


def _extract_from_artifact(source_dir: str) -> dict[str, Any]:
    html_path = os.path.join(source_dir, "response.html")
    text_path = os.path.join(source_dir, "response.txt")
    json_path = os.path.join(source_dir, "response.json")
    xml_path = os.path.join(source_dir, "response.xml")

    source_artifact_path = None
    raw = ""
    title = ""
    headings: list[dict[str, Any]] = []

    if os.path.isfile(html_path):
        source_artifact_path = html_path
        raw = _read_text(html_path)
        parser = DeterministicHTMLExtractor()
        parser.feed(raw)
        title = _normalize_whitespace(" ".join(parser.title_parts))
        headings = parser.headings
        visible_text = _normalize_whitespace(" ".join(parser.text_parts))
    elif os.path.isfile(text_path):
        source_artifact_path = text_path
        raw = _read_text(text_path)
        visible_text = _normalize_whitespace(raw)
    elif os.path.isfile(json_path):
        source_artifact_path = json_path
        raw = _read_text(json_path)
        visible_text = _normalize_whitespace(raw)
    elif os.path.isfile(xml_path):
        source_artifact_path = xml_path
        raw = _read_text(xml_path)
        visible_text = _normalize_whitespace(raw)
    else:
        raise SystemExit(f"error: no response artifact found in {source_dir}")

    lines = [ln for ln in visible_text.splitlines() if ln.strip()]
    preview = "\n".join(lines[:12]).strip()
    return {
        "source_artifact_path": source_artifact_path,
        "title": title,
        "headings": headings,
        "visible_text": visible_text,
        "text_preview": preview,
        "text_char_count": len(visible_text),
        "text_line_count": len(lines),
    }


def _update_run_json(run_dir: str, status: str, extracted_at: str) -> None:
    path = _run_json_path(run_dir)
    data = _read_json(path)
    if not isinstance(data, dict):
        raise SystemExit("error: run.json root must be an object")
    data["status"] = status
    data["notes_extracted_at"] = extracted_at
    data["notes_extractor_version"] = TOOL_VERSION
    data["model_used"] = None
    data["completed_at"] = None
    _write_json(path, data)


def _update_index(run_id: str, status: str, extracted_at: str) -> None:
    idx = _read_json(_index_path())
    if not isinstance(idx, dict) or not isinstance(idx.get("items"), list):
        raise SystemExit("error: research/indexes/index.json must contain an items array")
    for item in idx["items"]:
        if isinstance(item, dict) and item.get("immutable_run_id") == run_id:
            item["status"] = status
            item["notes_extracted_at"] = extracted_at
            item["notes_extractor_version"] = TOOL_VERSION
            item["model_used"] = None
            break
    _write_json(_index_path(), idx)


def _append_timeline(run_dir: str, action: str, description: str, status: str) -> None:
    entry = {
        "step": _next_timeline_step(run_dir),
        "action": action,
        "description": description,
        "status": status,
    }
    path = _timeline_path(run_dir)
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")


def _format_headings_for_markdown(headings: list[dict[str, Any]]) -> str:
    if not headings:
        return "(No headings extracted)"
    lines = []
    for h in headings:
        lines.append(f"- H{h['level']}: {h['text']}")
    return "\n".join(lines)


def _render_note(record: dict[str, Any], extracted_json_rel: str, preview: str) -> str:
    warning = EXTRACTION_WARNING
    smoke = bool(record.get("final_url") == "https://example.com/" or record.get("url") == "https://example.com/")
    smoke_block = ""
    if smoke:
        smoke_block = (
            "\n## Smoke/Test Source Note\n\n"
            "This source is the `https://example.com/` smoke/test source used to verify the deterministic extractor. "
            "Do not create final report findings from it unless a later reviewer explicitly approves that use.\n"
        )
    headings_md = _format_headings_for_markdown(record["headings_structured"])
    return (
        f"# Source Notes: {record['extracted_title'] or record.get('title') or record['source_id']}\n\n"
        f"> {warning}\n\n"
        f"## Source Metadata\n\n"
        f"- **Source ID:** `{record['source_id']}`\n"
        f"- **URL:** `{record.get('url') or ''}`\n"
        f"- **Final URL:** `{record.get('final_url') or ''}`\n"
        f"- **HTTP Status:** `{record.get('http_status')}`\n"
        f"- **SHA256:** `{record.get('sha256') or ''}`\n"
        f"- **Extracted Text Path:** `{extracted_json_rel.replace('.json', '.txt')}`\n"
        f"- **Extracted JSON Path:** `{extracted_json_rel}`\n"
        f"- **Extracted At:** `{record['notes_extracted_at']}`\n"
        f"- **Extractor Version:** `{TOOL_VERSION}`\n\n"
        f"## Extracted Title\n\n"
        f"{record['extracted_title'] or '(No title extracted)'}\n\n"
        f"## Extracted Headings\n\n"
        f"{headings_md}\n\n"
        f"## Extracted Text Preview\n\n"
        f"```text\n{preview or '(No visible text extracted)'}\n```\n"
        f"{smoke_block}"
        f"\n## Reviewer Checklist\n\n"
        f"- [ ] summary reviewed\n"
        f"- [ ] key claims reviewed\n"
        f"- [ ] claim extraction approved\n"
        f"- [ ] citation eligibility approved\n\n"
        f"## Summary\n\n"
        f"(Human reviewer fills this in later. Deterministic extraction only in Phase 6C.)\n\n"
        f"## Key Claims\n\n"
        f"(Human reviewer fills this in later. Keep `claims.jsonl` empty in Phase 6C.)\n\n"
        f"## Claim Extraction Approval Notes\n\n"
        f"(Human reviewer fills this in later.)\n"
    )


def cmd_inspect(args: argparse.Namespace) -> int:
    run_dir = _resolve_run_dir(args.run)
    run_json = _read_json(_run_json_path(run_dir))
    if not isinstance(run_json, dict):
        raise SystemExit("error: run.json root must be an object")
    fetched_sources = _real_fetched_sources(run_dir)
    print(f"run_dir:        {run_dir}")
    print(f"run_id:         {run_json.get('immutable_run_id')}")
    print(f"status:         {run_json.get('status')}")
    print(f"source_count:   {run_json.get('source_count')}")
    print(f"citation_count: {run_json.get('citation_count')}")
    print(f"fetched sources:{len(fetched_sources)}")
    print("fetched artifacts:")
    for rec in fetched_sources:
        source_id = rec["source_id"]
        source_dir = os.path.join(_fetched_dir(run_dir), source_id)
        names = sorted(os.listdir(source_dir)) if os.path.isdir(source_dir) else []
        print(f"  - {source_id}: {', '.join(names) if names else '(missing dir)'}")
    print("notes files:")
    note_dir = _notes_dir(run_dir)
    if os.path.isdir(note_dir):
        for name in sorted(os.listdir(note_dir)):
            print(f"  - {name}")
    return 0


def cmd_extract(args: argparse.Namespace) -> int:
    run_dir = _resolve_run_dir(args.run)
    run_json = _read_json(_run_json_path(run_dir))
    if not isinstance(run_json, dict):
        raise SystemExit("error: run.json root must be an object")
    run_id = str(run_json.get("immutable_run_id") or "")
    fetched_sources = _real_fetched_sources(run_dir)
    if not fetched_sources:
        raise SystemExit("error: no fetched sources found to extract")

    planned: list[dict[str, Any]] = []
    for rec in fetched_sources:
        source_id = str(rec["source_id"])
        source_dir = os.path.join(_fetched_dir(run_dir), source_id)
        extraction = _extract_from_artifact(source_dir)
        extracted_txt = os.path.join(source_dir, "extracted-text.txt")
        extracted_json = os.path.join(source_dir, "extracted-text.json")
        note_path = os.path.join(_notes_dir(run_dir), f"{source_id}.notes.md")
        planned.append(
            {
                "record": rec,
                "source_id": source_id,
                "source_dir": source_dir,
                "extracted_txt": extracted_txt,
                "extracted_json": extracted_json,
                "note_path": note_path,
                "extraction": extraction,
            }
        )

    if args.dry_run:
        print("DRY-RUN: would process the following fetched sources:")
        for item in planned:
            print(f"  - {item['source_id']}:")
            print(f"      extracted-text.txt -> {os.path.relpath(item['extracted_txt'], run_dir)}")
            print(f"      extracted-text.json -> {os.path.relpath(item['extracted_json'], run_dir)}")
            print(f"      notes update -> {os.path.relpath(item['note_path'], run_dir)}")
            print(f"      extracted title -> {item['extraction']['title'] or '(no title)'}")
        return 0

    extracted_at = _utcnow_iso()
    for item in planned:
        rec = dict(item["record"])
        extraction = item["extraction"]
        extracted_txt_rel = os.path.relpath(item["extracted_txt"], run_dir)
        extracted_json_rel = os.path.relpath(item["extracted_json"], run_dir)
        extracted_json = {
            "schema_version": 1,
            "run_id": run_id,
            "source_id": rec["source_id"],
            "source_url": rec.get("url"),
            "final_url": rec.get("final_url"),
            "http_status": rec.get("http_status"),
            "content_type": rec.get("content_type"),
            "source_sha256": rec.get("sha256"),
            "source_artifact_path": os.path.relpath(extraction["source_artifact_path"], run_dir),
            "artifact_path": extracted_json_rel,
            "extracted_at": extracted_at,
            "notes_extractor_version": TOOL_VERSION,
            "title": extraction["title"],
            "headings": extraction["headings"],
            "text_preview": extraction["text_preview"],
            "text_char_count": extraction["text_char_count"],
            "text_line_count": extraction["text_line_count"],
            "smoke_source": bool(rec.get("final_url") == "https://example.com/" or rec.get("url") == "https://example.com/"),
        }
        rec["extracted_title"] = extraction["title"]
        rec["headings_structured"] = extraction["headings"]
        rec["notes_extracted_at"] = extracted_at
        os.makedirs(item["source_dir"], exist_ok=True)
        os.makedirs(_notes_dir(run_dir), exist_ok=True)
        _write_text(item["extracted_txt"], extraction["visible_text"] + ("\n" if extraction["visible_text"] else ""))
        _write_json(item["extracted_json"], extracted_json)
        note_text = _render_note(rec, extracted_json_rel, extraction["text_preview"])
        _write_text(item["note_path"], note_text)

    _update_run_json(run_dir, "notes_ready", extracted_at)
    _update_index(run_id, "notes_ready", extracted_at)
    _append_timeline(
        run_dir,
        action="source_notes_extracted",
        description=f"Phase 6C deterministic source-note extraction complete ({len(planned)} source(s))",
        status="notes_ready",
    )
    print(f"processed {len(planned)} fetched source(s); run status -> notes_ready")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog=TOOL_NAME,
        description="Phase 6C deterministic source-note extraction for a research run.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    inspect_parser = sub.add_parser("inspect", help="inspect current extracted-note state")
    inspect_parser.add_argument("run", help="run id or research/runs/<id> path")
    inspect_parser.set_defaults(func=cmd_inspect)

    extract_parser = sub.add_parser("extract", help="extract deterministic source notes")
    extract_parser.add_argument("run", help="run id or research/runs/<id> path")
    extract_parser.add_argument("--dry-run", action="store_true")
    extract_parser.set_defaults(func=cmd_extract)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
