


class AppInterface:
    def __init__(self):
        import os
        import sys
        
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError:
                import toml as tomllib
                
        # Dynamically determine the app's directory by looking at the child class's module
        module_name = self.__class__.__module__
        module_file = sys.modules[module_name].__file__
        app_dir = os.path.dirname(module_file)
        
        manifest_path = os.path.join(app_dir, "manifest.toml")
        
        if os.path.exists(manifest_path):
            with open(manifest_path, "r", encoding="utf-8") as f:
                content = f.read()
            try:
                manifest = tomllib.loads(content)
            except AttributeError:
                manifest = tomllib.load(manifest_path)
            self.name = manifest.get("name", "Unknown App")
            self.version = manifest.get("version", "0.0")
        else:
            self.name = "Unknown App"
            self.version = "0.0"
            
        self._thread = None # Reference to the WThread running this app
        self._state_dir = os.path.join("data", self.name.replace(" ", "_").lower())
        os.makedirs(self._state_dir, exist_ok=True)

    def __str__(self):
        return f"{self.name} {self.version}"

    def get_public_dir(self):
        """Returns the global structured 'public' directory at root."""
        import os
        base_dir = os.path.join(os.getcwd(), "public")
        os.makedirs(os.path.join(base_dir, "music"), exist_ok=True)
        os.makedirs(os.path.join(base_dir, "images"), exist_ok=True)
        os.makedirs(os.path.join(base_dir, "files"), exist_ok=True)
        return base_dir

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
