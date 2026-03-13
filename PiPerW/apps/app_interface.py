


class AppInterface:
    def __init__(self, name, version):
        import os
        self.name = name
        self.version = version
        self._thread = None # Reference to the WThread running this app
        self._state_dir = os.path.join("data", self.name.replace(" ", "_").lower())
        os.makedirs(self._state_dir, exist_ok=True)

    def __str__(self):
        return f"{self.name} {self.version}"

    def get_state_dir(self):
        """Returns a guaranteed persistent directory for this app's files."""
        return self._state_dir

    def save_state(self, filename, data):
        """Helper to save string/bytes to the app's persistent data folder."""
        import os
        path = os.path.join(self._state_dir, filename)
        mode = 'wb' if isinstance(data, bytes) else 'w'
        with open(path, mode) as f:
            f.write(data)

    def is_stopped(self):
        """Check if the system has requested this app to stop."""
        if self._thread:
            return self._thread.stopped()
        return False

    def wait_for_input(self, process=None):
        """
        Non-blocking wait for key press or process completion.
        Returns the key pressed, or None if stopped/process ended.
        """
        import time
        from PiPerW.driver.pheripherals import Pheripherals
        pheripherals = Pheripherals()
        
        while not self.is_stopped():
            if process and process.poll() is not None:
                break
            key = pheripherals.get_key()
            if key is not None:
                return key
            time.sleep(0.1)
        return None

    def run(self):
        pass
