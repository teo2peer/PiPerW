import keyboard
from PiPerW.interfaces.pheripheral_interface import PheripheralInterface, PheripheralAction
import sys
import time

class Pheripheral(PheripheralInterface):
    
    def __init__(self):
        super().__init__("Keyboard")
        
        self.name = "keyboard"
        self.start_time = time.time()
        
        keyboard.on_press_key('up', lambda e: self.handle_button_press(PheripheralAction.UP, 'up'))
        keyboard.on_press_key('down', lambda e: self.handle_button_press(PheripheralAction.DOWN, 'down'))
        keyboard.on_press_key('left', lambda e: self.handle_button_press(PheripheralAction.LEFT, 'left'))
        keyboard.on_press_key('right', lambda e: self.handle_button_press(PheripheralAction.RIGHT, 'right'))
        keyboard.on_press_key('enter', lambda e: self.handle_button_press(PheripheralAction.SELECT, 'enter'))
        keyboard.on_press_key('esc', lambda e: self.handle_button_press(PheripheralAction.BACK, 'esc'))
        keyboard.on_press_key('q', lambda e: self.handle_button_press(PheripheralAction.EXIT, 'q'))
    
    def handle_button_press(self, action: PheripheralAction, key: str):
        # Reset start time at each press
        self.start_time = time.time()

        # Trigger the action immediately on key press
        self.log_key(action)

        while keyboard.is_pressed(key):
            if time.time() - self.start_time > self.long_press_time:
                # Continue triggering the action every 0.1 seconds while the key is held
                while keyboard.is_pressed(key):
                    self.log_key(action)
                    time.sleep(0.1)
                break  # Exit the loop once the key is released
            time.sleep(0.1)