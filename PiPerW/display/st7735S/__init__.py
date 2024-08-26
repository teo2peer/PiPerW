# -*- coding:utf-8 -*-
from PiPerW.display.display_interface import DisplayInterface
import digitalio
import board
from PIL import Image, ImageDraw
import sys, time, subprocess, os, string

from adafruit_rgb_display import st7735

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import RPi.GPIO as GPIO



GPIO.setmode(GPIO.BCM) 


class Driver(DisplayInterface):
    
    

    def __init__(self):
        
        
       

        
        
        self.item_height = 32
        self.horizontal_margin = 10
        self.vertical_margin = 10
        
        # Some constants
        self.SCREEN_LINES = 6
        self.CHAR_WIDTH = 19
        
        
        
        #GPIO define
        self.cs_pin = digitalio.DigitalInOut(board.CE0)
        self.dc_pin = digitalio.DigitalInOut(board.D25)
        self.reset_pin = digitalio.DigitalInOut(board.D24)
        
        self.BAUDRATE = 24000000
        
        self.spi = board.SPI()
        self.device = st7735.ST7735(
            self.spi, 
            cs=self.cs_pin, 
            dc=self.dc_pin, 
            rst=self.reset_pin, 
            baudrate=self.BAUDRATE
        )
        
        self.width = self.device.width
        self.height = self.device.height
        
        super().__init__(self.width, self.height, self.item_height, self.horizontal_margin, self.vertical_margin)
        

        
    def command(self, cmd):
        """Send a command to the display."""
        self.device.write(cmd)
        
        

    def reset(self):
        """Reset the display."""
        self.device.reset()
        time.sleep(0.01)

    

    def show(self, image):
        """Show an image on the display."""
        
        self.device.image(image)
            
        

    def clear(self):
        """Clear the display."""
        image = Image.new("RGB", (self.width, self.height), 0)
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
        
        self.show(image)

