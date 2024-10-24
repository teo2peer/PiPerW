from .badusb import BadUSB, DuckyScriptInterpreter
from PiPerW.interfaces.app_interface import AppInterface
from PiPerW.pheripherals import Pheripherals
from PiPerW.display import Display
from PiPerW.helpers import Log, Config, download_lib_from_github
from PiPerW.utils.Menu import MenuFolderFiles
import os, time, subprocess, multiprocessing


display = Display()
pheripherals = Pheripherals()



class App(AppInterface):
    
    # Loads and executes commands from the payload
    def __init__(self):
        self.usb = BadUSB()

    
    def run(self):
        display.clear()
        display.text("Running Bad USB")
        self.usb.run("powershell")
        time.sleep(0.125)
        self.usb.write("whoami")
        display.text("Bad USB Done\nPress any key to exit")
        pheripherals.await_any_key_press()