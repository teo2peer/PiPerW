


class AppInterface:
    def __init__(self, name, version):
        self.name = name
        self.version = version
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
