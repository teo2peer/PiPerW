from PiPerW.interfaces.app_interface import AppInterface
from PiPerW.driver.pheripherals import Pheripherals
from PiPerW.driver.display import Display
from PiPerW.helpers import Log
from PiPerW.utils.Menu import Menu
import subprocess
import time
import os
import threading
import shutil
from datetime import datetime

display = Display()

class App(AppInterface):
    name = "BlueKit (Bluetooth Tools)"
    version = "1.0"

    def __init__(self):
        super().__init__()
        self.menu = None
        self.nearby = []
        self.interface = "hci0"

    def check_adapter(self):
        """Verify the local Bluetooth adapter is present and up."""
        try:
            res = subprocess.run(["hciconfig"], capture_output=True, text=True)
            Log.debug(f"hciconfig output:\n{res.stdout}")

            if "hci0" not in res.stdout:
                Log.warning("No Bluetooth adapter (hci0) found")
                return False, "No adapter"

            if "UP RUNNING" not in res.stdout:
                Log.warning("Bluetooth adapter is present but down")
                return False, "Adapter Down"

            return True, "OK"
        except FileNotFoundError:
            Log.error("hciconfig not found on system")
            return False, "hciconfig missing"

    def wait_for_back(self, prompt=None, process=None, timeout=None):
        """Wait until the user presses BACK (or optional timeout)."""
        if prompt:
            display.text(prompt)
        Log.debug("Waiting for BACK key")
        start = time.time()

        while not self.is_stopped():
            if timeout and (time.time() - start) >= timeout:
                Log.debug("wait_for_back timed out")
                return False

            key = self.wait_for_input(process=process)
            if key == "back":
                Log.debug("BACK pressed")
                return True

            # Avoid tight spinning if process is finished / no key available
            time.sleep(0.05)

        Log.debug("wait_for_back exiting because app stopped")
        return False

    def choose_device(self, prompt=None):
        """Select a device from the last scan results."""
        if not self.nearby:
            display.text("Scan Classic first!\n\nPress BACK")
            self.wait_for_back()
            return None, None

        if prompt:
            display.text(prompt)

        dev_list = [f"{n[:15]}: {a}" for a, n in self.nearby]
        sm = Menu(dev_list)
        while not self.is_stopped():
            display.draw(sm.generate())
            key = self.wait_for_input()
            if key == "up":
                sm.previous()
            elif key == "down":
                sm.next()
            elif key == "back":
                return None, None
            elif key == "select":
                idx = sm.get_index()
                return self.nearby[idx]

        return None, None

    def run(self):
        Log.info("BlueKit: starting. Reference: https://github.com/Cinnamon1212/BlueKit")
        
        # Pequeña pausa inicial para evitar que se pise el botón "Select" 
        # que el usuario acaba de pulsar en el menú al abrir la aplicación.
        time.sleep(0.5)

        options = [
            "Scan Classic",
            "Scan BLE",
            "Find Services",
            "Device Info",
            "Pair Device",
            "Connect Device",
            "Disconnect Device",
            "Trust Device",
            "Untrust Device",
            "Kick Device",
            "Flood (l2ping)",
            "Play Sound",
            "Send File",
            "Discoverable",
            "Sniff Packets",
            "Spoof MAC",
            "Toggle Power",
            "Exit",
        ]
        self.menu = Menu(options)

        while not self.is_stopped():
            display.draw(self.menu.generate())
            key = self.wait_for_input()
            Log.debug(f"Menu key: {key}")

            if key == "up":
                self.menu.previous()
            elif key == "down":
                self.menu.next()
            elif key == "select":
                sel = self.menu.get_selected()
                Log.info(f"BlueKit: selected action '{sel}'")
                if sel == "Exit":
                    break

                # Execute action directly (each action manages its own display and loading states)
                self.execute_action(sel)
            elif key == "back":
                display.text("App root menu:\n\nHold EXIT 3s\nto force quit")
                time.sleep(1.5)

    def execute_action(self, action):
        Log.info(f"Executing action: {action}")
        try:
            if action == "Scan Classic":
                self.scan_classic()
            elif action == "Scan BLE":
                self.scan_ble()
            elif action == "Find Services":
                self.scan_services()
            elif action == "Device Info":
                self.device_info()
            elif action == "Pair Device":
                self.pair_device()
            elif action == "Connect Device":
                self.connect_device()
            elif action == "Disconnect Device":
                self.disconnect_device()
            elif action == "Trust Device":
                self.trust_device()
            elif action == "Untrust Device":
                self.untrust_device()
            elif action == "Kick Device":
                self.kick_device()
            elif action == "Flood (l2ping)":
                self.flood_ping()
            elif action == "Play Sound":
                self.play_sound()
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
        Log.info("Starting classic (BR/EDR) device discovery")
        is_ok, status = self.check_adapter()
        if not is_ok:
            display.text(f"No Adapter\nStatus: {status}\nUse Toggle Power")
            self.wait_for_back()
            return

        display.text("Scanning classic...\n\n(Takes time)")
        try:
            import bluetooth
            self.nearby = bluetooth.discover_devices(lookup_names=True)
            Log.debug(f"Found devices: {self.nearby}")
        except Exception as e:
            Log.error(f"pybluez error: {e}")
            display.text("Error scanning.\nCheck pybluez\ndependencies")
            self.wait_for_back()
            return

        if not self.nearby:
            Log.info("No classic devices found")
            display.text("No devices found.\n\nPress BACK")
            self.wait_for_back()
            return

        dev_list = [f"{n[:15]}: {a[-8:]}" for a, n in self.nearby]
        res_menu = Menu(dev_list)
        Log.info(f"Displaying {len(dev_list)} devices")

        while not self.is_stopped():
            display.draw(res_menu.generate())
            key = self.wait_for_input()
            if key == "up":
                res_menu.previous()
            elif key == "down":
                res_menu.next()
            elif key == "back":
                break

    def scan_ble(self):
        Log.info("Starting BLE scan")
        is_ok, status = self.check_adapter()
        if not is_ok:
            display.text(f"No Adapter\nStatus: {status}\nUse Toggle Power")
            self.wait_for_back()
            return

        display.text("Scanning BLE...\n\nPress BACK to stop")
        proc = subprocess.Popen(
            ["sudo", "hcitool", "lescan"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        found_devices = set()

        def read_output(pipe):
            try:
                for line in iter(pipe.readline, ""):
                    if not line:
                        break
                    line = line.strip()
                    if ":" in line and "LE Scan" not in line:
                        Log.debug(f"BLE line: {line}")
                        found_devices.add(line)
            except Exception as e:
                Log.error(f"Error reading BLE scan output: {e}")

        t = threading.Thread(target=read_output, args=(proc.stdout,), daemon=True)
        t.start()

        while not self.is_stopped():
            key = self.wait_for_input(process=proc)
            if key == "back":
                Log.info("Stopping BLE scan (user pressed BACK)")
                break
            if proc.poll() is not None:
                Log.info("BLE scan process ended")
                break

        if proc.poll() is None:
            proc.terminate()
            subprocess.run(["sudo", "killall", "-9", "hcitool"], capture_output=True)

        if not found_devices:
            Log.info("No BLE devices found")
            display.text("No BLE devices.\n\nPress BACK")
            self.wait_for_back()
        else:
            dev_list = sorted(list(found_devices))
            Log.info(f"BLE devices found: {len(dev_list)}")
            res_menu = Menu(dev_list)
            while not self.is_stopped():
                display.draw(res_menu.generate())
                key = self.wait_for_input()
                if key == "up":
                    res_menu.previous()
                elif key == "down":
                    res_menu.next()
                elif key == "back":
                    break

    def scan_services(self):
        Log.info("Starting service scan")
        if not self.nearby:
            display.text("Scan Classic first!\n\nPress BACK")
            self.wait_for_back()
            return

        dev_list = [f"{n[:15]}" for a, n in self.nearby]
        sm = Menu(dev_list)
        while not self.is_stopped():
            display.draw(sm.generate())
            key = self.wait_for_input()
            if key == "up":
                sm.previous()
            elif key == "down":
                sm.next()
            elif key == "back":
                return
            elif key == "select":
                idx = sm.get_index()
                break

        addr, name = self.nearby[idx]
        Log.info(f"Scanning services on {name} ({addr})")
        display.text(f"Scanning:\n{name[:10]}\nWait...")
        try:
            import bluetooth
            services = bluetooth.find_service(address=addr)
            Log.debug(f"Services result: {services}")
        except Exception as e:
            Log.error(f"Service discovery error: {e}")
            display.text(f"Error: {e}")
            self.wait_for_back()
            return

        if not services:
            Log.info("No services found")
            display.text("No services.\n\nPress BACK")
            self.wait_for_back()
            return

        srv_list = [f"{s.get('name','')[:10]} {s.get('port','')}" for s in services]
        res_menu = Menu(srv_list)
        while not self.is_stopped():
            display.draw(res_menu.generate())
            key = self.wait_for_input()
            if key == "up":
                res_menu.previous()
            elif key == "down":
                res_menu.next()
            elif key == "back":
                break

    def pair_device(self):
        Log.info("Pairing requested")
        if not self.nearby:
            display.text("Scan Classic first!\n\nPress BACK")
            self.wait_for_back()
            return

        dev_list = [f"{n[:15]}" for a, n in self.nearby]
        sm = Menu(dev_list)
        while not self.is_stopped():
            display.draw(sm.generate())
            key = self.wait_for_input()
            if key == "up":
                sm.previous()
            elif key == "down":
                sm.next()
            elif key == "back":
                return
            elif key == "select":
                idx = sm.get_index()
                break

        addr, name = self.nearby[idx]
        display.text(f"Pairing:\n{name[:15]}")

        Log.debug(f"Pairing to {addr}")
        cmds = [
            ["sudo", "bluetoothctl", "remove", addr],
            ["sudo", "bluetoothctl", "agent", "on"],
            ["sudo", "bluetoothctl", "trust", addr],
            ["sudo", "bluetoothctl", "pair", addr],
            ["sudo", "bluetoothctl", "connect", addr],
        ]
        for cmd in cmds:
            Log.debug(f"Running: {' '.join(cmd)}")
            res = subprocess.run(cmd, capture_output=True, text=True)
            Log.debug(f"Exit {res.returncode}, stdout={res.stdout.strip()}, stderr={res.stderr.strip()}")

        display.text("Pairing sent.\nConnecting...")
        time.sleep(2)
        display.text("Done.\nCheck target.\nPress BACK")
        self.wait_for_back()

    def connect_device(self):
        Log.info("Connecting to selected device")
        addr, name = self.choose_device(prompt="Select device to connect")
        if not addr:
            return

        display.text(f"Connecting to:\n{name[:12]}")
        
        # Enforce agent, trust and connect sequence
        subprocess.run(["sudo", "bluetoothctl", "agent", "on"], capture_output=True)
        subprocess.run(["sudo", "bluetoothctl", "default-agent"], capture_output=True)
        
        res = subprocess.run(["sudo", "bluetoothctl", "connect", addr], capture_output=True, text=True)
        Log.debug(f"connect return {res.returncode}, stdout={res.stdout.strip()}, stderr={res.stderr.strip()}")

        if res.returncode == 0:
            display.text("Connected!\n\nPress BACK")
        else:
            display.text("Connect failed.\nCheck logs.\nPress BACK")
        self.wait_for_back()

    def disconnect_device(self):
        Log.info("Disconnecting selected device")
        addr, name = self.choose_device(prompt="Select device to disconnect")
        if not addr:
            return

        display.text(f"Disconnecting:\n{name[:12]}")
        res = subprocess.run(["sudo", "bluetoothctl", "disconnect", addr], capture_output=True, text=True)
        Log.debug(f"disconnect return {res.returncode}, stdout={res.stdout.strip()}, stderr={res.stderr.strip()}")

        if res.returncode == 0:
            display.text("Disconnected!\n\nPress BACK")
        else:
            display.text("Disconnect failed.\nCheck logs.\nPress BACK")
        self.wait_for_back()

    def kick_device(self):
        Log.info("Kicking selected device")
        addr, name = self.choose_device(prompt="Select device to kick")
        if not addr:
            return

        display.text(f"Kicking:\n{name[:12]}")
        # Try disconnecting a few times to force a drop
        for i in range(3):
            subprocess.run(["sudo", "bluetoothctl", "disconnect", addr], capture_output=True)
            time.sleep(0.3)
        subprocess.run(["sudo", "bluetoothctl", "remove", addr], capture_output=True)

        display.text("Kicked!\n\nPress BACK")
        self.wait_for_back()

    def device_info(self):
        Log.info("Device info requested")
        addr, name = self.choose_device(prompt="Select device to inspect")
        if not addr:
            return

        display.text(f"Info for:\n{name[:12]}\nWait...")
        res = subprocess.run(["sudo", "bluetoothctl", "info", addr], capture_output=True, text=True)
        Log.debug(f"info return {res.returncode}, stdout={res.stdout.strip()}, stderr={res.stderr.strip()}")
        
        info_lines = [line.strip() for line in res.stdout.split('\n') if line.strip() and not line.startswith("Device")]
        
        if not info_lines:
            display.text("No details found.\nTry to pair first.\nPress BACK")
            self.wait_for_back()
            return

        info_menu = Menu([l[:15] for l in info_lines])
        while not self.is_stopped():
            display.draw(info_menu.generate())
            key = self.wait_for_input()
            if key == "up":
                info_menu.previous()
            elif key == "down":
                info_menu.next()
            elif key == "back":
                break

    def trust_device(self):
        Log.info("Trusting selected device")
        addr, name = self.choose_device(prompt="Select device to trust")
        if not addr:
            return

        display.text(f"Trusting:\n{name[:12]}")
        res = subprocess.run(["sudo", "bluetoothctl", "trust", addr], capture_output=True, text=True)
        Log.debug(f"trust return {res.returncode}, stdout={res.stdout.strip()}, stderr={res.stderr.strip()}")

        if res.returncode == 0:
            display.text("Trusted!\n\nPress BACK")
        else:
            display.text("Trust failed.\nCheck logs.\nPress BACK")
        self.wait_for_back()

    def untrust_device(self):
        Log.info("Untrusting selected device")
        addr, name = self.choose_device(prompt="Select device to untrust")
        if not addr:
            return

        display.text(f"Untrusting:\n{name[:12]}")
        res = subprocess.run(["sudo", "bluetoothctl", "untrust", addr], capture_output=True, text=True)
        Log.debug(f"untrust return {res.returncode}, stdout={res.stdout.strip()}, stderr={res.stderr.strip()}")

        if res.returncode == 0:
            display.text("Untrusted!\n\nPress BACK")
        else:
            display.text("Untrust failed.\nCheck logs.\nPress BACK")
        self.wait_for_back()

    def flood_ping(self):
        Log.info("l2ping flood requested")
        addr, name = self.choose_device(prompt="Select device to flood")
        if not addr:
            return

        display.text(f"Flooding (l2ping):\n{name[:10]}\n\nPress BACK to stop")
        
        # Envolver l2ping en un bucle while para que resucite automáticamente 
        # si el dispositivo objetivo desactiva brevemente su bluetooth o rompe la conexión en respuesta al flood
        flood_script = f"while true; do sudo l2ping -f {addr}; sleep 0.1; done"
        proc = subprocess.Popen(
            ["bash", "-c", flood_script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            preexec_fn=os.setsid # Necesario para matar el bg process tree luego
        )

        while not self.is_stopped():
            key = self.wait_for_input(process=None) # Ya no confiamos en que el proceso muera
            if key == "back":
                Log.info("Stopping flood (user pressed BACK)")
                break

        # Matar todo el árbol de bash y l2ping
        try:
            os.killpg(os.getpgid(proc.pid), 9)
        except Exception:
            pass
        subprocess.run(["sudo", "killall", "-9", "l2ping"], capture_output=True)

        display.text("Flood stopped.\n\nPress BACK")
        self.wait_for_back()

    def play_sound(self):
        Log.info("Play sound requested")
        public_dir = self.get_public_dir()
        music_dir = os.path.join(public_dir, "music")

        files = [f for f in os.listdir(music_dir) if os.path.isfile(os.path.join(music_dir, f))]
        if not files:
            display.text("No sound files in:\npublic/music/\n\nPress BACK")
            self.wait_for_back()
            return

        fm = Menu([f[:15] for f in files])
        while not self.is_stopped():
            display.draw(fm.generate())
            key = self.wait_for_input()
            if key == "up":
                fm.previous()
            elif key == "down":
                fm.next()
            elif key == "back":
                return
            elif key == "select":
                file_idx = fm.get_index()
                break

        sound_file = os.path.join(music_dir, files[file_idx])
        display.text(f"Playing:\n{files[file_idx][:12]}")
        player = shutil.which("aplay") or shutil.which("paplay")
        if not player:
            display.text("No audio player\n(aplay/paplay)\n\nPress BACK")
            self.wait_for_back()
            return
        proc = subprocess.Popen([player, sound_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        while not self.is_stopped():
            key = self.wait_for_input(process=proc)
            if key == "back":
                Log.info("Stopping playback (BACK)")
                break
            if proc.poll() is not None:
                break

        if proc.poll() is None:
            proc.terminate()

        display.text("Done.\nPress BACK")
        self.wait_for_back()

    def send_file(self):
        Log.info("Send file invoked")
        if not self.nearby:
            display.text("Scan Classic first!\n\nPress BACK")
            self.wait_for_back()
            return

        public_dir = self.get_public_dir()
        
        all_files = []
        for category in ["music", "images", "files"]:
            cat_dir = os.path.join(public_dir, category)
            for f in os.listdir(cat_dir):
                if os.path.isfile(os.path.join(cat_dir, f)):
                    all_files.append((category, f))

        Log.debug(f"Files available to send: {all_files}")
        if not all_files:
            display.text("No files found in:\npublic/...\n\nPress BACK")
            self.wait_for_back()
            return

        # Prepare strings for menu
        menu_items = [f"{cat[:3]}/{fname}"[:15] for cat, fname in all_files]
        fm = Menu(menu_items)
        while not self.is_stopped():
            display.draw(fm.generate())
            key = self.wait_for_input()
            if key == "up":
                fm.previous()
            elif key == "down":
                fm.next()
            elif key == "back":
                return
            elif key == "select":
                file_idx = fm.get_index()
                break

        selected_cat, selected_fname = all_files[file_idx]
        file_path = os.path.join(public_dir, selected_cat, selected_fname)
        Log.info(f"Sending file: {selected_fname} from {selected_cat}")

        dev_list = [f"{n[:15]}" for a, n in self.nearby]
        sm = Menu(dev_list)
        while not self.is_stopped():
            display.draw(sm.generate())
            key = self.wait_for_input()
            if key == "up":
                sm.previous()
            elif key == "down":
                sm.next()
            elif key == "back":
                return
            elif key == "select":
                idx = sm.get_index()
                break

        addr, name = self.nearby[idx]
        display.text(f"Sending file:\n{selected_file[:10]}\nto {name[:10]}")
        Log.info(f"Sending {selected_file} to {addr}")

        res = subprocess.run(["bt-obex", "-p", addr, file_path], capture_output=True, text=True)
        Log.debug(f"bt-obex return {res.returncode}, stdout={res.stdout.strip()}, stderr={res.stderr.strip()}")

        if res.returncode == 0:
            display.text("File Sent!\n\nPress BACK")
        else:
            Log.error(f"Send failed: {res.stderr}")
            display.text("Send Failed.\nCheck logs.\nPress BACK")

        self.wait_for_back()

    def discoverable_mode(self):
        Log.info("Enabling discoverable mode")
        display.text("Discoverable ON...")
        subprocess.run(["sudo", "bluetoothctl", "agent", "on"], capture_output=True)
        subprocess.run(["sudo", "bluetoothctl", "discoverable", "on"], capture_output=True)
        subprocess.run(["sudo", "bluetoothctl", "pairable", "on"], capture_output=True)
        display.text("Device is visible!\n\nPress BACK to stop")
        self.wait_for_back()
        subprocess.run(["sudo", "bluetoothctl", "discoverable", "off"], capture_output=True)

    def sniff_packets(self):
        Log.info("Starting packet sniffing")
        display.text("Sniffing packets\nPress BACK to stop")
        filename = f'bt_{datetime.now().strftime("%d%m%M")}.pcap'
        out_path = os.path.join(self.get_state_dir(), filename)
        Log.debug(f"Saving pcap to {out_path}")

        proc = subprocess.Popen(
            ["sudo", "tshark", "-i", "bluetooth0", "-w", out_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        while not self.is_stopped():
            key = self.wait_for_input(process=proc)
            if key == "back":
                Log.info("Stopping packet capture (BACK)")
                break
            if proc.poll() is not None:
                Log.info("tshark process ended")
                break

        if proc.poll() is None:
            proc.terminate()
            subprocess.run(["sudo", "killall", "tshark"], capture_output=True)

        display.text(f"Saved PCAP:\n{filename}\n\nPress BACK")
        self.wait_for_back()

    def spoof_mac(self):
        Log.info("Spoofing MAC")
        display.text("Spoofing MAC...\nRandomizing...")
        res = subprocess.run(["sudo", "spooftooph", "-i", self.interface, "-R"], capture_output=True)
        Log.debug(f"spooftooph return {res.returncode}, stdout={res.stdout.strip()}, stderr={res.stderr.strip()}")

        if res.returncode == 0:
            mac = "Unknown"
            hciconfig_res = subprocess.run(["hciconfig", self.interface], capture_output=True, text=True)
            for line in hciconfig_res.stdout.split("\n"):
                if "BD Address" in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        mac = parts[2]
                    break
            display.text(f"Spoofed!\nMAC: {mac}\n\nPress BACK")
        else:
            display.text("Failed.\nIs spooftooph\ninstalled?\nPress BACK")
        self.wait_for_back()

    def toggle_power(self):
        Log.info("Toggling Bluetooth power")
        res = subprocess.run(["rfkill", "list", "bluetooth"], capture_output=True, text=True)
        Log.debug(f"rfkill list output:\n{res.stdout}")
        if "Soft blocked: yes" in res.stdout:
            display.text("Enabling BT...")
            subprocess.run(["sudo", "rfkill", "unblock", "bluetooth"])
            subprocess.run(["sudo", "hciconfig", "hci0", "up"])
        else:
            display.text("Disabling BT...")
            subprocess.run(["sudo", "rfkill", "block", "bluetooth"])
            subprocess.run(["sudo", "hciconfig", "hci0", "down"])
        display.text("Press BACK")
        self.wait_for_back()
