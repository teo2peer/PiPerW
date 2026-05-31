"""Log Viewer — page through the tail of output.log."""
import os

from PiPerW.driver.display import Display
from PiPerW.driver.pheripherals import Pheripherals
from PiPerW.helpers import PIPERW_ROOT
from PiPerW.interfaces.app_interface import AppInterface

display = Display()
pheripherals = Pheripherals()


class App(AppInterface):
    PAGE_LINES = 5

    def run(self):
        log_path = os.path.join(str(PIPERW_ROOT), "output.log")
        if not os.path.exists(log_path):
            display.text("output.log\nnot found")
            self.wait_for_input()
            return

        with open(log_path, "rb") as f:
            try:
                f.seek(-8192, os.SEEK_END)
            except OSError:
                f.seek(0)
            tail = f.read().decode("utf-8", "replace").splitlines()

        if not tail:
            display.text("(empty)")
            self.wait_for_input()
            return

        idx = max(0, len(tail) - self.PAGE_LINES)
        while not self.is_stopped():
            window = tail[idx : idx + self.PAGE_LINES]
            display.text("\n".join(line[:24] for line in window))
            k = pheripherals.await_key()
            if k == "up":
                idx = max(0, idx - 1)
            elif k == "down":
                idx = min(len(tail) - 1, idx + 1)
            elif k in ("back", "exit", "select"):
                break
