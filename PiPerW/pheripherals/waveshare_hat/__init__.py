import keyboard
from PiPerW.pheripherals.pheripheral_interface import PheripheralInterface, PheripheralAction
import sys
import RPi.GPIO as GPIO
import time



class Pheripheral(PheripheralInterface):
    
    def __init__(self):
        self.name = "WaveShare Hat"
        super().__init__(self.name)
        
        self.JS_UP_PIN = 6    # Up
        self.JS_DOWN_PIN = 19 # Down
        self.JS_LEFT_PIN = 5  # Left
        self.JS_RIGHT_PIN = 26 # Right
        self.JS_PRESS_PIN = 13 # Select Joystick
        self.BTN1_PIN = 21    # Back Button
        self.BTN2_PIN = 20    # Select Button
        self.BTN3_PIN = 16    # Exit Button
        
        self.init_pins()
        
    def init_pins(self):
        '''
        Init pins
        '''
        GPIO.setmode(GPIO.BCM)
        
        # Setup pins with pull-up resistors
        pins = [self.JS_UP_PIN, self.JS_DOWN_PIN, self.JS_LEFT_PIN, self.JS_RIGHT_PIN,
                self.JS_PRESS_PIN, self.BTN1_PIN, self.BTN2_PIN, self.BTN3_PIN]
        
        for pin in pins:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # Register event detection for key presses
        GPIO.add_event_detect(self.JS_UP_PIN, GPIO.FALLING, callback=lambda channel: self.handle_button_press(PheripheralAction.UP, channel), bouncetime=200)
        GPIO.add_event_detect(self.JS_DOWN_PIN, GPIO.FALLING, callback=lambda channel: self.handle_button_press(PheripheralAction.DOWN, channel), bouncetime=200)
        GPIO.add_event_detect(self.JS_LEFT_PIN, GPIO.FALLING, callback=lambda channel: self.handle_button_press(PheripheralAction.LEFT, channel), bouncetime=200)
        GPIO.add_event_detect(self.JS_RIGHT_PIN, GPIO.FALLING, callback=lambda channel: self.handle_button_press(PheripheralAction.RIGHT, channel), bouncetime=200)
        GPIO.add_event_detect(self.JS_PRESS_PIN, GPIO.FALLING, callback=lambda channel: self.handle_button_press(PheripheralAction.SELECT, channel), bouncetime=200)
        GPIO.add_event_detect(self.BTN1_PIN, GPIO.FALLING, callback=lambda channel: self.handle_button_press(PheripheralAction.BACK, channel), bouncetime=200)
        GPIO.add_event_detect(self.BTN2_PIN, GPIO.FALLING, callback=lambda channel: self.handle_button_press(PheripheralAction.SELECT, channel), bouncetime=200)
        GPIO.add_event_detect(self.BTN3_PIN, GPIO.FALLING, callback=lambda channel: self.handle_button_press(PheripheralAction.EXIT, channel), bouncetime=200)
    
    def handle_button_press(self, action: PheripheralAction, channel: int):
        '''
        Handle the button press event, execute action immediately, and continue if held
        '''
        # Trigger the action immediately
        self.log_key(action)
        
        start_time = time.time()
        hold_time = 1.5  # 1.5 seconds hold time
        
        # Check if the button is still being held down
        while GPIO.input(channel) == 0:  # While the button is pressed
            if time.time() - start_time > hold_time:
                
                while GPIO.input(channel) == 0:
                    self.log_key(action)
                    time.sleep(0.1)
                break
            time.sleep(0.1)  # Small delay to avoid high CPU usage
