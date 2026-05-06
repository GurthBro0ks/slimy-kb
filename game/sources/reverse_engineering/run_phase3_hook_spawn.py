#!/usr/bin/env python3
"""
Phase 3 Protocol Hook Runner — Spawn-gate version
Spawns the Super Snail game process, loads the Frida hook script before
any Lua code runs, and captures AddMsgDefine registrations + early traffic.
"""

import frida
import sys
import os
import datetime
import signal

PACKAGE = "com.qcplay.snail.android.na"
SCRIPT_PATH = "scripts/frida_protocol_hook.js"
LOG_PATH = ".harness/logs/phase3_protocol_hook_spawn.log"

def on_message(message, data):
    ts = datetime.datetime.now().isoformat()
    if message["type"] == "send":
        line = f"[{ts}] SEND: {message['payload']}"
    elif message["type"] == "error":
        line = f"[{ts}] ERROR: {message['stack']}"
    else:
        line = f"[{ts}] {message}"
    print(line)
    with open(LOG_PATH, "a") as f:
        f.write(line + "\n")

def main():
    device = frida.get_usb_device()
    pid = device.spawn([PACKAGE])
    print(f"[*] Spawned {PACKAGE} PID {pid}")

    session = device.attach(pid)

    with open(SCRIPT_PATH, "r") as f:
        script_source = f.read()

    script = session.create_script(script_source)
    script.on("message", on_message)
    script.load()

    print(f"[*] Hook script loaded before resume. Logging to {LOG_PATH}")
    device.resume(pid)
    print("[*] Process resumed. Waiting for protocol traffic...")

    def signal_handler(sig, frame):
        print("\n[*] Detaching...")
        session.detach()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()

if __name__ == "__main__":
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    main()
