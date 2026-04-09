# NUC2 State Digest

**Timestamp:** 2026-04-09T15:11:16Z
**Host:** slimy-nuc2

## Systemd User Services

-   dbus.service               loaded active running D-Bus User Message Bus
-   gpg-agent.service          loaded active running GnuPG cryptographic agent and passphrase cache
-   mission-control.service    loaded active running Mission Control (chriss.slimyai.xyz)
-   openclaw-gateway.service   loaded active running OpenClaw Gateway (v2026.2.23)
-   slimy-mysql-tunnel.service loaded active running SSH tunnel for MySQL to NUC1
-   slimy-web.service          loaded active running Slimy Web (Next.js standalone on port 3000)

## Systemd User Timers

Fri 2026-04-10 02:32:57 UTC      11h Thu 2026-04-09 14:32:57 UTC    38min ago kb-maintenance.timer           kb-maintenance.service
Fri 2026-04-10 03:09:42 UTC      11h Thu 2026-04-09 15:09:42 UTC 1min 34s ago wiki-manager-stage1.timer      wiki-manager-stage1.service

## KB Maintenance Timer Status

- Fri 2026-04-10 02:32:57 UTC      11h Thu 2026-04-09 14:32:57 UTC    38min ago kb-maintenance.timer           kb-maintenance.service

## Active PM2 Processes

- │ 0  │ obsidian-headless-sync    │ default     │ N/A     │ fork    │ 169392   │ 29h    │ 0    │ online    │ 0%       │ 83.2mb   │ slimy    │ disabled │

## Network Listening Ports (KB-relevant)

- LISTEN 0      511                        0.0.0.0:3838       0.0.0.0:*    users:(("next-server (v1",pid=1731,fd=21))  
- LISTEN 0      128                        0.0.0.0:3850       0.0.0.0:*    users:(("python3",pid=1228,fd=3))           
- LISTEN 0      511                        0.0.0.0:3000       0.0.0.0:*    users:(("next-server (v1",pid=215978,fd=21))
- LISTEN 0      200                      127.0.0.1:5432       0.0.0.0:*                                                
- LISTEN 0      511                  192.168.68.65:443        0.0.0.0:*                                                
- LISTEN 0      511                  192.168.68.65:80         0.0.0.0:*                                                
- LISTEN 0      128                      127.0.0.1:3307       0.0.0.0:*    users:(("ssh",pid=1734,fd=5))               
- LISTEN 0      4096                100.105.119.62:443        0.0.0.0:*                                                
- LISTEN 0      511                      127.0.0.1:18790      0.0.0.0:*    users:(("openclaw-gatewa",pid=1732,fd=23))  
- LISTEN 0      511                      127.0.0.1:18793      0.0.0.0:*    users:(("openclaw-gatewa",pid=1732,fd=28))  
- LISTEN 0      511                      127.0.0.1:18792      0.0.0.0:*    users:(("openclaw-gatewa",pid=1732,fd=29))  
- LISTEN 0      4096                     127.0.0.1:443        0.0.0.0:*                                                
- LISTEN 0      4096                     127.0.0.1:80         0.0.0.0:*                                                
- LISTEN 0      4096   [fd7a:115c:a1e0::5737:773e]:443           [::]:*                                                
- LISTEN 0      128                          [::1]:3307          [::]:*    users:(("ssh",pid=1734,fd=4))               
- LISTEN 0      511                          [::1]:18790         [::]:*    users:(("openclaw-gatewa",pid=1732,fd=24))  

## Disk Usage (KB-relevant paths)

- /home/slimy/kb: 7.3M
- /home/slimy: 36G
