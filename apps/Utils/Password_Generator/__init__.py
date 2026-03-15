from PiPerW.interfaces.app_interface import AppInterface
from PiPerW.driver.pheripherals import Pheripherals
from PiPerW.driver.display import Display
from PiPerW.utils.Menu import Menu
from PIL import Image, ImageDraw
import time
import random
import string

display = Display()
pheripherals = Pheripherals()

class App(AppInterface):
    def __init__(self):
        super().__init__()

    def run(self):
        while not self.is_stopped():
            options = ["Generate 8 chars", "Generate 12 chars", "Generate 16 chars", "Generate 32 chars", "Exit"]
            menu = Menu(options)
            
            while True:
                menu.show()
                key = pheripherals.await_key()
                
                if key == "up":
                    menu.previous()
                elif key == "down":
                    menu.next()
                elif key == "select":
                    sel = options[menu.index]
                    if sel == "Exit":
                        return
                    else:
                        length = int(sel.split(" ")[1])
                        self.show_password(length)
                        break
                elif key in ["back", "exit"]:
                    return

    def show_password(self, length):
        # Generate complex password
        chars = string.ascii_letters + string.digits + "!@#$%^&*()_+"
        pwd = "".join(random.choice(chars) for _ in range(length))
        
        last_timestamp = pheripherals.get_key()[1]
        
        while not self.is_stopped():
            img = Image.new('1', (display.width, display.height), 0)
            draw = ImageDraw.Draw(img)
            
            draw.rectangle([0, 0, display.width, 14], fill=255)
            draw.text((2, 1), f"Password ({length})", font=display.font, fill=0)
            
            # Text wrapping for long passwords
            y_pos = 25
            for i in range(0, len(pwd), 16):
                draw.text((5, y_pos), pwd[i:i+16], font=display.font, fill=255)
                y_pos += 15
                
            draw.text((2, display.height - 12), "[Any key to Return]", font=display.font, fill=255)
            
            display.draw(img)
            time.sleep(0.1)
            
            key, ts = pheripherals.get_key()
            if ts != last_timestamp:
                break