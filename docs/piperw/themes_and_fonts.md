# Directorios: themes/ y fonts/

Gran parte del "branding" y el flujo lógico-visual de PiPerW vive completamente desacoplado de los microcálculos de píxeles en hardware mediante estras tres carpetas dedicadas a personalizar visualmente un entorno muy hostil y de escasos recursos.

## `themes/`
Los "temas" no solo implican colores, sino que agrupan lógicas matemáticas de dibujado dentro del display genérico. 

* **`theme_interface.py`**: Interfaz base. Cualquier tema que programes deberá incluir esta jerarquía para asegurar que se definen variables exigidas por aplicaciones o Menús como `background_color` y `accent_color`.
* **Tema `default/`**:
  * **`__init__.py`**: Aquí se sobreescriben constantes, como el relleno (padding), el grosor de border al estar sobre un elemento y si quieres que se aplique un texto inverso (invertir bits) sobre el índice seleccionado actual en los menús que dibuja PIL.
  * **`/frames/`**: Para pantallas de gama baja OLED conectadas en I2C con bajos FPS las aplicaciones deben evitar calcular cosas costosas. Esta carpeta suele empaquetar animaciones cuadro a cuadro pre-procesadas para facilitar carga, logotipos precargados y elementos repetitivos con sus transformaciones espaciales calculadas y serializadas previamente.
  * **`/resources/`**: Iconos estáticos representativos. Son recargados y servidos a la clase `Menu` a petición cuando se especifican `icons=True`.

## `fonts/`
PiPerW se apoya un 100% en TrueType Fonts (`.ttf`) gracias a su estrecho vínculo con la API de `Pillow (PIL)`.
Todo el firmware central lee de este directorio unificadamente la fuente `pixel.ttf` u otras opciones del estilo para inyectarle parámetros al sistema de cálculo predictivo de colisiones (`text_bbox` de PIL), de modo que puedan realizar las complejas operaciones de justificación y centrado de textos asumiendo unos DPI predeterminados que empaten con resoluciones diminutas (128x64 px o 160x80 px).