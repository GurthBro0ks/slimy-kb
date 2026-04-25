# Chriss Agent
> Category: projects
> Sources: raw/decisions/2026-04-05-project-chriss-agent-nuc2-state.md
> Created: 2026-04-05
> Status: draft

<!-- KB METADATA
> Last edited: 2026-04-24 12:32 UTC (git)
> Version: r37 / 11541da
KB METADATA -->

Chriss Agent is a webhook bridge service running on NUC2, providing a Python-based HTTP bridge on port 3850.

## Runtime State (NUC2 — 2026-04-05)
- **Path:** `/home/slimy/chriss-agent`
- **Remote:** none (not a git repo)
- **Process:** `python3 /home/slimy/chriss-agent/scripts/webhook-bridge.py`
- **PID:** 1178942
- **Port:** **3850**
- **Running since:** 2026-03-14
- **Classification:** ACTIVE | Confidence: HIGH

## Service Management
- Managed by `chriss-bridge.service` (systemd --user, inferred)
- No PM2 involvement
- Process survives independently since mid-March 2026

## KB Gap
- No wiki/projects/ article existed before this session
- Explicitly flagged as HIGH-priority missing article in NUC2 project discovery
- No references found in Cross-NUC Communication Matrix or NUC Topology

## See Also
- [NUC Topology and Services](../architecture/nuc-topology-and-services.md)
- [Cross-NUC Communication Matrix](../architecture/cross-nuc-communication-matrix.md)
