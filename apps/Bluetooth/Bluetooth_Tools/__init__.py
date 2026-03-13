from PiPerW.apps.app_interface import AppInterface
from PiPerW.driver.pheripherals import Pheripherals
from PiPerW.driver.display import Display
from PiPerW.helpers import Log
from PiPerW.utils.Menu import Menu
import subprocess
import time
import os
import threading
from datetime import datetime

display = Display()

class App(AppInterface):
    name = "BlueKit (Bluetooth Tools)"
    version = "1.0"

    def __init__(self):
        super().__init__(self.name, self.version)
        self.menu = None
        self.nearby = []
        self.interface = "hci0"

    def check_adapter(self):
        try:
            res = subprocess.run(["hciconfig"], capture_output=True, text=True)
            if "hci0" not in res.stdout:
                return False, "No adapter"
            if "UP RUNNING" not in res.stdout:
                return False, "Adapter Down"
            return True, "OK"
        except FileNotFoundError:
            return False, "hciconfig missing"

    def run(self):
        Log.info("BlueKit: starting. Reference: https://github.com/Cinnamon1212/BlueKit")
        options = [
            "Scan Classic",
            "Scan BLE",
            "Find Services",
            "Pair Device",
            "Send File",
            "Discoverable",
            "Sniff Packets",
            "Spoof MAC",
            "Toggle Power",
            "Exit"
        ]
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
                Log.info(f"BlueKit: selected action '{sel}'")
                if sel == "Exit":
                    break
                else:
                    self.execute_action(sel)
            elif key == "back":
                display.text("App root menu:\n\nHold EXIT 3s\nto force quit")
                time.sleep(1.5)

    def execute_action(self, action):
        try:
            if action == "Scan Classic":
                self.scan_classic()
            elif action == "Scan BLE":
                self.scan_ble()
            elif action == "Find Services":
                self.scan_services()
            elif action == "Pair Device":
                self.pair_device()
            elif action == "Send File":
                self.send_file()
            elif action == "Discoverable":
                self.discoverable_mode()
            elif action == "Sniff Packets":
                self.sniff_packets()
            elif action == "Spoof MAC":
                self.spoof_mac()
            elif action == "Toggle Power":
                self.toggle_power()
        except Exception as e:
            Log.error(f"BlueKit: action '{action}' failed: {e}")
            display.text(f"Error:\n{e}\n\nPress any key")
            self.wait_for_input()

    def scan_classic(self):
        is_ok, status = self.check_adapter()
        if not is_ok:
            display.text(f"No Adapter\nStatus: {status}\nUse Toggle Power")
            time.sleep(2)
            return

        display.text("Scanning classic...\n\n(Takes time)")
        try:
            import bluetooth
            self.nearby = bluetooth.discover_devices(lookup_names=True)
        except Exception as e:
            Log.error(f"pybluez error: {e}")
            display.text("Error scanning.\nCheck pybluez\ndependencies")
            time.sleep(2)
            return

        if not self.nearby:
            display.text("No devices found.\n\nPress BACK")
            while not self.is_stopped() and self.wait_for_input() != "back": pass
            return

        dev_list = [f"{n[:15]}: {a[-8:]}" for a, n in self.nearby]
        res_menu = Menu(dev_list)
        while not self.is_stopped():
            display.draw(res_menu.generate())
            k = self.wait_for_input()
            if k == "up": res_menu.previous()
            if k == "down": res_menu.next()
            if k == "back": break

    def scan_ble(self):
        is_ok, status = self.check_adapter()
        if not is_ok:
            display.text(f"No Adapter\nStatus: {status}\nUse Toggle Power")
            time.sleep(2)
            return

        display.text("Scanning BLE...\n\nPress BACK to stop")
        proc = subprocess.Popen(["sudo", "hcitool", "lescan"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        found_devices = set()

        def read_output(pipe):
            try:
                for line in iter(pipe.readline, ''):
                    if not line: break
                    line = line.strip()
                    if ":" in line and "LE Scan" not in line: found_devices.add(line)
            except Exception: pass

        t = threading.Thread(target=read_output, args=(proc.stdout,), daemon=True)
        t.start()

        while not self.is_stopped():
            key = self.wait_for_input(process=proc)
            if key == "back": break
            if proc.poll() is not None:
                display.text("BLE scan ended\n\nPress BACK")
                while not self.is_stopped() and self.wait_for_input() != "back": pass
                break

        if proc.poll() is None:
            proc.terminate()
            subprocess.run(["sudo", "killall", "-9", "hcitool"], capture_output=True)

        if not found_devices:
            display.text("No BLE devices.\n\nPress BACK")
            while not self.is_stopped() and self.wait_for_input() != "back": pass
        else:
            dev_list = sorted(list(found_devices))
            res_menu = Menu(dev_list)
            while not self.is_stopped():
                display.draw(res_menu.generate())
                k = self.wait_for_input()
                if k == "up": res_menu.previous()
                if k == "down": res_menu.next()
                if k == "back": break

    def scan_services(self):
        if not self.nearby:
            display.text("Scan Classic first!\n\nPress BACK")
            while not self.is_stopped() and self.wait_for_input() != "back": pass
            return

        dev_list = [f"{n[:15]}" for a, n in self.nearby]
        sm = Menu(dev_list)
        idx = 0
        while not self.is_stopped():
            display.draw(sm.generate())
            k = self.wait_for_input()
            if k == "up": sm.previous()
            if k == "down": sm.next()
            if k == "back": return
            if k == "select":
                idx = sm.get_index()
                break
        
        addr, name = self.nearby[idx]
        display.text(f"Scanning:\n{name[:10]}\nWait...")
        try:
            import bluetooth
            services = bluetooth.find_service(address=addr)
        except Exception as e:
            display.text(f"Error: {e}")
            while not self.is_stopped() and self.wait_for_input() != "back": pass
            return

        if not services:
            display.text("No services.\n\nPress BACK")
            while not self.is_stopped() and self.wait_for_input() != "back": pass
            return
            
        srv_list = [f"{s['name'][:10]} {s['port']}" for s in services]
        res_menu = Menu(srv_list)
        while not self.is_stopped():
            display.draw(res_menu.generate())
            k = self.wait_for_input()
            if k == "up": res_menu.previous()
            if k == "down": res_menu.next()
            if k == "back": break

    def pair_device(self):
        if not self.nearby:
            display.text("Scan Classic first!\n\nPress BACK")
            while not self.is_stopped() and self.wait_for_input() != "back": pass
            return
        
        dev_list = [f"{n[:15]}" for a, n in self.nearby]
        sm = Menu(dev_list)
        idx = 0
        while not self.is_stopped():
            display.draw(sm.generate())
            k = self.wait_for_input()
            if k == "up": sm.previous()
            if k == "down": sm.next()
            if k == "back": return
            if k == "select":
                idx = sm.get_index()
                break

        addr, name = self.nearby[idx]
        display.text(f"Pairing:\n{name[:15]}")
        subprocess.run(["sudo", "bluetoothctl", "remove", addr], capture_output=True)
        subprocess.run(["sudo", "bluetoothctl", "agent", "on"], capture_output=True)
        subprocess.run(["sudo", "bluetoothctl", "trust", addr], capture_output=True)
        subprocess.run(["sudo", "bluetoothctl", "pair", addr], capture_output=True)
        display.text("Pairing sent.\nConnecting...")
        time.sleep(2)
        subprocess.run(["sudo", "bluetoothctl", "connect", addr], capture_output=True)
        display.text("Done.\nCheck target.\nPress BACK")
        while not self.is_stopped() and self.wait_for_input() != "back": pass

    def send_file(self):
        if not self.nearby:
            display.text("Scan Classic first!\n\nPress BACK")
            while not self.is_stopped() and self.wait_for_input() != "back": pass
            return

        files_dir = os.path.join(self.get_state_dir(), "files")
        os.makedirs(files_dir, exist_ok=True)
        
        files = os.listdir(files_dir)
        if not files:
            display.text("No files found in:\nstate/files/\n\nPress BACK")
            while not self.is_stopped() and self.wait_for_input() != "back": pass
            return

        fm = Menu(files)
        file_idx = 0
        while not self.is_stopped():
            display.draw(fm.generate())
            k = self.wait_for_input()
            if k == "up": fm.previous()
            if k == "down": fm.next()
            if k == "back": return
            if k == "select":
                file_idx = fm.get_index()
                break
                
        selected_file = files[file_idx]
        file_path = os.path.join(files_dir, selected_file)
        
        dev_list = [f"{n[:15]}" for a, n in self.nearby]
        sm = Menu(dev_list)
        idx = 0
        while not self.is_stopped():
            display.draw(sm.generate())
            k = self.wait_for_input()
            if k == "up": sm.previous()
            if k == "down": sm.next()
            if k == "back": return
            if k == "select":
                idx = sm.get_index()
                break

        addr, name = self.nearby[idx]
        display.text(f"Sending file:\n{selected_file[:10]}\nto {name[:10]}")
        
        # Using bt-obex which is part of bluez-tools (already in manifest)
        res = subprocess.run(["bt-obex", "-p", addr, file_path], capture_output=True, text=True)
        
        if res.returncode == 0:
            display.text("File Sent!\n\nPress BACK")
        else:
            Log.error(f"Send failed: {res.stderr}")
            display.text("Send Failed.\nCheck logs.\nPress BACK")
            
        while not self.is_stopped() and self.wait_for_input() != "back": pass

    def discoverable_mode(self):
        display.text("Discoverable ON...")
        subprocess.run(["sudo", "bluetoothctl", "agent", "on"], capture_output=True)
        subprocess.run(["sudo", "bluetoothctl", "discoverable", "on"], capture_output=True)
        subprocess.run(["sudo", "bluetoothctl", "pairable", "on"], capture_output=True)
        display.text("Device is visible!\n\nPress BACK to stop")
        while not self.is_stopped() and self.wait_for_input() != "back": pass
        subprocess.run(["sudo", "bluetoothctl", "discoverable", "off"], capture_output=True)

    def sniff_packets(self):
        display.text("Sniffing packets\nPress BACK to stop")
        filename = f'bt_{datetime.now().strftime("%d%m%M")}.pcap'
        out_path = os.path.join(self.get_state_dir(), filename)
        
        proc = subprocess.Popen(
            ["sudo", "tshark", "-i", "bluetooth0", "-w", out_path],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        
        while not self.is_stopped():
            k = self.wait_for_input(process=proc)
            if k == "back": break
            if proc.poll() is not None: break
            
        if proc.poll() is None:
            proc.terminate()
            subprocess.run(["sudo", "killall", "tshark"], capture_output=True)
            
        display.text(f"Saved PCAP:\n{filename}\n\nPress BACK")
        while not self.is_stopped() and self.wait_for_input() != "back": pass

    def spoof_mac(self):
        display.text("Spoofing MAC...\nRandomizing...")
        res = subprocess.run(["sudo", "spooftooph", "-i", self.interface, "-R"], capture_output=True)
        if res.returncode == 0:
            mac = "Unknown"
            hciconfig_res = subprocess.run(["hciconfig", self.interface], capture_output=True, text=True)
            for line in hciconfig_res.stdout.split('\n'):
                if "BD Address" in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        mac = parts[2]
                    break
            display.text(f"Spoofed!\nMAC: {mac}\n\nPress BACK")
        else:
            display.text("Failed.\nIs spooftooph\ninstalled?\nPress BACK")
        while not self.is_stopped() and self.wait_for_input() != "back": pass

    def toggle_power(self):
        res = subprocess.run(["rfkill", "list", "bluetooth"], capture_output=True, text=True)
        if "Soft blocked: yes" in res.stdout:
            display.text("Enabling BT...")
            subprocess.run(["sudo", "rfkill", "unblock", "bluetooth"])
            subprocess.run(["sudo", "hciconfig", "hci0", "up"])
        else:
            display.text("Disabling BT...")
            subprocess.run(["sudo", "rfkill", "block", "bluetooth"])
            subprocess.run(["sudo", "hciconfig", "hci0", "down"])
        display.text("Press BACK")
        while not self.is_stopped() and self.wait_for_input() != "back": pass

