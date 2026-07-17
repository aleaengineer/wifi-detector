from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, DataTable, RichLog
from textual.reactive import reactive
from textual import work
from rich.text import Text
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
import asyncio
import wifi_scanner

class SignalBar(Static):
    def __init__(self, pct: int, level: str, **kwargs):
        super().__init__(**kwargs)
        self.pct = pct
        self.level = level

    def on_mount(self):
        filled = "█" * (self.pct // 5)
        empty = "░" * (20 - self.pct // 5)
        color = {"Kuat": "green", "Sedang": "yellow", "Lemah": "red"}.get(self.level, "white")
        bar = Text(f"{filled}{empty} {self.pct:.0f}%", style=color)
        self.update(bar)

class StatusBar(Static):
    connected = reactive("")
    count = reactive(0)

    def watch_connected(self, val):
        self._update()

    def watch_count(self, val):
        self._update()

    def _update(self):
        text = Text()
        if self.connected:
            text.append(f"Terhubung: {self.connected}", style="green bold")
        else:
            text.append("Tidak terhubung", style="red")
        text.append(f"  |  {self.count} jaringan ditemukan", style="white")
        self.update(text)

class NetworkTable(DataTable):
    def on_mount(self):
        self.add_columns("SSID", "BSSID", "Sinyal", "Level", "dBm")

    def refresh_networks(self, networks, connected_ssid):
        self.clear()
        for net in networks:
            ssid = net.get("ssid", "<hidden>") or "<hidden>"
            bssid = net.get("bssid", "N/A")
            rssi = net.get("rssi", 0)
            level = net.get("level", "N/A")
            pct = net.get("pct", 0)
            color = {"Kuat": "green", "Sedang": "yellow", "Lemah": "red"}.get(level, "white")

            filled = "█" * (pct // 5)
            empty = "░" * (20 - pct // 5)
            bar = Text(f"{filled}{empty} {pct:.0f}%", style=color)

            ssid_text = Text(ssid, style="bold")
            level_text = Text(level, style=color)

            self.add_row(ssid_text, bssid, bar, level_text, str(rssi))

class WifiDetector(App):
    TITLE = "WiFi Signal Detector"
    CSS = """
    Screen {
        background: #1e1e1e;
    }
    NetworkTable {
        height: 1fr;
        border: solid #444;
    }
    NetworkTable DataTable {
        background: #252526;
    }
    StatusBar {
        height: 3;
        padding: 0 1;
        background: #333;
        color: white;
        dock: bottom;
    }
    #header {
        background: #005a9e;
        color: white;
        text-align: center;
        height: 3;
        padding: 0 1;
    }
    Button {
        dock: bottom;
        height: 3;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield NetworkTable()
        yield StatusBar()

    def on_mount(self):
        self.set_interval(5, self.do_scan)
        self.do_scan()

    @work(thread=True)
    def do_scan(self):
        connected = wifi_scanner.get_connected()
        networks = wifi_scanner.scan()

        status_bar = self.query_one(StatusBar)
        status_bar.connected = connected or ""
        status_bar.count = len(networks)

        table = self.query_one(NetworkTable)
        self.call_from_thread(table.refresh_networks, networks, connected)

if __name__ == "__main__":
    WifiDetector().run()
