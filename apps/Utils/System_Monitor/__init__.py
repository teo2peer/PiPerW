from PiPerW.interfaces.app_interface import AppInterface
from PiPerW.driver.pheripherals import Pheripherals
from PiPerW.driver.display import Display
from PiPerW.helpers import Log
from PIL import Image, ImageDraw
import time
import os

try:
    import psutil
except ImportError:
    psutil = None

display = Display()
pheripherals = Pheripherals()

class App(AppInterface):
    def __init__(self):
        super().__init__()

    def run(self):
        if not psutil:
            display.text("psutil required.\nInstall via pip.")
            time.sleep(2)
            return

        last_timestamp = pheripherals.get_key()[1]

        while not self.is_stopped():
            img = Image.new('1', (display.width, display.height), 0)
            draw = ImageDraw.Draw(img)

            # Get system metrics
            cpu_percent = psutil.cpu_percent()
            mem = psutil.virtual_memory()
            mem_percent = mem.percent
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Try to get temperature (Linux/RPi specific)
            try:
                temp_output = os.popen("cat /sys/class/thermal/thermal_zone0/temp").read().strip()
                if temp_output:
                    temp_c = float(temp_output) / 1000.0
                else:
                    temp_c = 0.0
            except:
                temp_c = 0.0

            # Draw Header
            draw.rectangle([0, 0, display.width, 14], fill=255)
            draw.text((2, 1), "SYS MONITOR", font=display.font, fill=0)
            if temp_c > 0:
                draw.text((display.width - 40, 1), f"{temp_c:.1f}C", font=display.font, fill=0)

            # Draw Bars
            y_offset = 18
            self.draw_progress_bar(draw, "CPU", cpu_percent, y_offset)
            y_offset += 15
            self.draw_progress_bar(draw, "RAM", mem_percent, y_offset)
            y_offset += 15
            self.draw_progress_bar(draw, "DSK", disk_percent, y_offset)

            display.draw(img)

            # Check input to exist
            key, ts = pheripherals.get_key()
            if ts != last_timestamp:
                break
            
            time.sleep(1)

    def draw_progress_bar(self, draw, label, percent, y):
        draw.text((2, y), label, font=display.font, fill=255)
        
        bar_x = 30
        bar_width = display.width - bar_x - 5
        bar_height = 10
        
        # Background outline
        draw.rectangle([bar_x, y, bar_x + bar_width, y + bar_height], outline=255)
        
        # Fill
        fill_width = int(bar_width * (percent / 100))
        if fill_width > 0:
            draw.rectangle([bar_x, y, bar_x + fill_width, y + bar_height], fill=255)
        
        # Value text inside or next to it
        val_str = f"{int(percent)}%"
        draw.text((bar_x + 2, y - 1), val_str, font=display.font, fill=0 if percent > 15 else 255)