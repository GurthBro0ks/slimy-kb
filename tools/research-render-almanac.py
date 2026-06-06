#!/usr/bin/env python3

from __future__ import annotations

import html
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RENDERER_VERSION = "slimy-research-render-almanac@0.1.0"

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
RESEARCH_ROOT = os.path.join(REPO_ROOT, "research")

CHROME_SEARCH_PATHS = [
    os.path.expanduser("~/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome"),
    "/usr/bin/chromium-browser",
    "/usr/bin/chromium",
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
]

TEMPLATE_PATH = os.path.join(RESEARCH_ROOT, "templates", "almanac.html.template")
CSS_PATH = os.path.join(RESEARCH_ROOT, "templates", "almanac.css")


def e(text: str) -> str:
    return html.escape(str(text))


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def find_chrome() -> str | None:
    for path in CHROME_SEARCH_PATHS:
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    return None


def read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def read_json(path: str) -> Any:
    return json.loads(read_file(path))


def write_json(path: str, data: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def resolve_run_dir(run_arg: str) -> str:
    if os.path.isabs(run_arg):
        return run_arg
    if run_arg.startswith("research/"):
        return os.path.join(REPO_ROOT, run_arg)
    return os.path.join(REPO_ROOT, "research", "runs", run_arg)


def validate_run_dir(run_dir: str) -> tuple[bool, str]:
    if not os.path.isdir(run_dir):
        return False, f"run directory does not exist: {run_dir}"
    run_json_path = os.path.join(run_dir, "run.json")
    if not os.path.isfile(run_json_path):
        return False, f"run.json not found in: {run_dir}"
    return True, ""


def read_optional(run_dir: str, filename: str) -> str:
    path = os.path.join(run_dir, filename)
    if os.path.isfile(path):
        return read_file(path)
    return ""


def read_optional_json(run_dir: str, filename: str) -> Any:
    path = os.path.join(run_dir, filename)
    if os.path.isfile(path):
        try:
            return read_json(path)
        except (json.JSONDecodeError, OSError):
            return None
    return None


def read_sources_jsonl(run_dir: str) -> list[dict]:
    path = os.path.join(run_dir, "sources.jsonl")
    if not os.path.isfile(path):
        return []
    sources = []
    for line in read_file(path).strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        try:
            sources.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return sources


def md_to_simple_html(md_text: str) -> str:
    if not md_text.strip():
        return '<p class="empty-state">(Empty)</p>'
    lines = md_text.split("\n")
    out_parts: list[str] = []
    in_list = False
    in_blockquote = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if in_list:
                out_parts.append("</ul>")
                in_list = False
            if in_blockquote:
                out_parts.append("</blockquote>")
                in_blockquote = False
            continue
        if stripped.startswith("#"):
            if in_list:
                out_parts.append("</ul>")
                in_list = False
            if in_blockquote:
                out_parts.append("</blockquote>")
                in_blockquote = False
            level = len(stripped) - len(stripped.lstrip("#"))
            level = min(level, 6)
            content = stripped.lstrip("#").strip()
            out_parts.append(f"<h{level}>{e(content)}</h{level}>")
        elif stripped.startswith(">"):
            content = stripped.lstrip(">").strip()
            if not in_blockquote:
                out_parts.append("<blockquote>")
                in_blockquote = True
            out_parts.append(e(content))
        elif stripped.startswith("- ") or stripped.startswith("* "):
            if in_blockquote:
                out_parts.append("</blockquote>")
                in_blockquote = False
            content = stripped[2:].strip()
            if not in_list:
                out_parts.append("<ul>")
                in_list = True
            out_parts.append(f"<li>{e(content)}</li>")
        elif re.match(r"^\d+\.\s", stripped):
            if in_blockquote:
                out_parts.append("</blockquote>")
                in_blockquote = False
            if in_list:
                out_parts.append("</ul>")
                in_list = False
            content = re.sub(r"^\d+\.\s+", "", stripped)
            out_parts.append(f"<li>{e(content)}</li>")
        elif stripped.startswith("```"):
            continue
        else:
            if in_list:
                out_parts.append("</ul>")
                in_list = False
            if in_blockquote:
                out_parts.append("</blockquote>")
                in_blockquote = False
            safe = e(stripped)
            safe = re.sub(r"`([^`]+)`", r"<code>\1</code>", safe)
            safe = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", safe)
            safe = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", safe)
            out_parts.append(f"<p>{safe}</p>")
    if in_list:
        out_parts.append("</ul>")
    if in_blockquote:
        out_parts.append("</blockquote>")
    return "\n".join(out_parts)


def is_placeholder_run(run_dir: str, run_data: dict) -> bool:
    result_path = os.path.join(run_dir, "RESULT.md")
    if os.path.isfile(result_path):
        result_text = read_file(result_path)
        if "RESULT=PLANNED" in result_text:
            return True
    sources = read_sources_jsonl(run_dir)
    real_sources = [s for s in sources if s.get("url") and s.get("status") != "pending"]
    if not real_sources:
        return True
    return False


def render_status_badge(status: str) -> str:
    cls = {
        "planned": "badge-planned",
        "queued": "badge-planned",
        "running": "badge-running",
        "in_progress": "badge-running",
        "completed": "badge-completed",
        "done": "badge-completed",
        "failed": "badge-failed",
    }.get(status, "badge-planned")
    return f'<span class="badge {cls}">{e(status)}</span>'


def render_tags(tags: list[str]) -> str:
    if not tags:
        return ""
    parts = [f'<span class="tag">{e(t)}</span>' for t in tags]
    return f'<div class="tag-list">{"".join(parts)}</div>'


def render_sources(sources: list[dict]) -> str:
    if not sources:
        return '<p class="empty-state">No sources fetched yet.</p>'
    real = [s for s in sources if s.get("url") or s.get("title")]
    if not real:
        return '<p class="empty-state">No real sources yet (only placeholders).</p>'
    items = []
    for s in real:
        url = s.get("url", "")
        title = s.get("title", "") or url
        status = s.get("status", "")
        url_html = f'<a class="source-url" href="{e(url)}">{e(url)}</a>' if url else ""
        title_html = f'<span class="source-title">{e(title)}</span>' if title else ""
        status_html = f'<span class="source-status">{e(status)}</span>' if status else ""
        items.append(f"<li>{title_html} {url_html} {status_html}</li>")
    return f'<ul class="sources-list">{"".join(items)}</ul>'


def render_citations(citations: Any) -> str:
    if not citations:
        return '<p class="empty-state">No citations recorded yet.</p>'
    if isinstance(citations, list):
        items = []
        for c in citations:
            if isinstance(c, dict):
                text = c.get("text", "") or c.get("title", "") or json.dumps(c, ensure_ascii=False)
                source = c.get("source", "")
                items.append(f'<li>{e(text)}' + (f' <span class="source-status">— {e(source)}</span>' if source else "") + "</li>")
            else:
                items.append(f"<li>{e(str(c))}</li>")
        return f'<ul class="citations-list">{"".join(items)}</ul>'
    return f'<div class="content-block"><pre><code>{e(json.dumps(citations, indent=2, ensure_ascii=False))}</code></pre></div>'


def build_almanac_html(run_dir: str, run_data: dict, css_text: str) -> str:
    topic_md = read_optional(run_dir, "topic.md")
    report_md = read_optional(run_dir, "report.md")
    slides_md = read_optional(run_dir, "slides.md")
    critic_md = read_optional(run_dir, "critic.md")
    result_md = read_optional(run_dir, "RESULT.md")
    plan_md = read_optional(run_dir, "plan.md")
    sources = read_sources_jsonl(run_dir)
    citations = read_optional_json(run_dir, "citations.json")

    placeholder = is_placeholder_run(run_dir, run_data)

    title = run_data.get("title") or "Untitled Research Run"
    status = run_data.get("status") or "unknown"
    slug = run_data.get("slug") or ""
    run_id = run_data.get("immutable_run_id") or ""
    depth = run_data.get("depth") or ""
    priority = run_data.get("priority") or ""
    model = run_data.get("model_used") or "none"
    runner = run_data.get("runner_version") or ""
    tags = run_data.get("tags") or []
    source_count = run_data.get("source_count") or 0
    citation_count = run_data.get("citation_count") or 0
    created_at = run_data.get("created_at") or ""
    started_at = run_data.get("started_at") or ""
    completed_at = run_data.get("completed_at") or ""

    meta_items = []
    meta_items.append(("Run ID", run_id))
    meta_items.append(("Slug", slug))
    meta_items.append(("Depth", depth))
    meta_items.append(("Priority", priority))
    meta_items.append(("Model", model))
    meta_items.append(("Runner", runner))
    meta_items.append(("Sources", str(source_count)))
    meta_items.append(("Citations", str(citation_count)))
    meta_items.append(("Created", created_at))
    if started_at:
        meta_items.append(("Started", started_at))
    if completed_at:
        meta_items.append(("Completed", completed_at))

    meta_html = '<div class="meta-grid">'
    for label, value in meta_items:
        if value:
            meta_html += f'<div class="meta-item"><div class="meta-label">{e(label)}</div><div class="meta-value">{e(value)}</div></div>'
    meta_html += "</div>"

    placeholder_banner = ""
    if placeholder:
        placeholder_banner = """<div class="placeholder-banner">
<strong>Placeholder / Demo Output</strong><br>
This run has not completed real research yet. The content below is a skeleton
generated by the seed-to-run planner. No web sources were fetched, no model
synthesis was performed, and no findings should be treated as verified.
</div>"""

    sections = []

    if topic_md:
        topic_question = ""
        topic_what = ""
        for line in topic_md.split("\n"):
            stripped = line.strip()
            if stripped.startswith("question:"):
                topic_question = stripped.split(":", 1)[1].strip().strip('"')
        sections.append(f"""<section>
<h2><span class="icon">&#127793;</span> Research Seed</h2>
<div class="content-block">{md_to_simple_html(topic_md)}</div>
</section>""")

    if plan_md:
        sections.append(f"""<section>
<h2><span class="icon">&#128203;</span> Forage Plan</h2>
<div class="content-block">{md_to_simple_html(plan_md)}</div>
</section>""")

    sections.append(f"""<section>
<h2><span class="icon">&#128220;</span> Report</h2>
<div class="content-block">{md_to_simple_html(report_md)}</div>
</section>""")

    sections.append(f"""<section>
<h2><span class="icon">&#127916;</span> Slides</h2>
<div class="content-block">{md_to_simple_html(slides_md)}</div>
</section>""")

    sections.append(f"""<section>
<h2><span class="icon">&#128214;</span> Sources</h2>
<div class="content-block">{render_sources(sources)}</div>
</section>""")

    sections.append(f"""<section>
<h2><span class="icon">&#128218;</span> Citations</h2>
<div class="content-block">{render_citations(citations)}</div>
</section>""")

    sections.append(f"""<section>
<h2><span class="icon">&#128270;</span> Critic Notes</h2>
<div class="content-block">{md_to_simple_html(critic_md)}</div>
</section>""")

    if result_md:
        sections.append(f"""<section>
<h2><span class="icon">&#128373;</span> Proof Burrow / RESULT</h2>
<div class="result-block">{e(result_md)}</div>
</section>""")

    tags_html = render_tags(tags)
    if tags_html:
        sections.append(f"""<section>
<h2><span class="icon">&#127991;</span> Tags</h2>
{tags_html}
</section>""")

    sections_html = "\n".join(sections)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(title)} — Research Farm Almanac</title>
<style>
{css_text}
</style>
</head>
<body>
<div class="page">
<header>
<div class="title-row">
<h1>{e(title)}</h1>
{render_status_badge(status)}
</div>
<div class="subtitle">Research Farm Almanac &middot; Slimy Knowledge Base</div>
{meta_html}
</header>
{placeholder_banner}
{sections_html}
<footer class="footer">
<span class="farm-brand">Slimy Research Farm</span> &middot; {e(RENDERER_VERSION)} &middot; generated {iso_now()}
</footer>
</div>
</body>
</html>"""


def cmd_inspect(args: list[str]) -> int:
    if not args:
        print("Usage: research-render-almanac.py inspect <run-dir>", file=sys.stderr)
        return 1
    run_dir = resolve_run_dir(args[0])
    ok, err = validate_run_dir(run_dir)
    if not ok:
        print(f"ERROR: {err}", file=sys.stderr)
        return 1

    run_data = read_json(os.path.join(run_dir, "run.json"))

    print(f"run_dir: {run_dir}")
    print(f"title: {run_data.get('title', '')}")
    print(f"status: {run_data.get('status', '')}")
    print(f"slug: {run_data.get('slug', '')}")
    print(f"immutable_run_id: {run_data.get('immutable_run_id', '')}")
    print(f"source_count: {run_data.get('source_count', 0)}")
    print(f"citation_count: {run_data.get('citation_count', 0)}")
    print(f"depth: {run_data.get('depth', '')}")
    print(f"priority: {run_data.get('priority', '')}")
    print(f"model_used: {run_data.get('model_used', 'none')}")
    print(f"runner_version: {run_data.get('runner_version', '')}")
    print(f"report_path: {run_data.get('report_path', '')}")
    print(f"pdf_path: {run_data.get('pdf_path', '')}")
    print(f"almanac_path: {run_data.get('almanac_path', '')}")
    print()

    for fname in ["report.md", "slides.md", "critic.md", "RESULT.md", "plan.md", "topic.md"]:
        exists = os.path.isfile(os.path.join(run_dir, fname))
        print(f"  {fname}: {'EXISTS' if exists else 'MISSING'}")

    print()
    almanac_path = os.path.join(run_dir, "almanac.html")
    print(f"  almanac.html: {'EXISTS' if os.path.isfile(almanac_path) else 'NOT YET'}")
    pdf_path = os.path.join(run_dir, "presentation.pdf")
    print(f"  presentation.pdf: {'EXISTS' if os.path.isfile(pdf_path) else 'NOT YET'}")

    return 0


def cmd_render_html(args: list[str]) -> int:
    if not args:
        print("Usage: research-render-almanac.py render-html <run-dir> [--dry-run] [--force]", file=sys.stderr)
        return 1

    dry_run = "--dry-run" in args
    force = "--force" in args
    run_arg = [a for a in args if not a.startswith("--")]
    if not run_arg:
        print("ERROR: no run directory specified", file=sys.stderr)
        return 1

    run_dir = resolve_run_dir(run_arg[0])
    ok, err = validate_run_dir(run_dir)
    if not ok:
        print(f"ERROR: {err}", file=sys.stderr)
        return 1

    almanac_path = os.path.join(run_dir, "almanac.html")
    print(f"run_dir: {run_dir}")
    print(f"planned_output: {almanac_path}")

    if dry_run:
        print("dry_run: true (no files modified)")
        return 0

    if os.path.isfile(almanac_path) and not force:
        print(f"ERROR: {almanac_path} already exists. Use --force to overwrite.", file=sys.stderr)
        return 1

    if not os.path.isfile(CSS_PATH):
        print(f"ERROR: CSS file not found: {CSS_PATH}", file=sys.stderr)
        return 1

    run_data = read_json(os.path.join(run_dir, "run.json"))
    css_text = read_file(CSS_PATH)

    almanac_html = build_almanac_html(run_dir, run_data, css_text)

    with open(almanac_path, "w", encoding="utf-8") as f:
        f.write(almanac_html)
    print(f"almanac.html written: {almanac_path}")

    rel_almanac = os.path.relpath(almanac_path, RESEARCH_ROOT)
    run_data["almanac_path"] = rel_almanac
    run_data["almanac_generated_at"] = iso_now()
    run_data["almanac_renderer_version"] = RENDERER_VERSION
    write_json(os.path.join(run_dir, "run.json"), run_data)
    print(f"run.json updated with almanac metadata")

    index_path = os.path.join(RESEARCH_ROOT, "indexes", "index.json")
    if os.path.isfile(index_path):
        index_data = read_json(index_path)
        run_id = run_data.get("immutable_run_id", "")
        for item in index_data.get("items", []):
            if item.get("immutable_run_id") == run_id:
                item["almanac_path"] = rel_almanac
                item["almanac_generated_at"] = run_data["almanac_generated_at"]
                if run_data.get("pdf_path"):
                    item["pdf_path"] = run_data["pdf_path"]
                break
        index_data["generated_at"] = iso_now()
        write_json(index_path, index_data)
        print(f"index.json updated for run {run_id}")

    return 0


def cmd_render_pdf(args: list[str]) -> int:
    if not args:
        print("Usage: research-render-almanac.py render-pdf <run-dir> [--dry-run] [--force]", file=sys.stderr)
        return 1

    dry_run = "--dry-run" in args
    force = "--force" in args
    run_arg = [a for a in args if not a.startswith("--")]
    if not run_arg:
        print("ERROR: no run directory specified", file=sys.stderr)
        return 1

    run_dir = resolve_run_dir(run_arg[0])
    ok, err = validate_run_dir(run_dir)
    if not ok:
        print(f"ERROR: {err}", file=sys.stderr)
        return 1

    chrome = find_chrome()
    print(f"run_dir: {run_dir}")

    if chrome:
        print(f"pdf_renderer_available: true ({chrome})")
    else:
        print("pdf_renderer_available: false")
        print("No Chrome/Chromium found in search paths:")
        for p in CHROME_SEARCH_PATHS:
            print(f"  {p}")

    pdf_path = os.path.join(run_dir, "presentation.pdf")
    print(f"planned_output: {pdf_path}")

    if dry_run:
        print("dry_run: true (no files modified)")
        return 0

    if os.path.isfile(pdf_path) and not force:
        print(f"ERROR: {pdf_path} already exists. Use --force to overwrite.", file=sys.stderr)
        return 1

    if not chrome:
        print("", file=sys.stderr)
        print("RESULT=WARN", file=sys.stderr)
        print("No local Chrome/Chromium browser runtime found for PDF rendering.", file=sys.stderr)
        print("To enable PDF output, install Chrome/Chromium or Playwright browsers.", file=sys.stderr)
        print("Searched paths:", file=sys.stderr)
        for p in CHROME_SEARCH_PATHS:
            print(f"  {p}", file=sys.stderr)
        return 2

    almanac_path = os.path.join(run_dir, "almanac.html")
    if not os.path.isfile(almanac_path):
        run_data_check = read_json(os.path.join(run_dir, "run.json"))
        print(f"almanac.html not found, creating it first...")
        rc = cmd_render_html(run_arg + (["--force"] if force else []))
        if rc != 0:
            print("ERROR: failed to create almanac.html before PDF render", file=sys.stderr)
            return 1

    almanac_abs = os.path.abspath(almanac_path)
    pdf_abs = os.path.abspath(pdf_path)

    print(f"rendering PDF with: {chrome}")
    cmd = [
        chrome,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        f"--print-to-pdf={pdf_abs}",
        "--no-pdf-header-footer",
        almanac_abs,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            print(f"Chrome exited with code {result.returncode}", file=sys.stderr)
            if result.stderr:
                print(result.stderr[:2000], file=sys.stderr)
            return 1
    except subprocess.TimeoutExpired:
        print("ERROR: Chrome timed out after 60 seconds", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"ERROR: failed to run Chrome: {exc}", file=sys.stderr)
        return 1

    if not os.path.isfile(pdf_path):
        print(f"ERROR: Chrome ran but did not produce {pdf_path}", file=sys.stderr)
        return 1

    pdf_size = os.path.getsize(pdf_path)
    print(f"presentation.pdf written: {pdf_path} ({pdf_size} bytes)")

    run_data = read_json(os.path.join(run_dir, "run.json"))
    rel_pdf = os.path.relpath(pdf_path, RESEARCH_ROOT)
    run_data["pdf_path"] = rel_pdf
    run_data["pdf_generated_at"] = iso_now()
    run_data["pdf_renderer"] = f"chrome-headless ({os.path.basename(chrome)})"
    write_json(os.path.join(run_dir, "run.json"), run_data)
    print("run.json updated with PDF metadata")

    index_path = os.path.join(RESEARCH_ROOT, "indexes", "index.json")
    if os.path.isfile(index_path):
        index_data = read_json(index_path)
        run_id = run_data.get("immutable_run_id", "")
        for item in index_data.get("items", []):
            if item.get("immutable_run_id") == run_id:
                item["pdf_path"] = rel_pdf
                item["pdf_generated_at"] = run_data["pdf_generated_at"]
                break
        index_data["generated_at"] = iso_now()
        write_json(index_path, index_data)
        print(f"index.json updated for run {run_id}")

    return 0


def cmd_self_test() -> int:
    import tempfile

    print("Phase 3 almanac renderer self-test")
    tmp = tempfile.mkdtemp(prefix="research-render-test-")
    try:
        run_dir = os.path.join(tmp, "test-run")
        os.makedirs(run_dir)

        run_data = {
            "schema_version": 1,
            "immutable_run_id": "test-run",
            "slug": "test",
            "title": "Self-Test Run",
            "status": "planned",
            "priority": "normal",
            "depth": "deep",
            "confidence": None,
            "source_count": 0,
            "citation_count": 0,
            "created_at": "2026-06-06",
            "started_at": None,
            "completed_at": None,
            "model_used": None,
            "runner_version": "test",
            "pdf_path": None,
            "report_path": "test/report.md",
            "critic_path": "test/critic.md",
            "proof_path": "test",
            "topic_path": "test/topic.md",
            "tags": ["test"],
            "related_harness_session": None,
            "related_guild_campaign": None,
            "assigned_critter": None,
            "source_topic_path": "test/topic.md",
        }
        write_json(os.path.join(run_dir, "run.json"), run_data)

        for fname, content in [
            ("topic.md", "# Test Topic\n\nTest question?"),
            ("report.md", "# Report\n\nPlaceholder report."),
            ("slides.md", "# Slides\n\nSlide content."),
            ("critic.md", "# Critic\n\nCritic notes."),
            ("RESULT.md", "# Result\n\nRESULT=PLANNED"),
            ("plan.md", "# Plan\n\n1. Step one\n2. Step two"),
        ]:
            with open(os.path.join(run_dir, fname), "w") as f:
                f.write(content)

        with open(os.path.join(run_dir, "sources.jsonl"), "w") as f:
            f.write('{"url": "", "title": "", "fetched_at": null, "status": "pending"}\n')

        css_text = read_file(CSS_PATH)
        almanac_html = build_almanac_html(run_dir, run_data, css_text)

        assert "<!DOCTYPE html>" in almanac_html, "missing DOCTYPE"
        assert "Self-Test Run" in almanac_html, "missing title"
        assert "badge-planned" in almanac_html, "missing status badge"
        assert "Placeholder" in almanac_html, "missing placeholder banner"
        assert "Research Seed" in almanac_html, "missing seed section"
        assert "Report" in almanac_html, "missing report section"
        assert "Slides" in almanac_html, "missing slides section"
        assert "Sources" in almanac_html, "missing sources section"
        assert "Citations" in almanac_html, "missing citations section"
        assert "Critic Notes" in almanac_html, "missing critic section"
        assert "Proof Burrow" in almanac_html, "missing proof burrow section"
        assert "Research Farm Almanac" in almanac_html, "missing farm brand"
        assert "slimy-research-render-almanac" in almanac_html, "missing renderer version"
        assert "remote" not in almanac_html.lower() or "src=" not in almanac_html, "no remote deps"

        print("PASS: self-test complete")
        return 0
    except AssertionError as exc:
        print(f"FAIL: {exc}")
        return 1
    except Exception as exc:
        print(f"FAIL: unexpected error: {exc}")
        return 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print("Usage: research-render-almanac.py <command> [args]", file=sys.stderr)
        print("Commands: inspect, render-html, render-pdf, self-test", file=sys.stderr)
        return 1

    command = args[0]
    rest = args[1:]

    if command == "inspect":
        return cmd_inspect(rest)
    elif command == "render-html":
        return cmd_render_html(rest)
    elif command == "render-pdf":
        return cmd_render_pdf(rest)
    elif command == "self-test":
        return cmd_self_test()
    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        print("Commands: inspect, render-html, render-pdf, self-test", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
