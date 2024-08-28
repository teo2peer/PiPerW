import keyboard
from PiPerW.pheripherals.pheripheral_interface import PheripheralInterface, PheripheralAction
import sys
import RPi.GPIO as GPIO



class Pheripheral(PheripheralInterface):
    
    def __init__(self):
        self.name = "WaveShare Hat"
        super().__init__(self.name)
        
        
        self.JS_UP_PIN = 6  # Up
        self.JS_DOWN_PIN = 19 # Down
        self.JS_LEFT_PIN = 5  # Left
        self.JS_RIGHT_PIN = 26 # Right
        self.JS_PRESS_PIN = 13 # Select Joystick
        self.BTN1_PIN = 21 #Back Button
        self.BTN2_PIN = 20 #Select Button
        self.BTN3_PIN = 16 #Exit Button
        
        self.init_pins()
        
        
    def init_pins(self):
        '''
        Init pins
        '''
        
        GPIO.setmode(GPIO.BCM)
        
        GPIO.setup(self.JS_UP_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.JS_DOWN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.JS_LEFT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.JS_RIGHT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.JS_PRESS_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.BTN1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.BTN2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.BTN3_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        
    
    def update(self):
        '''
        Update the pheripheral
        '''
        
        
        if GPIO.input(self.JS_UP_PIN) == 0:
            self.log_key(PheripheralAction.UP)
        elif GPIO.input(self.JS_DOWN_PIN) == 0:
            self.log_key(PheripheralAction.DOWN)
        elif GPIO.input(self.JS_LEFT_PIN) == 0:
            self.log_key(PheripheralAction.LEFT)
        elif GPIO.input(self.JS_RIGHT_PIN) == 0:
            self.log_key(PheripheralAction.RIGHT)
        elif GPIO.input(self.JS_PRESS_PIN) == 0:
            self.log_key(PheripheralAction.SELECT)
        elif GPIO.input(self.BTN1_PIN) == 0:
            self.log_key(PheripheralAction.BACK)
        elif GPIO.input(self.BTN2_PIN) == 0:
            self.log_key(PheripheralAction.SELECT)
        elif GPIO.input(self.BTN3_PIN) == 0:
            self.log_key(PheripheralAction.EXIT)
            
        
        
            
