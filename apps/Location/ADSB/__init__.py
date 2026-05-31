"""ADS-B receiver. Spawns dump1090-fa, reads its SBS-1 (BaseStation) feed."""
import socket
import subprocess
import time

from PiPerW.driver.display import Display
from PiPerW.driver.pheripherals import Pheripherals
from PiPerW.helpers import Log
from PiPerW.interfaces.app_interface import AppInterface

display = Display()
pheripherals = Pheripherals()


class App(AppInterface):
    def __init__(self):
        super().__init__()
        self.proc = None

    def run(self):
        try:
            self.proc = subprocess.Popen(
                ["dump1090-fa", "--net", "--quiet"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
        except FileNotFoundError:
            display.text("dump1090-fa\nnot installed")
            self.wait_for_input()
            return

        # SBS-1 port is 30003
        time.sleep(2)
        try:
            sock = socket.create_connection(("127.0.0.1", 30003), timeout=5)
        except Exception as e:
            Log.error(f"SBS-1 connect fail: {e!r}")
            display.text(f"Connect fail:\n{e}")
            self._stop_proc()
            self.wait_for_input()
            return

        seen = {}  # icao -> (callsign, alt, ts)
        sock.settimeout(0.5)
        try:
            buf = b""
            while not self.is_stopped():
                try:
                    chunk = sock.recv(4096)
                    if chunk:
                        buf += chunk
                        while b"\n" in buf:
                            line, buf = buf.split(b"\n", 1)
                            fields = line.decode("ascii", "ignore").split(",")
                            if len(fields) > 11:
                                icao = fields[4]
                                call = fields[10].strip()
                                alt = fields[11].strip()
                                prev = seen.get(icao, ("", "", 0))
                                seen[icao] = (
                                    call or prev[0],
                                    alt or prev[1],
                                    time.time(),
                                )
                except socket.timeout:
                    pass
                # prune > 60s
                now = time.time()
                seen = {k: v for k, v in seen.items() if now - v[2] < 60}
                top = list(seen.items())[:4]
                lines = [f"{c[:7]} {a}ft" for _, (c, a, _t) in top]
                display.text(f"ADS-B {len(seen)}\n" + "\n".join(lines) if lines else f"ADS-B 0\n(scanning)")
                key = pheripherals.get_key()
                if key in ("back", "exit"):
                    break
        finally:
            sock.close()
            self._stop_proc()

    def _stop_proc(self):
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=2)
            except Exception:
                self.proc.kill()
