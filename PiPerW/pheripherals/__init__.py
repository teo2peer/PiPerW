from PiPerW.helpers import Config, Log, WThread, save_config
from PiPerW.interfaces.pheripheral_interface import PheripheralAction
from PiPerW.utils.Singleton import Singleton
import importlib
import time, sys

class Pheripherals(metaclass=Singleton):
    
    def __init__(self):
        '''
        Initialize pheripherals.
        '''
        
        Log.warning("Initializing pheripherals")
        self.controllers = []
        self.key = None
        self.timestamp = 0
        
        # Load controllers from config or use default keyboard
        if Config['pheripherals'].get('controllers'):
            for controller in Config['pheripherals']['controllers']:
                self.register_controller(controller)
        else:
            Log.warning("No controllers defined in config file.")
            Log.warning("Adding default keyboard controller.")
            Config['pheripherals']['controllers'] = ['keyboard']
            save_config()
            self.register_controller('keyboard')
        
        try:
            self.thread = WThread(target=self.loop)
            self.thread.start()
            time.sleep(1)
        except Exception as e:
            Log.exception("Error initializing pheripherals: {}".format(e))
            sys.exit(1)
    
    
    def stop(self):
        '''
        Stop pheripherals.
        '''
        
        Log.warning("Stopping pheripherals")
        if self.thread.is_alive():
            self.thread.stop()
            self.thread.join()
    
    def register_controller(self, controller):
        '''
        Register a controller.
        
        :param controller: Controller to register.
        '''
        try:
            Log.warning("Registering controller: {}".format(controller))
            module = importlib.import_module(f"PiPerW.pheripherals.{controller}").Pheripheral()
            self.controllers.append(module)
        except ImportError as e:
            Log.exception(f"Failed to register controller '{controller}': {e}")
    
    def get_key(self):
        '''
        Get the latest key pressed.
        '''
        key = self.key.value if self.key else None
        self.key = None  # Reset key after fetching
        return key
    
    def await_key(self):
        '''
        Wait for a key to be pressed.
        '''
        
        self.key = None  # Ensure key is reset before awaiting a new one
        while not self.key:
            time.sleep(0.1)
        return self.get_key()
    
    def await_any_key_press(self):
        ''' 
        Wait for any key press.
        '''
        
        return self.await_key()
    
    def loop(self):
        '''
        Loop to check for key presses.
        '''
        
        Log.info("Pheripherals loop started")
        while True:
            if self.thread.stopped():
                break
            
            for controller in self.controllers:
                key, timestamp = controller.get_key()
                
                if key and timestamp > self.timestamp:
                    self.key = key
                    self.timestamp = timestamp
                
            if self.key == PheripheralAction.EXIT:
                Log.info("Exit key detected, stopping loop.")
                break

        Log.warning("Pheripherals loop ended.")
