import os
import json
from PiPerW.interfaces.app_interface import AppInterface
from PiPerW.utils.Menu import Menu
from PiPerW.utils.PinSelector import PinSelector

class BaseApp(AppInterface):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config_file = os.path.join(self.get_state_dir(), "ir_config.json")
        self.config = self.load_config()

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"rx_pin": None, "tx_pin": None}

    def save_config(self):
        self.save_state("ir_config.json", json.dumps(self.config))

    def run(self):
        while not self.is_stopped():
            rx_val = self.config.get("rx_pin") or "No asignado"
            tx_val = self.config.get("tx_pin") or "No asignado"

            menu_items = [
                "1. Capturar IR (Rx)",
                "2. Emitir IR (Tx)",
                f"3. Conf. Pin Rx [{rx_val}]",
                f"4. Conf. Pin Tx [{tx_val}]",
                "5. Salir"
            ]
            
            choice = Menu(menu_items).show()
            
            if choice == 0: # Capturar
                pin = self.config.get("rx_pin")
                if pin:
                    self.display.set_text(f"Escuchando IR...\nPin: {pin}")
                    self.sleep(2)
                else:
                    self.display.set_text("! Asigna un Pin Rx\nprimero !")
                    self.sleep(2)

            elif choice == 1: # Emitir
                pin = self.config.get("tx_pin")
                if pin:
                    self.display.set_text(f"Emitiendo IR...\nPin: {pin}")
                    self.sleep(2)
                else:
                    self.display.set_text("! Asigna un Pin Tx\nprimero !")
                    self.sleep(2)

            elif choice == 2: # Asignar Rx
                selected_pin = PinSelector.select_free_gpio("Pin Receptor (Rx)")
                if selected_pin:
                    self.config["rx_pin"] = selected_pin
                    self.save_config()
                    self.display.set_text(f"Pin Rx Guardado:\n{selected_pin}")
                    self.sleep(1.5)

            elif choice == 3: # Asignar Tx
                selected_pin = PinSelector.select_free_gpio("Pin Emisor (Tx)")
                if selected_pin:
                    self.config["tx_pin"] = selected_pin
                    self.save_config()
                    self.display.set_text(f"Pin Tx Guardado:\n{selected_pin}")
                    self.sleep(1.5)

            elif choice == 4 or choice is None: # Salir o back
                break
