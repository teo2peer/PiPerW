"""NotificationInterface — toast on display + log line.

Apps call `self.notify("Scan done")` instead of bespoke
`display.text + sleep` patterns.
"""
import threading
import time
from abc import ABC, abstractmethod

from PiPerW.helpers import Log


class NotificationInterface(ABC):
    @abstractmethod
    def notify(self, text, level="info", ttl=3.0): ...


class DisplayNotifier(NotificationInterface):
    def __init__(self, display):
        self._display = display
        self._lock = threading.Lock()

    def notify(self, text, level="info", ttl=3.0):
        logger = getattr(Log, level, Log.info)
        logger(f"[notify] {text}")
        with self._lock:
            try:
                self._display.text(str(text))
            except Exception as e:
                Log.warning(f"notify display failed: {e!r}")

        def _clear():
            time.sleep(ttl)
            try:
                self._display.clear()
            except Exception:
                pass

        threading.Thread(target=_clear, daemon=True).start()
