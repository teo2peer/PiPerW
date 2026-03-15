from PiPerW.interfaces.app_interface import AppInterface
from PiPerW.driver.pheripherals import Pheripherals
from PiPerW.driver.display import Display
from PiPerW.helpers import Log
from PiPerW.utils.Menu import Menu
import subprocess
import time
import os

display = Display()

class App(AppInterface):
    name = "NFC Manager"
    version = "1.0"

    def __init__(self):
        super().__init__()
        self.menu = None

    def check_libnfc(self):
        """Check if libnfc is installed."""
        result = subprocess.run(["which", "nfc-poll"], capture_output=True)
        return result.returncode == 0

    def run(self):
        if not self.check_libnfc():
            display.text("libnfc missing!\n\nRun:\nsudo apt install libnfc-bin")
            self.wait_for_input()
            return

        options = ["Read Tag (Poll)", "Emulate Tag", "Exit"]
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
        if action == "Read Tag (Poll)":
            self.read_tag()
        elif action == "Emulate Tag":
            self.emulate_tag()

    def read_tag(self):
        Log.info("Starting NFC Polling")
        display.text("Polling for NFC...\nApproach a tag.\n\nPress BACK to stop")

        # Running nfc-poll in stdbuf to prevent output buffering, allowing real-time parsing
        proc = subprocess.Popen(
            ["nfc-poll"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        output_log = ""
        while not self.is_stopped():
            # Check if process ended by itself (tag found or timeout)
            if proc.poll() is not None:
                output_log = proc.stdout.read()
                break

            key = self.wait_for_input(process=proc)
            if key == "back":
                Log.info("NFC Poll interrupted by user")
                proc.terminate()
                break
            time.sleep(0.1)

        # Basic parsing of UID
        uid = "Unknown"
        if output_log:
            for line in output_log.split('\n'):
                if "UID" in line:
                    uid = line.split(":")[-1].strip()
                    break

            if uid != "Unknown":
                self.save_state(f"nfc_capture_{int(time.time())}.txt", output_log)
                display.text(f"Tag Found!\nUID: {uid}\n\nPress KEY to exit")
            else:
                display.text("No valid tag found or\nread interrupted.\n\nPress KEY to exit")
        else:
            display.text("Scan cancelled.\n\nPress KEY to exit")

        self.wait_for_input()

    def emulate_tag(self):
        Log.info("Starting NFC Emulation")
        display.text("Emulating NFC Tag...\nWaiting for reader.\n\nPress BACK to stop")

        proc = subprocess.Popen(
            ["nfc-emulate-forum-tag4"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        self.wait_for_input(process=proc)

        if proc.poll() is None:
            proc.terminate()
            display.text("Emulation stopped.")
        else:
            display.text("Emulation completed.")

        time.sleep(1)
