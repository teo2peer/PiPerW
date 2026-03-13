import spidev
import time
from dataclasses import dataclass
from PiPerW.driver.SubGHz.reg import *


    
    

class CC1101:
    def __init__(self, bus=0, device=0):
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.max_speed_hz = 500000  # Adjust speed as necessary

    def _spi_trx(self, tx, size):
        timeout = time.time() + CC1101_TIMEOUT
        while time.time() < timeout:
            if self.spi.readbytes(1)[0] == 0:
                break
        else:
            return False

        rx = self.spi.xfer2(tx[:size])
        return rx

    def strobe(self, strobe):
        tx = [strobe]
        rx = self._spi_trx(tx, 1)
        return CC1101Status(CHIP_RDYn=0) if rx and rx[0] & 0x80 == 0 else None

    def write_reg(self, reg, data):
        tx = [reg, data]
        rx = self._spi_trx(tx, 2)
        if rx:
            assert (rx[0] & 0x80) == 0
            return CC1101Status(CHIP_RDYn=0)
        return None

    def read_reg(self, reg):
        tx = [reg | CC1101_READ, 0]
        rx = self._spi_trx(tx, 2)
        return rx[1] if rx else None

    def get_partnumber(self):
        return self.read_reg(CC1101_STATUS_PARTNUM | CC1101_BURST)

    def get_version(self):
        return self.read_reg(CC1101_STATUS_VERSION | CC1101_BURST)

    def get_rssi(self):
        return self.read_reg(CC1101_STATUS_RSSI | CC1101_BURST)

    def reset(self):
        return self.strobe(CC1101_STROBE_SRES)

    def shutdown(self):
        return self.strobe(CC1101_STROBE_SNOP)

    def set_frequency(self, value):
        real_value = (value * CC1101_FDIV) // CC1101_QUARTZ
        assert (real_value & CC1101_FMASK) == real_value
        self.write_reg(0x0D, (real_value >> 16) & 0xFF)
        self.write_reg(0x0E, (real_value >> 8) & 0xFF)
        self.write_reg(0x0F, real_value & 0xFF)
        return (real_value * CC1101_QUARTZ) // CC1101_FDIV

    def set_pa_table(self, values):
        tx = [0x3E | CC1101_BURST] + values
        rx = self._spi_trx(tx, len(tx))
        assert (rx[0] & 0x80) == 0

    def write_fifo(self, data):
        tx = [CC1101_FIFO | CC1101_BURST] + data
        self._spi_trx(tx, len(tx))
        return len(data)

    def read_fifo(self):
        tx = [CC1101_FIFO | CC1101_READ | CC1101_BURST, 0]
        rx = self._spi_trx(tx, 2)
        if rx and rx[1] <= 64:
            size = rx[1]
            data = self.spi.readbytes(size)
            return data, size
        return None, 0
