from PiPerW.interfaces.app_interface import AppInterface
from PiPerW.driver.pheripherals import Pheripherals
from PiPerW.driver.display import Display
from PiPerW.helpers import Log
from PiPerW.driver.SubGHz.CC1101 import CC1101
from PiPerW.driver.SubGHz.CC1101.reg import *
import time
from PIL import Image, ImageDraw

display = Display()
pheripherals = Pheripherals()

class App(AppInterface):
    def __init__(self):
        self.name = "Advanced Sub-GHz Scanner"
        self.version = "1.5"
        self.description = "Professional Sub-GHz scanner and spectrogram"
        self.author = "Copilot"
        super().__init__()
        self.cc1101 = None

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

        freqs = [315.0, 433.92, 868.0, 915.0]
        
        last_timestamp = pheripherals.get_key()[1]
        
        while not self.is_stopped():
            # Create a new image for the bar chart
            img = Image.new('1', (display.width, display.height), 0)
            draw = ImageDraw.Draw(img)
            
            draw.text((2, 2), "Sub-GHz Spectrum", font=display.font, fill=255)
            
            # Divide width by number of freqs
            bar_width = display.width // len(freqs)
            max_height = display.height - 20
            
            for i, f in enumerate(freqs):
                self.cc1101.set_frequency(f)
                self.cc1101.strobe(CC1101_STROBE_SRX)
                time.sleep(0.02) # Give it a bit to settle
                
                rssi_dbm = self.cc1101.get_rssi()
                if rssi_dbm is not None:
                    # Map range -120 dBm (weak) to -30 dBm (strong) to height percentage
                    normalized = max(0, min(100, (rssi_dbm + 120) * (100 / 90)))
                    bar_h = int((normalized / 100) * max_height)
                else:
                    bar_h = 0
                    rssi_dbm = -120
                
                x0 = i * bar_width + 5
                y0 = display.height - bar_h - 10
                x1 = x0 + bar_width - 10
                y1 = display.height - 10
                
                # Draw the bar
                draw.rectangle([x0, y0, x1, y1], outline=255, fill=255)
                # Draw frequency label and dBm
                draw.text((x0, display.height - 10), f"{int(f)}", font=display.font, fill=255)
                draw.text((x0, y0 - 10), f"{int(rssi_dbm)}", font=display.font, fill=255)
            
            display.draw(img)
            
            # Check for exit if key was updated
            key, ts = pheripherals.get_key()
            if ts != last_timestamp:
                break

        # Cleanup
        try:
            self.cc1101.shutdown()
        except Exception:
            pass
