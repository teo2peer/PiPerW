import keyboard
from PiPerW.pheripherals.pheripheral_interface import Pheripheral, PheripheralAction
import sys

class Keyboard(Pheripheral):
    
    def __init__(self):
        super().__init__("Keyboard")
        
        self.name = "keyboard"
    
    def update(self):
        if keyboard.is_pressed('up'):
            self.log_key(PheripheralAction.UP)
        elif keyboard.is_pressed('down'):
            self.log_key(PheripheralAction.DOWN)
        elif keyboard.is_pressed('left'):
            self.log_key(PheripheralAction.LEFT)
        elif keyboard.is_pressed('right'):
            self.log_key(PheripheralAction.RIGHT)
        elif keyboard.is_pressed('enter'):
            self.log_key(PheripheralAction.SELECT)
        elif keyboard.is_pressed('esc'):
            self.log_key(PheripheralAction.BACK)
        elif keyboard.is_pressed('ctrl+c'):
            self.log_key(PheripheralAction.EXIT)
        
            
pheripheral = Keyboard()
