from PiPerW.helpers import Config
from PiPerW.helpers import Log
from PiPerW.pheripherals.pheripheral_interface import PheripheralAction
from PiPerW.utils.Singleton import Singleton
import importlib
import time

class Pheripherals(metaclass=Singleton):
    
    def __init__(self):
        
        Log.warning("Initializing pheripherals")
        self.controllers = []
        self.key = None
        self.timestamp = 0
        
        if Config['pheripherals']['enable_keyboard']:
            self.register_controller("keyboard")
    
    def register_controller(self, controller):
        Log.warning("Registering controller: {}".format(controller))
        module = importlib.import_module("PiPerW.pheripherals.{}".format(controller)).pheripheral
        
        self.controllers.append(module)
        
    def get_event(self):
        key = self.key.value if self.key else None
        self.key = None
        return key
        
    def loop(self):
        Log.info("Pheripherals loop started")
        while True:
            key = None
            timestamp = 0
            diferent_key = False
            last_controller = None
            for controller in self.controllers:
                controller.update()
                key, timestamp = controller.get_key()
                
                if key and timestamp > self.timestamp:
                    self.key = key
                    self.timestamp = timestamp
                    last_controller = controller
                    print("Key: {}".format(self.key))
                    
        
            # check if is long press
            if key:
                time.sleep(0.12)
            

                
            if self.key == PheripheralAction.EXIT:
                break