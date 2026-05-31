import os
import psutil
import time
import threading
from PiPerW.helpers import Log
from PiPerW.driver.display import Display

class HardwareTelemetry:
    def __init__(self, temp_threshold=80.0, check_interval=5.0, mem_threshold_mb=80):
        self.temp_threshold = temp_threshold
        self.check_interval = check_interval
        self.mem_threshold_mb = mem_threshold_mb
        self._running = False
        self._thread = None
        self._mem_warned = False
        self.display = Display()

    def get_cpu_temp(self):
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                temp = float(f.read()) / 1000.0
            return temp
        except Exception:
            return 0.0

    def monitor_loop(self):
        while self._running:
            temp = self.get_cpu_temp()
            # Log.info(f"Telemetry - CPU Temp: {temp}C")
            
            # Memory pressure check
            try:
                from PiPerW.utils.memory import available_mb
                mb = available_mb()
                if 0 <= mb < self.mem_threshold_mb:
                    if not self._mem_warned:
                        Log.error(f"[SRE] LOW MEMORY: {mb} MB available (threshold {self.mem_threshold_mb})")
                        try:
                            self.display.stop_animation()
                        except Exception:
                            pass
                        self._mem_warned = True
                elif mb >= self.mem_threshold_mb * 2:
                    self._mem_warned = False
            except Exception as e:
                Log.warning(f"mem check failed: {e!r}")

            if temp >= self.temp_threshold:
                Log.error(f"[SRE] THERMAL THROTTLING! CPU Temp ({temp}C) exceeded {self.temp_threshold}C.")
                self.display.text(f"WARNING: OVERHEATING\nCPU {temp}C")
                # Wait before resuming checks, or trigger a graceful shutdown
                time.sleep(3)
                Log.warning("Initiating safety cool-down shutdown")
                import subprocess
                subprocess.run(["sudo", "shutdown", "now"])
            
            time.sleep(self.check_interval)

    def start(self):
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self.monitor_loop, daemon=True)
            self._thread.start()
            Log.info("Hardware Telemetry Monitor Started")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join()
