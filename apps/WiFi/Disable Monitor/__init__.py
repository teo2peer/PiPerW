# sudo airmon-ng start wlan0
# iwconfig check if monitor mode is enabled

# get all bssid
# sudo airodump-ng wlan0mon --output-format csv -w /tmp/scan

# disconnect all clients
# sudo aireplay-ng --deauth 0 -a BSSID wlan0mon

from PiPerW.interfaces.app_interface import AppInterface
from PiPerW.driver.pheripherals import Pheripherals
from PiPerW.driver.display import Display
from PiPerW.helpers import Log, Config
import os, time

display = Display()
pheripherals = Pheripherals()



class App(AppInterface):

    def __init__(self):
        super().__init__()
        self.menu = None

    def init(self):
        Log.warning("Disabling Monitor Mode")
        display.text("Disabling Monitor Mode")
        time.sleep(1)

        import subprocess
        result = subprocess.run(["sudo", "airmon-ng", "stop", f"{Config['network']['interface']}mon"], capture_output=True, text=True)
        if result.returncode != 0:
            result = subprocess.run(["sudo", "airmon-ng", "stop", Config['network']['interface']], capture_output=True, text=True)
        
        subprocess.run(["sudo", "service", "NetworkManager", "start"])
        subprocess.run(["sudo", "ifconfig", Config['network']['interface'], "up"])

        Log.info("Monitor mode disabled")
        display.text("Monitor mode \ndisabled\n\n[Press any key]")



    def run(self):
        self.init()
