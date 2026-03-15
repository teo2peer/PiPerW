from PiPerW.interfaces.app_interface import AppInterface
from PiPerW.driver.pheripherals import Pheripherals
from PiPerW.driver.display import Display
from PiPerW.helpers import Log, Config
from PiPerW.utils.Menu import Menu
import os, time, subprocess

display = Display()
pheripherals = Pheripherals()

class App(AppInterface):
    def __init__(self):
        super().__init__()
        self.mon_interface = Config['network']['interface'] + "mon"

    def init(self):
        display.text("Starting\nBeacon Flood\n...")
        time.sleep(1)

        # Check / enable monitor mode
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
                display.text("Error enabling\nmonitor mode")
                self.wait_for_input()
                return

        attacks = [
            "Random SSIDs",
            "RickRoll Name",
            "Copy Nearby APs",
            "Exit"
        ]
        menu = Menu(attacks, "Attack Type:")

        while not self.is_stopped():
            display.clear()
            menu.show()
            key = self.wait_for_input()
            
            if key == "up":
                menu.previous()
            elif key == "down":
                menu.next()
            elif key == "select":
                sel = menu.get_selected()
                if sel == 3: # Exit
                    return
                else:
                    self.execute_flood(sel)

    def execute_flood(self, mode):
        # mode 0: random, 1: rickroll, 2: copy nearby
        cmd = ["sudo", "mdk4", self.mon_interface, "b"]
        
        if mode == 1:
            cmd.extend(["-n", "Never_Gonna_Give_You_Up"])
        elif mode == 2:
            cmd.extend(["-am"]) # Automatic mode, mimics nearby APs

        display.text("Flooding Beacons!\n\n[Press BACK \nto stop]")
        Log.info(f"Starting Beacon Flood: {' '.join(cmd)}")
        
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        while not self.is_stopped():
            key = self.wait_for_input()
            if key == "back" or self.is_stopped():
                Log.info("Stopping Beacon Flood")
                proc.terminate()
                subprocess.run(["sudo", "killall", "mdk4"], capture_output=True)
                break

    def run(self):
        self.init()