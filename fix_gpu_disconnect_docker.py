#!/usr/bin/env python3
import json, os, re, shutil, subprocess
from datetime import datetime

# Paths
DAEMON_JSON = "/etc/docker/daemon.json"
NVIDIA_CONF = "/etc/nvidia-container-runtime/config.toml"

def backup(path):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = f"{path}.bak_{ts}"
    shutil.copy2(path, bak)
    print(f"Backed up {path} → {bak}")

def ensure_daemon_json():
    # Create minimal JSON if missing/empty
    if not os.path.isfile(DAEMON_JSON) or os.path.getsize(DAEMON_JSON) == 0:
        with open(DAEMON_JSON, "w") as f:
            json.dump({}, f)
        print(f"Initialized empty JSON at {DAEMON_JSON}")

    backup(DAEMON_JSON)
    # Update exec-opts
    with open(DAEMON_JSON, "r+") as f:
        data = json.load(f)
        data["exec-opts"] = ["native.cgroupdriver=cgroupfs"]
        f.seek(0); json.dump(data, f, indent=2); f.truncate()
    print(f"Set exec-opts in {DAEMON_JSON}")

def ensure_nvidia_conf():
    # Create file if missing
    if not os.path.isfile(NVIDIA_CONF):
        open(NVIDIA_CONF, "w").close()
        print(f"Created empty file {NVIDIA_CONF}")

    backup(NVIDIA_CONF)
    with open(NVIDIA_CONF, "r+") as f:
        content = f.read()
        # Replace any existing (commented or not) no-cgroups line
        new_content, count = re.subn(
            r'^[ \t]*#?no-cgroups\s*=.*',
            'no-cgroups = false',
            content,
            flags=re.MULTILINE
        )
        # If no replacement made, append under [nvidia-container-cli]
        if count == 0:
            new_content = new_content.rstrip() + "\n\n[nvidia-container-cli]\nno-cgroups = false\n"
        f.seek(0); f.write(new_content); f.truncate()
    print(f"Ensured no-cgroups=false in {NVIDIA_CONF}")

def restart_services():
    subprocess.run(["systemctl", "daemon-reload"], check=True)
    subprocess.run(["systemctl", "restart", "docker"], check=True)
    subprocess.run(["systemctl", "restart", "nvidia-container-runtime"], check=False)
    print("Reloaded systemd and restarted Docker & NVIDIA runtime")

def main():
    ensure_daemon_json()
    ensure_nvidia_conf()
    restart_services()

if __name__ == "__main__":
    main()
