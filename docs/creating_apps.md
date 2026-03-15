# Guía para Desarrolladores: Creación de Aplicaciones

Las aplicaciones en PiPerW son módulos *Plug and Play*. Para crear una aplicación, necesitas colocarla dentro de la categoría y carpeta correspondiente (Ej. `apps/WiFi/Mi_Nueva_App/`).

Cada script debe tener obligatoriamente dos archivos mínimos:
1. `manifest.toml`: Para configuración y dependencias.
2. `__init__.py`: Donde reside la lógica de ejecución (La clase `App`).

---

## 1. El Fichero `manifest.toml`

Este archivo evita tener que hacer validaciones *hardcodeadas* de versión o forzar comprobaciones de paquetes (`apt`/`pip`) cada vez que se arranca. Ejemplo:

```toml
[app]
name = "Scanner Personalizado"
version = "1.0"
author = "Mi Nombre"
description = "Una utilidad para escanear cosas"

[requirements]
apt = ["nmap", "aircrack-ng"]
pip = ["requests", "toml"]
github = []
```
*PiPerW analizará durante la carga si las dependencias existen. Si no, las instalará y cacheará.*

---

## 2. El Fichero `__init__.py`

Esta es la estructura base con la que **todas** las aplicaciones deben ser inicializadas:

```python
from PiPerW.interfaces.app_interface import AppInterface
from PiPerW.driver.pheripherals import Pheripherals
from PiPerW.driver.display import Display
from PiPerW.utils.Menu import Menu
from PiPerW.helpers import Log
import time

display = Display()
pheripherals = Pheripherals()

class App(AppInterface):
    def __init__(self, *args, **kwargs):
        # MUY IMPORTANTE lanzar el super().__init__ sin parámetros explícitos obligatorios.
        super().__init__()
        
    def run(self):
        # Bucle de vida de tu aplicación
        while not self.is_stopped():
            display.clear()
            display.text("Hola Mundo!")
            
            # Bloqueo vigilado hacia inputs del usuario
            key = pheripherals.await_key()
            
            # Siempre se debe respetar is_stopped() para permitir que el SO o 
            # el usuario destruyan o salgan de la aplicación sin congelar el hardware
            if key is None or self.is_stopped():
                break
                
            if key in ["back", "exit"]:
                break
```

---

## 3. Renderizado de Menús

Para renderizar selecciones multi-opción es recomendable usar la clase `Menu` empaquetada, ya que ella gestiona coordenadas, scroll e inputs:

```python
def run(self):
    opciones = ["Escanear", "Ajustes", "Salir"]
    menu = Menu(opciones)
    
    while not self.is_stopped():
        menu.show()
        key = pheripherals.await_key()
        
        if key is None or self.is_stopped() or key in ["back", "exit"]:
            break
            
        if key == "up":
            menu.previous()
        elif key == "down":
            menu.next()
        elif key == "select":
            seleccion = menu.index # Retorna 0, 1 o 2 (el índice int)
            if seleccion == 0:
                self.hacer_scan()
            elif seleccion == 2:
                break
```

---

## 4. Persistencia de Datos

Para guardar configuraciones, un JSON, o salidas de comando en formato `.csv` (como los Pcap de Kali), NO uses rutas absolutas quemadas en el código, llama a los helpers integrados para evitar ensuciar el `root_dir`:

```python
def guardar_log(self, datos):
    # Esto guardará en `data/nombre_de_la_app/mi_archivo.txt`
    # Carpeta creada automáticamente y sanitizada.
    self.save_state("mi_archivo.txt", datos)
    
    # Si quieres la ruta literal:
    ruta = self.get_state_dir()
    
    # Si necesitas una ruta que se exporte obligatoriamente vía web o a un USB
    # y que un no-root pueda acceder:
    carpeta_publica = self.get_public_dir() # apunta a ./public/
```

---

## 5. El Fichero `__on_exit__.py` (Opcional - Nivel Categoría)

A veces, las utilidades alteran el estado del sistema base (por ejemplo, apagar un servicio de red temporalmente o activar el modo Monitor `wlan0mon`). 

Si cierras una app de repente por un error o dándole a *Exit*, la placa se quedará con el hardware secuestrado. Para evitarlo, en la raíz de cualquier categoría (ej: `apps/WiFi/`) puedes incluir un archivo `__on_exit__.py` que restaure la conectividad al cerrarse cualquier aplicación que estuviera alojada en dicha categoría.

**Ejemplo de apps/Mi_Seccion/__on_exit__.py**
```python
from PiPerW.helpers import Log
import subprocess

class Execute:
    def __init__(self):
        Log.info("Restaurando hardware después de cerrar la app de esta categoría...")
        # Ejemplo:
        # subprocess.run(["sudo", "service", "NetworkManager", "start"], capture_output=True)
```
*`main.py` instanciará localmente y en un hilo seguro esta clase base justo en el instante en que tu App haya devuelto el control.*