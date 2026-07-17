import subprocess
import json

def scan():
    try:
        result = subprocess.run(
            ["termux-wifi-scaninfo"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            return []
        networks = json.loads(result.stdout)
        for net in networks:
            rssi = net.get("rssi", -100)
            net["level"], net["pct"], net["color"] = signal_info(rssi)
        return networks
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError):
        return []

def get_connected():
    try:
        result = subprocess.run(
            ["termux-wifi-connectioninfo"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode != 0:
            return None
        data = json.loads(result.stdout)
        ssid = data.get("ssid")
        return ssid if ssid else None
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError):
        return None

def signal_info(rssi):
    if rssi >= -50:
        return "Kuat", min(100, max(0, 2 * (rssi + 100))), "green"
    elif rssi >= -70:
        return "Sedang", min(100, max(0, 2 * (rssi + 100))), "yellow"
    else:
        return "Lemah", min(100, max(0, 2 * (rssi + 100))), "red"
