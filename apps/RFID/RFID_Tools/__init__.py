from PiPerW.interfaces.app_interface import AppInterface
from PiPerW.driver.pheripherals import Pheripherals
from PiPerW.driver.display import Display
from PiPerW.helpers import Log
from PiPerW.utils.Menu import Menu
import subprocess
import time

display = Display()

class App(AppInterface):
    name = "RFID 125kHz"
    version = "1.0"

    def __init__(self):
        super().__init__(self.name, self.version)
        self.menu = None

    def run(self):
        options = ["Read Card", "Clone Card", "Exit"]
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
                Log.info("RFID Tools: back requested at root menu - ignoring")
                display.text("App root menu:\n\nHold EXIT 3s\nto force quit")
                time.sleep(1.5)

    def execute_action(self, action):
        if action == "Read Card":
            self.read_rfid()
        elif action == "Clone Card":
            self.clone_rfid()

    def read_rfid(self):
        Log.info("Starting RFID 125kHz Polling")
        display.text("Reading RFID...\nApproach a card.\n\nPress BACK to stop")

        # Mocking proxmark3 or custom SPI python scripts
        proc = subprocess.Popen(
            ["sleep", "10"], # Placeholder
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        while not self.is_stopped():
            if proc.poll() is not None:
                Log.info("RFID Poll completed passively")
                break
                
            key = self.wait_for_input(process=proc)
            if key == "back":
                Log.info("RFID Poll interrupted by user")
                proc.terminate()
                break

        display.text("Read finished.\n\nPress ANY key")
        self.wait_for_input()

    def clone_rfid(self):
        display.text("Place target card\nand press SELECT\n\nBACK to cancel")
        
        while not self.is_stopped():
            key = self.wait_for_input()
            if key == "select":
                display.text("Cloning...\nPlease wait...")
                time.sleep(2)
                display.text("Done!\n\nPress ANY key")
                self.wait_for_input()
                break
            elif key == "back":
                break
