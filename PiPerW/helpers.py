import toml
import os
import sys
import inspect
import threading
from pathlib import Path
from PiPerW.utils.Logging import Logging


# Absolute project root, resolved once at import. PiPerW/helpers.py -> repo root.
PIPERW_ROOT = Path(__file__).resolve().parent.parent


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
        
        Log.info(f"\n{BCOLORS.OKCYAN}{self.message}{BCOLORS.ENDC}")
        for i, option in enumerate(self.options):
            Log.info(f"{BCOLORS.OKGREEN}{i+1}{BCOLORS.ENDC}. {option}")
        
        while True:
            try:
                choice = int(input(BCOLORS.OKBLUE+  "Option: "+BCOLORS.ENDC))
                if choice > 0 and choice <= len(self.options):
                    return self.options[choice-1]
                else:
                    Log.error("Invalid option")
            except ValueError:
                Log.error("Invalid option")

#---------------------------
# Custom trheading class for exception handling
#---------------------------
class WThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, daemon=None):
        threading.Thread.__init__(self, group=group, target=target, name=name, args=args, kwargs=kwargs, daemon=daemon)
        self.exc = None
        self.setDaemon(True)
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
    
        '''
        Add in the loop:
        if self.thread.stopped():
                break
        '''

#---------------------------
#     Helper with PiPerW/lib
#---------------------------

def download_lib_from_github(url, lib_name):
    '''
    Download the PiPerW library from github
    '''
    # check if the resources folder exists
    Log.warning("Downloading library {} from github into {}".format(url, lib_name))
    import subprocess
    res = subprocess.run(["git", "clone", url, "PiPerW/lib/" + lib_name]).returncode

    if res != 0:
        Log.error("Error downloading the library")
        raise Exception("Error downloading the library")


def select_number(display, pheripherals, title="Select a number", start_number=0, scale=1, decimals=0, min=-99999, max=99999, unit = None):
    '''
    Select number with options for scaling and decimal places
    '''
    
    multiplier = 1
    number = start_number
    if start_number < min:
        number = min
    if start_number > max:
        number = max
    while True:
        text = "\n"
        text += title + "\n"
        if not unit:
            text += "Number: {}\n".format(round(number, decimals))  # Round number to the correct decimal places
        else:
            text += "{} {}\n".format(round(number, decimals), unit)
        text += "Multiplier: {}\n ↕ to modify".format(multiplier)
        display.text(text)
        
        key = pheripherals.await_key()
        
        if key == "right":
            number += (1 * multiplier * scale) / (10 ** decimals)
            if number > max:
                number = max  # Fix condition to cap the number at the maximum
        elif key == "left":
            number -= (1 * multiplier * scale) / (10 ** decimals)
            if number < min:
                number = min  # Fix condition to cap the number at the minimum
        elif key == "up":
            multiplier = multiplier * 10 if multiplier < 1000 else 1000
        elif key == "down":
            multiplier = multiplier / 10 if multiplier > 1 else 1
        elif key == "select":
            break
        elif key == "back":
            sys.exit(0)
        
        # Ensure number is rounded to the appropriate decimal places
        number = round(number, decimals)
    
    return number


#---------------------------
#     Congiguration file
#---------------------------
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

config_path = BASE_DIR / 'config.toml'
example_path = BASE_DIR / 'config.toml.example'

# check if the config file exists
if not config_path.exists():
    # copy the default config file
    import shutil
    if example_path.exists():
        shutil.copy(example_path, config_path)
    else:
        Log.warning("No config.toml.example found")

Config = {}
if config_path.exists():
    Config = toml.load(str(config_path))  


def save_config():
    '''
    Save the Configuration file
    '''
    Log.info("Saving configuration file")
    with open(str(config_path), 'w') as f:
        toml.dump(Config, f)
        

#---------------------------
#     Logging
#---------------------------
# Get the parent directory of this file as the root path (the main PiPerW dir)
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Log = Logging(Config['general']['debug'], root_dir)
Log.info("Helpers loaded")
