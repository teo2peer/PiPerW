from PiPerW.apps.app_interface import AppInterface
from PiPerW.driver.pheripherals import Pheripherals
from PiPerW.driver.display import Display
from PiPerW.helpers import Log
from PiPerW.utils.Menu import Menu
import subprocess
import time

display = Display()
pheripherals = Pheripherals()

class App(AppInterface):
    def __init__(self):
        super().__init__()

    def run(self):
        while not self.is_stopped():
            display.text("Scanning local\nWiFi Networks...\n(This takes a sec)")
            
            networks = self.scan_wifi()
            
            if not networks:
                networks = ["No networks found", "Try Again", "Exit"]
                
            networks.extend(["-- Scan Again --", "Exit"])
            
            menu = Menu(networks)
            
            while True:
                menu.show()
                key = pheripherals.await_key()
                
                if key == "up":
                    menu.previous()
                elif key == "down":
                    menu.next()
                elif key == "select":
                    sel = networks[menu.index]
                    if sel == "Exit":
                        return
                    elif sel == "-- Scan Again --" or sel == "Try Again":
                        break # Break inner loop to trigger rescan
                elif key in ["back", "exit"]:
                    return

    def scan_wifi(self):
        found = []
        try:
            # Try nmcli (NetworkManager) first as it provides clean outputs
            out = subprocess.check_output(["nmcli", "-t", "-f", "SSID,SIGNAL", "dev", "wifi"], stderr=subprocess.DEVNULL)
            lines = out.decode('utf-8', errors='ignore').split('\n')
            for line in lines:
                if ":" in line:
                    ssid, sig = line.split(":", 1)
                    if ssid: # avoid empty hidden networks
                        found.append(f"{ssid} [{sig}%]")
        except Exception as e:
            Log.error(f"nmcli scan failed: {e}")
            try:
                # Fallback to pure iw scan for standard Raspberry Pi environments
                out = subprocess.check_output(["sudo", "iw", "dev", "wlan0", "scan"], stderr=subprocess.DEVNULL)
                lines = out.decode('utf-8', errors='ignore').split('\n')
                current_ssid = ""
                for line in lines:
                    line = line.strip()
                    if line.startswith("SSID: "):
                        current_ssid = line[6:]
                        if current_ssid and current_ssid != "\\x00":
                            found.append(f"{current_ssid} [??]")
            except Exception as e2:
                Log.error(f"iw scan failed: {e2}")
                
        # Remove duplicates preserving order
        unique_nets = []
        [unique_nets.append(x) for x in found if x not in unique_nets]
        return unique_nets