import subprocess
import json
import re

def freq_to_channel(freq):
    if 2412 <= freq <= 2484:
        return (freq - 2407) // 5
    elif 5180 <= freq <= 5825:
        ch = (freq - 5000) // 5
        return {36:36,38:36,40:36,42:36,44:36,46:36,48:36,52:36,56:36,60:36,64:36,
                100:36,104:36,108:36,112:36,116:36,120:36,124:36,128:36,132:36,136:36,140:36,
                149:149,153:149,157:149,161:149,165:149}.get(ch, ch)
    return 0

def parse_security(capabilities):
    caps = capabilities or ""
    has_wpa3 = "SAE" in caps
    has_wpa2 = "WPA2" in caps or "RSN" in caps
    has_wpa = "WPA-PSK" in caps or "WPA" in caps
    has_wps = "WPS" in caps
    is_open = not (has_wpa3 or has_wpa2 or has_wpa)

    if is_open:
        return "Open"
    parts = []
    if has_wpa3:
        parts.append("WPA3")
    if has_wpa2:
        parts.append("WPA2")
    if has_wpa and not has_wpa2:
        parts.append("WPA")
    label = "+".join(parts) if parts else "Unknown"
    if has_wps:
        label += "+WPS"
    return label

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
            freq = net.get("frequency_mhz", 0)
            net["channel"] = freq_to_channel(freq)
            band = "2.4GHz" if 2412 <= freq <= 2484 else "5GHz" if 5180 <= freq <= 5825 else "?"
            net["band"] = band
            net["security"] = parse_security(net.get("capabilities", ""))
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
