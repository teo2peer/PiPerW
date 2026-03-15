from PiPerW.boards.core import active_board
from PiPerW.boards.board_interface import PinMode, PinPull

# Map standard GPIO operations to the active board
setup_pin = active_board.setup_pin
read_pin = active_board.read_pin
write_pin = active_board.write_pin
get_real_gpio = active_board.get_real_gpio
