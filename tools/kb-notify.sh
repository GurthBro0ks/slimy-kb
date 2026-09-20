#!/usr/bin/env bash
# Architecture B: categories are metadata; the Harness owns the single destination.
# Usage: kb-notify.sh --route daily|changelog|recommend|alerts --message TEXT
set -euo pipefail
exec python3 - "$@" <<'PY'
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import socket
import subprocess
import sys
from datetime import datetime, timezone

parser = argparse.ArgumentParser(description="Credential-free NUC2 Harness client")
parser.add_argument("--route", required=True,
                    choices=("daily", "changelog", "recommend", "alerts"))
parser.add_argument("--message", required=True)
args = parser.parse_args()

# Pin the sole sanctioned adapter, from a0e0031a262ec97432e01416d780a16dc40dd25c.
adapter = Path("/home/slimy/slimy-harness/sequencer/notify-proof-dir-complete.sh")
adapter_sha256 = "fdcb90721a8eb59553b67de32efe0bc50fc00e835d64c5a8745e4d743378d4f1"
state = Path("/home/slimy/harness-logs/notify-state")
events = Path("/home/slimy/harness-logs/kb-notify")

def relay_redact(value):
    # Same webhook/assignment suppression as the adapter, before persistence too.
    value = re.sub(r"https://discord(?:app)?\.com/api/" + r"webhooks/\S+",
                   "[REDACTED-WEBHOOK]", value)
    value = value.replace("DISCORD_HARNESS_WEBHOOK_URL", "[REDACTED-WEBHOOK]")
    return re.sub(r"(?i)(password|token|secret|key)=\S+", r"\1=[REDACTED]", value)

message = relay_redact(args.message)
key = hashlib.sha256((args.route + "\0" + message).encode()).hexdigest()
event = events / key
host = ""

def fail(rc, reason, ssh_rc="not_attempted"):
    safe_host = relay_redact(host).replace("\n", " ").replace("\r", " ") or "unset"
    diagnostic = (f"WARN route={args.route} host={safe_host} rc={rc} "
                  f"ssh_exit_code={ssh_rc} reason={reason}")
    print("[kb-notify] " + diagnostic, file=sys.stderr)
    try:
        state.mkdir(parents=True, exist_ok=True)
        marker = state / ("kb-" + key + ".relay-failed")
        marker.write_text(json.dumps({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "route": args.route, "relay_host": safe_host,
            "relay_status": "failed", "adapter_exit_code": rc,
            "ssh_exit_code": ssh_rc, "reason": reason,
        }) + "\n")
        marker.chmod(0o600)
    except OSError:
        print("[kb-notify] WARN failure marker unavailable", file=sys.stderr)
    sys.exit(rc)

os.umask(0o077)
try:
    if "HARNESS_NOTIFY_RELAY_HOST" in os.environ:
        host = os.environ["HARNESS_NOTIFY_RELAY_HOST"]
    else:
        # Parse only the nonsecret pointer as data; never source configuration.
        config = Path("/home/slimy/.slimy-harness.env")
        if config.is_file():
            for line in config.read_text().splitlines():
                match = re.fullmatch(r"\s*(?:export\s+)?HARNESS_NOTIFY_RELAY_HOST\s*=(.*)", line)
                if match:
                    words = shlex.split(match[1], comments=True)
                    host = words[0] if len(words) == 1 else ""
    if not host:
        fail(67, "relay_host_missing")
    if not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.@-]*", host):
        host = "invalid"
        fail(67, "relay_host_invalid")
    if "nuc2" not in socket.gethostname().lower():
        fail(67, "nuc2_required")
    if not adapter.is_file() or hashlib.sha256(adapter.read_bytes()).hexdigest() != adapter_sha256:
        fail(69, "sanctioned_adapter_unavailable")

    event.mkdir(parents=True, exist_ok=True)
    # Arguments and JSON carry data; no message text becomes executable source.
    metadata = {"repo_path": "/home/slimy/kb", "repo_name": "slimy-kb",
                "feature_id": "kb-" + args.route, "task_title": "KB " + args.route,
                "source_nuc": "nuc2", "agent": "manual", "summary": message,
                "status": "fail" if args.route == "alerts" else "completed"}
    (event / "harness-metadata.json").write_text(json.dumps(metadata) + "\n")
    # No inherited credential, alternate adapter/root, env-file, or local-send path.
    clean_env = {"PATH": "/usr/bin:/bin", "HOME": "/home/slimy",
                 "HARNESS_ROOT": "/home/slimy/slimy-harness",
                 "HARNESS_ENV_FILE": "/dev/null",
                 "HARNESS_NOTIFY_RELAY_HOST": host,
                 "PYTHONDONTWRITEBYTECODE": "1"}
    result = subprocess.run([
        "/bin/bash", str(adapter), "--require-relay", "--proof-dir", str(event),
        "--repo-path", metadata["repo_path"], "--repo-name", metadata["repo_name"],
        "--feature-id", metadata["feature_id"], "--task-title", metadata["task_title"],
        "--source-nuc", "nuc2", "--agent", "manual", "--status", metadata["status"],
        "--summary", message,
    ], env=clean_env, cwd=event, capture_output=True, text=True)
    if result.stdout:
        print(relay_redact(result.stdout), end="")
    if result.stderr:
        print(relay_redact(result.stderr), end="", file=sys.stderr)
    if result.returncode:
        match = re.search(r"ssh_exit_code=(\d+)", result.stderr)
        fail(result.returncode if result.returncode > 0 else 70, "relay_failed",
             match[1] if match else "not_reported")
except (OSError, ValueError):
    fail(69, "local_notification_error")
PY
