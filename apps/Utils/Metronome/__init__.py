
from PiPerW.apps.app_interface import AppInterface
from PiPerW.pheripherals import Pheripherals
from PiPerW.display import Display
from PiPerW.helpers import Log
import os, time

display = Display()
pheripherals = Pheripherals()



class App(AppInterface):
    
    name = "Metronome"
    version = "0.1"
    
    def __init__(self):
        super().__init__(self.name, self.version)
        
        self.bpm = 120
        self.beat = 4
        self.start = False
        
        
        
    def generate_image(self):
        '''
        Generate the image for the app
        '''
        
        img = display.new_image_from_file(os.path.join(os.path.dirname(__file__), "metronome.png"))
        # open image 
        return img


    def run(self):
        '''
        Main loop of the app
        '''
        # while True:
            
        #     while not self.start:
                
        
        display.draw(self.generate_image())
        pheripherals.await_any_key_press()