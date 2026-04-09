#!/usr/bin/env python3
"""
collect_repo_digests.py — Compact digest of all known repos on NUC2.
Output: /home/slimy/kb/raw/research/YYYY-MM-DD-nuc2-repo-digests.md
"""
import os
import subprocess
import json
from datetime import datetime, timezone
from pathlib import Path

HOST = os.uname()[1]
TIMESTAMP = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
DATE = TIMESTAMP[:10]
OUTPUT_DIR = Path("/home/slimy/kb/raw/research")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / f"{DATE}-{HOST}-repo-digests.md"

# Known repos on NUC2 (from server-state.md / project map)
REPOS = {
    "slimy-monorepo": "/home/slimy/slimy-monorepo",
    "mission-control": "/home/slimy/mission-control",
    "clawd": "/home/slimy/clawd",
    "pm_updown_bot_bundle": "/home/slimy/pm_updown_bot_bundle",
    "mailbox_ingest": "/home/slimy/nuc-comms/mailbox_ingest",
    "agents-backup-full": "/home/slimy/agents-backup-full",
    "mailbox": "/home/slimy/nuc-comms/mailbox.git",
    "workspace": "/home/slimy/.openclaw/workspace",
    "git-notes-ledger": "/home/slimy/.openclaw/memory/git-notes-ledger",
    "mcp_agent_mail": "/home/slimy/.mcp_agent_mail_git_mailbox_repo",
    "slimyai-web": "/home/slimy/slimy-web",
    "nuc-comms": "/home/slimy/nuc-comms",
    "kb": "/home/slimy/kb",
}

KB_MARKERS = {
    "AGENTS.md": "has_agents_md",
    "package.json": "has_package_json",
    "pyproject.toml": "has_pyproject",
    "Cargo.toml": "has_rust",
    "systemd": ".service or .timer in ~/.config/systemd/user",
}

lines = []
lines.append(f"# NUC2 Repo Digests — {TIMESTAMP}")
lines.append("")
lines.append(f"**Host:** {HOST}")
lines.append(f"**Timestamp:** {TIMESTAMP}")
lines.append("")

for name, path in sorted(REPOS.items()):
    lines.append(f"## {name}")
    lines.append(f"- **Path:** `{path}`")

    if not os.path.exists(path):
        lines.append("- **Status:** PATH NOT FOUND")
        lines.append("")
        continue

    is_git = os.path.exists(os.path.join(path, ".git"))
    lines.append(f"- **Git:** {is_git}")

    if is_git:
        try:
            rev = subprocess.run(
                ["git", "-C", path, "rev-parse", "--short", "HEAD"],
                capture_output=True, text=True, timeout=5
            )
            commit = rev.stdout.strip() if rev.returncode == 0 else "?"

            subject = subprocess.run(
                ["git", "-C", path, "log", "--oneline", "-1", "--format=%s"],
                capture_output=True, text=True, timeout=5
            )
            subject_str = subject.stdout.strip() if subject.returncode == 0 else "?"

            branch = subprocess.run(
                ["git", "-C", path, "branch", "--show-current"],
                capture_output=True, text=True, timeout=5
            )
            branch_str = branch.stdout.strip() if branch.returncode == 0 else "?"

            dirty = subprocess.run(
                ["git", "-C", path, "diff", "--stat"],
                capture_output=True, text=True, timeout=5
            )
            is_dirty = dirty.stdout.strip() != "" if dirty.returncode == 0 else False

            lines.append(f"- **Branch:** {branch_str}")
            lines.append(f"- **Commit:** {commit}")
            lines.append(f"- **Subject:** {subject_str}")
            lines.append(f"- **Dirty:** {is_dirty}")

            # Check origin remote
            remote = subprocess.run(
                ["git", "-C", path, "remote", "get-url", "origin"],
                capture_output=True, text=True, timeout=5
            )
            if remote.returncode == 0:
                lines.append(f"- **Origin:** {remote.stdout.strip()}")

        except subprocess.TimeoutExpired:
            lines.append("- **Git:** TIMEOUT")
        except Exception as e:
            lines.append(f"- **Git:** ERROR ({e})")
    else:
        # Not a git repo — just check key markers
        for marker, label in KB_MARKERS.items():
            if marker.startswith("systemd"):
                has_sysd = any(
                    f.endswith(".service") or f.endswith(".timer")
                    for f in os.listdir(os.path.expanduser("~/.config/systemd/user/"))
                ) if os.path.exists(os.path.expanduser("~/.config/systemd/user/")) else False
                lines.append(f"- **{label}:** {has_sysd}")
            elif os.path.exists(os.path.join(path, marker)):
                lines.append(f"- **{label}:** yes")

    # Package presence
    if os.path.exists(os.path.join(path, "package.json")):
        try:
            import json
            with open(os.path.join(path, "package.json")) as f:
                pkg = json.load(f)
                lines.append(f"- **Name:** {pkg.get('name', 'unknown')}")
                lines.append(f"- **Version:** {pkg.get('version', '?')}")
        except:
            pass

    lines.append("")

lines.append("## Summary")
lines.append("")
total = len(REPOS)
found = sum(1 for _, p in REPOS.items() if os.path.exists(p))
lines.append(f"- Tracked repos: {total}")
lines.append(f"- Present: {found}")
lines.append(f"- Missing: {total - found}")

with open(OUTPUT_FILE, "w") as f:
    f.write("\n".join(lines) + "\n")

print(f"Repo digests: {OUTPUT_FILE}")
