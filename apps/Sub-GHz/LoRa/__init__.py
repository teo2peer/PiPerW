"""LoRa Messenger. Minimal RX/TX of short ASCII frames via SX127x."""
import time

from PiPerW.driver.display import Display
from PiPerW.driver.pheripherals import Pheripherals
from PiPerW.helpers import Log
from PiPerW.interfaces.app_interface import AppInterface
from PiPerW.utils.Menu import Menu

display = Display()
pheripherals = Pheripherals()


class App(AppInterface):
    def __init__(self):
        super().__init__()
        self.freq_mhz = 868.0

    def run(self):
        try:
            from SX127x.LoRa import LoRa, MODE
            from SX127x.board_config import BOARD
        except ImportError:
            display.text("pyLoRa missing")
            self.wait_for_input()
            return

        BOARD.setup()
        class _Radio(LoRa):
            def __init__(self_inner, verbose=False):
                super().__init__(verbose)
                self_inner.set_mode(MODE.SLEEP)
                self_inner.set_dio_mapping([0] * 6)
            def on_rx_done(self_inner):
                payload = self_inner.read_payload(nocheck=True)
                Log.info(f"LoRa rx: {payload!r}")
                self_inner.last_rx = bytes(payload)
                self_inner.set_mode(MODE.RXCONT)

        radio = _Radio(verbose=False)
        radio.set_pa_config(pa_select=1)
        radio.set_freq(self.freq_mhz)
        radio.last_rx = b""
        radio.set_mode(MODE.RXCONT)

        menu = Menu(["Listen", "Beacon TX", "Exit"])
        try:
            while not self.is_stopped():
                menu.show()
                key = pheripherals.await_key()
                if key == "up":
                    menu.previous()
                elif key == "down":
                    menu.next()
                elif key == "select":
                    sel = menu.get_selected()
                    if sel == "Exit":
                        break
                    elif sel == "Listen":
                        display.text("Listening...\nback to stop")
                        while not self.is_stopped():
                            if radio.last_rx:
                                display.text(f"RX:\n{radio.last_rx[:40]!r}")
                                radio.last_rx = b""
                            k = pheripherals.get_key()
                            if k in ("back", "exit"):
                                break
                            time.sleep(0.2)
                    elif sel == "Beacon TX":
                        msg = b"PiPerW LoRa beacon"
                        radio.set_mode(MODE.STDBY)
                        radio.write_payload(list(msg))
                        radio.set_mode(MODE.TX)
                        display.text("Sent beacon")
                        time.sleep(1)
                        radio.set_mode(MODE.RXCONT)
                elif key in ("back", "exit"):
                    break
        finally:
            try:
                radio.set_mode(MODE.SLEEP)
            except Exception:
                pass
            BOARD.teardown()
