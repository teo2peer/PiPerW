# -*- coding:utf-8 -*-
from PiPerW.display.display_interface import DisplayInterface

import sys, time, subprocess, os, string

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont



class Driver(DisplayInterface):
    
    def __init__(self):
        self.width = self.LCD_WIDTH
        self.height = self.LCD_HEIGHT
        self.item_height = 32
        self.horizontal_margin = 10
        self.vertical_margin = 10
        

    def __init__(self):
        super().__init__(256, 128, 32, 10, 10)
        
    
    def init(self):
        print("Initializing OnlyWeb display")
    
    def reset(self):
        pass
    
    def show(self, image):
        # save image in PiPerW/tmp
        pass

    
    def clear(self):
        pass
    

