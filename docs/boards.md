# Arquitectura de Boards (Hardware Abstraction Layer - HAL)

Este documento detalla el funcionamiento interno, el mecanismo de auto-hidratación y la guía paso a paso para agregar y configurar nuevas placas en **PiPerW**.

## 1. Funcionamiento Interno del HAL (Hardware Abstraction Layer)

El ecosistema PiPerW está diseñado para ser **Agnóstico al Hardware (Hardware Agnostic)**. Esto significa que las aplicaciones (como SubGHz suiteSuite o System Monitor) y los drivers (como CC1101) no incluyen importaciones directas a librerías de hardware específicas (por ejemplo, `RPi.GPIO` o `spidev`). 

En lugar de eso, todas las interacciones con el hardware pasan a través del módulo central `PiPerW.boards`.

### Módulos Principales
La carpeta `boards/` se divide por sub-responsabilidades para mantener el código base limpio:

- **`board_interface.py`**: Define el contrato o interfaz (`BoardInterface`) que toda placa nueva debe cumplir (métodos `setup_pin`, `write_pin`, `get_spi`, etc.) y enumeraciones estándar (`PinMode.IN`, `PinPull.UP`).
- **`core.py`**: Lee la configuración global `config.toml` (sección `[hardware] board="rpi_zero"`) e importa dinámicamente el módulo correspondiente mediante `importlib`. Instancia la placa activa en el objeto `active_board`.
- **`gpio.py`, `spi.py`, `i2c.py`**: Exponen alias o referencias a los métodos de la placa instanciada (`setup_pin`, `get_spi`).
- **`pins.py`**: Se encarga de la inyección dinámica (auto-hidratación) de los identificadores de pines de la placa.

---

## 2. Auto-Hidratación (Hydration) y Propagación de Pines

### ¿Qué es la auto-hidratación en PiPerW?
Existen multitud de placas y todas nombran físicamente e indexan los pines de maneras distintas (Ej. En RPi `BCM 5`, en un Arduino algo numérico simplemente, o en otras SBC algo como `PA_05`). Un desarrollador de PiPerW no debería tener que adivinar qué pin físico corresponde a cuál bus de datos.

Para aislar esta complejidad, cada placa define sus propios **pines abstractos** en un archivo de configuración interno: `manifest.toml`.

El módulo `PiPerW.boards.pins` recupera esa lista abstracta de propiedades de la placa y "Auto-hidrata" (inyecta variables dinámicamente) de la siguiente manera:

```python
# PiPerW/boards/pins.py
if hasattr(active_board, 'pins'):
    for pin_name in active_board.pins.keys():
        globals()[pin_name] = pin_name
```

### Propagación
1. `core.py` carga la placa activa (Ej. `rpi_zero`).
2. La placa lee su propio `manifest.toml` y almacena las claves en un objeto `self.pins`.
3. `pins.py` lee un iterador de claves y las "escribe" literalmente en el espacio de nombres (namespace) global del módulo como strings usando el diccionario `globals()`.
4. El desarrollador de la app o driver importa transparentemente esos strings como si fueran constantes reales:

```python
from PiPerW.boards.pins import GPIO0, SPI_MOSI, SPI_CS
from PiPerW.boards.spi import get_spi
from PiPerW.boards.gpio import setup_pin, PinMode

# El driver nunca supo si SPI_CS representa físicamente el número 8 o el 25.
spi = get_spi(bus=0, device=0)
setup_pin(GPIO0, PinMode.IN)
```

---

## 3. Guía: Cómo Agregar y Configurar una Nueva Placa

Agregar un nuevo soporte de hardware en PiPerW requiere crear una nueva carpeta en `boards/` con **dos archivos básicos**: `__init__.py` y `manifest.toml`.

### Paso 1: Crear la Carpeta
Supongamos que quieres añadir soporte para una placa ficticia llamada "Orange Pi 3":
Crea la carpeta: `PiPerW/boards/orange_pi3/`

### Paso 2: Crear el `manifest.toml` de la Placa
Este archivo funciona como diccionario de traducción (mapeo). Asocia el **nombre abstracto** global de PiPerW con el valor **físico real** que requiere tu librería para esa placa (por ejemplo, números de pin del microprocesador).

```toml
# PiPerW/boards/orange_pi3/manifest.toml
name = "Orange Pi 3"

[pins]
# Formato: PIN_ABSTRACTO_PIPERW = "identificador_fisico_interno"
GPIO0 = 12
GPIO1 = 13
GPIO2 = 14

I2C_SDA = 2
I2C_SCL = 3

SPI_MOSI = 10
SPI_MISO = 9
SPI_SCLK = 11
SPI_CS   = 8
```

### Paso 3: Crear el driver de la Placa (`__init__.py`)
El framework necesita instanciar una `Board()` que herede de `BoardInterface`. Debes programar qué pasará "físicamente" cuando PiPerW pida interactuar con un pin o bus.

```python
# PiPerW/boards/orange_pi3/__init__.py
from PiPerW.boards.board_interface import BoardInterface, PinMode, PinPull
from PiPerW.helpers import Log

# Aquí importa la librería específica del hardware de la placa (Ej: OPi.GPIO)
import OPi.GPIO as GPIO 
import spidev

class Board(BoardInterface):
    def __init__(self):
        super().__init__("orange_pi3")
        # El padre (BoardInterface) se encarga de leer manifest.toml
        # y popular self.pins en base al nombre "orange_pi3".
        
        GPIO.setmode(GPIO.BOARD) # EJEMPLO
        self._spi_instances = {}

    def get_real_gpio(self, pipW_abstract_pin: str) -> int:
        # pipW_abstract_pin podría ser "GPIO0", esto busca el número '12' físico
        return self.pins.get(pipW_abstract_pin, None)

    def setup_pin(self, pipW_abstract_pin: str, mode: PinMode, pull: PinPull = PinPull.NONE):
        real_pin = self.get_real_gpio(pipW_abstract_pin)
        
        # Lógica de traducción OPi.GPIO
        opi_mode = GPIO.IN if mode == PinMode.IN else GPIO.OUT
        opi_pull = GPIO.PUD_UP if pull == PinPull.UP else GPIO.PUD_DOWN
        if pull == PinPull.NONE: opi_pull = GPIO.PUD_OFF
        
        GPIO.setup(real_pin, opi_mode, pull_up_down=opi_pull)

    def read_pin(self, pipW_abstract_pin: str) -> bool:
        real_pin = self.get_real_gpio(pipW_abstract_pin)
        return GPIO.input(real_pin) == GPIO.HIGH

    def write_pin(self, pipW_abstract_pin: str, state: bool):
        real_pin = self.get_real_gpio(pipW_abstract_pin)
        GPIO.output(real_pin, GPIO.HIGH if state else GPIO.LOW)

    def get_spi(self, bus=0, device=0):
        # Manejo de instancias SPI como Singleton si lo requiere la librería
        name = f"spi_{bus}_{device}"
        if name not in self._spi_instances:
            spi = spidev.SpiDev()
            spi.open(bus, device)
            self._spi_instances[name] = spi
        return self._spi_instances[name]

    def cleanup(self):
        GPIO.cleanup()
        for spi in self._spi_instances.values():
            spi.close()
```

### Paso 4: Configurar el `.toml` Global
Por último, para que PiPerW inicie tu placa al arrancar, tienes que decírselo en tu configuración raíz global `config.toml` (ubicada en la carpeta principal del proyecto).

```toml
# PiPerW/config.toml
[hardware]
board = "orange_pi3"
```
Una vez configurado y arrancado el bot, `core.py` leerá este string, invocará la placa vía importlib, registrará los alias en `gpio.py` / `spi.py`, e hidratará los pines dinámicamente en el namespace `PiPerW.boards.pins`. Todo de manera automática.