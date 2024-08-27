import toml
import os
import sys
import inspect
import threading
from PiPerW.utils.Logging import Logging



class BCOLORS:
    '''
    Colors for the terminal
    '''
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'



#---------------------------
#     Filter dir
#---------------------------
class DirFilter:
    
    def __init__(self, dir):
        '''
        Filter directories and files
        
        :param dir: str: Directory to filter
        '''
        self.dir = dir
    
    def files(self):
        '''
        Get all files in a directory
        
        :return: list: List of files
        '''
        return [f for f in os.listdir(self.dir) if os.path.isfile(os.path.join(self.dir, f))]
    
    def folders(self):
        '''
        Get all directories in a directory
        
        :return: list: List of directories
        '''
        return [f for f in os.listdir(self.dir) if os.path.isdir(os.path.join(self.dir, f))]
    
    def dirs(self):
        '''
        Get all directories and files in a directory
        
        :return: list: List of directories and files
        '''
        return self.folders() 

#---------------------------
#     SECTION HEADER
#---------------------------

class Selector:
    def __init__(self, options, message = "Select an option"):
        '''
        Select an option from a list
        
        :param options: list: List of options
        :param message: str: Message to display
        '''
        self.options = options
        self.message = message
        
    def select(self):
        '''
        Select an option from a list
        
        :return: str: Selected option
        '''
        
        print(f"\n{BCOLORS.OKCYAN}{self.message}{BCOLORS.ENDC}")
        for i, option in enumerate(self.options):
            print(f"{BCOLORS.OKGREEN}{i+1}{BCOLORS.ENDC}. {option}")
        
        while True:
            try:
                choice = int(input(BCOLORS.OKBLUE+  "Option: "+BCOLORS.ENDC))
                if choice > 0 and choice <= len(self.options):
                    return self.options[choice-1]
                else:
                    print("Invalid option")
            except ValueError:
                print("Invalid option")

#---------------------------
# Custom trheading class for exception handling
#---------------------------
class WThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, daemon=None):
        threading.Thread.__init__(self, group=group, target=target, name=name, args=args, kwargs=kwargs, daemon=daemon)
        self.exc = None
        self._stop_event = threading.Event()


    def run(self):
        try:
            if self._target:
                self._target(*self._args, **self._kwargs)
        except Exception as e:
            self.exc = e

    def join(self, timeout=None):
        threading.Thread.join(self, timeout)
        if self.exc:
            raise self.exc
    
    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()



#---------------------------
#     Congiguration file
#---------------------------
# check if the config file exists
if not os.path.exists('config.toml'):
    # copy the default config file
    os.system('cp config.toml.example config.toml')
Config = {}
Config = toml.load('config.toml')  


def save_config():
    '''
    Save the Configuration file
    '''
    with open('Config.toml', 'w') as f:
        toml.dump(Config, f)
        

#---------------------------
#     Logging
#---------------------------
Log = Logging(Config['general']['debug'], os.path.dirname(os.path.abspath(__file__)))
Log.info("Helpers loaded")
