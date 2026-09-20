#!/usr/bin/env python3
"""Accepted FR-2 T1-T10 only. Run with --evidence-dir under the checkpoint proof.

Production consumers are never executed: copies relocate /home/slimy and
/opt/slimy into fixtures. The adapter copy has only these path relocations;
its fixture checksum replaces the production checksum in the helper copy.
PATH stubs deny transport and git mutation; bash intercepts helper calls.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
NAMES = ["kb-calendar-sync.sh", "kb-changelog-rollup.sh", "kb-compile-if-needed.sh",
         "kb-recommend.sh", "kb-todo.sh", "kb-version-scan.sh",
         "slimy-agent-finish.sh", "slimy-session-finish.sh"]
ROUTES = ["daily", "changelog", "alerts", "recommend", "daily", "changelog", "alerts", "alerts"]
ADAPTER = Path("/home/slimy/slimy-harness/sequencer/notify-proof-dir-complete.sh")
ADAPTER_HASH = "fdcb90721a8eb59553b67de32efe0bc50fc00e835d64c5a8745e4d743378d4f1"
ALL = NAMES + ["kb-notify.sh"]

def check(ok, message):
    if not ok:
        raise AssertionError(message)

def write(path, text, executable=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    if executable:
        path.chmod(0o700)

def snapshot():
    base = Path("/home/slimy/.config/systemd/user")
    paths = []
    for stem in ("kb-daily-note", "kb-maintenance"):
        for suffix in ("timer", "service"):
            path = base / (stem + "." + suffix)
            check(path.is_file(), "T8 required unit missing")
            paths.append(path)
            drop = base / (path.name + ".d")
            if drop.exists():
                paths.extend(drop.glob("*.conf"))
    return {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}

class Fixture:
    def __init__(self, base, label, host="fixture-unavailable"):
        self.base = base / label
        check(not self.base.exists(), "fixture must be fresh")
        self.home = self.base / "home"
        self.kb = self.home / "kb"
        self.bin = self.base / "bin"
        self.log = self.base / "calls.jsonl"
        self.host = host
        for d in (self.kb / "raw", self.kb / "wiki", self.kb / "output",
                  self.bin, self.base / "tmp", self.home / "obsidian/slimyai-vault/Daily"):
            d.mkdir(parents=True, exist_ok=True)
        write(self.kb / "raw/fixture.md", "# Synthetic compile candidate\n")
        write(self.kb / "wiki/example.md", "# Fixture\n")
        adapter_text = self.relocate(ADAPTER.read_text())
        relocated_adapter = self.home / "slimy-harness/sequencer/notify-proof-dir-complete.sh"
        write(relocated_adapter, adapter_text)
        adapter_hash = hashlib.sha256(adapter_text.encode()).hexdigest()
        for name in ALL:
            text = self.relocate((TOOLS / name).read_text())
            if name == "kb-notify.sh":
                text = text.replace(ADAPTER_HASH, adapter_hash)
                text = text.replace('"PATH": "/usr/bin:/bin"',
                                    '"PATH": ' + json.dumps(str(self.bin) + ":/usr/bin:/bin"))
            write(self.kb / "tools" / name, text)
        # Safe data-only config; never inspect the machine-local config.
        write(self.home / ".slimy-harness.env", "HARNESS_NOTIFY_RELAY_HOST=fixture-unavailable\n")
        # Stubs read their fixture root from __file__, never embed dynamic data in code.
        stub = '''#!/usr/bin/python3
import json, os, pathlib, subprocess, sys
base = pathlib.Path(__file__).resolve().parent.parent
name = pathlib.Path(sys.argv[0]).name
args = sys.argv[1:]
with (base / "calls.jsonl").open("a") as f:
    f.write(json.dumps([name, args]) + "\\n")
if name in ("ssh", "scp", "curl", "wget", "nc", "sftp"):
    if name == "ssh":
        print("synthetic transport unavailable", file=sys.stderr)
    sys.exit(255)
if name == "hostname":
    print("slimy-nuc2")
    sys.exit(0)
if name == "systemctl":
    if args[:2] == ["--user", "is-failed"]:
        print("inactive")
        sys.exit(1)
    if args[:2] == ["--user", "is-active"]:
        print("active")
        sys.exit(0)
    sys.exit(99)
if name == "claude":
    # Empty output forces C3's existing failure branch directly.
    sys.exit(1)
if name == "git":
    if "push" in args:
        print("fatal: synthetic push unavailable")
        sys.exit(1)
    if "rev-parse" in args:
        sys.exit(1)
    sys.exit(0)
if name == "mktemp":
    os.environ["TMPDIR"] = str(base / "tmp")
    os.execv("/usr/bin/mktemp", ["mktemp"] + args)
if name == "bash":
    # Intercept each consumer's helper invocation and allow fixture scripts only.
    if not args or not pathlib.Path(args[0]).resolve().is_relative_to(base):
        sys.exit(99)
    os.execv("/bin/bash", ["bash"] + args)
sys.exit(99)
'''
        for name in ("bash", "git", "hostname", "systemctl", "claude", "mktemp",
                     "ssh", "scp", "curl", "wget", "nc", "sftp"):
            write(self.bin / name, stub, True)

    def relocate(self, text):
        return text.replace("/home/slimy", str(self.home)).replace("/opt/slimy", str(self.base / "opt"))

    def calls(self, name):
        if not self.log.exists():
            return []
        return [args for command, args in map(json.loads, self.log.read_text().splitlines()) if command == name]

    def run(self, consumer=None, message="Synthetic fixture event", inherited=None, exit_hook=False):
        env = {"PATH": str(self.bin) + ":/usr/bin:/bin", "HOME": str(self.home),
               "TMPDIR": str(self.base / "tmp"), "PYTHONDONTWRITEBYTECODE": "1"}
        if self.host is not None:
            env["HARNESS_NOTIFY_RELAY_HOST"] = self.host
        if inherited:
            env.update(inherited)
        if consumer is None:
            command = ["/bin/bash", str(self.kb / "tools/kb-notify.sh"),
                       "--route", "alerts", "--message", message]
        elif consumer == 8:
            # C8 is an EXIT-hook library: exercise the error branch explicitly.
            command = ["/bin/bash", "-c",
                       ('source "$1"; exit 1' if exit_hook else
                        'source "$1"; trap - EXIT; run_bounded_finish'), "fixture",
                       str(self.kb / "tools" / NAMES[7])]
        else:
            command = ["/bin/bash", str(self.kb / "tools" / NAMES[consumer - 1])]
            if consumer == 3:
                command += ["run", "--force"]
            if consumer == 7:
                command += ["--agent", "codex", "--skip-compile", "--summary", "Synthetic finish"]
        result = subprocess.run(command, env=env, cwd=self.base, capture_output=True, text=True, timeout=30)
        # Only synthetic fixture evidence is persisted.
        write(self.base / "stdout.txt", result.stdout)
        write(self.base / "stderr.txt", result.stderr)
        write(self.base / "returncode.txt", str(result.returncode) + "\n")
        return result

    def helpers(self):
        return [a for a in self.calls("bash") if a and a[0].endswith("/kb-notify.sh")]

    def markers(self, suffix):
        return list((self.home / "harness-logs/notify-state").glob("*.relay-" + suffix))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--c3-only", action="store_true")
    args = parser.parse_args()
    base = args.evidence_dir.resolve()
    base.mkdir(parents=True, exist_ok=True)
    check(hashlib.sha256(ADAPTER.read_bytes()).hexdigest() == ADAPTER_HASH, "adapter dependency changed")
    units_before = snapshot()
    write(base / "units-before.json", json.dumps(units_before, indent=2) + "\n")
    if args.c3_only:
        f = Fixture(base, "c3-direct")
        r = f.run(3)
        assert_loud(f, r, 3)
        check(list((f.kb / "output").glob("compile-failure-*.md")), "C3 failure artifact missing")
        check(len(f.calls("claude")) == 1, "C3 child not directly forced")
        print("C3_DIRECT_FORCED_TEST=PASS")
        return

    for name in ALL:
        check("webhooks.env" not in (TOOLS / name).read_text(), "T1 dependency survived")
    # Scan runtime tools generally; tests intentionally name the forbidden dependency.
    for path in TOOLS.rglob("*"):
        if path.is_file() and "tests" not in path.relative_to(TOOLS).parts and path.suffix in (".sh", ".py"):
            check("webhooks.env" not in path.read_text(), "T1 tools dependency survived")
    print("T1=PASS static dependency removed from 8/8 and runtime tools")

    for name in ALL:
        text = (TOOLS / name).read_text()
        check(not re.search(r"\$\{?DISCORD_", text), "T2 credential variable read")
        check(not re.search(r"os\.environ.*DISCORD_", text), "T2 credential environment read")
    helper = (TOOLS / "kb-notify.sh").read_text()
    check('"HARNESS_ENV_FILE": "/dev/null"' in helper and 'env=clean_env' in helper,
          "T2 adapter environment not isolated")
    boundary = Fixture(base, "boundary")
    fake_config = boundary.base / "must-not-source.sh"
    write(fake_config, "exit 98\n")
    r = boundary.run(inherited={"HARNESS_ENV_FILE": str(fake_config),
                               "HARNESS_ROOT": str(boundary.base / "wrong-adapter"),
                               "DISCORD_HARNESS_WEBHOOK_URL": "SYNTHETIC_NOT_A_URL"})
    check(r.returncode == 70 and len(boundary.calls("ssh")) == 1,
          "T2 inherited environment bypassed sanctioned relay")
    print("T2=PASS credential-free consumers/helper; adapter environment allowlisted")

    runs = {}
    for n in range(1, 9):
        f = Fixture(base, "c" + str(n))
        r = f.run(n)
        calls = f.helpers()
        # C8 wraps C7: preserve the inherited alert plus the wrapper's own alert.
        check(len(calls) == (2 if n == 8 else 1), "T3 helper call count C" + str(n))
        for call in calls:
            check(call[call.index("--route") + 1] == ROUTES[n - 1], "T3 wrong category")
        runs[n] = (f, r)
    print("T3=PASS intercepted all eight categories; C8-to-C7 topology preserved")

    for n in (3, 7, 8):
        assert_loud(*runs[n], n)
    hook = Fixture(base, "c8-exit-hook")
    hook_result = hook.run(8, exit_hook=True)
    assert_loud(hook, hook_result, 8)
    print("T4=PASS C3 direct/forced, C7 and C8 loud failures; failed markers only")

    missing = Fixture(base, "missing-host", host="")
    r = missing.run()
    check(r.returncode == 67 and missing.markers("failed") and not missing.calls("ssh"), "T5 empty host")
    check("host=unset" in r.stderr and "ssh_exit_code=not_attempted" in r.stderr, "T5 missing host diagnostic")
    for n, (f, r) in runs.items():
        if n in (1, 2, 4, 5, 6):
            check(r.returncode == 0 and "WARN" in r.stderr, "T5 warn-and-continue")
        check(len(f.calls("ssh")) == (2 if n == 8 else 1), "T5 retry or missing attempt")
        check(all(a[-1] == "true" for a in f.calls("ssh")), "T5 went beyond failed V14 probe")
        check(not f.calls("scp"), "T5 copied after failure")
    print("T5=PASS empty host fail-closed; one attempt per event; informational jobs continue")

    payload = Fixture(base, "payload", host=None)
    message = "Synthetic 'quote' \\" + '"' + " line\n$(touch SENTINEL) `touch SENTINEL`\n雪"
    r = payload.run(message=message)
    check(r.returncode == 70, "T6 failed relay status")
    reports = list((payload.home / "slimy-kb/raw/sessions").glob("report-proof-*.json"))
    check(len(reports) == 1, "T6 report count")
    report = json.loads(reports[0].read_text())
    check(report["summary"] == message and report["feature_id"] == "kb-alerts" and
          report["source_nuc"] == "nuc2" and report["task_title"] == "KB alerts", "T6 metadata shape")
    check(not list(payload.base.rglob("SENTINEL")), "T6 payload executed")
    redacted = Fixture(base, "redaction")
    r = redacted.run(message="Synthetic token=FAKE_ONLY password=FAKE_ONLY secret=FAKE_ONLY key=FAKE_ONLY")
    for path in redacted.base.rglob("*"):
        if path.is_file() and path.suffix in (".json", ".txt", ".relay-failed"):
            check("FAKE_ONLY" not in path.read_text(), "T6 synthetic diagnostic not suppressed")
    print("T6=PASS nonsecret payload round-trip and redaction; metacharacters remain data")

    patterns = {1: "../obsidian/slimyai-vault/Daily/*.md", 2: "output/changelog-*.md",
                3: "output/compile-failure-*.md", 4: "output/recommend-*.md",
                5: "output/todo-*.md", 6: "output/versions-*.md",
                7: "raw/agent-learnings/*.md", 8: "raw/changelogs/*.md"}
    for n, (f, r) in runs.items():
        check(list(f.kb.glob(patterns[n])), "T7 primary artifact missing C" + str(n))
    check("SKIP_COMPILE set" in runs[7][1].stdout and "Finish automation failed" in runs[8][1].stdout,
          "T7 finish work/wrapping missing")
    print("T7=PASS all eight primary work products/finish wrapping retained")

    units_after = snapshot()
    write(base / "units-after.json", json.dumps(units_after, indent=2) + "\n")
    check(units_before == units_after, "T8 units changed")
    for f, _ in runs.values():
        check(all(a[:2] in (["--user", "is-active"], ["--user", "is-failed"])
                  for a in f.calls("systemctl")), "T8 service mutation attempted")
    print("T8=PASS four unit files byte-identical; no service mutation calls")

    diff = subprocess.run(["git", "-C", str(ROOT), "diff", "--", *["tools/" + n for n in ALL]],
                          capture_output=True, text=True, check=True).stdout
    # Names/regexes and the reviewed source-code checksum are not credentials.
    suspect = re.compile(r"https://discord(?:app)?\.com/api/" + r"webhooks/[0-9]+/\S+|"
                         r"(?:mfa\.[A-Za-z0-9_-]{20,}|[A-Za-z0-9_-]{24}\.[A-Za-z0-9_-]{6}\.[A-Za-z0-9_-]{27,})|"
                         r"-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----")
    texts = [(TOOLS / n).read_text() for n in ALL] + [diff, Path(__file__).read_text()]
    check(not any(suspect.search(text) for text in texts), "T9 suspected credential; value suppressed")
    print("T9=PASS changed files/diff secret scan; no candidate values printed")

    for log in base.rglob("calls.jsonl"):
        calls = list(map(json.loads, log.read_text().splitlines()))
        check(not any(name in ("curl", "wget", "scp", "nc", "sftp") for name, _ in calls), "T10 forbidden transport")
        check(all("fixture-unavailable" in a and a[-1] == "true" for name, a in calls if name == "ssh"),
              "T10 unexpected relay target/command")
    print("T10=PASS only denied synthetic SSH probes; zero outbound delivery or NUC1 contact")

def assert_loud(f, result, n):
    check(result.returncode == 70, "T4 caller did not reflect lost alert C" + str(n))
    check("WARN route=alerts host=fixture-unavailable rc=70 ssh_exit_code=255" in result.stderr,
          "T4 diagnostic missing C" + str(n))
    check(f.markers("failed") and not f.markers("sent"), "T4 marker semantics C" + str(n))
    if n in (7, 8):
        check("Finish automation complete." not in result.stdout, "T4 misleading completion")
    if n == 3:
        check(len(f.calls("claude")) == 1, "T4 C3 not forced")

if __name__ == "__main__":
    try:
        main()
    except (AssertionError, subprocess.SubprocessError) as error:
        print("FR2_TEST_FAILURE=" + str(error), file=sys.stderr)
        sys.exit(1)
