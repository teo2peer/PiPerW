from PiPerW.boards.core import active_board

# Map I2C operations to the active board
get_i2c = active_board.get_i2c
