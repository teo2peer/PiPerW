# Directorio: interfaces/

Aquí es donde reside el "Contrato de Software" del sistema. PiPerW obliga al aislamiento entre la capa base y las extensiones. Las interfaces dictaminan cómo pueden comportarse tanto los drivers que crean la capa de abstracción de hardware (HAL), como las aplicaciones de usuario de un tercero.

### `app_interface.py`
Provee una clase abstracta `AppInterface` de la cual ***toda*** aplicación de la carpeta `apps/` debe heredar obligatoriamente.
* **Ciclo de vida**: Administra un objeto oculto interno (`_thread`) inyectado por `main.py` antes de llamar al logíco `run()`. De esta forma la app obtiene la función vital `.is_stopped()`.
* **Metadatos y Cacheo**: Reemplaza el paso de parámetros hardcodeados leyendo y parseando directamente sobreescribiendo una caché del `manifest.toml` colindante en la carpeta propia de la app.
* **Persistencia local**: Encapsula métodos tipo `get_state_dir()` y `save_state()` para impedir que las apps del usuario escriban basura o generen logs ilegales fuera de los límites de las carpetas `/data/<nombre_app>` designadas, con opción de acceso especial a carpeta de exportación vía web o usb (`get_public_dir()`).

### `display_interface.py`
Contrato para crear sub-placas. Todo driver en el directorio `driver/display/` debe cumplirlo sin excusa:
* Enmarca funciones estandarizadas `.init()`, `.clear()`, y las lógicas primarias para dibujar como `.text(string, color, coords)` o `.image(PIL.Image)`. Gracias a esto, un desarrollador externo no tiene que crear código independiente según si su software correrá en pantallas SH1106 de 128x64 o en un monitor a Full HD color. 

### `pheripheral_interface.py`
Normaliza todos los posibles "inputs" al framework principal definiendo los enums maestros lógicos:
* Todo teclado Bluetooth, Hat con pines embebidos, simulación en PC o driver futuro de rotación (rotary encoder) **DEBE ENVIAR** diccionarios que coincidan con la acción de tipo de evento lógico `UP`, `DOWN`, `SELECT`, `BACK`, `EXIT`. De esa manera asimila y centraliza los flujos de hardware con una misma interpretación genérica global.