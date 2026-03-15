from PiPerW.utils.Menu import Menu
from PiPerW.boards.core import active_board
from PiPerW.helpers import Log

class PinSelector:
    @staticmethod
    def select_free_gpio(title="Select GPIO Pin") -> str:
        """
        Displays a menu for the user to select an available, non-reserved GPIO pin.
        Returns the abstract pin name (e.g. 'GPIO0') or None if the user cancels.
        """
        if not hasattr(active_board, 'pins'):
            Log.error("Active board has no pins defined.")
            return None

        # Sort the pins nicely. We assume free pins are named like GPIO0, GPIO1...
        # or we filter out anything starting with I2C, SPI, UART.
        free_pins = []
        for pin_name, bcm_num in active_board.pins.items():
            # Exclude reserved buses 
            if not pin_name.startswith(("I2C_", "SPI_", "UART_")):
                free_pins.append({
                    "name": pin_name,
                    "bcm": bcm_num,
                    "sort_id": int(pin_name.replace("GPIO", "")) if pin_name.startswith("GPIO") else 999
                })
        
        # Sort by logical number
        free_pins = sorted(free_pins, key=lambda x: x["sort_id"])

        # Prepare Menu items
        menu_items = [f"{pin['name']} (BCM {pin['bcm']})" for pin in free_pins]
        menu_items.append("Cancel / Exit")

        # Show Menu with an optional contextual title if we had title support
        # (Assuming Menu is basic, we'll just instantiate and show)
        menu = Menu(menu_items)
        # Note: If your Menu constructor accepts a title, you can add it: Menu(menu_items, title=title)
        
        choice_idx = menu.show()

        if choice_idx is None or choice_idx == len(menu_items) - 1:
            return None # Cancelled
            
        return free_pins[choice_idx]["name"]
