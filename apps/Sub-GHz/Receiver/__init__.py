from PiPerW.apps.app_interface import AppInterface
from PiPerW.driver.pheripherals import Pheripherals
from PiPerW.driver.display import Display
from PiPerW.helpers import Log, select_number
from PiPerW.utils.Menu import Menu
from PiPerW.driver.SubGHz.CC1101 import CC1101
from PiPerW.driver.SubGHz.CC1101.reg import *
import time
from PIL import Image, ImageDraw

display = Display()
pheripherals = Pheripherals()

class App(AppInterface):
    def __init__(self):
        self.name = "Advanced Sub-GHz RX"
        self.version = "1.5"
        self.description = "Professional Sub-GHz Receiver and Decoder"
        self.author = "Copilot"
        super().__init__(self.name, self.version)
        self.cc1101 = None
        self.frequency = 433.92

    def run(self):
        display.text("Initializing CC1101 RX...")
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
            options = ["Set RX Frequency", "Start Listening", "Exit"]
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
            
        elif option == "Set RX Frequency":
            display.text(f"Current RX Freq:\n{self.frequency} MHz")
            time.sleep(1)
            self.frequency = select_number(display, pheripherals, start_number=self.frequency, title="Set RX Frequency", decimals=2, min=300, max=928)
            Log.info(f"RX Frequency set to: {self.frequency}")
            
        elif option == "Start Listening":
            self.listen_mode()

    def listen_mode(self):
        self.cc1101.set_frequency(self.frequency)
        self.cc1101.strobe(CC1101_STROBE_SRX)
        
        last_timestamp = pheripherals.get_key()[1]
        
        while not self.is_stopped():
            rx_data, size = self.cc1101.read_fifo()
            
            # create ui for listening
            img = Image.new('1', (display.width, display.height), 0)
            draw = ImageDraw.Draw(img)
            
            draw.text((2, 2), f"Listening: {self.frequency}MHz", font=display.font, fill=255)
            draw.line((0, 15, display.width, 15), fill=255)
            
            if size > 0:
                hex_data = " ".join([f"{b:02X}" for b in rx_data])
                draw.text((2, 20), f"Size: {size} bytes", font=display.font, fill=255)
                
                # Split hex_data into lines if too long
                y_offset = 35
                for i in range(0, len(hex_data), 20):
                    draw.text((2, y_offset), hex_data[i:i+20], font=display.font, fill=255)
                    y_offset += 15
                
                display.draw(img)
                time.sleep(2) # Show packet for 2 seconds
                
                self.cc1101.strobe(CC1101_STROBE_SFRX) # Flush RX FIFO
                self.cc1101.strobe(CC1101_STROBE_SRX)  # Return to RX
            else:
                draw.text((display.width // 2 - 20, display.height // 2), "Waiting...", font=display.font, fill=255)
                display.draw(img)
                
            time.sleep(0.1)
            
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
