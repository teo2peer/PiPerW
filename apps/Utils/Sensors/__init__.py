"""Sensor Dashboard — show readings from registered SensorInterface."""
import time

from PiPerW.driver.display import Display
from PiPerW.driver.pheripherals import Pheripherals
from PiPerW.interfaces.app_interface import AppInterface
from PiPerW.interfaces.sensor_interface import all_sensors

display = Display()
pheripherals = Pheripherals()


class App(AppInterface):
    def run(self):
        sensors = all_sensors()
        if not sensors:
            display.text("No sensors\nregistered")
            self.wait_for_input()
            return

        idx = 0
        last = 0.0
        while not self.is_stopped():
            now = time.time()
            if now - last > 1.0:
                s = sensors[idx]
                try:
                    readings = s.read()
                except Exception as e:
                    readings = {"err": repr(e)[:20]}
                body = "\n".join(f"{k}: {v}" for k, v in list(readings.items())[:4])
                display.text(f"{s.name}\n{body}")
                last = now
            k = pheripherals.get_key()
            if k == "down":
                idx = (idx + 1) % len(sensors)
                last = 0
            elif k == "up":
                idx = (idx - 1) % len(sensors)
                last = 0
            elif k in ("back", "exit"):
                break
            time.sleep(0.1)
