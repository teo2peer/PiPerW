# Arquitectura Interna de PiPerW

PiPerW está diseñado bajo una arquitectura modular, orientada a eventos y fuertemente desacoplada. Se inspira en sistemas embebidos de hacking y pentesting, separando rigurosamente el núcleo de hardware de la lógica de software.

A continuación se detalla la estructura profunda del core ubicado en `PiPerW/`:

---

## 1. Archivos Core en la Raíz

- **`helpers.py`**: Es la columna vertebral utilitaria del sistema. Aquí se instancian módulos globales como la Configuración (`Config`), el logger base (`Log`) y herramientas de manejo de directorios (`DirFilter`). También contiene la clase **`WThread`**, que es un *wrapper* asíncrono de `threading.Thread` diseñado para crear hilos abortables (posee un Dead Man's Switch), garantizando que si una aplicación se cuelga eternamente, el sistema principal recupere el control de la pantalla y los periféricos.
- **`setup.py`**: Encargado de la inicialización de primera ejecución y la comprobación de integridad. Prepara el entorno, revisa si hay temas, valida que se cumplan las estructuras en `public/` y monta el ecosistema del menú principal antes de entregar el testigo al `main.py` de la raíz del firmware.

---

## 2. Abstracción de Roles (`interfaces/`)

Esta carpeta contiene los **Contratos (Clases Abstractas)**. Aseguran que cualquier hardware nuevo que conectes hable el mismo idioma estándar interno que las aplicaciones que usará el usuario final.
- **`app_interface.py`**: Toda aplicación hereda de aquí. Provee la lectura automática de su `manifest.toml`, un entorno seguro de persistencia de datos mediante `get_state_dir()`, acceso de escritura a la carpeta pública si necesita exportar archivos, y un chequeo constante del ciclo de vida (`self.is_stopped()`).
- **`display_interface.py`**: Define las primitivas obligatorias para dibujar (`.text()`, `.clear()`, `.image()`, `.progress_bar()`). Las apps mandan estos datos de alto a esta interfaz, nunca atacando al hardware de los píxeles de forma directa.
- **`pheripheral_interface.py`**: Unifica la definición de un "input". Traslada pulsaciones físicas (de diferentes orígenes como pines GPIO, Teclados USB, WebSockets de la interfaz web) a un vocabulario estándar unificado e imitable: `UP`, `DOWN`, `SELECT`, `BACK`, `EXIT`.

---

## 3. Implementación de Hardware (`driver/`)

Aquí es donde los contratos de las *interfaces* reciben código físico real. Implementan de forma aislada la traducción hacia los protocolos I2C, SPI o HID real.
- **`display/`**: Contiene los controladores que saben cómo transferir frames a pantallas físicas (ej. `sh1106`, `ssd1306`, `st7735S`). También incluye el potente controlador `only_web`, un display virtual que escupe el renderizado a un WebSocket hosteado en un cliente local para facilitar el testeo desde un PC de escritorio sin forzar el uso de una Raspberry Pi durante el desarrollo.
- **`pheripherals/`**: Define los listeners y botones físicos. 
  - `keyboard/`: Lee eventos de la terminal y teclado del PC con el que el programador corre PiPerW.
  - `waveshare_hat/`: Mapea físicamente las resistencias pull-up y botones de los HAT de componentes de Raspberry hacia comandos lógicos.
- **`SubGHz/`**: Controladores aislados para manejo de módulos de transceptores de rádio externos. Por ejemplo, incluye la librería `CC1101/` y su respectivo mapa maestro de registros de hardware (`reg.py`) usado por las apps de escaneo e inyección.

---

## 4. Capa Física y Dispositivos de Bajo nivel (`boards/`)

Mueve la lógica sucia de la gestión de memoria y el bus del procesador a un único intermediario universal (para adaptar a RPi 4, Zero, Banana Pi...).
- **`core.py`, `gpio.py`, `i2c.py`, `spi.py`**: Librerías que configuran y abren los streams crudos, inyectando control de errores de fallos Linux en los buses.
- **`rpi_zero/`**: Un submódulo base nativo del repositorio enfocado en la Pi Zero. Contiene su `manifest.toml` y un `rpi_pins.txt`, un fichero que documenta cómo asociar las interfaces lógicas arriba mencionadas con pines físicos particulares del SoC.

---

## 5. Utilidades y Extras (`utils/`)

Una extensa caja de herramientas a disposición del firmware y de todo aquél que programe una App.
- **`Menu.py`**: El fabuloso motor de renderizado asíncrono de Interfaz de Usuario. Gestiona el encolamiento de elementos, scroll de pantallas pequeñas, resaltado automático (cuadros, texto invertido), compresión de iconos, y renderización a un buffer PIL de imagen plano compatible con `Display`.
- **`Logging.py`**: Un interceptor avanzado fabricado como Singleton. Genera e imprime trazas de consola coloreadas para el debugger usando las normativas `DEBUG`, `INFO` o `ERROR`, a la par que vuelca todo discretamente en archivos rotativos dentro de la carpeta global `/logs` para analizar fallos fatales tras un bloqueo.
- **`Singleton.py`**: Clase base de control de memoria. Fuerza a que componentes únicos de Hardware (La Pantalla y el puerto I2C o el SPI) sólo posean una instancia virtual viva en la memoria del programa de Python a la vez, eludiendo problemas de asincronía y colisiones.
- **`telemetry.py` / `resilience.py`**: Componentes auxiliares para monitorizar la salud interna del sistema operativo y lanzar alertas de recursos (RAM, Storage, Temps).
- **`Web/`**: Subservidor local basado en Flask/Werkzeug que renderiza y sirve las plantillas web dinámicas (por ejemplo el simulador de pantalla incrustado en `templates/index.html`).

---

## 6. Lógica de UI / Estética Global (`themes/` y `fonts/`)

El modelo visual de PiPerW se renderiza primero en Memoria RAM a través de componentes gráficos usando el estándar en Python **Pillow (PIL)**.
- **`fonts/`**: Ficheros crudos `.ttf` accesibles mediante path para que todo texto posea un aspecto Cyberpunk/Retro constante sin depender del SO emisor.
- **`themes/`**: El entorno está preparado para que el usuario pueda aplicar estéticas visuales diferentes. Cada carpeta de un tema (v.g. el preconfigurado en `default/`) hereda de `theme_interface.py` y carga sus propios constantes definitorias de colores y márgenes, al igual que todos los extras gráficos provistos sobre su subdirectorio interno `/resources/` o frames pre-búffer localizados para acelerar las transiciones en pantallas OLED pequeñas en su subcarpeta `/frames/`.

---

## 7. Dependencias Comunes y Temporales (`lib/` y `tmp/`)

- **`lib/`**: Este espacio almacena software "intrusivo", como integraciones de bajo nivel con el Kernel de GNU/Linux o repositorios enteros clonados al vuelo. En `lib/gadget/hid_script` radica los scripts nativos en bash que instancian en tiempo real un Dispositivo Composite USB mediante `/sys/kernel/config/usb_gadget`, posibilitando mágicamente emular un teclado físico e inyectar payloads con aplicativos tipo Pi Pico BadUSB. Igualmente, las liberías foráneas (como el entorno de utilidades RPi) si fueron especificadas como requerimiento en Github, la utilidad interna de *Deendency Manager* las aislará y descargará por ti directamente de forma silenciosa dentro de `lib/`.
- **`tmp/`**: Ubicación para la recolección efímera de volcados de datos binarios y volcados de disco. Ficheros como las tablas en Excel separadas por comas (`.csv` procedentes de `airodump-ng`) o las capturas de paquetes WPA (ficheros `.pcap` y `.cap` generados por el Handshake de Aircrack) viven aquí temporalmente hasta que un script termina de procesarlos. Su contenido es susceptible de borrado entre reinicios o reseteos de interfaz.