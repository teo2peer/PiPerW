import time
from enum import Enum

class PheripheralAction(Enum):
    UP = 'up'
    DOWN = 'down'
    LEFT = 'left'
    RIGHT = 'right'
    SELECT = 'select'
    BACK = 'back'
    EXIT = 'exit'

class PheripheralInterface:
    
    def __init__(self, name):
        self.name = name
        
        self.key = None
        self.timestamp = time.time()
        self.long_press_time = 1.2
        
    def get_key(self):
        return self.key, self.timestamp
    

    
    def log_key(self, key: PheripheralAction):
        
        self.key = key
        self.timestamp = time.time()
    
    
    def update(self):
        pass