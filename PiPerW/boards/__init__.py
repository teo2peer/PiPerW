# Board Core Initialization exported for convenience
from .core import active_board as _current_board

# Hardware Interfaces
from .board_interface import PinMode, PinPull
from .gpio import setup_pin, read_pin, write_pin, get_real_gpio
from .spi import get_spi
from .i2c import get_i2c

# Pins
from .pins import *

# Utility
get_board = lambda: _current_board
get_gpio = get_real_gpio
cleanup = _current_board.cleanup

