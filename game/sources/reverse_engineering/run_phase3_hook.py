#!/usr/bin/env python3
"""
Phase 3 Protocol Hook Runner
Attaches to the running Super Snail game process, loads the Frida hook script,
and logs sanitized output to a file.
"""

import frida
import sys
import os
import datetime
import signal

PID = None  # Will be auto-detected
SCRIPT_PATH = "scripts/frida_protocol_hook.js"
LOG_PATH = ".harness/logs/phase3_protocol_hook.log"

def find_pid():
    device = frida.get_usb_device()
    for proc in device.enumerate_processes():
        if proc.name == "Super Snail":
            return proc.pid
    return None

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
    pid = find_pid()
    if pid is None:
        print("[-] Super Snail process not found")
        sys.exit(1)
    print(f"[*] Attaching to Super Snail PID {pid}")

    device = frida.get_usb_device()
    session = device.attach(pid)

    with open(SCRIPT_PATH, "r") as f:
        script_source = f.read()

    script = session.create_script(script_source)
    script.on("message", on_message)
    script.load()

    print(f"[*] Hook script loaded. Logging to {LOG_PATH}")
    print("[*] Navigate the game (Rankings, Club, Arena) to trigger protocol messages.")
    print("[*] Press Ctrl+C to stop.")

    # Keep running until interrupted
    def signal_handler(sig, frame):
        print("\n[*] Detaching...")
        session.detach()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()

if __name__ == "__main__":
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    main()
