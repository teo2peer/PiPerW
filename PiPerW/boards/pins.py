from PiPerW.boards.core import active_board

# Injects dynamically all abstract pins (E.g. I2C_SDA, GPIO0) from the manifest
# so developers can do: from PiPerW.boards.pins import I2C_SDA, GPIO1

if hasattr(active_board, 'pins'):
    for pin_name in active_board.pins.keys():
        globals()[pin_name] = pin_name
