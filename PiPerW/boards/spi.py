from PiPerW.boards.core import active_board

# Map SPI operations to the active board
get_spi = active_board.get_spi
