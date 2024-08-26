import importlib
from PiPerW.helpers import Config, Log

class Display:
    def __init__(self):
        self.driver = self._load_driver()

    def _load_driver(self):
        try:
            display_module = importlib.import_module(f"PiPerW.display.{Config['display']['driver']}")
            driver = display_module.Driver()
            driver.init()
            Log.info(f"Loaded and initialized display driver: {Config['display']['driver']}")
            return driver
        except Exception as e:
            Log.exception(f"Error initializing display driver: {e}")
            raise

    def __getattr__(self, name):
        """
        Delegate attribute access to the driver instance.
        """
        return getattr(self.driver, name)