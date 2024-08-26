# -*- coding:utf-8 -*-
from PiPerW.display.display_interface import DisplayInterface
from luma.core.interface.serial import i2c, spi
from luma.core.render import canvas
from luma.core import lib

from luma.oled.device import sh1106
import sys, time, subprocess, os, string

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import RPi.GPIO as GPIO



GPIO.setmode(GPIO.BCM) 


class Driver(DisplayInterface):
    super().__init__(128, 64)
    
    #GPIO define
    self.RST_PIN  = 25 #Reset
    self.CS_PIN   = 8
    self.DC_PIN   = 24

    # Some constants
    self.SCREEN_LINES = 4
    self.CHAR_WIDTH = 19
    
    

    def SH1106(self):
        self.width = self.LCD_WIDTH
        self.height = self.LCD_HEIGHT
        


        # Initialize DC and RST pins
        self._dc = self.DC_PIN
        self._rst = self.RST_PIN
        self.Device = self.CS_PIN
        self.font = ImageFont.load_default()
        

        
    def command(self, cmd):
        """Send a command to the display."""
        if self.Device == config.Device_SPI:
            self.RPI.digital_write(self._dc, False)
            self.RPI.spi_writebyte([cmd])
        else:
            self.RPI.i2c_writebyte(0x80, cmd)

    def show(self):
        """Show the image on the display."""
        serial = spi(device=0, port=0, bus_speed_hz = 8000000, transfer_size = 4096, gpio_DC = DC_PIN, gpio_RST = RST_PIN)
        device = sh1106(serial, rotate=2) #sh1106
        
        

    def reset(self):
        """Reset the display."""
        self.RPI.digital_write(self._rst, False)
        time.sleep(0.01)
        self.RPI.digital_write(self._rst, True)
        time.sleep(0.1)

    

    def show(self, image):
        """Show an image on the display."""
        with canvas(device) as draw:
            draw.bitmap((0, 0), image, fill=255)
            
        

    def clear(self):
        """Clear the display."""
        with canvas(device) as draw:
            draw.rectangle(device.bounding_box, outline="black", fill="black")

Driver = SH1106()