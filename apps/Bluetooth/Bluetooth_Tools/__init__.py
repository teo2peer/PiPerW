from PiPerW.apps.app_interface import AppInterface
from PiPerW.driver.pheripherals import Pheripherals
from PiPerW.driver.display import Display
from PiPerW.helpers import Log
from PiPerW.utils.Menu import Menu
import subprocess
import time

display = Display()

class App(AppInterface):
    name = "Bluetooth Tools"
    version = "1.0"

    def __init__(self):
        super().__init__(self.name, self.version)
        self.menu = None

    def run(self):
        options = ["Scan BLE Devices", "Discoverable Mode", "Toggle Power", "Exit"]
        self.menu = Menu(options)

        while not self.is_stopped():
            display.draw(self.menu.generate())
            key = self.wait_for_input()

            if key == "up":
                self.menu.previous()
            elif key == "down":
                self.menu.next()
            elif key == "select":
                sel = self.menu.get_selected()
                if sel == "Exit":
                    break
                else:
                    self.execute_action(sel)
            elif key == "back":
                break

    def execute_action(self, action):
        if action == "Scan BLE Devices":
            self.scan_ble()
        elif action == "Discoverable Mode":
            self.discoverable_mode()
        elif action == "Toggle Power":
            self.toggle_power()

    def scan_ble(self):
        Log.info("Starting BLE Scan")
        display.text("Scanning BLE...\n\nPress BACK to stop")

        # hcitool is commonly available in bluez
        proc = subprocess.Popen(
            ["sudo", "hcitool", "lescan"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # Let the scan run for a few seconds or until the user presses BACK
        while not self.is_stopped():
            key = self.wait_for_input(process=proc)
            if key == "back":
                break

        Log.info("Stopping BLE Scan")
        if proc.poll() is None:
            proc.terminate()
            # Failsafe cleanup for hcitool
            subprocess.run(["sudo", "killall", "-9", "hcitool"], capture_output=True)

    def discoverable_mode(self):
        Log.info("Toggling Discoverable Mode")
        display.text("Making device\ndiscoverable...")
        
        subprocess.run(["sudo", "bluetoothctl", "discoverable", "on"], capture_output=True)
        time.sleep(1)
        
        display.text("Device is now\ndiscoverable!\n\nPress any key to stop")
        self.wait_for_input()
        
        display.text("Turning off\ndiscoverable mode...")
        subprocess.run(["sudo", "bluetoothctl", "discoverable", "off"], capture_output=True)
        time.sleep(1)

    def toggle_power(self):
        # Check current status using rfkill
        res = subprocess.run(["rfkill", "list", "bluetooth"], capture_output=True, text=True)
        is_blocked = "Soft blocked: yes" in res.stdout
        
        if is_blocked:
            display.text("Enabling Bluetooth...")
            subprocess.run(["sudo", "rfkill", "unblock", "bluetooth"], capture_output=True)
            Log.info("Bluetooth enabled")
        else:
            display.text("Disabling Bluetooth...")
            subprocess.run(["sudo", "rfkill", "block", "bluetooth"], capture_output=True)
            Log.info("Bluetooth disabled")
            
        time.sleep(1.5)
