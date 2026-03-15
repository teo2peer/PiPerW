from .badusb import BadUSB, DuckyScriptInterpreter
from PiPerW.apps.app_interface import AppInterface
from PiPerW.driver.pheripherals import Pheripherals
from PiPerW.driver.display import Display
from PiPerW.helpers import Log, Config, download_lib_from_github
from PiPerW.utils.Menu import MenuFolderFiles
import os, time, subprocess, multiprocessing


display = Display()
pheripherals = Pheripherals()



class App(AppInterface):
    
    # Loads and executes commands from the payload
    def __init__(self):
        super().__init__()
        self.usb = BadUSB()

    
    def run(self):
        display.clear()
        display.text("Running Bad USB")
        self.usb.run("powershell")
        time.sleep(0.125)
        self.usb.write("whoami")
        display.text("Bad USB Done\nPress any key to exit")
        self.wait_for_input(getattr(self, 'process', None))
