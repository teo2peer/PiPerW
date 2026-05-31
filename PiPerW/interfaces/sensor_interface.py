"""SensorInterface — common base for I2C/SPI/UART sensors.

Concrete sensors return {field: float} from read().
Registry lets a dashboard auto-discover all attached sensors.
"""
from abc import ABC, abstractmethod
from PiPerW.helpers import Log


class SensorInterface(ABC):
    name = "sensor"
    unit = {}  # {field_name: "unit string"}

    @abstractmethod
    def read(self):
        """Return dict[str, float] of latest readings. Empty dict on failure."""
        ...

    def describe(self):
        return {"name": self.name, "unit": self.unit}


_REGISTRY = []


def register_sensor(sensor):
    _REGISTRY.append(sensor)
    Log.info(f"Registered sensor: {sensor.name}")


def all_sensors():
    return list(_REGISTRY)
