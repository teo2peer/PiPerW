from PiPerW.helpers import Config, Log, WThread, save_config
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
        
        if Config['pheripherals']['controllers']:
            for controller in Config['pheripherals']['controllers']:
                self.register_controller(controller)
        else:
            Log.warning("No controllers defined in config file")
            Log.warning("Adding default keyboard controller")
            Config['pheripherals']['controllers'] = ['keyboard']
            save_config()
            register_controller('keyboard')
            
        try:
            trhead = WThread(target=self.loop)
            trhead.start()
            time.sleep(1)
        except Exception as e:
            Log.exception("Error initializing pheripherals: {}".format(e))
            sys.exit(1)
    
    def register_controller(self, controller):
        Log.warning("Registering controller: {}".format(controller))
        module = importlib.import_module("PiPerW.pheripherals.{}".format(controller)).Pheripheral()
        
        self.controllers.append(module)
        
    def get_key(self):
        key = self.key.value if self.key else None
        self.key = None
        return key
    
    def await_key(self):
        self.key = None
        while not self.key:
            time.sleep(0.1)
        return self.get_key()

    def await_any_key_press(self):
        self.await_key()
        self.key = None
        
        
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