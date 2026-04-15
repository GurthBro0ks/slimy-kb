# NUC2 State Digest

**Timestamp:** 2026-04-15T17:25:47Z
**Host:** slimy-nuc2

## Systemd User Services

- (none)

## Systemd User Timers

Thu 2026-04-16 00:22:03 UTC   6h Wed 2026-04-15 12:22:03 UTC 5h 3min ago kb-maintenance.timer           kb-maintenance.service
Thu 2026-04-16 00:22:03 UTC   6h Wed 2026-04-15 12:22:03 UTC 5h 3min ago wiki-manager-stage1.timer      wiki-manager-stage1.service

## KB Maintenance Timer

Thu 2026-04-16 00:22:03 UTC   6h Wed 2026-04-15 12:22:03 UTC 5h 3min ago kb-maintenance.timer           kb-maintenance.service

## Active PM2 Processes

│ 0  │ obsidian-headless-sync    │ default     │ N/A     │ fork    │ 5365     │ 2D     │ 190  │ online    │ 0%       │ 81.3mb   │ slimy    │ disabled │

## Network Listening Ports (KB-relevant)

LISTEN 0      200                      127.0.0.1:5432       0.0.0.0:*                                              
LISTEN 0      511                  192.168.68.65:80         0.0.0.0:*                                              
LISTEN 0      511                  192.168.68.65:443        0.0.0.0:*                                              
LISTEN 0      4096                     127.0.0.1:80         0.0.0.0:*                                              
LISTEN 0      4096                     127.0.0.1:443        0.0.0.0:*                                              
LISTEN 0      128                        0.0.0.0:3850       0.0.0.0:*    users:(("python3",pid=1009,fd=3))         
LISTEN 0      511                        0.0.0.0:3838       0.0.0.0:*    users:(("next-server (v1",pid=2447,fd=21))
LISTEN 0      511                        0.0.0.0:3000       0.0.0.0:*    users:(("next-server (v1",pid=2451,fd=21))
LISTEN 0      511                      127.0.0.1:18792      0.0.0.0:*    users:(("openclaw-gatewa",pid=2448,fd=30))
LISTEN 0      511                      127.0.0.1:18793      0.0.0.0:*    users:(("openclaw-gatewa",pid=2448,fd=31))
LISTEN 0      511                      127.0.0.1:18790      0.0.0.0:*    users:(("openclaw-gatewa",pid=2448,fd=21))
LISTEN 0      4096                100.105.119.62:443        0.0.0.0:*                                              
LISTEN 0      128                      127.0.0.1:3307       0.0.0.0:*    users:(("ssh",pid=2449,fd=5))             
LISTEN 0      128                          [::1]:3307          [::]:*    users:(("ssh",pid=2449,fd=4))             
LISTEN 0      511                          [::1]:18790         [::]:*    users:(("openclaw-gatewa",pid=2448,fd=24))
LISTEN 0      4096   [fd7a:115c:a1e0::5737:773e]:443           [::]:*                                              

## Disk Usage (KB-relevant paths)

12M	/home/slimy/kb
36G	/home/slimy
- /home/slimy: (unable to measure)

## Uptime

 17:25:50 up 2 days, 17:12,  2 users,  load average: 1.54, 0.86, 0.43

## KB Git Status

 M tools/wiki_manager_stage1.py
 M tools/wiki_manager_stage1.sh
?? raw/research/2026-04-15-slimy-nuc2-state.md
?? tools/__pycache__/
- ahead: 0
- behind: 0

## KB Health Snapshot

- orphans (total): 30
- weak-links (total): 8

## KB Raw Files (recent, 48h)

- 7 raw/*.md files modified in last 48h

## Vault Sync Status

│ status            │ online                                                            │
│ uptime            │ 2D                                                                │
