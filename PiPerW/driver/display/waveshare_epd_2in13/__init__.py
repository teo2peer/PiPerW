"""Waveshare 2.13" e-paper display driver.

Requires `waveshare-epd` library (vendored or pip). On Pi Zero 2 W
e-ink is excellent for battery: zero current when idle. Partial
refresh is fast enough for menu nav (~300 ms); full refresh is
reserved for splash/clear to avoid ghosting.
"""
from PIL import Image, ImageFont
from PiPerW.helpers import Log
from PiPerW.interfaces.display_interface import DisplayInterface

try:
    from waveshare_epd import epd2in13_V3 as _epd_module
except ImportError:
    _epd_module = None
    Log.warning("waveshare_epd not installed; e-ink driver inert")


class Driver(DisplayInterface):
    def __init__(self):
        self.width = 250
        self.height = 122
        self.item_height = 22
        self.horizontal_margin = 4
        self.vertical_margin = 4
        super().__init__(
            self.width, self.height, self.item_height,
            self.horizontal_margin, self.vertical_margin, "b",
        )
        self.font = ImageFont.load_default()
        self._partial_count = 0
        self._full_refresh_every = 30  # full refresh every N partials to flush ghosting

        if _epd_module is None:
            self.device = None
            return

        self.device = _epd_module.EPD()
        self.device.init()
        self.device.Clear(0xFF)
        self.device.init_Partial()

    def show(self, image):
        if self.device is None:
            return
        img = image.convert("1").resize((self.width, self.height))
        self._partial_count += 1
        if self._partial_count >= self._full_refresh_every:
            self.device.init()
            self.device.display(self.device.getbuffer(img))
            self.device.init_Partial()
            self._partial_count = 0
        else:
            self.device.displayPartial(self.device.getbuffer(img))

    def clear(self):
        if self.device is None:
            return
        self.device.init()
        self.device.Clear(0xFF)
        self.device.init_Partial()
        self._partial_count = 0

    def sleep(self):
        if self.device is None:
            return
        try:
            self.device.sleep()
        except Exception as e:
            Log.warning(f"epd sleep failed: {e!r}")
