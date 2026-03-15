import importlib
import traceback
from PiPerW.helpers import Config, Log
from PiPerW.boards.board_interface import BoardInterface

# 1. Resolve board name from configuration
board_name = "rpi_zero" # Default fallback
if "hardware" in Config and "board" in Config["hardware"]:
    board_name = Config["hardware"]["board"]

# 2. Dynamically load the active board instance
try:
    module = importlib.import_module(f"PiPerW.boards.{board_name}")
    active_board = module.Board()
    Log.info(f"Loaded hardware board: {board_name}")
except Exception as e:
    Log.error(f"Failed to load board '{board_name}': {e}")
    Log.error(traceback.format_exc())
    active_board = BoardInterface("Dummy")
