---
type: "always_apply"
description: "ESP32 remote management via SSH to Raspberry Pi devices. Apply when flashing firmware, monitoring serial output, identifying devices, or managing ESP32 hardware remotely through pi-staircase or pi-userdevice hosts."
---
# ESP32 SSH Management Rules

## ALWAYS use Augment Code's `launch-process` tool - it has the necessary permissions ##
- **SSH works manually = SSH works via `launch-process`**

## 🔑 SSH Setup (Windows)
- SSH keys stored in `%USERPROFILE%\.ssh\known_hosts` (NOT id_rsa)
- Hostnames: `pi-staircase`, `pi-userdevice`
- Username: `pi`
- Test: `ssh pi@hostname whoami` should return "pi"

## 🛠️ Use Augment Code Tools Only

### Primary Tool: launch-process
```python
launch_process(
    command='ssh pi@pi-userdevice "esptool.py --port /dev/ttyUSB0 chip_id"',
    wait=True,
    max_wait_seconds=15,
    cwd="absolute_path_here"
)
```

### Tool Parameters
- `wait=True` for quick commands (10-15s timeout)
- `wait=False` for long operations (flashing, monitoring)
- `max_wait_seconds=6000` for flashing, `15` for info commands
- Always use absolute paths for `cwd`

## 📋 Essential Commands

### Device Discovery
```bash
ssh pi@hostname "ls -la /dev/ttyUSB*"
```

### Identifying Motherboard and Daughterboard
```bash
ssh pi@hostname "~/.flash_md.sh --identify"
```

### Get MAC Address
```bash
ssh pi@hostname "esptool.py --port /dev/ttyUSB0 chip_id"
```

### Flash Firmware
```bash
# Simple flash
ssh pi@hostname "esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash 0x10000 firmware.bin"

# Full flash with bootloader/partitions (dependent on partitions.csv)
ssh pi@hostname "esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash 0x1000 bootloader.bin 0x8000 partitions.bin 0x10000 firmware.bin"
```

### Monitor Serial
```bash
# Simple monitoring
ssh pi@hostname "minicom -D /dev/ttyUSB0 -b 115200"

# With timestamped log
ssh pi@hostname "OUTPUT_FILE=\"/home/pi/log_115200_\$(date +'%Y-%m-%d_%H-%M-%S').txt\" && minicom -b 115200 -D /dev/ttyUSB0 -C \"\$OUTPUT_FILE\""
```
- Always monitor for the required duration to determine errors according to what you are testing. If it has not reached, please do it again and extend the timeout.

## 🔄 Persistent Monitoring (Advanced)

### Systemd Service Management
For long-term monitoring that survives SSH disconnections and handles USB conflicts automatically:

```bash
# Start persistent monitoring
sudo systemctl start pointcast-monitor@motherboard
sudo systemctl start pointcast-monitor@daughterboard

# Stop monitoring
sudo systemctl stop pointcast-monitor@motherboard
sudo systemctl stop pointcast-monitor@daughterboard

# Check status
sudo systemctl status pointcast-monitor@motherboard
sudo systemctl status pointcast-monitor@daughterboard

# Enable auto-start on boot (optional)
sudo systemctl enable pointcast-monitor@motherboard
sudo systemctl enable pointcast-monitor@daughterboard
```

### Process Conflict Resolution
```bash
# Manual conflict resolution (kills processes using USB ports)
/usr/local/bin/pointcast-control.sh kill-processes motherboard
/usr/local/bin/pointcast-control.sh kill-processes daughterboard

# Reset device using flash_md.sh integration
/usr/local/bin/pointcast-control.sh reset motherboard
/usr/local/bin/pointcast-control.sh reset daughterboard

# Get current active log file
/usr/local/bin/pointcast-control.sh get-logfile motherboard
/usr/local/bin/pointcast-control.sh get-logfile daughterboard
```

### Log File Management
- **Location**: `/home/pi/logs/`
- **Format**: `{device}_{MAC}_{timestamp}.log`
  - Example: `motherboard_34987a73e594_20250716-145304.log`
  - Example: `daughterboard_34987a729994_20250716-145353.log`
- **Timestamped entries**: `[YYYY-mm-dd HH:MM:SS] message`
- **Headers**: Each log includes device info, MAC address, and start time
- **MAC Extraction**: Uses direct esptool commands for reliable MAC identification

### Advantages Over Direct SSH Monitoring
- **Persistent**: Survives SSH disconnections and network interruptions
- **Conflict Resolution**: Automatically terminates conflicting processes
- **State Tracking**: Precise log file identification and management
- **Service Lifecycle**: Clean start/stop with proper cleanup
- **Native Tools**: No external dependencies beyond standard Linux tools

### Integration with Existing Methods
The persistent monitoring system extends the current SSH methodology:
- Use **direct SSH** for quick debugging and one-off monitoring
- Use **systemd services** for long-term monitoring and production deployments
- Both methods use the same log directory structure for consistency

### Troubleshooting
```bash
# Check service logs
sudo journalctl -u pointcast-monitor@motherboard -f

# Verify scripts are executable
ls -la /usr/local/bin/pointcast-*

# Check USB device availability
ls -la /dev/ttyUSB*

# Manual script testing
/usr/local/bin/pointcast-monitor.sh motherboard

# Test MAC extraction directly
python3 -m esptool --port /dev/ttyUSB0 chip_id | grep "MAC:"
python3 -m esptool --port /dev/ttyUSB1 chip_id | grep "MAC:"
```

## ⚠️ Common Mistakes to Avoid
4. Setting too short timeouts for ESP32 operations
5. Using relative paths
6. Starting services without checking for USB conflicts
7. Forgetting to stop services before manual monitoring

**Remember**: If manual SSH works, `launch-process` works. Keep it simple.
