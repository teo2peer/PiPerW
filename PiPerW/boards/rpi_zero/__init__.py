import os
import toml
from PiPerW.boards.board_interface import BoardInterface, PinMode, PinPull
from PiPerW.helpers import Log

try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None

try:
    import spidev
except ImportError:
    spidev = None


class Board(BoardInterface):
    def __init__(self):
        super().__init__("Raspberry Pi Zero")
        self.pins = {}
        self._spi_instances = {}
        self._i2c_instances = {}
        self.load_manifest()
        
        if GPIO:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            Log.info("RPI.GPIO initialized in BCM mode.")
        else:
            Log.warning("RPi.GPIO not installed. Hardware IO will be simulated.")

    def load_manifest(self):
        manifest_path = os.path.join(os.path.dirname(__file__), "manifest.toml")
        if os.path.exists(manifest_path):
            try:
                data = toml.load(manifest_path)
                self.pins = data.get("pins", {})
            except Exception as e:
                Log.error(f"Failed to load board manifest: {e}")

    def get_real_gpio(self, pin_name: str) -> int:
        """
        Translates 'I2C_SDA' or 'GPIO0' directly to integer (e.g. 2 or 4).
        If the pin_name is not in the manifest, relies on it being a raw int, else fails.
        """
        val = self.pins.get(pin_name, pin_name)
        try:
            return int(val)
        except (ValueError, TypeError):
            Log.error(f"Hardware-Agnostic Error: Cannot resolve abstract pin '{pin_name}' to real GPIO.")
            return -1

    def setup_pin(self, pin_name: str, mode: PinMode, pull: PinPull = PinPull.NONE):
        pin = self.get_real_gpio(pin_name)
        if pin < 0 or not GPIO: return
        
        gmode = GPIO.IN if mode == PinMode.IN else GPIO.OUT
        gpull = GPIO.PUD_OFF
        
        if pull == PinPull.UP:
            gpull = GPIO.PUD_UP
        elif pull == PinPull.DOWN:
            gpull = GPIO.PUD_DOWN
            
        GPIO.setup(pin, gmode, pull_up_down=gpull)

    def read_pin(self, pin_name: str) -> bool:
        pin = self.get_real_gpio(pin_name)
        if pin < 0 or not GPIO: return False
        return bool(GPIO.input(pin))

    def write_pin(self, pin_name: str, value: bool):
        pin = self.get_real_gpio(pin_name)
        if pin < 0 or not GPIO: return
        GPIO.output(pin, GPIO.HIGH if value else GPIO.LOW)

    def get_spi(self, bus_id: int = 0, device_id: int = 0):
        # Hardware Agnostic Singleton Factory for SPI
        key = f"{bus_id}_{device_id}"
        if key not in self._spi_instances:
            if not spidev:
                raise ImportError("spidev is required for RPi hardware SPI.")
            spi = spidev.SpiDev()
            spi.open(bus_id, device_id)
            self._spi_instances[key] = spi
        return self._spi_instances[key]

    def get_i2c(self, bus_id: int = 1):
        # Example Factory for I2C (Could use smbus2)
        key = f"{bus_id}"
        if key not in self._i2c_instances:
            # Fake placeholder or import smbus here
            self._i2c_instances[key] = f"I2C_BUS_{bus_id}"
        return self._i2c_instances[key]

    def cleanup(self):
        for spi in self._spi_instances.values():
            try: spi.close()
            except: pass
        if GPIO:
            GPIO.cleanup()
