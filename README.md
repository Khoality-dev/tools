# Tools

This repository contains small utilities for system configuration.

## fix_gpu_disconnect_docker.py

This Python script updates Docker and NVIDIA container runtime settings to
prevent GPU disconnect issues. It edits `/etc/docker/daemon.json` and
`/etc/nvidia-container-runtime/config.toml`, backing up the original files
before applying changes.

Run the script with root privileges:

```bash
sudo python3 fix_gpu_disconnect_docker.py
```

The script sets Docker's `cgroupdriver` option and ensures that NVIDIA's
`no-cgroups` flag is disabled, then restarts the relevant services.

More tools may be added over time.
