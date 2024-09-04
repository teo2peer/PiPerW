# -*- coding:utf-8 -*-
from PiPerW.interfaces.display_interface import DisplayInterface
from luma.core.interface.serial import i2c, spi
from luma.core.render import canvas
from luma.core import lib

from luma.oled.device import ssd1306
import sys, time, subprocess, os, string

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageOps


class Driver(DisplayInterface):
    
    

    def __init__(self):
        #GPIO define
        self.RST_PIN  = 25 #Reset
        self.CS_PIN   = 8
        self.DC_PIN   = 24

        # Some constants
        self.SCREEN_LINES = 4
        self.CHAR_WIDTH = 19
        
        
        self.width = 128
        self.height = 64
        self.item_height = 16
        self.horizontal_margin = 10
        self.vertical_margin = 10
        
        
        super().__init__(self.width, self.height, self.item_height, self.horizontal_margin, self.vertical_margin, "b")
        
        # Initialize DC and RST pins
        self._dc = self.DC_PIN
        self._rst = self.RST_PIN
        self.cs = self.CS_PIN
        self.font = ImageFont.load_default()
        
        self.serial = i2c(port=1, address=0x3C)
        self.device = ssd1306(self.serial, rotate=2) #ssd1306

        
    def command(self, cmd):
        """Send a command to the display."""
        if self.Device == config.Device_SPI:
            self.RPI.digital_write(self._dc, False)
            self.RPI.spi_writebyte([cmd])
        else:
            self.RPI.i2c_writebyte(0x80, cmd)
        
        

    def reset(self):
        """Reset the display."""
        self.RPI.digital_write(self._rst, False)
        time.sleep(0.01)
        self.RPI.digital_write(self._rst, True)
        time.sleep(0.1)

    

    def show(self, image):
        """Show an image on the display."""
        
        image = image.convert("1")
        # image = ImageOps.invert(image)
        
        with canvas(self.device) as draw:
            draw.bitmap((0, 0), image, fill=255)
            
        

    def clear(self):
        """Clear the display."""
        with canvas(self.device) as draw:
            draw.rectangle(self.device.bounding_box, outline="black", fill="black")

