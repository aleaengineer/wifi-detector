import time

class SignalHistory:
    def __init__(self, max_samples=20):
        self.data = {}
        self.max_samples = max_samples

    def record(self, bssid, ssid, rssi):
        bssid = bssid or "unknown"
        if bssid not in self.data:
            self.data[bssid] = {"ssid": ssid, "samples": []}
        self.data[bssid]["samples"].append({"rssi": rssi, "time": time.time()})
        if len(self.data[bssid]["samples"]) > self.max_samples:
            self.data[bssid]["samples"].pop(0)

    def trend(self, bssid):
        bssid = bssid or "unknown"
        if bssid not in self.data or len(self.data[bssid]["samples"]) < 2:
            return "●", "white"
        samples = self.data[bssid]["samples"]
        recent = samples[-1]["rssi"]
        old = samples[0]["rssi"]
        diff = recent - old
        if diff > 3:
            return "▲", "green"
        elif diff < -3:
            return "▼", "red"
        return "●", "yellow"

    def sparkline(self, bssid, width=10):
        bssid = bssid or "unknown"
        if bssid not in self.data or len(self.data[bssid]["samples"]) < 2:
            return "░" * width
        samples = [s["rssi"] for s in self.data[bssid]["samples"]]
        if len(samples) > width:
            step = len(samples) // width
            samples = [min(samples[i * step:(i + 1) * step]) for i in range(width)]
        elif len(samples) < width:
            samples = [samples[0]] * (width - len(samples)) + samples
        bars = "▁▂▃▄▅▆▇█"
        rssi_min, rssi_max = min(samples), max(samples)
        rng = rssi_max - rssi_min if rssi_max != rssi_min else 1
        result = ""
        for v in samples:
            idx = int((v - rssi_min) / rng * (len(bars) - 1))
            result += bars[idx]
        return result

    def stats(self, bssid):
        bssid = bssid or "unknown"
        if bssid not in self.data:
            return None
        samples = [s["rssi"] for s in self.data[bssid]["samples"]]
        return {
            "min": min(samples),
            "max": max(samples),
            "avg": sum(samples) / len(samples),
            "cur": samples[-1],
            "count": len(samples),
        }

    def record_scan(self, networks):
        for net in networks:
            bssid = net.get("bssid")
            ssid = net.get("ssid", "<hidden>") or "<hidden>"
            rssi = net.get("rssi", -100)
            self.record(bssid, ssid, rssi)

history = SignalHistory()
