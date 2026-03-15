from PiPerW.interfaces.app_interface import AppInterface
from PiPerW.driver.pheripherals import Pheripherals
from PiPerW.driver.display import Display
from PiPerW.helpers import Log, select_number
from PiPerW.utils.Menu import Menu
from PiPerW.driver.SubGHz.CC1101 import CC1101
from PiPerW.driver.SubGHz.CC1101.reg import *
import time

display = Display()
pheripherals = Pheripherals()

class App(AppInterface):
    def __init__(self):
        self.name = "Advanced Sub-GHz TX"
        self.version = "1.5"
        self.description = "Professional Sub-GHz Transmitter with UI"
        self.author = "Copilot"
        super().__init__(self.name, self.version)
        self.cc1101 = None
        self.frequency = 433.92

    def run(self):
        display.text("Initializing CC1101...")
        time.sleep(0.5)
        try:
            self.cc1101 = CC1101()
            self.cc1101.reset()
        except Exception as e:
            Log.error(f"Failed to init CC1101: {e}")
            display.text("CC1101 not found!")
            time.sleep(2)
            return

        while not self.is_stopped():
            options = ["Select Frequency", "Send Test Data", "Send SOS Carrier", "Exit"]
            menu = Menu(options)
            
            while True:
                menu.show()
                key = pheripherals.await_key()
                if key == "up":
                    menu.previous()
                elif key == "down":
                    menu.next()
                elif key == "select":
                    selected = options[menu.index]
                    self.execute_option(selected)
                    break
                elif key == "back" or key == "exit":
                    self.cleanup()
                    return

    def execute_option(self, option):
        if option == "Exit":
            self.cleanup()
            return
            
        elif option == "Select Frequency":
            display.text(f"Current Freq:\n{self.frequency} MHz")
            time.sleep(1)
            self.frequency = select_number(display, pheripherals, start_number=self.frequency, title="Set Frequency", decimals=2, min=300, max=928)
            Log.info(f"Frequency set to: {self.frequency}")
            
        elif option == "Send Test Data":
            self.transmit_mode([0xDE, 0xAD, 0xBE, 0xEF, 0x13, 0x37], "Sending Test Data")
            
        elif option == "Send SOS Carrier":
            self.transmit_mode([0x53, 0x4F, 0x53, 0x53, 0x4F, 0x53], "Sending SOS")

    def transmit_mode(self, payload, title):
        self.cc1101.set_frequency(self.frequency)
        self.cc1101.set_pa_table([0xC0])  # Max power
        
        display.text(f"{title}\nFreq: {self.frequency} MHz\n\nPress any key to stop.")
        
        last_timestamp = pheripherals.get_key()[1]
        
        while not self.is_stopped():
            self.cc1101.strobe(CC1101_STROBE_SIDLE)
            self.cc1101.strobe(CC1101_STROBE_SFTX)  # Flush TX FIFO
            self.cc1101.write_fifo(payload)
            self.cc1101.strobe(CC1101_STROBE_STX)   # Transmit
            
            time.sleep(0.3)  # TX interval
            
            key, ts = pheripherals.get_key()
            if ts != last_timestamp:
                break
                
        self.cc1101.strobe(CC1101_STROBE_SIDLE)

    def cleanup(self):
        try:
            if self.cc1101:
                self.cc1101.shutdown()
        except Exception:
            pass
