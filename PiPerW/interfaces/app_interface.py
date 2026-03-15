


import sys
import os

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        import toml as tomllib

class AppInterface:
    def __init__(self):
        # Dynamically determine the app's directory by looking at the child class's module
        module_name = self.__class__.__module__
        module_file = sys.modules[module_name].__file__
        app_dir = os.path.dirname(module_file)
        
        manifest_path = os.path.join(app_dir, "manifest.toml")
        
        if os.path.exists(manifest_path):
            with open(manifest_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            try:
                # Use loads which works with both tomllib, tomli and toml on string content
                manifest = tomllib.loads(content)
            except AttributeError:
                # Fallback if loads is not available (some very old versions)
                manifest = tomllib.load(manifest_path)
                
            self.name = manifest.get("name", "Unknown App")
            self.version = manifest.get("version", "0.0")
        else:
            self.name = "Unknown App"
            self.version = "0.0"
            
        self._thread = None # Reference to the WThread running this app

    def __str__(self):
        return f"{self.name} {self.version}"

    def is_stopped(self):
        """Check if the system has requested this app to stop."""
        if self._thread:
            return self._thread.stopped()
        return False

    def run(self):
        pass
