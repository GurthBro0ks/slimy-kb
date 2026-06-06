#!/usr/bin/env python3
"""research-fetch-sources.py — owner-gated source fetcher for a research run.

This is the Phase 6B implementation. It does NOT search, crawl, follow
links, summarize, claim-synthesize, or report-write. It fetches ONLY the
URLs the owner has pre-approved and written into a run-local
`pending-sources.json` file. Every fetch is one HTTP exchange with hard
caps on time and bytes; redirects are re-validated against the same URL
safety rules. The fetched response is saved to
`research/runs/<run-id>/fetched/<source_id>/` and the run's
`sources.jsonl`, `run.json`, `timeline.jsonl`, and
`research/indexes/index.json` are updated in place.

This is stdlib-only by design. No requests, urllib3, curl wrapper,
headless browser, or model client. Network is used only for the
explicit approved URLs and only when called without --dry-run.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import ipaddress
import json
import os
import re
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Iterable

# ----------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------

TOOL_NAME = "research-fetch-sources"
TOOL_VERSION = "0.1.0"
USER_AGENT = f"slimy-research-fetch-sources/{TOOL_VERSION} (+phase-6b)"

MAX_URL_LEN = 4096
MAX_REDIRECTS = 3
CONNECT_TIMEOUT_S = 10
READ_TIMEOUT_S = 30
MAX_BODY_BYTES = 5 * 1024 * 1024  # 5 MiB

# Network ranges that must NEVER be reached, even via redirect.
# These are evaluated against the resolved IP, not the textual host.
_BLOCKED_NETWORKS = [
    ipaddress.ip_network("0.0.0.0/8"),       # current network
    ipaddress.ip_network("10.0.0.0/8"),      # RFC1918
    ipaddress.ip_network("100.64.0.0/10"),   # CGNAT
    ipaddress.ip_network("127.0.0.0/8"),     # loopback
    ipaddress.ip_network("169.254.0.0/16"),  # link-local
    ipaddress.ip_network("172.16.0.0/12"),   # RFC1918
    ipaddress.ip_network("192.0.0.0/24"),    # IETF protocol assignments
    ipaddress.ip_network("192.0.2.0/24"),    # TEST-NET-1
    ipaddress.ip_network("192.88.99.0/24"),  # 6to4 anycast
    ipaddress.ip_network("192.168.0.0/16"),  # RFC1918
    ipaddress.ip_network("198.18.0.0/15"),   # benchmark
    ipaddress.ip_network("198.51.100.0/24"), # TEST-NET-2
    ipaddress.ip_network("203.0.113.0/24"),  # TEST-NET-3
    ipaddress.ip_network("224.0.0.0/4"),     # multicast
    ipaddress.ip_network("240.0.0.0/4"),     # reserved
    ipaddress.ip_network("::1/128"),         # IPv6 loopback
    ipaddress.ip_network("fc00::/7"),        # IPv6 ULA
    ipaddress.ip_network("fe80::/10"),       # IPv6 link-local
    ipaddress.ip_network("ff00::/8"),        # IPv6 multicast
    ipaddress.ip_network("::/128"),          # IPv6 unspecified
    ipaddress.ip_network("64:ff9b::/96"),    # IPv4-IPv6 translation
    ipaddress.ip_network("100::/64"),        # discard
    ipaddress.ip_network("2001::/32"),       # Teredo
    ipaddress.ip_network("2001:db8::/32"),   # documentation
]


# ----------------------------------------------------------------------
# Small utilities
# ----------------------------------------------------------------------

def _utcnow_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _repo_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


def _research_root() -> str:
    return os.path.join(_repo_root(), "research")


def _index_path() -> str:
    return os.path.join(_research_root(), "indexes", "index.json")


def _pending_path(run_dir: str) -> str:
    return os.path.join(run_dir, "pending-sources.json")


def _sources_path(run_dir: str) -> str:
    return os.path.join(run_dir, "sources.jsonl")


def _run_json_path(run_dir: str) -> str:
    return os.path.join(run_dir, "run.json")


def _timeline_path(run_dir: str) -> str:
    return os.path.join(run_dir, "timeline.jsonl")


def _fetched_root(run_dir: str) -> str:
    return os.path.join(run_dir, "fetched")


def _notes_dir(run_dir: str) -> str:
    return os.path.join(run_dir, "notes")


def _safe_filename(name: str) -> str:
    # Restrict to ASCII alnum, dash, underscore, dot.
    s = re.sub(r"[^A-Za-z0-9._-]", "_", name)
    return s[:120] or "source"


# ----------------------------------------------------------------------
# URL safety
# ----------------------------------------------------------------------

class UrlSafetyError(ValueError):
    pass


def _is_blocked(ip: ipaddress._BaseAddress) -> bool:
    for net in _BLOCKED_NETWORKS:
        try:
            if ip.version != net.version:
                continue
            if ip in net:
                return True
        except (TypeError, ValueError):
            continue
    return False


def validate_url(url: str) -> tuple[str, list[str], str]:
    """Validate a URL. Returns (safe_url, resolved_ips, scheme).

    Raises UrlSafetyError on any safety violation.
    """
    if not isinstance(url, str) or not url:
        raise UrlSafetyError("url is empty")
    if len(url) > MAX_URL_LEN:
        raise UrlSafetyError(f"url length {len(url)} > {MAX_URL_LEN}")
    # Strip whitespace just in case.
    url = url.strip()
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise UrlSafetyError(f"scheme must be http or https, got {parsed.scheme!r}")
    if not parsed.netloc:
        raise UrlSafetyError("url has no host")
    # Credentials in URL?
    if parsed.username or parsed.password:
        raise UrlSafetyError("url contains credentials")
    host = parsed.hostname
    if not host:
        raise UrlSafetyError("url has no hostname")
    # Resolve host to all addresses.
    try:
        infos = socket.getaddrinfo(host, parsed.port or (443 if parsed.scheme == "https" else 80))
    except socket.gaierror as exc:
        raise UrlSafetyError(f"DNS resolution failed for {host}: {exc}") from exc
    resolved: list[str] = []
    for info in infos:
        sockaddr = info[4]
        addr = sockaddr[0]
        try:
            ip = ipaddress.ip_address(addr)
        except ValueError:
            continue
        if _is_blocked(ip):
            raise UrlSafetyError(
                f"hostname {host!r} resolves to blocked IP {addr} (range check)"
            )
        resolved.append(addr)
    if not resolved:
        raise UrlSafetyError(f"hostname {host!r} produced no usable IP addresses")
    # Sort for determinism.
    resolved.sort()
    return url, resolved, parsed.scheme


# ----------------------------------------------------------------------
# Run directory validation
# ----------------------------------------------------------------------

def _resolve_run_dir(run_arg: str) -> str:
    """Accept either an absolute path, a 'research/runs/<id>' relative path,
    or a bare run id (which will be resolved under research/runs/)."""
    if not run_arg:
        raise SystemExit("error: run directory argument is required")
    research_runs = os.path.join(_research_root(), "runs")
    if os.path.isabs(run_arg):
        run_dir = run_arg
    elif run_arg.startswith("research" + os.sep) or run_arg.startswith("research/"):
        # Treat as repo-root-relative.
        run_dir = os.path.join(_repo_root(), run_arg)
    else:
        # Bare run id.
        run_dir = os.path.join(research_runs, run_arg)
    run_dir = os.path.abspath(run_dir)
    if not os.path.isdir(run_dir):
        raise SystemExit(f"error: run directory not found: {run_dir}")
    if not run_dir.startswith(research_runs + os.sep) and run_dir != research_runs:
        raise SystemExit(
            f"error: run directory must be under research/runs/, got: {run_dir}"
        )
    return run_dir


def _read_run_id(run_dir: str) -> str:
    rp = _run_json_path(run_dir)
    if not os.path.isfile(rp):
        raise SystemExit(f"error: run.json not found: {rp}")
    try:
        with open(rp, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"error: run.json is not valid JSON: {exc}")
    run_id = data.get("immutable_run_id")
    if not run_id:
        raise SystemExit("error: run.json missing immutable_run_id")
    return str(run_id)


# ----------------------------------------------------------------------
# pending-sources.json IO
# ----------------------------------------------------------------------

def _load_pending(run_dir: str) -> dict[str, Any]:
    pp = _pending_path(run_dir)
    if not os.path.isfile(pp):
        raise SystemExit(
            f"error: pending-sources.json not found at {pp}; run init-pending first"
        )
    try:
        with open(pp, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"error: pending-sources.json is not valid JSON: {exc}")
    if not isinstance(data, dict):
        raise SystemExit("error: pending-sources.json root must be a JSON object")
    if data.get("schema_version") != 1:
        raise SystemExit(
            f"error: pending-sources.json schema_version must be 1 (got {data.get('schema_version')!r})"
        )
    if not isinstance(data.get("sources"), list):
        raise SystemExit("error: pending-sources.json 'sources' must be a list")
    for i, src in enumerate(data["sources"]):
        for required in ("source_id", "url", "title_hint", "source_type",
                         "reason", "approved_by", "approved_at"):
            if required not in src or not src[required]:
                raise SystemExit(
                    f"error: pending-sources.json sources[{i}] missing required field {required!r}"
                )
        if not re.match(r"^[A-Za-z0-9._-]{1,64}$", src["source_id"]):
            raise SystemExit(
                f"error: pending-sources.json sources[{i}].source_id has invalid characters"
            )
    return data


# ----------------------------------------------------------------------
# Fetch core
# ----------------------------------------------------------------------

class FetchOutcome:
    def __init__(self) -> None:
        self.requested_url: str = ""
        self.final_url: str | None = None
        self.http_status: int | None = None
        self.content_type: str | None = None
        self.bytes_saved: int | None = None
        self.sha256: str | None = None
        self.truncated: bool = False
        self.resolved_ips: list[str] = []
        self.redirect_chain: list[str] = []
        self.duration_ms: int = 0
        self.status: str = "failed"   # fetched | failed
        self.error_message: str | None = None
        self.artifact_path: str | None = None
        self.body_bytes: bytes | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "requested_url": self.requested_url,
            "final_url": self.final_url,
            "http_status": self.http_status,
            "content_type": self.content_type,
            "bytes_saved": self.bytes_saved,
            "sha256": self.sha256,
            "truncated": self.truncated,
            "resolved_ips": self.resolved_ips,
            "redirect_chain": self.redirect_chain,
            "duration_ms": self.duration_ms,
            "status": self.status,
            "error_message": self.error_message,
            "artifact_path": self.artifact_path,
        }


def _do_fetch(url: str) -> FetchOutcome:
    out = FetchOutcome()
    out.requested_url = url
    started = time.monotonic()

    # Validate first, including DNS resolution.
    safe_url, resolved_ips, scheme = validate_url(url)
    out.resolved_ips = list(resolved_ips)
    out.final_url = safe_url

    req = urllib.request.Request(
        safe_url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "*/*",
            "Accept-Encoding": "identity",
        },
    )

    # Manual redirect handling so we can re-validate each target.
    redirects_left = MAX_REDIRECTS
    current_url = safe_url
    response: urllib.response.addinfourl | None = None
    try:
        while True:
            try:
                response = urllib.request.urlopen(
                    req, timeout=CONNECT_TIMEOUT_S
                )  # type: ignore[assignment]
            except urllib.error.HTTPError as exc:
                # 3xx after manual handling shouldn't reach here, but be safe.
                out.http_status = exc.code
                out.content_type = exc.headers.get("Content-Type") if exc.headers else None
                out.duration_ms = int((time.monotonic() - started) * 1000)
                out.status = "failed"
                out.error_message = f"HTTP {exc.code} {exc.reason}"
                return out
            except urllib.error.URLError as exc:
                out.duration_ms = int((time.monotonic() - started) * 1000)
                out.status = "failed"
                out.error_message = f"URLError: {exc.reason}"
                return out
            except (TimeoutError, socket.timeout) as exc:
                out.duration_ms = int((time.monotonic() - started) * 1000)
                out.status = "failed"
                out.error_message = f"timeout: {exc}"
                return out
            status = response.getcode()
            if 300 <= status < 400 and response.headers is not None:
                location = response.headers.get("Location")
                if not location:
                    out.http_status = status
                    out.duration_ms = int((time.monotonic() - started) * 1000)
                    out.status = "failed"
                    out.error_message = f"HTTP {status} with no Location header"
                    return out
                if redirects_left <= 0:
                    out.http_status = status
                    out.duration_ms = int((time.monotonic() - started) * 1000)
                    out.status = "failed"
                    out.error_message = f"too many redirects (>={MAX_REDIRECTS})"
                    return out
                redirects_left -= 1
                out.redirect_chain.append(location)
                # Re-validate the redirect target.
                target_url, target_ips, _ = validate_url(
                    urllib.parse.urljoin(current_url, location)
                )
                out.resolved_ips = sorted(set(out.resolved_ips) | set(target_ips))
                out.final_url = target_url
                current_url = target_url
                req = urllib.request.Request(
                    target_url,
                    headers={
                        "User-Agent": USER_AGENT,
                        "Accept": "*/*",
                        "Accept-Encoding": "identity",
                    },
                )
                continue
            break  # Non-redirect, fall through to read body.

        assert response is not None
        out.http_status = response.getcode()
        out.content_type = response.headers.get("Content-Type") if response.headers else None

        # Read body with read-timeout and size cap.
        chunks: list[bytes] = []
        total = 0
        truncated = False
        read_started = time.monotonic()
        try:
            while True:
                if (time.monotonic() - read_started) > READ_TIMEOUT_S:
                    out.status = "failed"
                    out.error_message = f"read timeout > {READ_TIMEOUT_S}s"
                    return out
                try:
                    chunk = response.read(64 * 1024)
                except (TimeoutError, socket.timeout) as exc:
                    out.status = "failed"
                    out.error_message = f"read timeout: {exc}"
                    return out
                if not chunk:
                    break
                total += len(chunk)
                if total > MAX_BODY_BYTES:
                    # Truncate and stop reading.
                    allowed = MAX_BODY_BYTES - (total - len(chunk))
                    if allowed > 0:
                        chunks.append(chunk[:allowed])
                    total = MAX_BODY_BYTES
                    truncated = True
                    break
                chunks.append(chunk)
        finally:
            try:
                response.close()
            except Exception:
                pass

        body = b"".join(chunks)
        out.bytes_saved = len(body)
        out.truncated = truncated
        out.sha256 = hashlib.sha256(body).hexdigest()
        out.body_bytes = body
        out.duration_ms = int((time.monotonic() - started) * 1000)
        out.status = "fetched"
        out.error_message = None
        return out
    except Exception as exc:  # last-ditch safety net
        out.duration_ms = int((time.monotonic() - started) * 1000)
        out.status = "failed"
        out.error_message = f"unexpected error: {type(exc).__name__}: {exc}"
        return out


# ----------------------------------------------------------------------
# Persist fetched artifacts
# ----------------------------------------------------------------------

def _safe_artifact_basename(content_type: str | None) -> str:
    ct = (content_type or "").lower()
    if "html" in ct:
        return "response.html"
    if "json" in ct:
        return "response.json"
    if "xml" in ct:
        return "response.xml"
    if "text/plain" in ct:
        return "response.txt"
    if ct.startswith("text/"):
        return "response.txt"
    return "response.bin"


def _write_atomic(path: str, content: bytes) -> None:
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(content)
    os.replace(tmp, path)


def _write_text_atomic(path: str, text: str) -> None:
    _write_atomic(path, text.encode("utf-8"))


def _write_json_atomic(path: str, obj: Any) -> None:
    text = json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False)
    _write_text_atomic(path, text + "\n")


def _persist_source(
    *,
    run_dir: str,
    run_id: str,
    src: dict[str, Any],
    outcome: FetchOutcome,
    artifact_dir: str,
    dry_run: bool,
) -> dict[str, Any]:
    """Persist per-source artifacts and return the source-record fields
    to append/update in sources.jsonl."""
    source_id = src["source_id"]
    fetched_at = _utcnow_iso()
    artifact_basename = _safe_artifact_basename(outcome.content_type)
    rel_artifact = os.path.relpath(
        os.path.join(artifact_dir, artifact_basename), run_dir
    )

    # Build source-fetch-record.
    fetch_record: dict[str, Any] = {
        "schema_version": 1,
        "source_id": source_id,
        "run_id": run_id,
        "requested_url": outcome.requested_url,
        "final_url": outcome.final_url,
        "fetched_at": fetched_at,
        "duration_ms": outcome.duration_ms,
        "fetcher_version": TOOL_VERSION,
        "user_agent": USER_AGENT,
        "http_status": outcome.http_status,
        "content_type": outcome.content_type,
        "bytes_saved": outcome.bytes_saved,
        "truncated": outcome.truncated,
        "sha256": outcome.sha256,
        "artifact_path": rel_artifact if outcome.status == "fetched" else None,
        "fetch_result_path": os.path.relpath(
            os.path.join(artifact_dir, "fetch-result.json"), run_dir
        )
        if outcome.status == "fetched"
        else None,
        "resolved_ips": outcome.resolved_ips,
        "redirect_chain": outcome.redirect_chain,
        "status": outcome.status,
        "error_message": outcome.error_message,
    }
    fetch_result: dict[str, Any] = {
        "schema_version": 1,
        "source_id": source_id,
        "run_id": run_id,
        "requested_url": outcome.requested_url,
        "final_url": outcome.final_url,
        "fetched_at": fetched_at,
        "duration_ms": outcome.duration_ms,
        "http_status": outcome.http_status,
        "content_type": outcome.content_type,
        "bytes_saved": outcome.bytes_saved,
        "sha256": outcome.sha256,
        "truncated": outcome.truncated,
        "redirect_chain": outcome.redirect_chain,
        "artifact_path": rel_artifact if outcome.status == "fetched" else None,
        "status": outcome.status,
        "error_message": outcome.error_message,
    }

    if not dry_run:
        os.makedirs(artifact_dir, exist_ok=True)
        if outcome.status == "fetched" and outcome.body_bytes is not None:
            _write_atomic(
                os.path.join(artifact_dir, artifact_basename),
                outcome.body_bytes,
            )
        _write_json_atomic(
            os.path.join(artifact_dir, "metadata.json"),
            fetch_record,
        )
        _write_json_atomic(
            os.path.join(artifact_dir, "fetch-result.json"),
            fetch_result,
        )

    # Build the source record (sources.jsonl entry).
    source_type = src.get("source_type") or "other"
    # Normalize alias to canonical form for sources.jsonl.
    if source_type == "official_docs":
        source_type = "official_documentation"
    record: dict[str, Any] = {
        "source_id": source_id,
        "url": src["url"],
        "final_url": outcome.final_url,
        "title": src.get("title_hint") or "",
        "source_type": source_type,
        "trust_level": "medium",
        "fetched_at": fetched_at if outcome.status == "fetched" else None,
        "status": outcome.status,
        "http_status": outcome.http_status,
        "content_type": outcome.content_type,
        "bytes_saved": outcome.bytes_saved,
        "sha256": outcome.sha256,
        "artifact_path": rel_artifact if outcome.status == "fetched" else None,
        "notes_path": os.path.relpath(
            os.path.join(_notes_dir(run_dir), f"{source_id}.notes.md"),
            run_dir,
        ),
        "error_message": outcome.error_message,
    }
    return record


def _write_source_notes_placeholder(
    run_dir: str, src: dict[str, Any], record: dict[str, Any]
) -> None:
    notes_path = os.path.join(_notes_dir(run_dir), f"{src['source_id']}.notes.md")
    if os.path.exists(notes_path):
        return
    body = (
        f"# Source Notes: {src.get('title_hint') or src['source_id']}\n\n"
        f"> Phase 6B placeholder. Reviewer must fill in summary, key claims, and\n"
        f"> extracted claims before any synthesis phase. This is not a citation.\n\n"
        f"## Source Metadata\n\n"
        f"- **Source ID:** `{src['source_id']}`\n"
        f"- **URL:** `{src['url']}`\n"
        f"- **Final URL:** `{record.get('final_url') or ''}`\n"
        f"- **Type:** `{record.get('source_type')}`\n"
        f"- **Trust Level:** medium (default; reviewer must re-assess)\n"
        f"- **Fetched At:** `{record.get('fetched_at') or ''}`\n"
        f"- **HTTP Status:** `{record.get('http_status')}`\n"
        f"- **Content-Type:** `{record.get('content_type') or ''}`\n"
        f"- **Bytes Saved:** `{record.get('bytes_saved')}`\n"
        f"- **SHA-256:** `{record.get('sha256') or ''}`\n"
        f"- **Artifact Path:** `{record.get('artifact_path') or ''}`\n"
        f"- **Approved By:** `{src.get('approved_by')}`\n"
        f"- **Approved At:** `{src.get('approved_at')}`\n"
        f"- **Reason:** {src.get('reason')}\n\n"
        f"## Summary\n\n(To be filled in by reviewer. Do not auto-generate.)\n\n"
        f"## Key Claims\n\n(Reviewer must list claims here with section/page references.)\n\n"
        f"## Extracted Claims\n\n(Reviewer must record claims that will be used in the final report.)\n"
    )
    _write_text_atomic(notes_path, body)


# ----------------------------------------------------------------------
# sources.jsonl, run.json, timeline.jsonl, index.json updates
# ----------------------------------------------------------------------

def _read_sources_jsonl(run_dir: str) -> list[dict[str, Any]]:
    path = _sources_path(run_dir)
    if not os.path.isfile(path):
        return []
    out: list[dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for ln, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SystemExit(
                    f"error: sources.jsonl line {ln} is not valid JSON: {exc}"
                )
            if not isinstance(obj, dict):
                raise SystemExit(
                    f"error: sources.jsonl line {ln} is not a JSON object"
                )
            out.append(obj)
    return out


def _write_sources_jsonl(run_dir: str, records: list[dict[str, Any]]) -> None:
    path = _sources_path(run_dir)
    lines = [json.dumps(r, ensure_ascii=False, sort_keys=True) for r in records]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + ("\n" if lines else ""))


def _append_timeline(
    run_dir: str, *, step: int, action: str, description: str, status: str
) -> None:
    entry = {
        "step": step,
        "action": action,
        "description": description,
        "status": status,
    }
    path = _timeline_path(run_dir)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")


def _update_run_json(
    run_dir: str,
    *,
    new_status: str,
    source_count: int,
    fetched_at: str,
) -> dict[str, Any]:
    rp = _run_json_path(run_dir)
    with open(rp, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise SystemExit("error: run.json is not a JSON object")
    data["status"] = new_status
    data["source_count"] = source_count
    data["fetched_at"] = fetched_at
    data["fetcher_version"] = TOOL_VERSION
    data["model_used"] = None  # Network fetcher, not a model.
    with open(rp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=True)
        f.write("\n")
    return data


def _update_index(
    run_id: str,
    *,
    new_status: str,
    source_count: int,
    fetched_at: str,
) -> None:
    idx_path = _index_path()
    if not os.path.isfile(idx_path):
        return
    with open(idx_path, "r", encoding="utf-8") as f:
        idx = json.load(f)
    if not isinstance(idx, dict) or not isinstance(idx.get("items"), list):
        return
    for item in idx["items"]:
        if isinstance(item, dict) and item.get("immutable_run_id") == run_id:
            item["status"] = new_status
            item["source_count"] = source_count
            item["fetched_at"] = fetched_at
            item["fetcher_version"] = TOOL_VERSION
            item["model_used"] = None
            break
    with open(idx_path, "w", encoding="utf-8") as f:
        json.dump(idx, f, indent=2, ensure_ascii=False, sort_keys=True)
        f.write("\n")


# ----------------------------------------------------------------------
# Sub-commands
# ----------------------------------------------------------------------

def cmd_inspect(args: argparse.Namespace) -> int:
    run_dir = _resolve_run_dir(args.run)
    run_id = _read_run_id(run_dir)
    print(f"run_id:        {run_id}")
    print(f"run_dir:       {run_dir}")

    rp = _run_json_path(run_dir)
    with open(rp, "r", encoding="utf-8") as f:
        run = json.load(f)
    print(f"status:        {run.get('status')}")
    print(f"source_count:  {run.get('source_count')}")
    print(f"citation_count:{run.get('citation_count')}")

    pending = _pending_path(run_dir)
    print(f"pending-sources.json: {'present' if os.path.isfile(pending) else 'absent'}")
    if os.path.isfile(pending):
        try:
            data = json.load(open(pending, "r", encoding="utf-8"))
            srcs = data.get("sources") or []
            print(f"  pending source count: {len(srcs)}")
        except Exception as exc:
            print(f"  (could not parse: {exc})")

    fetched_dir = _fetched_root(run_dir)
    if os.path.isdir(fetched_dir):
        subdirs = sorted(
            d for d in os.listdir(fetched_dir)
            if os.path.isdir(os.path.join(fetched_dir, d))
        )
        print(f"fetched/:      {len(subdirs)} source subdir(s)")
        for d in subdirs:
            print(f"  - {d}")
    else:
        print("fetched/:      absent")

    sources = _read_sources_jsonl(run_dir)
    real = [s for s in sources if s.get("url") or s.get("status") not in (None,)]
    placeholder = [
        s for s in sources
        if not s.get("url") and s.get("status") == "pending"
    ]
    fetched = [s for s in sources if s.get("status") == "fetched"]
    failed = [s for s in sources if s.get("status") == "failed"]
    print(f"sources.jsonl: {len(sources)} total ({len(fetched)} fetched, {len(failed)} failed, {len(placeholder)} placeholder)")
    return 0


def cmd_init_pending(args: argparse.Namespace) -> int:
    run_dir = _resolve_run_dir(args.run)
    run_id = _read_run_id(run_dir)
    pending = _pending_path(run_dir)
    if os.path.isfile(pending) and not args.force:
        print(f"pending-sources.json already exists at {pending} (use --force to overwrite)")
        return 0
    if args.dry_run:
        print(f"DRY-RUN: would create {pending} (no sources, run_id={run_id})")
        return 0
    payload = {
        "schema_version": 1,
        "run_id": run_id,
        "created_at": _utcnow_iso(),
        "updated_at": None,
        "approved_by": None,
        "notes": "Owner-approved URL list. Empty array means no fetches in this phase.",
        "sources": [],
    }
    _write_json_atomic(pending, payload)
    print(f"created {pending} (empty sources array, run_id={run_id})")
    return 0


def cmd_fetch(args: argparse.Namespace) -> int:
    run_dir = _resolve_run_dir(args.run)
    run_id = _read_run_id(run_dir)
    pending = _load_pending(run_dir)
    sources = pending.get("sources") or []
    if not sources:
        print("pending-sources.json has no sources; nothing to fetch.")
        if not args.dry_run:
            _append_timeline(
                run_dir,
                step=_next_timeline_step(run_dir),
                action="fetch_sources",
                description=f"Phase 6B fetch (v{TOOL_VERSION}) saw 0 approved sources.",
                status="skipped",
            )
        return 0

    # Validate every URL up front.
    print("validating URLs ...")
    validated: list[dict[str, Any]] = []
    for src in sources:
        try:
            safe_url, ips, _ = validate_url(src["url"])
        except UrlSafetyError as exc:
            print(f"  REJECT: {src['source_id']} -> {exc}")
            # In dry-run, the rejection is still a rejection; we record a
            # synthetic outcome for the sources.jsonl update below.
            validated.append({
                "src": src,
                "outcome": _failure_outcome(src["url"], f"url-safety-reject: {exc}"),
            })
            continue
        print(f"  OK:    {src['source_id']} -> {safe_url} (ips={ips})")
        if args.dry_run:
            artifact_dir = os.path.join(_fetched_root(run_dir), _safe_filename(src["source_id"]))
            rel_artifact = os.path.relpath(
                os.path.join(artifact_dir, _safe_artifact_basename("text/html")),
                run_dir,
            )
            validated.append({
                "src": src,
                "outcome": FetchOutcome(),  # empty; will be replaced if we actually fetch
                "dry_run_path": rel_artifact,
            })
        else:
            validated.append({"src": src})

    if args.dry_run:
        print()
        print("DRY-RUN: would perform the following:")
        for v in validated:
            src = v["src"]
            path = v.get("dry_run_path", "?")
            print(f"  - {src['source_id']}: GET {src['url']} -> {path}")
        print()
        print("DRY-RUN: would update run.json, sources.jsonl, timeline.jsonl, research/indexes/index.json.")
        return 0

    # Real fetch.
    all_records = _read_sources_jsonl(run_dir)
    by_source_id: dict[str, dict[str, Any]] = {}
    placeholder_lines: list[dict[str, Any]] = []
    for rec in all_records:
        sid = rec.get("source_id")
        if not sid:
            # Pre-existing placeholder line without source_id; preserve verbatim.
            placeholder_lines.append(rec)
            continue
        by_source_id[str(sid)] = rec
    timeline_step = _next_timeline_step(run_dir)
    fetched_count = 0
    failed_count = 0
    for v in validated:
        src = v["src"]
        if (
            "outcome" in v
            and v["outcome"].status == "failed"
            and v["outcome"].http_status is None
            and v["outcome"].error_message
            and v["outcome"].error_message.startswith("url-safety-reject")
        ):
            # Pre-flight URL safety rejection.
            outcome = v["outcome"]
        else:
            print(f"fetching {src['source_id']} -> {src['url']}")
            outcome = _do_fetch(src["url"])
        artifact_dir = os.path.join(
            _fetched_root(run_dir), _safe_filename(src["source_id"])
        )
        record = _persist_source(
            run_dir=run_dir,
            run_id=run_id,
            src=src,
            outcome=outcome,
            artifact_dir=artifact_dir,
            dry_run=False,
        )
        # Append/update source record.
        by_source_id[src["source_id"]] = record
        if outcome.status == "fetched":
            fetched_count += 1
            _write_source_notes_placeholder(run_dir, src, record)
        else:
            failed_count += 1
        _append_timeline(
            run_dir,
            step=timeline_step,
            action="fetch_source",
            description=f"Phase 6B fetch (v{TOOL_VERSION}) for {src['source_id']} -> {outcome.status}",
            status=outcome.status,
        )
        timeline_step += 1
        print(f"  -> {outcome.status} http={outcome.http_status} bytes={outcome.bytes_saved}")

    # Persist all source records: placeholders first, then real records.
    real_records = list(by_source_id.values())
    _write_sources_jsonl(run_dir, placeholder_lines + real_records)

    # Update run.json + index.
    new_status = "sources_fetched" if fetched_count > 0 and failed_count == 0 else "partial_fetch_failed"
    fetched_at = _utcnow_iso()
    source_count = sum(1 for r in real_records if r.get("status") == "fetched")
    _update_run_json(
        run_dir,
        new_status=new_status,
        source_count=source_count,
        fetched_at=fetched_at,
    )
    _update_index(
        run_id,
        new_status=new_status,
        source_count=source_count,
        fetched_at=fetched_at,
    )
    _append_timeline(
        run_dir,
        step=timeline_step,
        action="fetch_summary",
        description=f"Phase 6B fetch complete: fetched={fetched_count} failed={failed_count}",
        status="fetched" if failed_count == 0 else "partial",
    )

    print()
    print(f"summary: fetched={fetched_count} failed={failed_count} status={new_status}")
    return 0


def _failure_outcome(url: str, message: str) -> FetchOutcome:
    out = FetchOutcome()
    out.requested_url = url
    out.status = "failed"
    out.error_message = message
    return out


def _next_timeline_step(run_dir: str) -> int:
    path = _timeline_path(run_dir)
    if not os.path.isfile(path):
        return 1
    max_step = 0
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict) and isinstance(obj.get("step"), int):
                if obj["step"] > max_step:
                    max_step = obj["step"]
    return max_step + 1


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        prog=TOOL_NAME,
        description="Phase 6B owner-gated source fetcher for a research run.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_inspect = sub.add_parser("inspect", help="print run state and source counts (read-only)")
    p_inspect.add_argument("run", help="run id (e.g. 2026-06-06-sample-...) or absolute path")
    p_inspect.set_defaults(func=cmd_inspect)

    p_init = sub.add_parser(
        "init-pending", help="create pending-sources.json if missing"
    )
    p_init.add_argument("run", help="run id or absolute path")
    p_init.add_argument("--dry-run", action="store_true")
    p_init.add_argument("--force", action="store_true",
                        help="overwrite existing pending-sources.json")
    p_init.set_defaults(func=cmd_init_pending)

    p_fetch = sub.add_parser("fetch", help="fetch approved URLs and update run state")
    p_fetch.add_argument("run", help="run id or absolute path")
    p_fetch.add_argument("--dry-run", action="store_true")
    p_fetch.set_defaults(func=cmd_fetch)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
