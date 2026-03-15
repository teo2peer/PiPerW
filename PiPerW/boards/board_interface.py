from enum import Enum

class PinMode(Enum):
    IN = 0
    OUT = 1

class PinPull(Enum):
    UP = 1
    DOWN = -1
    NONE = 0

class BoardInterface:
    def __init__(self, name):
        self.name = name

    def get_real_gpio(self, pin_name: str) -> int:
        """
        Translates an abstract pin name (like 'SPI_MOSI' or 'GPIO0') 
        to the physical board's specific integer pin.
        """
        raise NotImplementedError()

    def setup_pin(self, pin_name: str, mode: PinMode, pull: PinPull = PinPull.NONE):
        raise NotImplementedError()

    def read_pin(self, pin_name: str) -> bool:
        raise NotImplementedError()

    def write_pin(self, pin_name: str, value: bool):
        raise NotImplementedError()

    def get_spi(self, bus_id: int = 0, device_id: int = 0):
        '''Return a shared, hardware-agnostic SPI object (e.g. spidev-like duck typed)'''
        raise NotImplementedError()

    def get_i2c(self, bus_id: int = 1):
        '''Return a shared, hardware-agnostic I2C object'''
        raise NotImplementedError()

    def cleanup(self):
        raise NotImplementedError()
