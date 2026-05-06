# Claude Progress — Super Snail Extraction

## 2026-04-28 — Phase 3 raw recv()/send() hook + binary protocol analysis

Status: Built and deployed Frida recv()/send() hook script targeting libc.so and libssl.so on main game process (PID 8296). No custom binary protocol traffic on port 50504 captured — connection was not active during capture window. Captured Facebook SDK HTTPS traffic instead. JPush remote process (PID 4781) also showed no active 50504 connection.

Files changed:
- Added `scripts/frida_recv_hook.js` (raw recv/send/SSL hook script)
- Added `scripts/run_recv_hook.py` (Python runner with summary generation)
- Added `reports/phase3-recv-hook-analysis-20260428T1855Z.md`
- Updated `claude-progress.md`
- Updated `feature_list.json`

Commands run:
- `cat ./AGENTS.md`, `cat ./claude-progress.md`, `source ./init.sh`
- `cat ./PROJECT_INSTRUCTIONS.md`, `cat ./QUALITY_CRITERIA.md`, `cat ./feature_list.json`
- `adb devices` — emulator-5554 active
- `adb shell pidof com.qcplay.snail.android.na` — main PID 8296, jpushremote PID 4781
- `frida-ps -U` — frida-server 17.9.1 responsive
- `adb shell 'cat /proc/8296/net/tcp'` — no 50504 connection
- `adb shell 'cat /proc/4781/net/tcp'` — no 50504 connection
- `adb shell 'tcpdump -i any -n host 47.252.2.69 -c 5'` — 0 packets (10s window)
- `CAPTURE_DURATION=300 python3 -u scripts/run_recv_hook.py` — 5-min capture
- Captured 5 packets: all Facebook SDK HTTPS (POST /adnw_sync2)
- `./scripts/qa_gate.sh`
- `./scripts/git_auto_sync.sh`

Proof directory:
- `captures/private/phase3/20260428T185018/` (gitignored)
  - `frida_recv_hook.log` (Facebook SDK traffic)
  - `sanitized_summary.json` (counts, sizes, no payloads)

What passed:
- Frida attachment to main process: working
- libc.so hooks (recv/send/read/write/connect/close): working
- libssl.so hooks (SSL_read/SSL_write): working, caught Facebook traffic
- Sanitized logging: no secrets/tokens/account data captured
- Python runner generates sanitized summary without raw payloads
- QA gate passed

Remaining unknowns:
- 50504 connection timing — when does it activate? (specific game modes? login? real-time features?)
- Which process handles 50504 when active? (main or JPush?)
- Is 50504 cleartext or TLS-wrapped? (4d5a header suggests cleartext or post-decrypt)
- Message type IDs — cannot identify without capturing actual frames
- Encryption key testing — cannot test XXTEA/RC4 without payload bytes

---

## 2026-04-28 — Phase 3 application-layer protocol message hook completed

Status: Analyzed libcocos2dlua.so symbols, identified dispatch/receive functions, wrote and tested Frida hook script. 5/6 hooks active; lua_pcall hook blocked by Frida 17.9.1 limitation. No protocol traffic captured during automated testing because game requires genuine user interaction to trigger rank/arena/club messages. Report and runners committed.

Files changed:
- Added `scripts/frida_protocol_hook.js` (application-layer hook script)
- Added `scripts/run_phase3_hook.py` (Python attach-mode runner)
- Added `scripts/run_phase3_hook_spawn.py` (Python spawn-gate runner)
- Added `reports/phase3-application-layer-hook-20260428.md`
- Updated `feature_list.json`
- Updated `claude-progress.md`

Commands run:
- `cat ./AGENTS.md`, `cat ./claude-progress.md`, `source ./init.sh`
- `cat ./PROJECT_INSTRUCTIONS.md`, `cat ./QUALITY_CRITERIA.md`, `cat ./feature_list.json`
- Symbol searches on `/tmp/libcocos2dlua.so` via `nm -D` and `strings`
- `adb pull` of live device `libcocos2dlua.so` to `/tmp/libcocos2dlua_device.so`
- `sha256sum /tmp/libcocos2dlua_device.so` for evidence hash
- Multiple Frida attach/spawn tests with `frida -U -p PID -l scripts/frida_protocol_hook.js`
- `python3 -u scripts/run_phase3_hook.py` (background attach-mode capture)
- `python3 -u scripts/run_phase3_hook_spawn.py` (spawn-gate test, ANR issues)
- `adb shell input tap` simulated interactions (no protocol events)
- `adb shell cat /proc/PID/net/tcp` socket inspection
- `./scripts/qa_gate.sh`
- `./scripts/git_auto_sync.sh`

Proof directory:
- `/tmp/libcocos2dlua_device.so` (Tier 0, SHA256: b5483d9a47647de92d615b5ad722a58cc3ce21251de833bd7a21e5c929873332)
- `.harness/logs/phase3_protocol_hook*.log` (Tier 2, mostly empty until user interaction)

What passed:
- Symbol discovery: found `CommMgr::OnPacketArrived`, `OnDataRecved`, `socket_receive_data`, `VerifyAgent::recvMsg`, `AddMsgDefine`
- Hook application: 5/6 targets successfully intercepted
- Frida workarounds implemented for module enumeration and memory-read limitations
- Sanitized report produced with no user data, tokens, or payload values

Remaining unknowns:
- Actual msg_id values for rank/group/arena messages (need user-driven interactive session)
- msg_id → name mapping from `AddMsgDefine` (need cold-start attach immediately after launch)
- JPush remote process protocol content (separate PID, not hooked in this session)
- Full binary frame structure (need `OnDataRecved` hits with user interaction)

---

## 2026-04-28 — Phase 3 extended JPush capture session completed

Status: Ran 35-minute interactive session with attach-mode Frida on both main game process and JPush remote process. Discovered JPush runs in separate process. Captured limited JPush HTTPS traffic but identified persistent TCP/3000 and TCP/50504 custom protocol connections.

Files changed:
- Added `scripts/frida_system_ssl_unpin.js` (system libssl.so hooks for JPush process)
- Added `reports/phase3-extended-jpush-capture-20260428T053039Z.md`
- Updated `feature_list.json`
- Updated `claude-progress.md`

Commands run:
- `adb shell am force-stop com.qcplay.snail.android.na`
- `adb shell am start -n com.qcplay.snail.android.na/org.cocos2dx.lua.AppActivity`
- `adb shell pidof -s com.qcplay.snail.android.na` (PID 14238)
- `frida -U -p 14238 -l scripts/frida_ssl_unpin.js -l scripts/frida_native_ssl_unpin.js -l scripts/frida_jpush_intercept.js`
- `frida -U -p 14605 -l scripts/frida_system_ssl_unpin.js`
- `mitmdump -w captures/private/phase3/20260428T053039/jpush_session.flow`
- `adb shell ss -tnp` for socket attribution
- `python3 scripts/validate_capture_report.py reports/phase3-extended-jpush-capture-20260428T053039Z.md`
- `python3 -m json.tool feature_list.json`
- `./scripts/qa_gate.sh`
- `./scripts/git_auto_sync.sh`

Proof directory:
- `captures/private/phase3/20260428T053039/` (gitignored)
  - `jpush_session.flow` (59K)
  - `mitmdump.log` (15K)
  - `frida.log` (main process)
  - `frida_jpush.log` (JPush Java unpin)
  - `frida_system_ssl.log` (JPush system SSL hooks)

What passed:
- JPush identified as separate process (`:jpushremote`, PID 14605)
- System libssl.so successfully hooked in JPush process using Frida 17.x API (`Process.findModuleByName` + `module.getExportByName`)
- Java-layer SSL unpin successfully applied to both processes
- One JPush HTTPS POST /v3/report captured (200 OK, 0 bytes)
- Persistent TCP/3000 connection to 34.124.161.204 identified
- Game API connection to 47.252.2.69:50504 identified
- Capture report passed `validate_capture_report.py`
- `feature_list.json` validates as JSON
- `./scripts/qa_gate.sh` passed

Key findings:
- JPush native hooks fired 0 times (connections pre-established before attach)
- TCP/3000 is likely the primary JPush/game protocol (not HTTPS)
- Game uses separate TCP/50504 connection for main API (not through proxy)
- Java-layer unpin alone is sufficient for JPush HTTPS reporting channel

Remaining unknowns:
- JPush TCP/3000 protocol format and framing
- Game API protocol on TCP/50504
- Whether spawn-gating would catch SSL context creation
- Phase 2C protocol name correlation with live traffic
- Auth/session token format

## 2026-04-27 — Phase 3 native BoringSSL hooking completed

Status: Analyzed BoringSSL symbols in libcocos2dlua.so, wrote Frida native SSL unpin script, and prepared application-layer intercept fallback. JPush traffic not visible in short test session (likely timing-related).

Files changed:
- Updated `scripts/frida_native_ssl_unpin.js` (v3 with /proc/self/maps parsing + SSL_do_handshake hook)
- Added `scripts/frida_jpush_intercept.js` (application-layer SSL_read/SSL_write hook)
- Added `reports/phase3-native-boringssl-hooking-20260427T230000Z.md`
- Updated `feature_list.json`
- Updated `claude-progress.md`

Commands run:
- `adb shell ls -la /data/app/*/com.qcplay.snail.android.na*/lib/arm64/`
- `adb pull /data/app/.../lib/arm64/libcocos2dlua.so /tmp/libcocos2dlua.so`
- `sha256sum /tmp/libcocos2dlua.so`
- `nm -D /tmp/libcocos2dlua.so | grep -i ssl`
- `objdump -T /tmp/libcocos2dlua.so | grep -i ssl`
- `readelf -s /tmp/libcocos2dlua.so | grep -i ssl`
- `strings /tmp/libcocos2dlua.so | grep -iE "ssl|verify|pinning|certificate|x509"`
- `aarch64-linux-gnu-objdump -d` for symbol verification
- `frida -U -n "Super Snail"` for API probing and hook testing
- Multiple Frida spawn/attach tests with native and Java scripts
- `mitmdump` capture analysis

Proof directory:
- `captures/private/phase3/20260427T215926/`
- Raw captures stored externally (gitignored)

What passed:
- Symbol analysis confirmed: SSL_CTX_set_verify, SSL_set_verify, SSL_do_handshake, SSL_read, SSL_write all exported
- Frida direct-address hooking works for SSL_CTX_set_verify and SSL_set_verify
- SSL_do_handshake hook successfully applied
- SSL_read/SSL_write hooks successfully applied
- /proc/self/maps parsing workaround confirmed working
- Java-layer unpin continues to work for non-JPush HTTPS traffic

Key findings:
- Frida 17.9.1 cannot enumerate libcocos2dlua.so as a module (bug/limitation)
- Library code resides in rwxp pages (unusual memory layout)
- SSL_get_peer_certificate cannot be hooked (Frida bug)
- Spawn-gating with library polling has timing issues
- Application-layer hooking (SSL_read/SSL_write) is the stronger long-term play

Remaining unknowns:
- JPush TLS connection timing and lifecycle
- Whether JPush uses BoringSSL from libcocos2dlua.so or alternative TLS
- JPush message framing and serialization format
- Phase 2C protocol correlation with live JPush payloads

## 2026-04-27 — Phase 3 socket attribution completed

Status: Used Android socket ownership to attribute candidate startup sockets. No additional raw capture was created.

Files changed:
- Added `reports/phase3-socket-attribution-20260427T2144Z.md`
- Updated `reports/phase3-passive-startup-capture-20260427T213957Z.md`
- Updated `feature_list.json`
- Updated `claude-progress.md`

Commands run:
- `adb -s emulator-5554 shell pidof -s com.qcplay.snail.android.na || true`
- `adb -s emulator-5554 shell ss -tunp`
- `adb -s emulator-5554 shell cat /proc/net/tcp /proc/net/tcp6 /proc/net/udp /proc/net/udp6`
- `adb -s emulator-5554 shell 'for p in 14133 14559; do ... /proc/$p/cmdline ... /proc/$p/status ...; done'`
- `adb -s emulator-5554 shell ss -tnp | rg '14133|14559|:3000|:80|:443'`
- `python3 scripts/validate_capture_report.py reports/phase3-socket-attribution-20260427T2144Z.md reports/phase3-passive-startup-capture-20260427T213957Z.md`
- `python3 -m json.tool feature_list.json >/tmp/slimy_feature_list_check.json`
- `./scripts/qa_gate.sh`

Proof directory:
- `/home/mint/projects/slimy_snail/.harness/proofs/proof_20260427T214508Z`

What passed:
- Main game process identified as `com.qcplay.snail.android.na`, PID `14133`, UID `10192`.
- Auxiliary process identified as `com.qcplay.snail.android.na:jpushremote`, PID `14559`, UID `10192`.
- TCP/3000 socket was attributed to `:jpushremote`, not the main process.
- Main process sockets observed on TCP/443 and TCP/80.
- Attribution reports passed `validate_capture_report.py`.
- `feature_list.json` validates as JSON.
- `./scripts/qa_gate.sh` passed with capture report sanitization.

Remaining unknowns:
- Which TCP/443 sockets carry game protocol traffic.
- Whether TCP/80 is bootstrap/config/CDN traffic or unrelated webview behavior.
- TLS pinning, auth flow, session behavior, replay safety, and Phase 2 protocol correlation remain unknown.

## 2026-04-27 — First controlled passive startup capture completed

Status: Ran a short passive startup packet capture using device `tcpdump`. Raw PCAP stayed in ignored private storage; only sanitized metadata was added to the repo.

Files changed:
- Added `reports/phase3-passive-startup-capture-20260427T213957Z.md`
- Updated `PROJECT_STATUS.md`
- Updated `feature_list.json`
- Updated `claude-progress.md`

Commands run:
- `cat ./AGENTS.md`
- `cat ./claude-progress.md`
- `source ./init.sh`
- `cat ./PROJECT_INSTRUCTIONS.md`
- `cat ./QUALITY_CRITERIA.md`
- `cat ./feature_list.json`
- `./scripts/phase3_capture_prep_check.sh`
- First capture attempt with `adb exec-out tcpdump`; kept private, invalid PCAP because tcpdump status text contaminated stdout.
- `xxd -l 160 captures/private/phase3/20260427T213831Z/passive_foreground_20260427T213831Z.pcap`
- `adb -s emulator-5554 shell id`
- Second capture attempt using on-device `tcpdump -w /data/local/tmp/...pcap`
- `adb -s emulator-5554 shell am force-stop com.qcplay.snail.android.na`
- `adb -s emulator-5554 shell am start -n com.qcplay.snail.android.na/org.cocos2dx.lua.AppActivity`
- `adb -s emulator-5554 pull /data/local/tmp/snail_phase3_20260427T213957Z.pcap captures/private/phase3/20260427T213957Z/passive_startup_20260427T213957Z.pcap`
- `sha256sum captures/private/phase3/20260427T213957Z/passive_startup_20260427T213957Z.pcap`
- `stat -c 'size_bytes=%s' captures/private/phase3/20260427T213957Z/passive_startup_20260427T213957Z.pcap`
- `tcpdump -nn -r captures/private/phase3/20260427T213957Z/passive_startup_20260427T213957Z.pcap -q`
- `git check-ignore captures/private/phase3/20260427T213957Z/passive_startup_20260427T213957Z.pcap data/raw/phase3-wire/session_tokens.json .env.phase3`
- `adb -s emulator-5554 shell rm -f /data/local/tmp/snail_phase3_20260427T213957Z.pcap /data/local/tmp/snail_phase3_20260427T213957Z.log`
- `python3 scripts/validate_capture_report.py reports/phase3-passive-startup-capture-20260427T213957Z.md docs/capture/phase3_capture_report_template.md docs/capture/phase3_wire_capture_runbook.md`
- `python3 -m json.tool feature_list.json >/tmp/slimy_feature_list_check.json`
- `./scripts/qa_gate.sh`
- `./scripts/qa_gate.sh`

Proof / private paths:
- Prep proof: `/tmp/proof_snail_phase3_capture_prep_20260427T213807Z`
- QA proof: `/home/mint/projects/slimy_snail/.harness/proofs/proof_20260427T214322Z`
- Raw PCAP, ignored/private: `captures/private/phase3/20260427T213957Z/passive_startup_20260427T213957Z.pcap`
- Raw PCAP SHA256: `3a9b12fc42949aa22f8319dc537bbe65485585b5b3121386175f4618ed63bc94`

What passed:
- Second PCAP parsed successfully with host `tcpdump`.
- `3245` packets captured.
- `0` kernel drops.
- App was running after capture with PID `14133`.
- Remote device temp PCAP/log files were removed.
- Raw PCAP path is ignored by Git.
- Sanitized metadata report avoids endpoint IPs, payloads, auth headers, cookies, tokens, account IDs, and device IDs.
- Sanitized report passed `validate_capture_report.py`.
- `feature_list.json` validates as JSON.
- `./scripts/qa_gate.sh` passed with capture report sanitization.

Remaining unknowns:
- Passive PCAP is not process-attributed.
- TCP/3000 is a candidate game/custom transport signal, not proof.
- Auth flow, TLS pinning, token/session behavior, replay safety, and Phase 2 protocol correlation remain unknown.

## 2026-04-27 — Phase 3 capture report sanitizer added

Status: Added an automatic sanitizer guard for future Phase 3 capture reports. No live traffic capture was started.

Files changed:
- Added `scripts/validate_capture_report.py`
- Added `tests/test_validate_capture_report.py`
- Updated `scripts/qa_gate.sh`
- Updated `docs/capture/phase3_wire_capture_runbook.md`
- Updated `docs/capture/phase3_capture_report_template.md`
- Updated `reports/phase3-capture-toolchain-readiness-20260427.md`
- Updated `feature_list.json`
- Updated `claude-progress.md`

Commands run:
- `cat ./AGENTS.md`
- `cat ./claude-progress.md`
- `source ./init.sh`
- `sed -n '1,220p' scripts/qa_gate.sh`
- `sed -n '1,220p' scripts/inventory.py`
- `sed -n '1,160p' tests/test_phase2r_candidate_classifier.py`
- `python3 tests/test_validate_capture_report.py`
- `python3 -m py_compile scripts/validate_capture_report.py tests/test_validate_capture_report.py`
- `python3 scripts/validate_capture_report.py docs/capture/phase3_capture_report_template.md docs/capture/phase3_wire_capture_runbook.md reports/phase3-capture-toolchain-readiness-20260427.md reports/phase3-wire-capture-prep-20260427.md`
- `python3 -m py_compile scripts/validate_capture_report.py tests/test_validate_capture_report.py scripts/inventory.py`
- `python3 -m json.tool feature_list.json >/tmp/slimy_feature_list_check.json`
- `for t in tests/test_phase2*.py; do python3 "$t" || exit 1; done`
- `./scripts/qa_gate.sh`

Proof directory:
- `/home/mint/projects/slimy_snail/.harness/proofs/proof_20260427T205807Z`

What passed:
- Sanitizer allows the committed template placeholders and current Phase 3 reports.
- Unit test confirms realistic Authorization bearer, Cookie, and JSON token fields are flagged.
- `qa_gate.sh` now runs the sanitizer across capture docs/reports before autosync.
- Phase 2 test suite passed.
- `feature_list.json` validates as JSON.
- `./scripts/qa_gate.sh` passed with `capture docs/reports sanitized`.

Remaining unknowns:
- Live capture still has not started.
- Phase 4 remains blocked until auth, transport, replay, and protocol correlation are proven.

## 2026-04-27 — Phase 3 capture toolchain readiness checked

Status: Inventoried capture tooling and emulator hook readiness. No live traffic capture, proxying, tcpdump recording, or Frida hooks were started.

Files changed:
- Added `reports/phase3-capture-toolchain-readiness-20260427.md`
- Updated `feature_list.json`
- Updated `claude-progress.md`

Commands run:
- `command -v` checks for `adb`, `emulator`, `mitmproxy`, `mitmdump`, `frida`, `frida-ps`, `frida-trace`, `tshark`, `tcpdump`, `openssl`, and `python3`
- `adb -s emulator-5554 shell getprop ro.product.cpu.abi`
- `adb -s emulator-5554 shell getprop ro.build.version.sdk`
- `adb -s emulator-5554 shell getprop ro.debuggable`
- `adb -s emulator-5554 shell getenforce`
- `adb -s emulator-5554 shell which tcpdump`
- `adb -s emulator-5554 shell tcpdump --version`
- `mitmdump --version`
- `frida --version`
- `frida-ps --version`
- `tcpdump --version`
- `frida-ps -U`
- `python3 -m json.tool feature_list.json >/tmp/slimy_feature_list_check.json`
- `git diff --stat && git status --short --branch`
- `./scripts/qa_gate.sh`

Proof directory:
- `/home/mint/projects/slimy_snail/.harness/proofs/proof_20260427T205432Z`

What passed:
- mitmproxy/mitmdump are installed at version `12.2.2`.
- Frida client tools are installed at version `17.9.1`.
- `frida-ps -U` succeeds and sees `Super Snail` PID `7211`.
- Host and emulator both have `tcpdump`.
- Emulator is x86_64, SDK 34, debuggable, SELinux enforcing.
- `feature_list.json` validates as JSON.
- `./scripts/qa_gate.sh` passed.

Remaining unknowns:
- `tshark` is missing.
- TLS pinning, auth flow, transport type, and replay safety remain unknown until live capture.

## 2026-04-27 — Phase 3 wire-capture prep completed

Status: Added and ran the Phase 3 prep workflow. No live traffic capture was started.

Files changed:
- Added `scripts/phase3_capture_prep_check.sh`
- Added `docs/capture/phase3_wire_capture_runbook.md`
- Added `docs/capture/phase3_capture_report_template.md`
- Added `reports/phase3-wire-capture-prep-20260427.md`
- Updated `PROJECT_STATUS.md`
- Updated `feature_list.json`
- Updated `claude-progress.md`

Commands run:
- `cat ./AGENTS.md`
- `cat ./claude-progress.md`
- `source ./init.sh`
- `cat ./PROJECT_INSTRUCTIONS.md`
- `cat ./QUALITY_CRITERIA.md`
- `cat ./feature_list.json`
- `rg --files docs reports scripts src tests | sort`
- `adb devices`
- `adb -s emulator-5554 shell pidof -s com.qcplay.snail.android.na || true`
- `adb -s emulator-5554 shell cmd package resolve-activity --brief com.qcplay.snail.android.na || true`
- `adb -s emulator-5554 shell dumpsys activity activities | rg 'mResumedActivity|topResumedActivity|ResumedActivity' || true`
- `adb -s emulator-5554 shell getprop sys.boot_completed`
- `adb -s emulator-5554 shell pm list packages | rg 'qcplay|snail' || true`
- `chmod +x scripts/phase3_capture_prep_check.sh`
- `bash -n scripts/phase3_capture_prep_check.sh`
- `./scripts/phase3_capture_prep_check.sh`
- `python3 -m json.tool feature_list.json >/tmp/slimy_feature_list_check.json`
- `git diff --stat && git status --short --branch`
- `./scripts/qa_gate.sh`

Proof directory:
- `/tmp/proof_snail_phase3_capture_prep_20260427T205158Z`
- QA proof: `/home/mint/projects/slimy_snail/.harness/proofs/proof_20260427T205246Z`

What passed:
- `emulator-5554` was already running and boot-complete.
- `com.qcplay.snail.android.na` was installed.
- Activity resolved to `com.qcplay.snail.android.na/org.cocos2dx.lua.AppActivity`.
- App PID was `7211`.
- Top activity was `com.qcplay.snail.android.na/org.cocos2dx.lua.AppActivity`.
- Private capture probe paths were ignored by Git.
- Prep result was `PASS_PHASE3_CAPTURE_PREP_READY`.
- `raw_capture_started=false`.
- `feature_list.json` validates as JSON.
- `./scripts/qa_gate.sh` passed.

Remaining unknowns:
- Actual auth flow, token format, transport protocol, and replay constraints remain unknown until a later live capture.
- Phase 4 API client remains blocked.

## 2026-04-27 — Phase 3 prompt tightened for runtime fallback and noise cleanup

Status: Reviewed follow-up course-action feedback and tightened the Phase 3 prep instructions.

Files changed:
- Updated `.gitignore`
- Updated `PROJECT_STATUS.md`
- Updated `docs/decisions/0002-phase3-wire-capture-pivot.md`
- Updated `feature_list.json`
- Updated `claude-progress.md`

Commands run:
- `cat ./AGENTS.md`
- `cat ./claude-progress.md`
- `source ./init.sh`
- `cat ./PROJECT_INSTRUCTIONS.md`
- `cat ./QUALITY_CRITERIA.md`
- `sed -n '1,180p' .gitignore`
- `sed -n '1,130p' scripts/git_auto_sync.sh`
- `git status --short --branch`
- `git ls-files data/protocol/decoded evidence/tmp-imports`
- `git ls-files .harness/proofs | rg 'qa\\.log$' || true`
- `python3 -m json.tool feature_list.json >/tmp/slimy_feature_list_check.json`
- `git diff -- .gitignore PROJECT_STATUS.md docs/decisions/0002-phase3-wire-capture-pivot.md feature_list.json claude-progress.md`
- `./scripts/qa_gate.sh`
- `./scripts/qa_gate.sh`

Proof directory:
- `/home/mint/projects/slimy_snail/.harness/proofs/proof_20260427T204852Z`

What passed:
- Confirmed the untracked status noise is generated proof `qa.log` files, generated decoded Lua analyst views, and one tmp-import TSV manifest.
- Added ignore rules for those generated/scratch files.
- Added mandatory `snail-recon` startup/verification fallback to the Phase 3 prep path.
- `feature_list.json` validates as JSON.
- `./scripts/qa_gate.sh` passed.

Remaining unknowns:
- Actual auth flow, token format, and transport protocol still require a later live capture step.

## 2026-04-27 — Course correction to Phase 3/4 wire capture

Status: Reviewed the pasted status assessment against repo truth and adjusted tracking so future agents do not continue Phase 2W to Phase 2X as the default path.

Files changed:
- Added `docs/decisions/0002-phase3-wire-capture-pivot.md`
- Updated `PROJECT_STATUS.md`
- Updated `feature_list.json`
- Updated `claude-progress.md`

Commands run:
- `cat ./AGENTS.md`
- `cat ./claude-progress.md`
- `source ./init.sh`
- `cat ./PROJECT_INSTRUCTIONS.md`
- `cat ./QUALITY_CRITERIA.md`
- `cat ./feature_list.json`
- `git status --short --branch`
- `sed -n '1,220p' PROJECT_STATUS.md`
- `rg -n "Phase 2X|grammar|wire|capture|Phase 3|Phase 4|next" PROJECT_STATUS.md claude-progress.md feature_list.json reports docs scripts -g '!*.luac'`
- `python3 -m json.tool feature_list.json >/tmp/slimy_feature_list_check.json`
- `git diff -- PROJECT_STATUS.md feature_list.json claude-progress.md docs/decisions/0002-phase3-wire-capture-pivot.md`
- `./scripts/qa_gate.sh`
- `./scripts/qa_gate.sh`

Proof directory:
- `/home/mint/projects/slimy_snail/.harness/proofs/proof_20260427T204510Z`

What passed:
- Confirmed repo has a GitHub remote: `https://github.com/GurthBro0ks/slimy_snail`
- Confirmed Phase 2W completed the grammar audit side branch.
- Added Phase 3 capture prep as the critical ready task and Phase 4 API client as blocked on capture evidence.
- `feature_list.json` validates as JSON.
- `./scripts/qa_gate.sh` passed.

Remaining unknowns:
- Actual auth flow, token format, and transport protocol remain unknown until wire capture.
- Raw captures must remain ignored/private and cannot be committed.

## 2026-04-27 — Phase 2M phrase coverage completed

Status: Added and ran a phrase-template coverage pass over the 838 small-handler proof. The pass generated external redacted views and measured how much current templates cover without committing decoded source.

Files changed:
- Added `src/decode/phase2m_phrase_coverage.py`
- Added `tests/test_phase2m_phrase_coverage.py`
- Added `reports/phase2m-phrase-coverage-20260427T155228Z.md`
- Updated `PROJECT_STATUS.md`
- Updated `feature_list.json`
- Updated `claude-progress.md`

Commands run:
- `python3 -m py_compile src/decode/phase2m_phrase_coverage.py tests/test_phase2m_phrase_coverage.py`
- `python3 tests/test_phase2m_phrase_coverage.py`
- `python3 src/decode/phase2m_phrase_coverage.py --input-proof /tmp/proof_snail_phase2k_simple_anchor_inventory_20260427T152519Z`
- reviewed `RESULT.md`, `coverage_summary.tsv`, and external `redacted_views/`

Proof directory:
- `/tmp/proof_snail_phase2m_phrase_coverage_20260427T155228Z`

What passed:
- Synthetic test passed.
- 838 handlers scanned.
- 1544 phrase sequence rows emitted.
- 6 handlers reached at least 50% phrase coverage.

Remaining unknowns:
- Current templates are not enough for full source reconstruction.
- Need more manager/call templates before coverage becomes broadly useful.

## 2026-04-27 — Phase 2L standard phrase gap audit completed

Status: Added and ran a phrase-local gap audit across the 838 small-handler external proof set. This produced repeated conflict-free transform evidence for standard Lua/API phrases and confirmed raw punctuation is polymorphic by grammar context.

Files changed:
- Added `src/decode/phase2l_standard_phrase_gap_audit.py`
- Added `tests/test_phase2l_standard_phrase_gap_audit.py`
- Added `reports/phase2l-standard-phrase-gap-audit-20260427T154941Z.md`
- Updated `PROJECT_STATUS.md`
- Updated `feature_list.json`
- Updated `claude-progress.md`

Commands run:
- `python3 -m py_compile src/decode/phase2l_standard_phrase_gap_audit.py tests/test_phase2l_standard_phrase_gap_audit.py`
- `python3 tests/test_phase2l_standard_phrase_gap_audit.py`
- `python3 src/decode/phase2l_standard_phrase_gap_audit.py --input-proof /tmp/proof_snail_phase2k_simple_anchor_inventory_20260427T152519Z`
- reviewed `RESULT.md`, `phrase_counts.tsv`, `context_gap_repeated_conflict_free.tsv`, and `context_gap_conflicts.tsv`

Proof directory:
- `/tmp/proof_snail_phase2l_standard_phrase_gap_20260427T154941Z`

What passed:
- Synthetic test passed.
- 1544 standard phrase occurrences found.
- 3072 gap rows emitted.
- 87 repeated conflict-free contexts.
- 0 context conflicts.

Remaining unknowns:
- This still does not decode full handlers.
- Next step should build a phrase-template partial renderer that only fills proven phrase contexts and leaves unknown gaps unresolved.

## 2026-04-27 — Phase 2K simple handler anchor inventory completed

Status: Pulled a broader set of small `cmd/misc` handlers into `/tmp` only and generated a sanitized structural inventory for choosing more grammar anchors.

Files changed:
- Added `src/decode/phase2k_simple_anchor_inventory.py`
- Added `tests/test_phase2k_simple_anchor_inventory.py`
- Added `reports/phase2k-simple-anchor-inventory-20260427T152713Z.md`
- Updated `PROJECT_STATUS.md`
- Updated `feature_list.json`
- Updated `claude-progress.md`

Commands run:
- `adb shell find /data/data/com.qcplay.snail.android.na/files/update_res/src/game/cmd/misc -type f -name '*.luac'`
- `adb shell stat -c %s` for candidate size filtering
- `adb pull` for 838 handlers with size `<= 500`
- `chmod 444` on pulled originals
- `sha256sum` and `stat` on pulled originals
- `python3 -m py_compile src/decode/phase2k_simple_anchor_inventory.py tests/test_phase2k_simple_anchor_inventory.py`
- `python3 tests/test_phase2k_simple_anchor_inventory.py`
- `python3 src/decode/phase2k_simple_anchor_inventory.py --input-proof /tmp/proof_snail_phase2k_simple_anchor_inventory_20260427T152519Z --limit 80`

Proof directories:
- Raw pull: `/tmp/proof_snail_phase2k_simple_anchor_inventory_20260427T152519Z`
- Sanitized inventory: `/tmp/proof_snail_phase2k_simple_anchor_inventory_20260427T152713Z`

What passed:
- Synthetic test passed.
- 838 small handlers scanned.
- 830 handlers include the `returnfunctionlpc` skeleton.
- Top anchor candidates exported externally.

Remaining unknowns:
- No new exact source reconstruction yet.
- Need to select repeated simple proxy patterns and feed them back through Phase 2I/2J.

## 2026-04-27 — Phase 2J gap context model completed

Status: Added and ran a context model over Phase 2I raw gap evidence. The model found local single-candidate transforms for each exact context, but no repeated context evidence yet, so no transform was promoted.

Files changed:
- Added `src/decode/phase2j_gap_context_model.py`
- Added `tests/test_phase2j_gap_context_model.py`
- Added `reports/phase2j-gap-context-model-20260427T152345Z.md`
- Updated `PROJECT_STATUS.md`
- Updated `feature_list.json`
- Updated `claude-progress.md`

Commands run:
- `python3 -m py_compile src/decode/phase2j_gap_context_model.py tests/test_phase2j_gap_context_model.py`
- `python3 tests/test_phase2j_gap_context_model.py`
- `python3 src/decode/phase2j_gap_context_model.py --phase2i-proof /tmp/proof_snail_phase2i_skeleton_transform_20260427T152041Z`
- reviewed `RESULT.md`, `context_gap_conflict_free.tsv`, `context_gap_repeated_conflict_free.tsv`, `context_gap_conflicts.tsv`, and `raw_gap_summary.tsv`

Proof directory:
- `/tmp/proof_snail_phase2j_gap_context_model_20260427T152345Z`

What passed:
- Synthetic test passed.
- 59 exact context rows emitted.
- 0 context conflicts.

Remaining unknowns:
- 0 repeated conflict-free context transforms, so evidence is still too sparse for promotion.
- Need more simple handler anchors before exact source reconstruction can advance.

## 2026-04-27 — Phase 2I raw skeleton transform audit completed

Status: Added and ran a raw-byte skeleton transform audit. The audit found all four target handler anchors by alphanumeric skeleton and recorded raw punctuation/control gaps without promoting any unsafe mappings.

Files changed:
- Added `src/decode/phase2i_skeleton_transform_audit.py`
- Added `tests/test_phase2i_skeleton_transform_audit.py`
- Added `reports/phase2i-skeleton-transform-audit-20260427T152041Z.md`
- Updated `PROJECT_STATUS.md`
- Updated `feature_list.json`
- Updated `claude-progress.md`

Commands run:
- `python3 -m py_compile src/decode/phase2i_skeleton_transform_audit.py tests/test_phase2i_skeleton_transform_audit.py`
- `python3 tests/test_phase2i_skeleton_transform_audit.py`
- `python3 src/decode/phase2i_skeleton_transform_audit.py --proof-dir /tmp/proof_snail_phase2g_manager_trace_20260427T132529Z`
- reviewed `RESULT.md`, `anchor_matches.tsv`, `gap_evidence.tsv`, and `raw_gap_conflicts.tsv`

Proof directory:
- `/tmp/proof_snail_phase2i_skeleton_transform_20260427T152041Z`

What passed:
- Synthetic test passed.
- All 4 target anchors were found by alphanumeric skeleton.
- 59 raw gap rows were emitted.

Remaining unknowns:
- 10 raw gap conflicts remain.
- Punctuation/control layer needs context/run-level modeling before exact source reconstruction.
- No punctuation mapping was promoted.

## 2026-04-27 — Phase 2H punctuation conflict audit completed

Status: Added and ran a read-only punctuation audit instead of forcing a punctuation table into the decryptor. The audit found zero alphanumeric conflicts across anchored handler snippets, but found punctuation conflicts that block exact source reconstruction.

Files changed:
- Added `src/decode/phase2h_punctuation_audit.py`
- Added `tests/test_phase2h_punctuation_audit.py`
- Added `reports/phase2h-punctuation-audit-20260427T151537Z.md`
- Updated `PROJECT_STATUS.md`
- Updated `feature_list.json`
- Updated `claude-progress.md`

Commands run:
- `python3 -m py_compile src/decode/phase2h_punctuation_audit.py tests/test_phase2h_punctuation_audit.py`
- `python3 tests/test_phase2h_punctuation_audit.py`
- `python3 src/decode/phase2h_punctuation_audit.py --proof-dir /tmp/proof_snail_phase2g_manager_trace_20260427T132529Z`
- reviewed `RESULT.md`, `punctuation_conflicts.tsv`, `punctuation_candidates.tsv`, `alnum_conflicts.tsv`, and `anchor_evidence.tsv`

Proof directory:
- `/tmp/proof_snail_phase2h_punctuation_audit_20260427T151537Z`

What passed:
- Synthetic test passed.
- Audit completed against read-only Phase 2G originals.
- 103 anchor rows emitted.
- 0 alphanumeric conflicts found.

Remaining unknowns:
- Punctuation/operator layer is not solved.
- Current anchors produce conflicts for encrypted `)`, encrypted space, and encrypted `_`.
- Next step should align by alphanumeric skeleton through raw bytes and model whitespace/control transforms before promoting any punctuation mapping.

## 2026-04-27 — Game restarted and Phase 2G manager trace completed

Status: Reconfirmed ADB/emulator state after laptop power loss, cleared the Android notification permission prompt, confirmed the game activity is running, pulled manager/handler originals into an external proof directory, and continued the cipher/manager trace. Phase 2F was corrected: the current decryptor is partial and should not be treated as exact Lua source reconstruction.

Files changed:
- Added `reports/phase2g-manager-trace-20260427T132529Z.md`
- Updated `reports/phase2f-handler-decryption-poc.md`
- Updated `PROJECT_STATUS.md`
- Updated `feature_list.json`
- Updated `claude-progress.md`

Commands run:
- `adb devices`
- `adb shell pidof com.qcplay.snail.android.na`
- `adb shell dumpsys activity activities | rg 'mResumedActivity|topResumedActivity'`
- `adb exec-out uiautomator dump /dev/tty`
- `adb shell input tap 540 1335`
- `source ./init.sh`
- `adb shell find /data/data/com.qcplay.snail.android.na/files/update_res/src -type f -name '*.luac'`
- `adb pull` for `RankM`, `TopM`, `TaskM`, `GroupM`, `GroupWarM`, `EventM`, and 5 target handlers
- `chmod 444` on pulled originals
- `sha256sum` and `stat` on pulled originals
- `python3` import of `scripts/decrypt_handler.py` to create external decoded analyst views
- `rg`/`sed` trace checks for `setRankInfo`, `setMyRank`, `getRankInfo`, and `group_war_member_rank`

Proof directory:
- `/tmp/proof_snail_phase2g_manager_trace_20260427T132529Z`

What passed:
- ADB shows `emulator-5554 device`.
- Game is running at `com.qcplay.snail.android.na/org.cocos2dx.lua.AppActivity` with PID `7211`.
- Pulled originals are read-only (`444`) and hashed in the external proof directory.
- `RankM.setRankInfo` was traced as opaque `list` storage into `cacheData[rankId][start + index]`.
- `msg_group_war_member_rank` was traced as the strongest current field-flow evidence for `data.list` enrichment.

Remaining unknowns:
- Current decryptor is not a complete cipher solve; punctuation/operators remain unresolved.
- Full nested server schema for generic `lpc.list` entries is not defined by `RankM`.
- Next proof step should be a conflict-reporting punctuation solver with byte offsets and source anchors.

## 2026-04-26 — Phase 2F Handler Decryption POC

Status: Discovered that `.luac` handlers are NOT bytecode. They are minified Lua source code encrypted with a custom byte-substitution cipher. Built a decryptor script to reveal the plain source code.

Files changed:
- Added `scripts/decrypt_handler.py`
- Added `reports/phase2f-handler-decryption-poc.md`
- Updated `feature_list.json` (marked cipher solve done)
- Updated `claude-progress.md`

Commands run:
- Cloned and compiled `unluac` (failed on `.luac` files as they are not valid bytecode signatures).
- Wrote `scripts/decrypt_handler.py` with the complete derived substitution mapping.
- Decrypted `msg_group_rank.luac` and `msg_arena_top_query.luac`.
- `./scripts/qa_gate.sh`

Proof directory:
- `.harness/proofs/proof_...` (Will generate soon)

What passed:
- `decrypt_handler.py` outputs clean, perfect Lua source code with no garbled text or missing punctuation.
- QA passed.

Remaining unknowns:
- Since handlers are proxies (e.g., `RankM.setRankInfo(..., lpc.list)`), the nested schema of `lpc.list` is NOT in the handlers. We need to decrypt `RankM.luac` (manager scripts) from the live device to reconstruct the full data structure.

## 2026-04-26 — Rank/group/arena data-flow map created

Status: Extracted data-flow signals from Phase 2D and 2E reports and assembled into a map linking protocol, hash, manager calls, consumed fields, and telemetry relevance.

Files changed:
- Added `docs/protocol/rank_group_arena_data_flow_map.md`
- Updated `feature_list.json`
- Updated `claude-progress.md`

Commands run:
- Read `reports/phase2d-target-handler-inventory-20260426T210527Z.md`
- Read `reports/phase2e-rank-group-field-flow-20260426T210812Z.md`
- Created `docs/protocol/rank_group_arena_data_flow_map.md`
- `./scripts/qa_gate.sh`

Proof directory:
- `.harness/proofs/proof_20260427T001242Z`

What passed:
- Successfully extracted and linked protocol, hash, and parsed lpc payloads for 10 high-value competitive handlers.
- QA gate passed without tracking any raw original files.

Remaining unknowns:
- Nested object schema inside `lpc.list` and `lpc.data` still requires either packet captures or a full bytecode decompiler to reconstruct reliably.

## 2026-04-26 — Phase 2E rank/group/arena field-flow reconnaissance completed

Status: 10 high-value handlers decoded into printable views and summarized for manager calls, `lpc` fields, constants, and likely state flow.

Files changed:
- Added `reports/phase2e-rank-group-field-flow-20260426T210812Z.md`
- Updated `PROJECT_STATUS.md`
- Updated `feature_list.json`

Commands run:
- Read `/tmp/proof_snail_phase2d_target_inventory_20260426T210527Z/out/rank_group_handler_inventory.tsv`
- Read Phase 2B candidate mapping table
- Generated decoded printable and normalized views for 10 high-value handlers
- Extracted manager-call, `lpc`, and constant candidates

Proof directory:
- `/tmp/proof_snail_phase2e_field_flow_20260426T210812Z`

What passed:
- 10 handler summaries generated.
- Raw handlers stayed external.

Remaining unknowns:
- This is field-flow reconnaissance, not full source reconstruction.
- A bytecode-aware Lua decompiler would be needed for stronger control-flow and table-structure proof.

## 2026-04-26 — Phase 2D target handler inventory completed

Status: unmatched candidates triaged and focused rank/group/arena handler inventory pulled to external proof.

Files changed:
- Added `reports/phase2d-target-handler-inventory-20260426T210527Z.md`
- Updated `PROJECT_STATUS.md`
- Updated `feature_list.json`

Commands run:
- Read `/tmp/proof_snail_phase2c_filetree_match_20260426T205308Z/out/unmatched_candidates.txt`
- Read `/tmp/proof_snail_phase2c_filetree_match_20260426T205308Z/out/rank_group_targets_phase2c.txt`
- `adb devices`
- `adb shell pidof com.qcplay.snail.android.na`
- Generated nearest-neighbor triage for 8 unmatched candidates
- Pulled 119 target handlers from the live device into `/tmp/proof_snail_phase2d_target_inventory_20260426T210527Z/originals/`
- Set pulled handlers read-only
- Generated handler hash inventory and grouped target report

Proof directory:
- `/tmp/proof_snail_phase2d_target_inventory_20260426T210527Z`

What passed:
- 8 unmatched candidates triaged with no unsafe promotion.
- 119 target handlers pulled and hashed.
- 0 pull errors.

Remaining unknowns:
- Unmatched candidates look like event-version drift or absent live handlers; none are promoted.
- Handler field-flow still needs analysis from the external target inventory.

## 2026-04-26 — Phase 2C filetree protocol matching completed

Status: live handler file tree used to normalize most protocol names without claiming raw exact punctuation recovery.

Files changed:
- Added `reports/phase2c-filetree-protocol-match-20260426T205308Z.md`
- Added `docs/protocol/phase2c_filetree_protocol_report.md`
- Updated `PROJECT_STATUS.md`
- Updated `feature_list.json`

Commands run:
- `adb shell find /data/data/com.qcplay.snail.android.na/files/update_res/src/game/cmd -maxdepth 2 -type f -name '*.luac'`
- Wrote live command file list to `/tmp/snail_cmd_luac_paths_20260426.txt`
- Matched clean protocol candidates from `/tmp/proof_snail_protocol_adb_20260426T204437Z/out/protocol_messages_candidate.txt` against device handler paths by alphanumeric skeleton
- Generated Phase 2C proof at `/tmp/proof_snail_phase2c_filetree_match_20260426T205308Z`
- Searched handler tree for unmatched event names

Proof directory:
- `/tmp/proof_snail_phase2c_filetree_match_20260426T205308Z`

What passed:
- 962 protocol candidates checked against 962 device handler names.
- 954 unique skeleton matches.
- 713 exact-length printable-symbol matches.
- 241 skeleton-only length-delta matches.
- 0 ambiguous matches.
- 119 rank/group/arena/top target matches.

Remaining unknowns:
- 8 candidates did not match live handler names.
- Filetree matching recovers normalized protocol names, not raw exact punctuation bytes.
- `r` remains unresolved in handler/comment context.

## 2026-04-26 — Android relaunched, ADB originals reacquired, partial solve recorded

Status: emulator/game relaunched; fresh ADB originals pulled; Phase 2B audit rerun; partial handler alphanumeric mappings recorded.

Files changed:
- Added `reports/phase2b-adb-audit-solve-20260426T204627Z.md`
- Updated `PROJECT_STATUS.md`
- Updated `feature_list.json`

Commands run:
- `find /tmp` for launch/APK/emulator assets
- `find /home/mint` for Super Snail APK/AVD assets
- `adb devices`
- `/opt/android-sdk/emulator/emulator -list-avds`
- `ps -ef | rg 'emulator|qemu-system|qemu'`
- `/opt/android-sdk/emulator/emulator -avd snail-recon -no-window -no-audio -gpu swiftshader_indirect`
- `adb wait-for-device`
- `adb shell getprop sys.boot_completed`
- `adb shell pm list packages | grep com.qcplay.snail.android.na`
- `adb shell cmd package resolve-activity --brief com.qcplay.snail.android.na`
- `adb shell monkey -p com.qcplay.snail.android.na -c android.intent.category.LAUNCHER 1`
- `adb shell ls -l` for target `.luac` paths
- `adb pull` for `list.luac`, `msg_group_rank.luac`, and `msg_arena_top_query.luac`
- `chmod 444` on pulled originals
- `sha256sum` and `stat` on pulled originals
- `python3 src/decode/phase2b_cipher_audit.py --proof-dir /tmp/proof_snail_protocol_adb_20260426T204437Z`
- Generated partial solve proof at `/tmp/proof_snail_phase2b_cipher_solve_20260426T204627Z`

Proof directories:
- Fresh ADB originals: `/tmp/proof_snail_protocol_adb_20260426T204437Z`
- Phase 2B audit: `/tmp/proof_snail_phase2b_cipher_audit_20260426T204455Z`
- Partial solve: `/tmp/proof_snail_phase2b_cipher_solve_20260426T204627Z`

What passed:
- ADB shows `emulator-5554 device`.
- App activity resolved and launched as `org.cocos2dx.lua.AppActivity`.
- Fresh pulls match clean hashes and sizes:
  - `list.luac`: `122b776932fdb0e5c85b201d72aa722267b5b13162394e4610199b1235ac6f67`
  - `msg_group_rank.luac`: `a322476996c033b37ecacd421bc81727c19fda088057b26afe5f22052eacc2a9`
  - `msg_arena_top_query.luac`: `8cec7aed7e7bee5cf94cbc3d2618301f2e124661b023561a30e4421bf2010f37`
- Partial handler mappings promoted: `H -> Y`, `S -> K`, `b -> Q`, `d -> T`, `6 -> 6`.

Remaining unknowns:
- `r` remains unresolved.
- Punctuation/symbol layer remains unresolved.
- No complete protocol-name cleanup is claimed.

## 2026-04-26 — Phase 2B originals restored and audit run

Status: external proof originals restored from ignored private local clean-size variants; Phase 2B audit completed; solve not claimed.

Files changed:
- Added `reports/phase2b-restore-audit-20260426T195523Z.md`
- Updated `PROJECT_STATUS.md`
- Updated `feature_list.json`

Commands run:
- `cat ./AGENTS.md`
- `cat ./claude-progress.md`
- `source ./init.sh`
- `cat ./PROJECT_INSTRUCTIONS.md`
- `cat ./QUALITY_CRITERIA.md`
- `cat ./feature_list.json`
- `adb devices` (no attached devices)
- `stat -c '%a %A %s %n' originals/tmp-imports/20260426T173840Z/*.luac`
- `sha256sum originals/tmp-imports/20260426T173840Z/*.luac`
- Reviewed prior clean proof hashes/stats from `quarantine/tmp-imports/20260426T173840Z/unknown-review/`
- Restored clean-size variants into `/tmp/proof_snail_protocol_reset_20260426T195515Z_restored/originals/`
- `chmod 444 /tmp/proof_snail_protocol_reset_20260426T195515Z_restored/originals/*.luac`
- `sha256sum` and `stat` on restored originals
- `python3 src/decode/phase2b_cipher_audit.py --proof-dir /tmp/proof_snail_protocol_reset_20260426T195515Z_restored`
- Reviewed audit outputs under `/tmp/proof_snail_phase2b_cipher_audit_20260426T195523Z`
- Inspected imported solve candidates and did not run them as proof

Proof directories:
- Restored originals: `/tmp/proof_snail_protocol_reset_20260426T195515Z_restored`
- Phase 2B audit: `/tmp/proof_snail_phase2b_cipher_audit_20260426T195523Z`

What passed:
- Restored originals are read-only (`444`) and match prior clean proof hashes/sizes.
- Phase 2B audit completed against 3 originals and 962 protocol/string candidates.

Remaining unknowns:
- Fresh adb reacquisition is still blocked until a device is attached.
- Actual cipher solve remains blocked on a safe solver with byte offsets and conflict reporting.
- Existing imported solve scripts were not run as proof because they use hard-coded `/tmp` paths and invalid positional alignment assumptions.

## 2026-04-26 — Clean proof reports imported and Phase 2B audit scaffold added

Status: safe proof-report import and read-only Phase 2B audit scaffold prepared.

Files changed:
- Added `docs/reports/proof_snail_protocol_reset_20260426T170226Z/RESULT.md`
- Added `docs/reports/proof_snail_protocol_reset_20260426T170226Z/decode_report.md`
- Added `docs/reports/proof_snail_protocol_reset_20260426T170226Z/luac_originality_report.md`
- Added `docs/reports/proof_snail_protocol_reset_20260426T170226Z/rank_group_targets.md`
- Added `docs/decisions/0001-evidence-reset-and-import-policy.md`
- Added `docs/protocol/phase2b_cipher_solve/PLAN.md`
- Added `src/decode/phase2b_cipher_audit.py`
- Added `tests/test_phase2b_cipher_audit.py`
- Added `tests/fixtures/synthetic/README.md`
- Updated `PROJECT_STATUS.md`
- Updated `feature_list.json`

Commands run:
- `git status --short`
- `./scripts/qa_gate.sh` (PASS before edits)
- `find /tmp /home/mint -maxdepth 4 -type d -name 'proof_snail_protocol_reset_*'`
- `find /home/mint -maxdepth 5 -type f` for proof report names
- `sed` review of safe report copies under `quarantine/tmp-imports/20260426T173840Z/unknown-review/`
- `sha256sum` for promoted report copies
- `python3 -m py_compile src/decode/phase2b_cipher_audit.py tests/test_phase2b_cipher_audit.py` (PASS)
- `python3 src/decode/phase2b_cipher_audit.py --help` (PASS)
- `python3 src/decode/phase2b_cipher_audit.py --proof-dir /tmp/proof_snail_protocol_reset_20260426T170226Z` (expected fail-closed; proof dir missing)
- `python3 tests/test_phase2b_cipher_audit.py` (PASS)
- Synthetic audit proof run: `/tmp/proof_snail_phase2b_cipher_audit_20260426T195232Z`
- `python3 -m pytest tests` (not run; pytest is not installed)
- `./scripts/qa_gate.sh` (PASS; proof `.harness/proofs/proof_20260426T195237Z`)

Proof/report source:
- Original handoff proof dir `/tmp/proof_snail_protocol_reset_20260426T170226Z` was no longer present.
- The four safe Markdown proof reports were reviewed and promoted from `quarantine/tmp-imports/20260426T173840Z/unknown-review/`.

Remaining unknowns:
- External proof originals must be restored or reacquired before the Phase 2B audit runner can complete a live audit.
- Cipher remains incomplete: unmapped alphanumerics are `6`, `H`, `S`, `b`, `d`, `r`; punctuation remains unresolved.

## 2026-04-26 — Evidence ledger and source-of-truth map created

Status: first proof-backed evidence review drafted without decoding or modifying raw evidence.

Files changed:
- Added `reports/evidence-inventory-report.md`
- Added `reports/source-of-truth-map.md`
- Updated `feature_list.json` for `evidence-inventory-001`
- Updated `scripts/qa_gate.sh` so deletion-only staged forbidden paths can be cleaned up safely
- Updated `scripts/git_auto_sync.sh` with the same deletion-only cleanup allowance
- Removed tracked placeholder files:
  - `evidence/originals/.gitkeep`
  - `evidence/quarantine/.gitkeep`

Commands run:
- `cat ./AGENTS.md`
- `cat ./claude-progress.md`
- `source ./init.sh`
- `cat ./PROJECT_INSTRUCTIONS.md`
- `cat ./QUALITY_CRITERIA.md`
- `cat ./feature_list.json`
- `ls -td evidence/tmp-imports/* | head -1`
- `cat evidence/tmp-imports/*/MANIFEST.md`
- `cat evidence/tmp-imports/*/MANIFEST.tsv`
- `cat reports/tmp-import-*.md`
- `find originals -maxdepth 4 -type f -print`
- `find quarantine -maxdepth 5 -type f -print`
- `find data/protocol -maxdepth 4 -type f -print`
- `find docs/protocol -maxdepth 4 -type f -print`
- `find scripts/imported-tools -maxdepth 3 -type f -print`
- `stat -c '%a %A %s %n' originals/tmp-imports/20260426T173840Z/*.luac`
- `sha256sum originals/tmp-imports/20260426T173840Z/*.luac`
- `sha256sum data/protocol/decoded/* data/protocol/substitution-tables/* docs/protocol/*`
- `rg -n "open\\(|write|wb|ab|shutil|copy|rename|replace|luac|original|quarantine|decoded|protocol" quarantine/tmp-imports/20260426T173840Z/suspect-scripts`
- `git status --short`
- `git ls-files | grep -Ei '\\.(luac|apk|xapk|apks|aab|so|pcap|pcapng|flow|har)$' || true`
- `git ls-files | grep -E '(^|/)originals/|(^|/)quarantine/|(^|/)captures/|(^|/)\\.env' || true`
- `git rm evidence/originals/.gitkeep evidence/quarantine/.gitkeep`
- `./snail-run init`
- `./snail-run qa` (initial fail: deletion-only placeholder cleanup was staged under forbidden paths)
- `./snail-run qa` (PASS)
- `git diff --cached --name-only`
- `git diff --cached --name-status`
- `./scripts/git_auto_sync.sh "docs: add Super Snail evidence ledger and source-of-truth map"` (PASS; commit `fcaa38d`)

Proof directory:
- Initial failed QA: `.harness/proofs/proof_20260426T174702Z`
- Passing QA: `.harness/proofs/proof_20260426T174744Z`
- Autosync QA: `.harness/proofs/proof_20260426T174820Z`

Remaining unknowns:
- Same-name `.luac` files have conflicting hashes and sizes; fresh reacquisition or source confirmation is required before decoding.
- Imported decoded/protocol outputs remain hypothesis-level until re-derived from confirmed Tier 0 originals.
- `quarantine/tmp-imports/20260426T173840Z/unknown-review/` still needs separate review before any item is promoted.

## 2026-04-26 — /tmp import organized and QA passed

Status: 90 files imported from /tmp into structured workspace.

Files changed:
- Created `scripts/import_tmp_project_files.py` (focused importer, exact filenames + proof_snail dirs)
- Imported 90 files from /tmp:
  - decoded_outputs: 7
  - protocol_docs: 6
  - raw_evidence: 9 (made read-only under `originals/tmp-imports/`)
  - safe_scripts: 23 (under `scripts/imported-tools/`)
  - substitution_tables: 4 (under `data/protocol/substitution-tables/`)
  - suspect_scripts: 10 (quarantined under `quarantine/tmp-imports/*/suspect-scripts/`)
  - unknown_review_required: 31 (quarantined under `quarantine/tmp-imports/*/unknown-review/`)
- Evidence dir: `evidence/tmp-imports/20260426T173840Z/`
  - MANIFEST.tsv, MANIFEST.md, source-tree.txt, skipped.txt
- Report: `reports/tmp-import-20260426T173840Z.md`

Commands run:
- `python3 scripts/import_tmp_project_files.py`
- `./snail-run init`
- `./snail-run qa` (PASS)

Proof directories:
- Harness install: `.harness/proofs/proof_20260426T172947Z`
- Import: `.harness/proofs/proof_20260426T173927Z`

Caveats:
- Fixed qa_gate.sh to exclude `import_tmp_project_files.py` from .luac overwrite scan (it contains detection regexes).
- Raw `.luac` files are read-only under ignored `originals/`.
- Suspect scripts (final_solve.py, solve_and_rewrite.py, etc.) are in quarantine.
- `unknown_review_required` files are mostly prior proof-pack metadata; they need review before use as evidence.

Next recommended task:
- Review quarantined scripts for actual `.luac` writes.
- Verify safe scripts before promoting from `scripts/imported-tools/`.
- Generate protocol inventory from imported substitution tables and decoded outputs.

## 2026-04-26 — Lite harness installed and QA passed

Status: integrated into workspace.

Files changed:
- Added AGENTS.md, PROJECT_INSTRUCTIONS.md, QUALITY_CRITERIA.md, feature_list.json, init.sh, snail-run
- Added scripts: inventory.py, proof_pack.sh, qa_gate.sh, git_auto_sync.sh, make_prompt.sh
- Added docs/INSTALL.md, reports/HARNESS_DESIGN_NOTES.md
- Created directories: .harness/, originals/, quarantine/, reports/, docs/
- Removed duplicate PROJECT_INSTRUCTIONS (2).md
- Updated .gitignore with harness rules (originals/, quarantine/, .harness/logs/, binary dumps)

Commands run:
- `./snail-run init`
- `./snail-run qa` (PASS)

Proof directory: .harness/proofs/proof_20260426T172947Z

Caveats:
- Fixed qa_gate.sh to exclude itself from .luac overwrite scan.
- Fixed qa_gate.sh to ignore comments when scanning for `git add .`.
- Fixed proof_pack.sh to suppress stdout from risky-file counter.

Next recommended task:
- Run `./scripts/qa_gate.sh`.
- Review generated proof directory.
- Run `./scripts/git_auto_sync.sh` only if QA passes.

## 2026-04-27 — Phase 2N template expansion

Status: expanded the shared Phase 2L/2M phrase-template set using stable API/member-access anchors only.

Files changed:
- Updated `src/decode/phase2l_standard_phrase_gap_audit.py`
- Added `reports/phase2n-template-expansion-20260427T155912Z.md`
- Updated `PROJECT_STATUS.md`
- Updated `feature_list.json`

Commands run:
- `python3 tests/test_phase2l_standard_phrase_gap_audit.py` (PASS)
- `python3 tests/test_phase2m_phrase_coverage.py` (PASS)
- `python3 src/decode/phase2l_standard_phrase_gap_audit.py --input-proof /tmp/proof_snail_phase2k_simple_anchor_inventory_20260427T152519Z`
- `python3 src/decode/phase2m_phrase_coverage.py --input-proof /tmp/proof_snail_phase2k_simple_anchor_inventory_20260427T152519Z`

Proof directories:
- `/tmp/proof_snail_phase2l_standard_phrase_gap_20260427T155912Z`
- `/tmp/proof_snail_phase2m_phrase_coverage_20260427T155912Z`

Result:
- Phase 2L phrase occurrences increased from 1544 to 1772.
- Repeated conflict-free contexts increased from 87 to 146.
- Context conflicts remained 0.
- Phase 2M handlers with >=50% phrase coverage increased from 6 to 22.
- Max phrase-template coverage increased from 54.84% to 69.33%.

Caveats:
- This is still phrase-template coverage, not full source recovery.
- No global punctuation mapping was promoted.
- Raw `.luac` originals remain external and uncommitted.

Next recommended task:
- Build a redacted template-overlay decoder that emits phrase IDs, known local gaps, unresolved spans, input hashes, and conflict ledgers.

## 2026-04-27 — Phase 2O template overlay decoder

Status: added a redacted template-overlay decoder that consumes the Phase 2N phrase ledger.

Files changed:
- Added `src/decode/phase2o_template_overlay_decoder.py`
- Added `tests/test_phase2o_template_overlay_decoder.py`
- Added `reports/phase2o-template-overlay-decoder-20260427T160243Z.md`
- Updated `PROJECT_STATUS.md`
- Updated `feature_list.json`

Commands run:
- `python3 tests/test_phase2o_template_overlay_decoder.py` (PASS)
- `python3 -m py_compile src/decode/phase2o_template_overlay_decoder.py` (PASS)
- `python3 src/decode/phase2o_template_overlay_decoder.py --input-proof /tmp/proof_snail_phase2k_simple_anchor_inventory_20260427T152519Z --phrase-proof /tmp/proof_snail_phase2l_standard_phrase_gap_20260427T155912Z`

Proof directory:
- `/tmp/proof_snail_phase2o_template_overlay_20260427T160243Z`

Result:
- 838 small handlers scanned.
- 1771 non-overlapping phrase overlays selected.
- 2133 unresolved spans recorded.
- 3338 known phrase-local gap rows.
- 0 unknown gap rows.
- 0 conflict gap rows.

Caveats:
- Redacted overlays are not source reconstruction.
- Unresolved spans remain intentionally opaque.
- Raw `.luac` originals remain external and uncommitted.

Next recommended task:
- Rank repeated unresolved spans and add only reusable high-confidence templates.

## 2026-04-27 — Phase 2P unresolved span inventory

Status: ranked unresolved spans from the Phase 2O redacted overlays.

Files changed:
- Added `src/decode/phase2p_unresolved_span_inventory.py`
- Added `tests/test_phase2p_unresolved_span_inventory.py`
- Added `reports/phase2p-unresolved-span-inventory-20260427T160515Z.md`
- Updated `PROJECT_STATUS.md`
- Updated `feature_list.json`

Commands run:
- `python3 tests/test_phase2p_unresolved_span_inventory.py` (PASS)
- `python3 -m py_compile src/decode/phase2p_unresolved_span_inventory.py` (PASS)
- `python3 src/decode/phase2p_unresolved_span_inventory.py --input-proof /tmp/proof_snail_phase2k_simple_anchor_inventory_20260427T152519Z --overlay-proof /tmp/proof_snail_phase2o_template_overlay_20260427T160243Z`

Proof directory:
- `/tmp/proof_snail_phase2p_unresolved_span_inventory_20260427T160515Z`

Result:
- 838 input handlers.
- 2000 unresolved span rows.
- 1867 unique unresolved spans.
- 36 repeated unresolved spans.
- Sensitive span text stayed external only.

Caveats:
- This inventory is for template targeting, not source reconstruction.
- The committed report contains only hashes/counts/sample filenames.

Next recommended task:
- Use the top repeated unresolved hashes to add a small Phase 2Q template pass.

## 2026-04-27 — Phase 2Q external template trial

Status: tested repeated unresolved spans as external-only candidate templates.

Files changed:
- Added `src/decode/phase2q_external_template_trial.py`
- Added `tests/test_phase2q_external_template_trial.py`
- Added `reports/phase2q-external-template-trial-20260427T160811Z.md`
- Updated `PROJECT_STATUS.md`
- Updated `feature_list.json`

Commands run:
- `python3 tests/test_phase2q_external_template_trial.py` (PASS)
- `python3 -m py_compile src/decode/phase2q_external_template_trial.py` (PASS)
- `python3 src/decode/phase2q_external_template_trial.py --input-proof /tmp/proof_snail_phase2k_simple_anchor_inventory_20260427T152519Z --span-proof /tmp/proof_snail_phase2p_unresolved_span_inventory_20260427T160515Z`

Proof directory:
- `/tmp/proof_snail_phase2q_external_template_trial_20260427T160811Z`

Result:
- 12 external candidate templates selected.
- 838 handlers scanned.
- 1977 phrase sequence rows.
- Handlers with >=50% phrase coverage increased from 22 to 45.
- Max coverage stayed 69.33%.
- Candidate template text stayed external only.

Caveats:
- External candidates are not promoted templates yet.
- Next pass must classify reusable API/grammar fragments versus event-specific constants.

Next recommended task:
- Classify the 12 external candidates and promote only reusable API/member or grammar templates.

## 2026-04-27 — Phase 2R candidate classifier

Status: classified the Phase 2Q external candidate templates into safe promotion buckets.

Files changed:
- Added `src/decode/phase2r_candidate_classifier.py`
- Added `tests/test_phase2r_candidate_classifier.py`
- Added `reports/phase2r-candidate-classifier-20260427T195222Z.md`
- Updated `PROJECT_STATUS.md`
- Updated `feature_list.json`

Commands run:
- `python3 tests/test_phase2r_candidate_classifier.py` (PASS)
- `python3 -m py_compile src/decode/phase2r_candidate_classifier.py` (PASS)
- `python3 src/decode/phase2r_candidate_classifier.py --template-proof /tmp/proof_snail_phase2q_external_template_trial_20260427T160811Z`

Proof directory:
- `/tmp/proof_snail_phase2r_candidate_classifier_20260427T195222Z`

Result:
- 12 candidate templates classified.
- 8 candidate-promotable rows.
- 3 API/member fragments.
- 5 grammar fragments.
- 4 domain/event constants kept external.
- Candidate text stayed external only.

Caveats:
- Candidate-promotable does not mean promoted into the decoder yet.
- The next pass must rerun conflict checks after any promotion.

Next recommended task:
- Promote only the 8 candidate-promotable rows into named template IDs, rerun Phase 2L/2M/2O, and verify no phrase-local conflicts.

## 2026-04-27 — Phase 2S promotable template trial

Status: tested only the Phase 2R candidate-promotable rows as external templates.

Files changed:
- Added `src/decode/phase2s_promotable_template_trial.py`
- Added `tests/test_phase2s_promotable_template_trial.py`
- Added `reports/phase2s-promotable-template-trial-20260427T195500Z.md`
- Updated `PROJECT_STATUS.md`
- Updated `feature_list.json`

Commands run:
- `python3 tests/test_phase2s_promotable_template_trial.py` (PASS)
- `python3 -m py_compile src/decode/phase2s_promotable_template_trial.py` (PASS)
- `python3 src/decode/phase2s_promotable_template_trial.py --input-proof /tmp/proof_snail_phase2k_simple_anchor_inventory_20260427T152519Z --classifier-proof /tmp/proof_snail_phase2r_candidate_classifier_20260427T195222Z`

Proof directory:
- `/tmp/proof_snail_phase2s_promotable_template_trial_20260427T195500Z`

Result:
- 8 promotable external templates selected.
- 838 handlers scanned.
- 1948 phrase sequence rows.
- Handlers with >=50% phrase coverage increased from 22 to 36 versus the Phase 2N base.
- Phase 2S is stricter than Phase 2Q's 45 because it excludes 4 domain/event constants.
- Candidate text stayed external only.

Caveats:
- This is a coverage trial, not a punctuation-complete source reconstruction.
- Next pass should verify overlap/conflict behavior with base and promotable templates separately tagged.

Next recommended task:
- Run a conflict-aware overlay pass that keeps base templates and promotable external templates separately tagged.

## 2026-04-27 — Phase 2T conflict-aware overlay

Status: rendered base and promotable external templates in one source-tagged redacted overlay.

Files changed:
- Added `src/decode/phase2t_conflict_overlay.py`
- Added `tests/test_phase2t_conflict_overlay.py`
- Added `reports/phase2t-conflict-overlay-20260427T195741Z.md`
- Updated `PROJECT_STATUS.md`
- Updated `feature_list.json`

Commands run:
- `python3 tests/test_phase2t_conflict_overlay.py` (PASS)
- `python3 -m py_compile src/decode/phase2t_conflict_overlay.py` (PASS)
- `python3 src/decode/phase2t_conflict_overlay.py --input-proof /tmp/proof_snail_phase2k_simple_anchor_inventory_20260427T152519Z --phrase-proof /tmp/proof_snail_phase2l_standard_phrase_gap_20260427T155912Z --classifier-proof /tmp/proof_snail_phase2r_candidate_classifier_20260427T195222Z`

Proof directory:
- `/tmp/proof_snail_phase2t_conflict_overlay_20260427T195741Z`

Result:
- 838 handlers scanned.
- 1948 candidate occurrences.
- 1945 selected occurrences.
- 3 skipped overlaps.
- 1771 selected base occurrences.
- 174 selected promotable external occurrences.
- 3338 known gap rows.
- 0 unknown gap rows.
- 0 conflict gap rows.

Caveats:
- Promotable template text stayed external only.
- This remains redacted overlay evidence, not decoded source.

Next recommended task:
- Identify which selected promotable external templates deserve stable committed names, while keeping exact sensitive text external unless it is already a known project-safe API/member name.

## 2026-04-27 — Phase 2U promotable stats

Status: ranked selected promotable external templates using sanitized metadata only.

Files changed:
- Added `src/decode/phase2u_promotable_stats.py`
- Added `tests/test_phase2u_promotable_stats.py`
- Added `reports/phase2u-promotable-stats-20260427T195959Z.md`
- Updated `PROJECT_STATUS.md`
- Updated `feature_list.json`

Commands run:
- `python3 tests/test_phase2u_promotable_stats.py` (PASS)
- `python3 -m py_compile src/decode/phase2u_promotable_stats.py` (PASS)
- `python3 src/decode/phase2u_promotable_stats.py --overlay-proof /tmp/proof_snail_phase2t_conflict_overlay_20260427T195741Z --classifier-proof /tmp/proof_snail_phase2r_candidate_classifier_20260427T195222Z`

Proof directory:
- `/tmp/proof_snail_phase2u_promotable_stats_20260427T195959Z`

Result:
- 8 promotable templates seen.
- 174 total selected promotable occurrences.
- 2 total skipped promotable overlaps.
- Top 2 API/member fragments had 83 selected overlays combined and zero skipped overlaps.
- The short grammar fragment had 42 selected overlays but 2 skipped overlaps.

Caveats:
- This proof uses sanitized metadata only.
- It ranks candidates but does not promote exact candidate text into committed code.

Next recommended task:
- Inspect the top API/member candidates externally and decide whether their exact names are safe to promote as committed template identifiers.

## 2026-04-27 — Phase 2V API template promotion

Status: promoted only the two strongest API/member candidates into the committed base phrase table.

Files changed:
- Updated `src/decode/phase2l_standard_phrase_gap_audit.py`
- Added `reports/phase2v-api-template-promotion-20260427T200147Z.md`
- Updated `PROJECT_STATUS.md`
- Updated `feature_list.json`

Commands run:
- `python3 tests/test_phase2l_standard_phrase_gap_audit.py` (PASS)
- `python3 tests/test_phase2m_phrase_coverage.py` (PASS)
- `python3 tests/test_phase2o_template_overlay_decoder.py` (PASS)
- `python3 -m py_compile src/decode/phase2l_standard_phrase_gap_audit.py src/decode/phase2m_phrase_coverage.py src/decode/phase2o_template_overlay_decoder.py` (PASS)
- `python3 src/decode/phase2l_standard_phrase_gap_audit.py --input-proof /tmp/proof_snail_phase2k_simple_anchor_inventory_20260427T152519Z`
- `python3 src/decode/phase2m_phrase_coverage.py --input-proof /tmp/proof_snail_phase2k_simple_anchor_inventory_20260427T152519Z`
- `python3 src/decode/phase2o_template_overlay_decoder.py --input-proof /tmp/proof_snail_phase2k_simple_anchor_inventory_20260427T152519Z --phrase-proof /tmp/proof_snail_phase2l_standard_phrase_gap_20260427T200142Z`

Proof directories:
- `/tmp/proof_snail_phase2l_standard_phrase_gap_20260427T200142Z`
- `/tmp/proof_snail_phase2m_phrase_coverage_20260427T200142Z`
- `/tmp/proof_snail_phase2o_template_overlay_20260427T200147Z`

Result:
- Promoted `dormutil_close_communicating`.
- Promoted `close_communicating_dorm`.
- Phase 2L context conflicts remained 0.
- Phase 2M handlers with >=50% base-template coverage increased from 22 to 32.
- Phase 2O unknown/conflict gap rows remained 0/0.

Caveats:
- Lower-confidence API and grammar candidates remain external.
- This is still phrase-template overlay progress, not full source recovery.

Next recommended task:
- Build a grammar-context audit for the remaining external grammar fragments, especially the short fragment with 42 selected overlays and 2 skipped overlaps.

## 2026-04-27 — Phase 2W grammar fragment audit

Status: audited external grammar fragments for promotion risk.

Files changed:
- Added `src/decode/phase2w_grammar_fragment_audit.py`
- Added `tests/test_phase2w_grammar_fragment_audit.py`
- Added `reports/phase2w-grammar-fragment-audit-20260427T200422Z.md`
- Updated `PROJECT_STATUS.md`
- Updated `feature_list.json`

Commands run:
- `python3 tests/test_phase2w_grammar_fragment_audit.py` (PASS)
- `python3 -m py_compile src/decode/phase2w_grammar_fragment_audit.py` (PASS)
- `python3 src/decode/phase2w_grammar_fragment_audit.py --classifier-proof /tmp/proof_snail_phase2r_candidate_classifier_20260427T195222Z --overlay-proof /tmp/proof_snail_phase2t_conflict_overlay_20260427T195741Z`

Proof directory:
- `/tmp/proof_snail_phase2w_grammar_fragment_audit_20260427T200422Z`

Result:
- 5 grammar candidates audited.
- 2 marked `trial_ok`.
- 3 marked `hold`.
- The high-count short fragment stayed on hold because it has skipped overlaps.
- Fragment text stayed external only.

Caveats:
- `trial_ok` means suitable for external-only trial, not committed plaintext promotion.
- Punctuation-aware validation is still needed.

Next recommended task:
- Run an external-only punctuation-aware trial for the two `trial_ok` grammar fragments.

## 2026-04-27 — Phase 3 proxy-readiness pass completed

Status: Tested emulator proxy setup, mitmproxy CA cert installation, and game traffic interception. HTTPS game traffic is not visible — TLS handshake failures indicate certificate pinning or user-CA rejection.

Files changed:
- Added `reports/phase3-proxy-readiness-20260427T220000Z.md`
- Updated `claude-progress.md`
- Updated `feature_list.json`

Commands run:
- `adb -s emulator-5554 shell settings put global http_proxy 10.0.2.2:8080`
- `adb -s emulator-5554 shell settings get global http_proxy`
- `mitmdump --set stream_large_bodies=1 -w captures/private/phase3/20260427T180051/proxy_flows.mitm`
- `adb -s emulator-5554 push ~/.mitmproxy/mitmproxy-ca-cert.cer /sdcard/`
- `adb -s emulator-5554 shell am start -a android.intent.action.VIEW -d file:///sdcard/mitmproxy-ca-cert.cer -t application/x-x509-ca-cert`
- `adb -s emulator-5554 shell "mkdir -p /data/misc/user/0/cacerts-added/ && cp /sdcard/mitmproxy-ca-cert.cer /data/misc/user/0/cacerts-added/"`
- `adb -s emulator-5554 shell am force-stop com.qcplay.snail.android.na`
- `adb -s emulator-5554 shell monkey -p com.qcplay.snail.android.na -c android.intent.category.LAUNCHER 1`
- `adb -s emulator-5554 shell "cat /proc/15163/net/tcp"`
- `adb -s emulator-5554 shell settings put global http_proxy :0`
- `sha256sum captures/private/phase3/20260427T180051/proxy_flows.mitm`
- `sha256sum captures/private/phase3/20260427T180051/mitmdump_pre_game.log`

Proof directory:
- `captures/private/phase3/20260427T180051/`
- Flow file SHA256: `c77d23dcf18a4ea79b998b2b4f40d79132fee148a310c0b1f54f84ae5c5408b5`
- Log file SHA256: `60b4f7f3ccf0389203eb9a302538606ea845f9e42c483995ee85935f63c6ac94`

What passed:
- Emulator proxy setting applied and removed cleanly.
- mitmdump started in private capture mode with `stream_large_bodies=1`.
- Flow files written to `captures/private/phase3/` (gitignored).
- Game process (PID 15163) confirmed routing TCP through proxy.
- HTTP telemetry to `log.game.qcplay.com:80` visible.
- TLS handshake failures documented for HTTPS traffic.

Remaining unknowns:
- Whether the game uses certificate pinning or just standard user-CA rejection.
- Primary HTTPS API domain(s) for game logic.
- Auth flow, token format, and transport protocol.
- Whether Frida SSL-unpinning will reveal game HTTPS traffic.

Recommended next step:
- Frida SSL-unpinning pass to disable certificate validation in the game process.

## 2026-04-27 — Phase 3 Frida SSL-unpinning pass completed

Status: Deployed frida-server, applied universal Java-layer SSL unpinning, and successfully intercepted HTTPS traffic from the game process.

Files changed:
- Added `scripts/frida_ssl_unpin.js`
- Added `reports/phase3-frida-unpin-20260427T220000Z.md`
- Updated `claude-progress.md`
- Updated `feature_list.json`

Commands run:
- `frida-ps -U | head -5` (verified Frida server running)
- `adb -s emulator-5554 push /tmp/frida-server /data/local/tmp/frida-server`
- `adb -s emulator-5554 shell "chmod 755 /data/local/tmp/frida-server && nohup /data/local/tmp/frida-server &"`
- `timeout 60 frida -U -f com.qcplay.snail.android.na -l scripts/frida_ssl_unpin.js`
- `adb -s emulator-5554 shell settings put global http_proxy 10.0.2.2:8080`
- `nohup mitmdump --set stream_large_bodies=1 -w captures/private/phase3/20260427T195500/proxy_flows.mitm`
- `adb -s emulator-5554 shell am force-stop com.qcplay.snail.android.na`
- `adb -s emulator-5554 shell "cat /proc/15750/net/tcp"` (socket analysis)
- `adb -s emulator-5554 shell "cat /proc/15750/net/udp"` (socket analysis)
- `sha256sum captures/private/phase3/20260427T195500/proxy_flows.mitm`
- `sha256sum captures/private/phase3/20260427T195500/mitmdump.log`
- `adb -s emulator-5554 shell settings put global http_proxy :0`
- `kill $(cat captures/private/phase3/20260427T195500/mitmdump.pid)`

Proof directory:
- `captures/private/phase3/20260427T195500/`
- Flow file SHA256: `36eb8789e55b23f56da5415b924724b3469eb284b57968c68c7ba3eb192ec8d9`
- Log file SHA256: `d5fb865ce9968bc675e05df4983e8365365f728b8e385d8fab42862e4a5cd075`

What passed:
- Frida server 17.9.1 deployed and running on emulator (PID 15695).
- Frida spawn-gating (-f) successfully launches game.
- Universal SSL unpinning script applied and active.
- Conscrypt TrustManagerImpl successfully bypassed.
- HTTPS flows from game process visible in mitmproxy (6 client connections, 11 requests).
- Domains intercepted: graph.facebook.com, qcplay.aihelp.net, x2eayo.launches.appsflyersdk.com, cloudfront.net.
- No TLS handshake failures observed after unpinning.
- Proxy setting removed after test.
- Raw captures stored in gitignored private directory.

Remaining unknowns:
- Game API endpoint — actual game server API not called during startup.
- Auth flow — login/authentication endpoint not observed.
- WebSocket usage — not observed, may be used for real-time features.
- Native TLS in libcocos2dlua.so — may have separate TLS implementation.
- Telemetry correlation — log.game.qcplay.com events vs. Phase 2C protocol names.
- Rank/group/arena endpoints — not triggered during startup-only capture.

Recommended next steps:
1. Interactive game session capture (5-10 min) with Frida active to trigger game API calls.
2. WebSocket detection pass if REST API doesn't appear.
3. Native BoringSSL hooking in libcocos2lua.so as fallback.
4. Extended telemetry correlation pass.

## 2026-04-28 — Phase 3 interactive session capture completed

Status: User completed tutorial and browsed game menus (rankings, club, arena) over ~40 minute session. Captured 3,094 client connections with Frida SSL unpinning active.

Files changed:
- Added `reports/phase3-interactive-session-20260428T010000Z.md`
- Updated `claude-progress.md`
- Updated `feature_list.json`

Commands run:
- `adb -s emulator-5554 shell am force-stop com.qcplay.snail.android.na`
- `timeout 600 frida -U -n "Super Snail" -l scripts/frida_ssl_unpin.js`
- `nohup mitmdump --set stream_large_bodies=1 -w captures/private/phase3/20260428T002048/interactive_session.flow`
- `adb -s emulator-5554 shell "monkey -p com.qcplay.snail.android.na -c android.intent.category.LAUNCHER 1"`
- User interaction: tutorial completion, login, rankings/club/arena menu browsing
- `kill -INT $(cat captures/private/phase3/20260428T002048/mitmdump.pid)`
- `adb -s emulator-5554 shell settings put global http_proxy :0`
- `sha256sum captures/private/phase3/20260428T002048/interactive_session.flow`
- `sha256sum captures/private/phase3/20260428T002048/mitmdump.log`
- Domain extraction and traffic analysis

Proof directory:
- `captures/private/phase3/20260428T002048/`
- Flow file SHA256: `1aaeaaf3b43bc9b6e8622ee7333790274250bac348aecbea3654539de5185dfc`
- Log file SHA256: `4f3825d20280307902c02fd0991b36f1db310f4ea7eee600943b53d863bf62f5`

What passed:
- ~40 minute interactive session captured with user performing tutorial + menu navigation.
- 3,094 client connections recorded.
- Java-layer SSL unpinning working (Conscrypt bypassed).
- Game API endpoint identified: `POST http://47.252.33.99:8081/game_post` (2 calls observed).
- Config infrastructure mapped: .dis files, relay configs, CDN endpoints.
- 58 telemetry sync calls to `log.game.qcplay.com` observed.
- Multiple game servers identified: 47.252.38.146, 47.88.17.195, 47.252.32.158.

Key findings:
- **JPush is the main transport**: 2,750 failed TLS connections to `jpush-hw-game.qcplay.com:443`.
- JPush uses native TLS (not Java-layer) — our Frida unpinning cannot intercept it.
- Only 2 game_post calls during 40-minute session suggests heavy caching or JPush for real-time.
- No Phase 2C protocol names (msg_group_rank, msg_arena_top_query, etc.) observed in URLs.

Remaining unknowns:
- JPush protocol content (requires native BoringSSL hooking).
- Phase 2C protocol correlation (may be in binary JPush payload).
- Auth mechanism (token in POST body vs header).
- Whether rank/group/arena API calls were triggered by user actions.

Recommended next step:
- Native BoringSSL hooking in libcocos2lua.so to intercept JPush traffic (the likely main protocol).

---

## 2026-04-28 — Phase 3 hook session (emulator cleanup + frida-server restart)

Status: Killed stale emulator process, restarted frida-server 17.9.1, attached application-layer hook to Super Snail PID 4063. User navigated game menus but no protocol traffic was captured in logs.

Files changed:
- Added `reports/phase3-hook-session-20260428T161430Z.md`
- Updated `claude-progress.md`

Commands run:
- `kill 774940` (already terminated)
- `adb root`
- `adb push /tmp/frida-server /data/local/tmp/frida-server`
- `adb shell chmod +x /data/local/tmp/frida-server`
- `adb shell "nohup /data/local/tmp/frida-server > /dev/null 2>&1 &"`
- `frida-ps -U | head` (verified frida-server running, PID 5136)
- `python3 scripts/run_phase3_hook.py` (attached to PID 4063)
- Inspected `.harness/logs/phase3_protocol_hook*.log` (initialization only, no traffic)
- `./scripts/qa_gate.sh` (PASS)

Proof directory:
- `.harness/proofs/proof_20260428T161535Z`

What passed:
- Frida-server deployed and stable on emulator.
- Attach-mode hook applied successfully to all 6 symbols.
- No secrets, tokens, or account data logged.
- QA gate passed.

Remaining unknowns:
- Why no `OnPacketArrived` / `OnDataRecved` events fired during user navigation.
- Whether target menus were already cached from prior session.
- Whether JPush remote process (PID 4594) handles the rank/arena/club protocol traffic.
- Need precise UI navigation instructions for user to trigger server sync.

Recommended next steps:
1. User performs precise navigation: Rankings tab switch, Club member list, Arena top players.
2. Try cold-start attach immediately after game launch to capture `AddMsgDefine` registrations.
3. Hook JPush remote process separately if main process remains silent.

---

## 2026-04-28 — Phase 3 live traffic capture via tcpdump

Status: Used device tcpdump to capture raw TCP traffic to game server (47.252.2.69:50504) during user navigation. Confirmed active protocol communication exists but bypasses the CommMgr application-layer hooks.

Files changed:
- Added `reports/phase3-live-traffic-capture-20260428.md`
- Updated `claude-progress.md`

Commands run:
- `adb shell am force-stop com.qcplay.snail.android.na` (multiple restarts)
- `adb shell am start -n com.qcplay.snail.android.na/org.cocos2dx.lua.AppActivity`
- `adb shell 'ps -A | grep qcplay'` (verified PIDs: 6997 main, 4781 jpushremote)
- `nohup python3 -u scripts/run_phase3_hook.py` (attached to PID 6997, no events)
- `adb shell "tcpdump -i any -n host 47.252.2.69 -c 20 -w /data/local/tmp/capture.pcap"` (captured 20 packets)
- `adb pull /data/local/tmp/capture.pcap /tmp/game_capture.pcap`
- `tcpdump -r /tmp/game_capture.pcap -X -n` (analyzed payloads)
- `adb shell 'cat /proc/6997/net/tcp'` (confirmed active connection to 47.252.2.69:50504)

Proof directory:
- External capture: `/tmp/game_capture.pcap` (4,657 bytes, 20 packets)
- SHA256: `3a9b12fc42949aa22f8319dc537bbe65485585b5b3121386175f4618ed63bc94`

What passed:
- Confirmed persistent TCP connection between main process and 47.252.2.69:50504.
- Captured 20 packets (20–1440 bytes) during user navigation.
- Identified custom binary protocol with 8-byte `4d5a` header/preamble.
- Both main and JPush processes show the same socket inode in /proc/net/tcp.

Key findings:
- **CommMgr hooks are functional but target the wrong layer.** Traffic does not flow through `OnPacketArrived` / `OnDataRecved` for this connection.
- Protocol uses custom binary framing, not HTTP/JSON.
- Payload structure (hypothesis): 8-byte magic (`4d5a 0000 0000 0000`) + 4-byte length + data.
- JPush remote process may be mediating or sharing the socket.

Remaining unknowns:
- Exact dispatch path (recv callback, SSL_read, or IPC from JPush process).
- Whether `msg_group_rank`, `msg_arena_top_query` etc. travel on this connection.
- Encryption/compression used on the wire.
- Full message framing and msg_id mapping.

Recommended next steps:
1. Hook native `recv()` or `SSL_read` directly on main process PID 6997.
2. Investigate socket sharing between main and JPush processes.
3. Run extended capture during specific menu actions (rankings tab switch, arena challenge).
