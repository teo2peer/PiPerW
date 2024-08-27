
from PiPerW.apps.app_interface import AppInterface
from PiPerW.pheripherals import Pheripherals
from PiPerW.display import Display
from PiPerW.helpers import Log
import os, time
import qrcode

display = Display()
pheripherals = Pheripherals()



class App(AppInterface):
    
    name = "QrCode"
    version = "0.1"
    
    def __init__(self):
        super().__init__(self.name, self.version)
        self.menu = None
        
    def init(self):
        # create qr code
        qr_code = "https://music.youtube.com/watch?v=9CtkaYEbVTY"
        img = qrcode.make(qr_code)
        
        display.image(img)
        
        pheripherals.await_any_key_press()
        
        
    

    def run(self):
        self.init()