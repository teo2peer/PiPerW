# Directorio: boards/

Este directorio se encarga de aislar la capa física de hardware (pines, buses y direccionamiento de memoria) de la lógica superior del sistema operativo y de los controladores específicos de pantalla o botones.

La motivación principal detrás de `boards/` es garantizar que **PiPerW pueda ser portado a distintas microcomputadoras** (Raspberry Pi Zero, RPi 4, Orange Pi, Banana Pi, etc.) sin tener que reescribir todo el código, simplemente cambiando el perfil de hardware cargado.

## Archivos Base

- **`core.py`**: Intermediario central que maneja el ciclo de vida del *SoC* subyacente. Inicializa y desarma las interfaces asociadas.
- **`gpio.py`**: Envoltura (wrapper) segura para abrir interactuar con los pines GPIO lógicos, inyectando control de errores para prevenir fallos nativos de Linux.
- **`i2c.py`**: Abstracción del bus I2C (Inter-Integrated Circuit). Prepara las direcciones de esclavo requeridas generalmente por las pantallas (como OLED SSD1306 u otros sensores).
- **`spi.py`**: Gestor de canales de la interfaz periférica serial (SPI). Empleado frecuentemente para pantallas ST7735S u otros módulos como el lector NFC.

## Subdirectorios de Placas Específicas

Actualmente, el sistema contiene perfiles de placas como `rpi_zero/`, enfocadas a emular y gestionar los pines físicos de esta pequeña placa.

### Ejemplo: `rpi_zero/`
Dentro de un directorio de placa como `rpi_zero` vas a encontrar:
- **`__init__.py`**: Lógica de auto-inicialización de los drivers de la RPi Zero.
- **`manifest.toml`**: Describe las capacidades de la placa, configuraciones de velocidad máxima y qué chipset lleva dentro.
- **`rpi_pins.txt`** (o equivalente): Un mapa de traducción. Documenta cómo se asocia, por ejemplo, el `PIN 12` lógico al pin físico real en el cabezal GPIO.