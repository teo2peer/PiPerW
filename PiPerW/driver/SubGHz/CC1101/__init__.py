import time
from PiPerW.driver.SubGHz.CC1101.reg import *
# Observa lo mucho que se ha separado en funciones
from PiPerW.boards.spi import get_spi
from PiPerW.boards.gpio import setup_pin, PinMode
from PiPerW.boards.pins import GPIO0, I2C_SDA  # Solo demostración

class CC1101Status:
    def __init__(self, CHIP_RDYn=0):
        self.CHIP_RDYn = CHIP_RDYn

class CC1101:
    def __init__(self, bus=0, device=0):
        # 100% Abstracto: Sin llamadas tediosas, auto-hidratado
        self.spi = get_spi(bus, device)
        
        # Ejemplo si algun dia ocupamos GPIOs abstractos directamente:
        # from PiPerW.boards import GPIO2
        # setup_pin(GPIO2, PinMode.IN)
        
        self.spi.max_speed_hz = 5000000  # Set to 5MHz for CC1101
        self.spi.mode = 0  # Mode 0 is required for CC1101
        self.reset()
        time.sleep(0.01)

    def _spi_trx(self, tx):
        """Simple helper to send/receive over SPI."""
        rx = self.spi.xfer2(tx)
        return rx

    def strobe(self, strobe_cmd):
        rx = self.spi.xfer2([strobe_cmd])
        return CC1101Status(CHIP_RDYn=(rx[0] & 0x80))

    def write_reg(self, reg, data):
        tx = [reg, data]
        rx = self._spi_trx(tx)
        return CC1101Status(CHIP_RDYn=(rx[0] & 0x80))

    def read_reg(self, reg):
        # If reading a status register (0x30 to 0x3D), ensure burst bit is set for TI CC1101
        flag = CC1101_READ
        if 0x30 <= reg <= 0x3D:
            flag |= CC1101_BURST
        tx = [reg | flag, 0x00]
        rx = self._spi_trx(tx)
        return rx[1]

    def read_burst(self, reg, length):
        tx = [reg | CC1101_READ | CC1101_BURST] + [0x00] * length
        rx = self._spi_trx(tx)
        return rx[1:]

    def write_burst(self, reg, data):
        tx = [reg | CC1101_BURST] + data
        rx = self._spi_trx(tx)
        return CC1101Status(CHIP_RDYn=(rx[0] & 0x80))

    def get_partnumber(self):
        return self.read_reg(CC1101_STATUS_PARTNUM)

    def get_version(self):
        return self.read_reg(CC1101_STATUS_VERSION)

    def get_rssi(self):
        rssi_raw = self.read_reg(CC1101_STATUS_RSSI)
        # Convert hex output directly to Float dBm
        return float((rssi_raw - 256) / 2 - 74) if rssi_raw >= 128 else float(rssi_raw / 2 - 74)

    def reset(self):
        self.strobe(CC1101_STROBE_SRES)

    def shutdown(self):
        self.strobe(CC1101_STROBE_SPWD)

    def set_frequency(self, freq_mhz):
        self.strobe(CC1101_STROBE_SIDLE) # 1) Must idle before modifying PLL parameters
        # 2) Calculate Float equation for Synth Freq: freq * (65536 / 26MHz Oscillators)
        real_value = int(freq_mhz * (65536.0 / 26.0))
        self.write_reg(CC1101_FREQ2, (real_value >> 16) & 0xFF)
        self.write_reg(CC1101_FREQ1, (real_value >> 8) & 0xFF)
        self.write_reg(CC1101_FREQ0, real_value & 0xFF)

    def set_pa_table(self, values):
        self.write_burst(CC1101_PATABLE, values)

    def write_fifo(self, data):
        self.strobe(CC1101_STROBE_SIDLE)
        self.strobe(CC1101_STROBE_SFTX)  # always start flush clean
        self.write_burst(CC1101_FIFO, data)
        return len(data)

    def read_fifo(self):
        rxbytes = self.read_reg(CC1101_STATUS_RXBYTES)
        # Bit 7 signals buffer overflow (Memory trap crash)
        overflow = bool(rxbytes & 0x80)
        bytes_in_fifo = rxbytes & 0x7F

        data = []
        if bytes_in_fifo > 0:
            data = self.read_burst(CC1101_FIFO, bytes_in_fifo)
            
        if overflow:
            # Defrost module manually:
            self.strobe(CC1101_STROBE_SFRX) 
            self.strobe(CC1101_STROBE_SRX)  
            
        return data, len(data)
