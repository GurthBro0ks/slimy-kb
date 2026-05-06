#!/usr/bin/env python3
"""
Phase 3 — Raw recv()/send() Hook Runner
Attaches Frida to main game process, captures output, logs to private dir.
"""
import sys
import os
import subprocess
import time
import signal
import json
from datetime import datetime
from pathlib import Path

CAPTURE_BASE = Path("captures/private/phase3")
FRIDA_SCRIPT = Path("scripts/frida_recv_hook.js")
PACKAGE = "com.qcplay.snail.android.na"
CAPTURE_DURATION = int(os.environ.get("CAPTURE_DURATION", "300"))  # 5 min default

def get_main_pid():
    """Get PID of main game process (not :jpushremote)."""
    try:
        result = subprocess.run(
            ["adb", "shell", f"pidof {PACKAGE}"],
            capture_output=True, text=True, timeout=10
        )
        pids = result.stdout.strip().split()
        if not pids:
            return None
        
        # If multiple PIDs, find the one that's NOT jpushremote
        if len(pids) == 1:
            return pids[0]
        
        for pid in pids:
            cmdline = subprocess.run(
                ["adb", "shell", f"cat /proc/{pid}/cmdline"],
                capture_output=True, text=True, timeout=5
            )
            if ":jpushremote" not in cmdline.stdout:
                return pid
        return pids[0]  # fallback
    except Exception as e:
        print(f"[-] Error getting PID: {e}")
        return None

def ensure_frida_server():
    """Check if frida-server is running by testing frida-ps connectivity."""
    try:
        result = subprocess.run(
            ["frida-ps", "-U"],
            capture_output=True, text=True, timeout=10
        )
        # frida-server hides itself from process list, but if frida-ps works,
        # frida-server is running
        if result.returncode == 0 and len(result.stdout.strip().split('\n')) > 2:
            print("[+] frida-server running (frida-ps responsive)")
            return True
    except Exception:
        pass
    
    print("[*] Starting frida-server...")
    try:
        subprocess.run(
            ["adb", "shell", "killall frida-server 2>/dev/null; nohup /data/local/tmp/frida-server > /dev/null 2>&1 &"],
            capture_output=True, timeout=5
        )
        time.sleep(3)
        result = subprocess.run(["frida-ps", "-U"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and len(result.stdout.strip().split('\n')) > 2:
            print("[+] frida-server started")
            return True
    except Exception as e:
        print(f"[-] Failed to start frida-server: {e}")
    return False

def run_capture(pid, duration):
    """Run Frida hook for specified duration."""
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    capture_dir = CAPTURE_BASE / timestamp
    capture_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = capture_dir / "frida_recv_hook.log"
    summary_file = capture_dir / "sanitized_summary.json"
    
    print(f"[*] Capture directory: {capture_dir}")
    print(f"[*] Logging to: {log_file}")
    print(f"[*] Duration: {duration}s (or Ctrl+C to stop early)")
    
    cmd = [
        "frida", "-U", "-p", pid,
        "-l", str(FRIDA_SCRIPT)
    ]
    
    with open(log_file, "w") as f:
        process = subprocess.Popen(
            cmd,
            stdout=f,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        try:
            process.wait(timeout=duration)
        except subprocess.TimeoutExpired:
            print("[*] Duration reached, stopping...")
            process.send_signal(signal.SIGINT)
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
        except KeyboardInterrupt:
            print("[*] Ctrl+C received, stopping...")
            process.send_signal(signal.SIGINT)
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
    
    # Generate sanitized summary
    print("[*] Generating sanitized summary...")
    summary = generate_summary(log_file)
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"[+] Summary written to: {summary_file}")
    return capture_dir

def generate_summary(log_file):
    """Parse log and produce sanitized summary (no raw payloads)."""
    summary = {
        "timestamp": datetime.utcnow().isoformat(),
        "packets": {"rx": 0, "tx": 0},
        "frame_sizes": [],
        "message_types": set(),
        "has_4d5a_frames": False,
        "readable_strings_found": False,
        "compression_detected": False,
        "encryption_likely": False,
        "duration_seconds": 0,
    }
    
    start_time = None
    end_time = None
    
    try:
        with open(log_file, "r") as f:
            for line in f:
                line = line.strip()
                
                # Track timestamps
                if "ts=" in line:
                    ts_str = line.split("ts=")[1].split()[0] if "ts=" in line else None
                    if ts_str:
                        try:
                            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                            if start_time is None:
                                start_time = ts
                            end_time = ts
                        except:
                            pass
                
                # Count packets
                if "SERVER->CLIENT" in line:
                    summary["packets"]["rx"] += 1
                elif "CLIENT->SERVER" in line:
                    summary["packets"]["tx"] += 1
                
                # Track frame sizes
                if "len=" in line and ("SERVER->CLIENT" in line or "CLIENT->SERVER" in line):
                    try:
                        size = int(line.split("len=")[1].split()[0])
                        summary["frame_sizes"].append(size)
                    except:
                        pass
                
                # Track 4d5a frames
                if "FRAME: magic=4d5a" in line:
                    summary["has_4d5a_frames"] = True
                
                # Track message types
                if "MSG_TYPE_" in line:
                    try:
                        parts = line.split("MSG_TYPE_LE=0x")
                        if len(parts) > 1:
                            msg_type = parts[1].split()[0]
                            summary["message_types"].add(msg_type)
                    except:
                        pass
                    try:
                        parts = line.split("MSG_TYPE_BE=0x")
                        if len(parts) > 1:
                            msg_type = parts[1].split()[0]
                            summary["message_types"].add(msg_type)
                    except:
                        pass
                
                # Track readable strings
                if "STRINGS:" in line and "found" in line:
                    try:
                        count = int(line.split("STRINGS:")[1].split()[0])
                        if count > 0:
                            summary["readable_strings_found"] = True
                    except:
                        pass
                
                # Check for compression headers
                if "HEX:" in line:
                    hex_part = line.split("HEX:")[1].strip()
                    if "789c" in hex_part or "1f8b" in hex_part:
                        summary["compression_detected"] = True
    except Exception as e:
        print(f"[-] Error parsing log: {e}")
    
    # Calculate duration
    if start_time and end_time:
        summary["duration_seconds"] = (end_time - start_time).total_seconds()
    
    # Determine if encryption is likely
    if summary["has_4d5a_frames"] and not summary["readable_strings_found"] and not summary["compression_detected"]:
        # If we see frames but no strings and no compression, likely encrypted
        if summary["packets"]["rx"] > 2 or summary["packets"]["tx"] > 2:
            summary["encryption_likely"] = True
    
    # Convert set to list for JSON serialization
    summary["message_types"] = sorted(list(summary["message_types"]))
    
    # Frame size stats
    if summary["frame_sizes"]:
        summary["frame_size_stats"] = {
            "count": len(summary["frame_sizes"]),
            "min": min(summary["frame_sizes"]),
            "max": max(summary["frame_sizes"]),
            "avg": round(sum(summary["frame_sizes"]) / len(summary["frame_sizes"]), 1)
        }
    
    return summary

def main():
    print("=" * 60)
    print("Phase 3 Raw recv()/send() Hook Runner")
    print("=" * 60)
    
    # Check game is running
    pid = get_main_pid()
    if not pid:
        print("[-] Game not running. Please start the game first.")
        print("    adb shell am start -n com.qcplay.snail.android.na/org.cocos2dx.lua.AppActivity")
        sys.exit(1)
    print(f"[+] Main game PID: {pid}")
    
    # Check frida-server
    if not ensure_frida_server():
        print("[-] frida-server not available")
        sys.exit(1)
    
    # Run capture
    capture_dir = run_capture(pid, CAPTURE_DURATION)
    
    print("\n" + "=" * 60)
    print("Capture complete!")
    print(f"Directory: {capture_dir}")
    print("=" * 60)

if __name__ == "__main__":
    main()
