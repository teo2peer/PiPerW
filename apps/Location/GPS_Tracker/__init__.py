"""GPS Tracker — read NMEA GPGGA/GPRMC and log GPX."""
import os
import time

from PiPerW.driver.display import Display
from PiPerW.driver.pheripherals import Pheripherals
from PiPerW.helpers import Log
from PiPerW.interfaces.app_interface import AppInterface

display = Display()
pheripherals = Pheripherals()


def _nmea_to_deg(raw, hemi):
    if not raw:
        return None
    try:
        if "." not in raw:
            return None
        dot = raw.index(".")
        deg = int(raw[: dot - 2])
        mins = float(raw[dot - 2 :])
        val = deg + mins / 60.0
        if hemi in ("S", "W"):
            val = -val
        return val
    except (ValueError, IndexError):
        return None


class App(AppInterface):
    def __init__(self):
        super().__init__()
        self.port = "/dev/ttyAMA0"
        self.baud = 9600

    def run(self):
        try:
            import serial
        except ImportError:
            display.text("pyserial missing")
            time.sleep(2)
            return

        gpx_dir = self.get_state_dir()
        gpx_path = os.path.join(gpx_dir, f"track_{int(time.time())}.gpx")
        with open(gpx_path, "w", encoding="utf-8") as gpx:
            gpx.write('<?xml version="1.0"?>\n<gpx version="1.1"><trk><trkseg>\n')

            try:
                ser = serial.Serial(self.port, self.baud, timeout=1)
            except Exception as e:
                Log.error(f"GPS open failed: {e!r}")
                display.text(f"Serial fail:\n{e}")
                self.wait_for_input()
                return

            display.text("GPS waiting fix...")
            lat = lon = None
            sats = 0
            fix = "no"
            while not self.is_stopped():
                try:
                    line = ser.readline().decode("ascii", errors="ignore").strip()
                except Exception as e:
                    Log.warning(f"GPS read: {e!r}")
                    continue
                if not line.startswith("$"):
                    continue
                parts = line.split(",")
                if parts[0].endswith("GGA") and len(parts) > 7:
                    lat = _nmea_to_deg(parts[2], parts[3])
                    lon = _nmea_to_deg(parts[4], parts[5])
                    fix = parts[6] or "0"
                    sats = parts[7] or "0"
                    if lat is not None and lon is not None and fix != "0":
                        gpx.write(f'<trkpt lat="{lat:.6f}" lon="{lon:.6f}"><time>{time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}</time></trkpt>\n')
                        gpx.flush()
                    display.text(f"lat {lat}\nlon {lon}\nsat {sats} fix {fix}")
                key = pheripherals.get_key()
                if key in ("back", "exit"):
                    break

            gpx.write("</trkseg></trk></gpx>\n")
        display.text(f"Saved\n{gpx_path}")
        self.wait_for_input()
