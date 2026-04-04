# NUC1 Running Services
> Source: NUC1 process inspection
> Captured: 2026-04-04

## PM2 Processes
```
┌────┬─────────────────┬─────────────┬─────────┬─────────┬──────────┬────────┬──────┬───────────┬──────────┬──────────┬──────────┬──────────┐
│ id │ name            │ namespace   │ version │ mode    │ pid      │ uptime │ ↺    │ status    │ cpu      │ mem      │ user     │ watching │
├────┼─────────────────┼─────────────┼─────────┼─────────┼──────────┼────────┼──────┼───────────┼──────────┼──────────┼──────────┼──────────┤
│ 0  │ agent-loop      │ default     │ N/A     │ fork    │ 3070551  │ 10D    │ 2    │ online    │ 0%       │ 17.3mb   │ slimy    │ disabled │
│ 10 │ slimy-bot-v2    │ default     │ 0.1.0   │ fork    │ 1561344  │ 12h    │ 2    │ online    │ 0%       │ 110.1mb  │ slimy    │ disabled │
└────┴─────────────────┴─────────────┴─────────┴─────────┴──────────┴────────┴──────┴───────────┴──────────┴──────────┴──────────┴──────────┘
```

## Docker Containers
```
NAMES                           STATUS                 PORTS
slimy-mysql                     Up 2 weeks (healthy)   0.0.0.0:3306->3306/tcp, [::]:3306->3306/tcp, 33060/tcp
database                        Up 5 weeks             192.168.68.64:27017->27017/tcp
slimy-chat_caddy_1              Up 2 weeks             443/udp, 2019/tcp, 0.0.0.0:8080->80/tcp, [::]:8080->80/tcp, 0.0.0.0:8443->443/tcp, [::]:8443->443/tcp
f800ed3ac6ec_slimy-chat_web_1   Up 5 weeks             5000/tcp
slimy-chat_smtp_1               Up 5 weeks (healthy)   587/tcp
slimy-chat_voice-ingress_1      Up 5 weeks             
slimy-chat_api_1                Up 5 weeks             14702/tcp
slimy-chat_pushd_1              Up 5 weeks             
slimy-chat_autumn_1             Up 5 weeks             14704/tcp
slimy-chat_events_1             Up 5 weeks             14703/tcp
slimy-chat_crond_1              Up 5 weeks             
slimy-chat_minio_1              Up 5 weeks             9000/tcp
slimy-chat_rabbit_1             Up 5 weeks (healthy)   4369/tcp, 5671-5672/tcp, 15691-15692/tcp, 25672/tcp
slimy-chat_livekit_1            Up 5 weeks             0.0.0.0:7881->7881/tcp, [::]:7881->7881/tcp, 0.0.0.0:50000-50100->50000-50100/udp, [::]:50000-50100->50000-50100/udp
slimy-chat_january_1            Up 5 weeks             14705/tcp
slimy-chat_gifbox_1             Up 5 weeks             14706/tcp
slimy-chat_redis_1              Up 5 weeks             6379/tcp
```

## Key Ports
```
LISTEN 0      4096                     127.0.0.1:11434      0.0.0.0:*                                                 
LISTEN 0      4096                       0.0.0.0:8080       0.0.0.0:*                                                 
LISTEN 0      511                      127.0.0.1:18791      0.0.0.0:*    users:(("openclaw-gatewa",pid=3849659,fd=28))
LISTEN 0      511                      127.0.0.1:18789      0.0.0.0:*    users:(("openclaw-gatewa",pid=3849659,fd=25))
LISTEN 0      511                      127.0.0.1:18792      0.0.0.0:*    users:(("openclaw-gatewa",pid=3849659,fd=32))
LISTEN 0      4096                       0.0.0.0:3306       0.0.0.0:*                                                 
LISTEN 0      4096                 192.168.68.64:27017      0.0.0.0:*                                                 
LISTEN 0      4096                          [::]:8080          [::]:*                                                 
LISTEN 0      511                          [::1]:18789         [::]:*    users:(("openclaw-gatewa",pid=3849659,fd=26))
LISTEN 0      511                              *:3000             *:*    users:(("node /opt/slimy",pid=1561344,fd=23))
LISTEN 0      4096                          [::]:3306          [::]:*                                                 
```
