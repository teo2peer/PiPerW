from PiPerW.apps.app_interface import AppInterface
from PiPerW.driver.pheripherals import Pheripherals
from PiPerW.driver.display import Display
from PiPerW.helpers import Log, select_number
from PiPerW.utils.Menu import Menu
from PiPerW.driver.SubGHz.CC1101 import CC1101
from PiPerW.driver.SubGHz.CC1101.reg import *
import os
import json
import time
from PIL import Image, ImageDraw

display = Display()
pheripherals = Pheripherals()

class App(AppInterface):
    def __init__(self):
        self.name = "Sub-GHz Suite"
        self.version = "2.0"
        self.description = "Professional All-In-One Sub-GHz Tool"
        self.author = "Teo2Peer"
        super().__init__(self.name, self.version)
        
        self.cc1101 = None
        self.frequency = 433.92
        self.modulation = "ASK" # ASK (OOK) or FSK
        
        # Ranges for the Frequency Analyzer (hopping)
        self.scan_sweep = [
            300.0, 315.0, 318.0, 390.0, 433.42, 433.92, 434.42, 438.90, 868.35, 915.0
        ]
        
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.root_path = os.path.dirname(os.path.dirname(os.path.dirname(self.path)))
        self.save_dir = os.path.join(self.root_path, "public", "SubGHz")
        if not os.path.exists(self.save_dir):
            try:
                os.makedirs(self.save_dir)
            except Exception:
                pass
        
    def run(self):
        self.init_radio()
        
        while not self.is_stopped():
            options = ["Read", "Saved", "Frequency Analyzer", "Send Data", "Radio Settings", "Exit"]
            menu = Menu(options)
            
            while True:
                # Top bar for the main menu is tricky with just a list, 
                # but we show the main menu normally.
                menu.show()
                key = pheripherals.await_key()
                
                if key == "up":
                    menu.previous()
                elif key == "down":
                    menu.next()
                elif key == "select":
                    selected = options[menu.index]
                    self.execute_main(selected)
                    # Re-init radio config after returning in case it was modified
                    self.apply_radio_config()
                    break
                elif key == "back" or key == "exit":
                    self.cleanup()
                    return

    def init_radio(self):
        display.text("Loading Sub-GHz\nRadio module...")
        time.sleep(0.5)
        try:
            self.cc1101 = CC1101()
            self.cc1101.reset()
            self.apply_radio_config()
        except Exception as e:
            Log.error(f"Failed to init CC1101: {e}")
            display.text("CC1101 ERROR!\nCheck HW connection.")
            time.sleep(2)
            # Not returning here allows viewing the UI empty if testing without antennas

    def apply_radio_config(self):
        if not self.cc1101: return
        self.cc1101.strobe(CC1101_STROBE_SIDLE)
        self.cc1101.set_frequency(self.frequency)
        
        if self.modulation == "ASK":
            self.cc1101.write_reg(CC1101_MDMCFG2, 0x30)  # MDMCFG2: ASK/OOK, no manchester
            self.cc1101.write_reg(CC1101_FREND0, 0x11)   # Needed for ASK
            self.cc1101.set_pa_table([0x00, 0xC0])       # PA structure ASK
        else: # FSK
            self.cc1101.write_reg(CC1101_MDMCFG2, 0x13)  # GFSK
            self.cc1101.write_reg(CC1101_FREND0, 0x10)
            self.cc1101.set_pa_table([0xC0])             # PA structure FSK

    def execute_main(self, option):
        if option == "Exit":
            self.cleanup()
            return
        elif option == "Radio Settings":
            self.settings_menu()
        elif option == "Read":
            self.read_mode()
        elif option == "Saved":
            self.saved_mode()
        elif option == "Frequency Analyzer":
            self.frequency_analyzer()
        elif option == "Send Data":
            self.send_mode()

    def draw_header(self, draw, title):
        # Inverted top bar
        draw.rectangle([0, 0, display.width, 14], fill=255)
        draw.text((2, 1), title, font=display.font, fill=0)

    # ----------------------------------------------------
    # READ MODE (Capture)
    # ----------------------------------------------------
    def read_mode(self):
        if self.cc1101:
            self.cc1101.strobe(CC1101_STROBE_SRX)
            
        last_timestamp = pheripherals.get_key()[1]
        anim_frame = 0
        is_recording = False
        
        last_packet = ""
        packet_time = 0

        while not self.is_stopped():
            key, ts = pheripherals.get_key()
            if ts != last_timestamp:
                last_timestamp = ts
                if key == "select":
                    is_recording = not is_recording
                elif key in ["back", "exit"]:
                    break

            img = Image.new('1', (display.width, display.height), 0)
            draw = ImageDraw.Draw(img)
            
            base_header = f"Read  {self.frequency}  {self.modulation}"
            if is_recording:
                # Blink REC every second
                if int(time.time() * 2) % 2 == 0:
                    title = base_header + " [REC]"
                else:
                    title = base_header + "      "
            else:
                title = base_header

            self.draw_header(draw, title)
            
            # Read FIFO
            if self.cc1101:
                rx_data, size = self.cc1101.read_fifo()
                if size > 0:
                    hex_str = " ".join([f"{b:02X}" for b in rx_data])
                    last_packet = f"Key: {hex_str[:20]}\nLen: {size} bytes"
                    packet_time = time.time()
                    
                    if is_recording:
                        file_name = f"sig_{int(time.time())}.json"
                        file_path = os.path.join(self.save_dir, file_name)
                        try:
                            with open(file_path, "w") as f:
                                json.dump({
                                    "frequency": self.frequency,
                                    "modulation": self.modulation,
                                    "payload": hex_str
                                }, f)
                            last_packet += "\n[SAVED to public/SubGHz]"
                        except Exception as e:
                            Log.error(f"Save failed: {e}")
                            
                    self.cc1101.strobe(CC1101_STROBE_SFRX)
                    self.cc1101.strobe(CC1101_STROBE_SRX)
            
            # Draw Content Activity
            if time.time() - packet_time < 5.0 and last_packet != "":
                # We have a recently received packet, draw with big prominence
                draw.rectangle([0, 16, display.width, 30], fill=255)
                draw.text((4, 18), "PACKET RECEIVED!", font=display.font, fill=0)
                
                # Split packet info into multiple lines cleanly
                y_pos = 35
                for line in last_packet.split("\n"):
                    if "[SAVED" in line:
                        draw.text((2, display.height - 12), line, font=display.font, fill=255)
                    else:
                        draw.text((2, y_pos), line, font=display.font, fill=255)
                        y_pos += 10
            else:
                # Idle scanning animation
                draw.text((10, 25), "Listening...", font=display.font, fill=255)
                # Radar-like lines animation
                anim_offset = (anim_frame % 20)
                draw.line((10 + anim_offset, 45, 30 + anim_offset, 45), fill=255, width=2)
                draw.line((10 + (anim_frame*2)%40, 50, 20 + (anim_frame*2)%40, 50), fill=255, width=2)
                anim_frame += 1
                
                # Input hint
                draw.text((2, display.height - 12), "(OK) to REC  [" + ("ON" if is_recording else "OFF") + "]", font=display.font, fill=255)

            display.draw(img)
            time.sleep(0.05)
                
        if self.cc1101:
            self.cc1101.strobe(CC1101_STROBE_SIDLE)

    # ----------------------------------------------------
    # SAVED MODE (Replay)
    # ----------------------------------------------------
    def saved_mode(self):
        while not self.is_stopped():
            if not os.path.exists(self.save_dir):
                os.makedirs(self.save_dir)
            files = [f for f in os.listdir(self.save_dir) if f.endswith('.json')]
            files.sort(reverse=True)
            
            if not files:
                img = Image.new('1', (display.width, display.height), 0)
                draw = ImageDraw.Draw(img)
                self.draw_header(draw, "Saved Data")
                draw.text((10, 30), "No saved signals", font=display.font, fill=255)
                display.draw(img)
                while True:
                    k, ts = pheripherals.get_key()
                    if k in ["back", "exit", "select"]:
                        break
                    time.sleep(0.1)
                return

            options = files + ["Back"]
            menu = Menu(options)
            
            while True:
                menu.show()
                k = pheripherals.await_key()
                if k == "select":
                    sel = options[menu.index]
                    if sel == "Back":
                        return
                    else:
                        filepath = os.path.join(self.save_dir, sel)
                        self.handle_saved_file(filepath)
                        break # refresh list after handling
                elif k in ["back", "exit"]:
                    return

    def handle_saved_file(self, filepath):
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
        except Exception as e:
            Log.error(f"Error reading {filepath}: {e}")
            return
            
        freq = data.get("frequency", 433.92)
        mod = data.get("modulation", "ASK")
        payload_hex = data.get("payload", "")
        
        while not self.is_stopped():
            options = ["Send", "Delete", "Back"]
            menu = Menu(options)
            menu.show()
            k = pheripherals.await_key()
            if k == "select":
                sel = options[menu.index]
                if sel == "Back":
                    return
                elif sel == "Delete":
                    os.remove(filepath)
                    display.text("Deleted!")
                    time.sleep(1)
                    return
                elif sel == "Send":
                    try:
                        payload_bytes = bytes.fromhex(payload_hex.replace(" ", ""))
                        old_freq = self.frequency
                        old_mod = self.modulation
                        
                        self.frequency = freq
                        self.modulation = mod
                        self.apply_radio_config()
                        
                        self.fire_tx(payload_bytes, 10)
                        
                        self.frequency = old_freq
                        self.modulation = old_mod
                        self.apply_radio_config()
                    except Exception as e:
                        Log.error(f"Send failed: {e}")
                        display.text("Send Error")
                        time.sleep(1)
            elif k in ["back", "exit"]:
                return

    # ----------------------------------------------------
    # FREQUENCY ANALYZER (Peak sweeping)
    # ----------------------------------------------------
    def frequency_analyzer(self):
        title = "Freq Analyzer"
        last_timestamp = pheripherals.get_key()[1]
        
        peak_rssi = -150
        peak_freq = 0.0
        peak_time = 0
        
        while not self.is_stopped():
            img = Image.new('1', (display.width, display.height), 0)
            draw = ImageDraw.Draw(img)
            self.draw_header(draw, title)
            
            # Fast Sweep
            if self.cc1101:
                current_loop_peak = -150
                current_loop_freq = 0
                
                for f in self.scan_sweep:
                    self.cc1101.set_frequency(f)
                    self.cc1101.strobe(CC1101_STROBE_SRX)
                    time.sleep(0.01) # Short settle
                    dBm = self.cc1101.get_rssi()
                    if dBm is not None:
                        if dBm > current_loop_peak:
                            current_loop_peak = dBm
                            current_loop_freq = f
                
                # Register global peak if strong enough
                if current_loop_peak > -75 and current_loop_peak >= peak_rssi:
                    peak_rssi = current_loop_peak
                    peak_freq = current_loop_freq
                    peak_time = time.time()
            
            # Decay the global peak after 3 seconds
            if time.time() - peak_time > 3.0:
                peak_rssi = -150
                peak_freq = 0.0

            # UI Rendering
            draw.text((2, 18), "Peak Detected:", font=display.font, fill=255)
            
            if peak_freq > 0:
                # Enlarge fake font effect by drawing thick or offsets
                fx = 20
                fy = 32
                val_str = f"{peak_freq:.2f} MHz"
                # Fake Bold
                draw.text((fx, fy), val_str, font=display.font, fill=255)
                draw.text((fx+1, fy), val_str, font=display.font, fill=255)
                draw.text((fx, fy+1), val_str, font=display.font, fill=255)
                
                rssi_str = f"RSSI: {int(peak_rssi)} dBm"
                draw.text((20, 48), rssi_str, font=display.font, fill=255)
            else:
                draw.text((20, 35), "Scanning Band...", font=display.font, fill=255)
                
            display.draw(img)
            
            key, ts = pheripherals.get_key()
            if ts != last_timestamp:
                break
                
        if self.cc1101:
            self.cc1101.strobe(CC1101_STROBE_SIDLE)


    # ----------------------------------------------------
    # SEND DATA (TX)
    # ----------------------------------------------------
    def send_mode(self):
        op = ["Send 10 Hex Pkts", "Send SOS Carrier", "Back"]
        menu = Menu(op)
        while True:
            menu.show()
            k = pheripherals.await_key()
            if k == "select":
                sel = op[menu.index]
                if sel == "Back": break
                elif sel == "Send 10 Hex Pkts":
                    self.fire_tx(b"\xAA\xBB\xCC\x11\x22\x33", 10)
                elif sel == "Send SOS Carrier":
                    self.fire_tx(b"\x53\x4F\x53\x53\x4F\x53", 20)
                break
            elif k in ["back", "exit"]:
                break

    def fire_tx(self, payload, cycles):
        if not self.cc1101: return
        self.cc1101.strobe(CC1101_STROBE_SIDLE)
        last_ts = pheripherals.get_key()[1]
        
        img = Image.new('1', (display.width, display.height), 0)
        draw = ImageDraw.Draw(img)
        self.draw_header(draw, f"TX  {self.frequency}")
        draw.text((10, 25), "Transmitting...", font=display.font, fill=255)
        display.draw(img)
        
        for i in range(cycles):
            self.cc1101.strobe(CC1101_STROBE_SFTX)
            self.cc1101.write_fifo(list(payload))
            self.cc1101.strobe(CC1101_STROBE_STX)
            time.sleep(0.1)
            
            k, ts = pheripherals.get_key()
            if ts != last_ts: break
            
        self.cc1101.strobe(CC1101_STROBE_SIDLE)


    # ----------------------------------------------------
    # SETTINGS
    # ----------------------------------------------------
    def settings_menu(self):
        while True:
            opts = [f"Freq: {self.frequency}", f"Mod: {self.modulation}", "Presets >>>", "Back"]
            menu = Menu(opts)
            menu.show()
            k = pheripherals.await_key()
            
            if k == "select":
                if menu.index == 0:
                    self.frequency = select_number(display, pheripherals, start_number=self.frequency, title="Set Frequency", decimals=2, min=300, max=928)
                elif menu.index == 1:
                    self.modulation = "FSK" if self.modulation == "ASK" else "ASK"
                elif menu.index == 2:
                    self.presets_menu()
                elif menu.index == 3:
                    break
            elif k in ["back", "exit"]:
                break
                
    def presets_menu(self):
        presets_list = [315.00, 318.00, 433.92, 434.42, 868.00, 868.35, 915.00]
        str_presets = [f"{p:.2f} MHz" for p in presets_list] + ["Back"]
        menu = Menu(str_presets)
        while True:
            menu.show()
            k = pheripherals.await_key()
            if k == "select":
                if menu.index < len(presets_list):
                    self.frequency = presets_list[menu.index]
                break
            elif k in ["back", "exit"]:
                break

    def cleanup(self):
        try:
            if self.cc1101: self.cc1101.shutdown()
        except: pass