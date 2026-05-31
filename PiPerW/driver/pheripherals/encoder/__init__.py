"""KY-040 rotary encoder peripheral driver.

Two GPIO pins (CLK/DT) + push button (SW). Interrupt-driven via
RPi.GPIO.add_event_detect. Emits UP/DOWN/SELECT/BACK on the
existing key bus.

Config (in config.toml under [pheripherals.encoder]):
    clk_pin = 17
    dt_pin = 18
    sw_pin = 27
    back_pin = 22   # optional, dedicated BACK button

Falls back to defaults if unset.
"""
import time

from PiPerW.helpers import Log
from PiPerW.interfaces.pheripheral_interface import PheripheralInterface, PheripheralAction

try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None
    Log.warning("encoder driver: RPi.GPIO unavailable, peripheral will be inert")


class Pheripheral(PheripheralInterface):
    def __init__(self, clk_pin=17, dt_pin=18, sw_pin=27, back_pin=22):
        self.name = "Rotary Encoder"
        super().__init__(self.name)
        self.clk_pin = clk_pin
        self.dt_pin = dt_pin
        self.sw_pin = sw_pin
        self.back_pin = back_pin
        self._last_clk = 1

        if GPIO is None:
            return

        GPIO.setmode(GPIO.BCM)
        for p in (clk_pin, dt_pin, sw_pin, back_pin):
            GPIO.setup(p, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        self._last_clk = GPIO.input(clk_pin)
        GPIO.add_event_detect(clk_pin, GPIO.BOTH, callback=self._on_rotate, bouncetime=2)
        GPIO.add_event_detect(sw_pin, GPIO.FALLING, callback=self._on_select, bouncetime=200)
        GPIO.add_event_detect(back_pin, GPIO.FALLING, callback=self._on_back, bouncetime=200)

    def _on_rotate(self, _channel):
        try:
            clk = GPIO.input(self.clk_pin)
            dt = GPIO.input(self.dt_pin)
        except Exception as e:
            Log.warning(f"encoder read failed: {e!r}")
            return
        if clk != self._last_clk:
            action = PheripheralAction.UP if dt != clk else PheripheralAction.DOWN
            self.log_key(action)
        self._last_clk = clk

    def _on_select(self, _channel):
        self.log_key(PheripheralAction.SELECT)
        self._maybe_hold(self.sw_pin, PheripheralAction.SELECT)

    def _on_back(self, _channel):
        self.log_key(PheripheralAction.BACK)
        self._maybe_hold(self.back_pin, PheripheralAction.EXIT)

    def _maybe_hold(self, pin, hold_action, hold_time=1.5):
        start = time.time()
        while GPIO is not None and GPIO.input(pin) == 0:
            if time.time() - start > hold_time:
                self.log_key(hold_action)
                while GPIO.input(pin) == 0:
                    time.sleep(0.1)
                return
            time.sleep(0.05)
