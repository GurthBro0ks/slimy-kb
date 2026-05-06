# Install — Super Snail Lite Harness

## Copy into the project root

```bash
# from inside the extracted bundle
cp -a . /path/to/super-snail-project/
cd /path/to/super-snail-project
chmod +x init.sh snail-run scripts/*.sh scripts/*.py
```

## Initialize git if needed

```bash
git init
git remote add origin https://github.com/<your-user>/<your-repo>.git
```

## Run the safety gate

```bash
./snail-run init
./snail-run qa
```

## Safe GitHub sync

```bash
./snail-run sync "chore: install Super Snail lite harness"
```

## Generate an agent prompt

```bash
./snail-run prompt build "Create a proof-backed inventory and quarantine suspect rewrite scripts."
```

Copy the output into Claude Code, Codex, OpenCode, or OpenClaw.

## Safety note

This project may contain proprietary or account-sensitive artifacts. The autosync script uses an allowlist and fails closed if raw artifacts are staged.
