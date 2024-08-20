import core.SH1106.config as config
import time
import numpy as np
from PiPerW.display.display_interface import Display

class SH1106(Display):
    LCD_WIDTH = 128  # LCD width
    LCD_HEIGHT = 64  # LCD height

    def SH1106(self):
        self.width = self.LCD_WIDTH
        self.height = self.LCD_HEIGHT

        # Initialize DC and RST pins
        self.RPI = config.RaspberryPi()
        self._dc = self.RPI.GPIO_DC_PIN if config.Device_SPI == 1 else None
        self._rst = self.RPI.GPIO_RST_PIN
        self.Device = self.RPI.Device

    def command(self, cmd):
        """Send a command to the display."""
        if self.Device == config.Device_SPI:
            self.RPI.digital_write(self._dc, False)
            self.RPI.spi_writebyte([cmd])
        else:
            self.RPI.i2c_writebyte(0x80, cmd)

    def init(self):
        """Initialize the display."""
        if self.RPI.module_init() != 0:
            return -1

        self.reset()
        init_commands = [
            0xAE, 0x02, 0x10, 0x40, 0x81, 0xA0, 0xC0, 0xA6, 0xA8, 0x3F,
            0xD3, 0x00, 0xD5, 0x80, 0xD9, 0xF1, 0xDA, 0x12, 0xDB, 0x40,
            0x20, 0x02, 0xA4, 0xA6, 0xAF
        ]

        for cmd in init_commands:
            self.command(cmd)
        time.sleep(0.1)

    def reset(self):
        """Reset the display."""
        self.RPI.digital_write(self._rst, True)
        time.sleep(0.1)
        self.RPI.digital_write(self._rst, False)
        time.sleep(0.1)
        self.RPI.digital_write(self._rst, True)
        time.sleep(0.1)

    

    def show_image(self, buffer):
        """Display the buffer on the screen."""
        for page in range(8):
            self.command(0xB0 + page)  # Set page address
            self.command(0x02)         # Set low column address
            self.command(0x10)         # Set high column address

            if self.Device == config.Device_SPI:
                self.RPI.digital_write(self._dc, True)

            for i in range(self.width):
                data = ~buffer[i + self.width * page]
                if self.Device == config.Device_SPI:
                    self.RPI.spi_writebyte([data])
                else:
                    self.RPI.i2c_writebyte(0x40, data)

    def clear(self):
        """Clear the display."""
        buffer = [0xFF] * (self.width * self.height // 8)
        self.show_image(buffer)
