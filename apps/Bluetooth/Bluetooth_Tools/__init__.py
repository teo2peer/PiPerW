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
        Log.info("Bluetooth Tools: starting")
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
                Log.info(f"Bluetooth Tools: selected action '{sel}'")
                if sel == "Exit":
                    Log.info("Bluetooth Tools: exit requested")
                    break
                else:
                    self.execute_action(sel)
            elif key == "back":
                Log.info("Bluetooth Tools: back requested at root menu - ignoring")
                display.text("App root menu:\n\nHold EXIT 3s\nto force quit")
                time.sleep(1.5)

        Log.info("Bluetooth Tools: exiting")

    def execute_action(self, action):
        Log.info(f"Bluetooth Tools: executing action '{action}'")
        try:
            if action == "Scan BLE Devices":
                self.scan_ble()
            elif action == "Discoverable Mode":
                self.discoverable_mode()
            elif action == "Toggle Power":
                self.toggle_power()
        except Exception as e:
            Log.error(f"Bluetooth Tools: action '{action}' failed: {e}")
            display.text(f"Error: {e}\n\nPress any key")
            self.wait_for_input()

    def scan_ble(self):
        Log.info("Bluetooth Tools: starting BLE scan")
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
                Log.info("Bluetooth Tools: BLE scan stopped by BACK key")
                break
            if key == "exit":
                # Exit only works via long press; let Pheripherals handle it
                continue

        Log.info("Bluetooth Tools: stopping BLE scan")
        if proc.poll() is None:
            proc.terminate()
            # Failsafe cleanup for hcitool
            res = subprocess.run(["sudo", "killall", "-9", "hcitool"], capture_output=True)
            Log.debug(f"BLE scan cleanup return code: {res.returncode}")

    def discoverable_mode(self):
        Log.info("Bluetooth Tools: enabling discoverable mode")
        display.text("Making device\ndiscoverable...")

        res_on = subprocess.run(["sudo", "bluetoothctl", "discoverable", "on"], capture_output=True, text=True)
        Log.debug(f"Bluetoothctl on stdout: {res_on.stdout.strip()} stderr: {res_on.stderr.strip()} returncode: {res_on.returncode}")
        time.sleep(1)

        display.text("Device is now\ndiscoverable!\n\nPress any key to stop")
        self.wait_for_input()

        display.text("Turning off\ndiscoverable mode...")
        res_off = subprocess.run(["sudo", "bluetoothctl", "discoverable", "off"], capture_output=True, text=True)
        Log.debug(f"Bluetoothctl off stdout: {res_off.stdout.strip()} stderr: {res_off.stderr.strip()} returncode: {res_off.returncode}")
        time.sleep(1)

    def toggle_power(self):
        # Check current status using rfkill
        res = subprocess.run(["rfkill", "list", "bluetooth"], capture_output=True, text=True)
        is_blocked = "Soft blocked: yes" in res.stdout
        Log.debug(f"rfkill status: {res.stdout.strip()}")

        if is_blocked:
            display.text("Enabling Bluetooth...")
            res2 = subprocess.run(["sudo", "rfkill", "unblock", "bluetooth"], capture_output=True, text=True)
            Log.info(f"Bluetooth enabled (rc={res2.returncode})")
            Log.debug(f"rfkill unblock output: {res2.stdout.strip()} {res2.stderr.strip()}")
        else:
            display.text("Disabling Bluetooth...")
            res2 = subprocess.run(["sudo", "rfkill", "block", "bluetooth"], capture_output=True, text=True)
            Log.info(f"Bluetooth disabled (rc={res2.returncode})")
            Log.debug(f"rfkill block output: {res2.stdout.strip()} {res2.stderr.strip()}")

        time.sleep(1.5)
