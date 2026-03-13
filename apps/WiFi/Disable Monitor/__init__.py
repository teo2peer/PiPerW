# sudo airmon-ng start wlan0
# iwconfig check if monitor mode is enabled

# get all bssid
# sudo airodump-ng wlan0mon --output-format csv -w /tmp/scan

# disconnect all clients
# sudo aireplay-ng --deauth 0 -a BSSID wlan0mon

from PiPerW.interfaces.app_interface import AppInterface
from PiPerW.driver.pheripherals import Pheripherals
from PiPerW.driver.display import Display
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
        Log.warning("Disabling Monitor Mode")
        display.text("Disabling Monitor Mode")
        time.sleep(1)
        
        import subprocess
        result = subprocess.run(["sudo", "airmon-ng", "stop", "wlan0mon"], capture_output=True, text=True)
        if result.returncode != 0:
            Log.error(f"Failed to stop monitor mode: {result.stderr}")
            display.text("Error stopping mode")
        else:    
            Log.info("Monitor mode disabled")
            display.text("Monitor mode disabled")
            
        pheripherals.await_any_key_press()
        
        
    

    def run(self):
        self.init()