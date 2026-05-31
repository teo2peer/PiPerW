"""Pytest fixtures: mock RPi-only deps so tests run on dev hosts."""
import sys
from unittest.mock import MagicMock


def _mock(name):
    sys.modules.setdefault(name, MagicMock())


_mock("RPi")
_mock("RPi.GPIO")
_mock("luma")
_mock("luma.core")
_mock("luma.core.interface")
_mock("luma.core.interface.serial")
_mock("luma.core.render")
_mock("luma.oled")
_mock("luma.oled.device")
_mock("smbus")
_mock("cc1101")
_mock("pn532pi")
_mock("keyboard")
_mock("adafruit_rgb_display")
_mock("psutil")
_mock("flask")
