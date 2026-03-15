# Archivos Core en la Raíz (`PiPerW/`)

Bajo el directorio base existen dos archivos sumamente clave que asocian todas las ramificaciones explicadas anteriormente (Drivers, Periféricos y UI) y se encargan de enlazarlas.

## `helpers.py`

Contiene la columna vertebral de dependencias de todo el sistema. Si el firmware fuera un esqueleto, los módulos de `helpers` serían la médula espinal.

* **Inicialización temprana**: Es el primer archivo en dictaminar si se cargan los loggers, instanciar clases de lectura de parámetros del disco y resolver si el entorno cuenta con requisitos especiales antes de exportar clases globales como `Config`.
* **Wrappers de Directorio**: Instancia utilitarios puramente sistémicos (Como `DirFilter` que agrupa sentencias for/loops oscuras de manejo del sistema de archivos `os` de importación sucia).
* **El módulo de concurrencia inyectable `WThread`**: 
  El subsistema más crítico. Es un envoltorio para la librería nativa de `threading.Thread`. PiPerW **no delega el control** al código de una Aplicación de forma bruta, PiPerW lo aísla.
  Esta clase adjunta a la instancia paralelizada de la ap un evento o señal bloqueante `_stop_event`. Está diseñado concretamente con un propósito: Funcionar como **Dead Man's Switch (Interruptor del Hombre Muerto)**. En el caso crítico de que los autores de la Aplicación hagan un `While True: pass` impune y provoquen que todo el equipo se quede congelado (algo que arruinaría un dispositivo embebido portátil obligando a desenchufarlo de la batería), `WThread` da poder a `main.py` a inyectar eventos remotos y exigir a esa clase que suspenda y devuelva de inmediato el control y el estado de detención (`.is_stopped()`) para rescatar la Interfaz Principal y prevenir bloqueos catastróficos.

## `setup.py`

Archivo que se dispara desde `main.py` pero cuyo rol es únicamente el de **Validación de Primera Ejecución y Pre-Configuracion**.

* Detecta si es la primera vez que se monta esta versión de Firmware en el host.
* Lee el kernel para comprobar si corres sobre un *Darwin*, *Linux nativo*, en *Windows* o *RPi*. (Módulo clave por el cual el `driver/dispaly/only_web/` se precarga por fallo y omisión si detecta que no estás en una placa de hardware embebido de la familia Broadcom/ARM lícita para ejecutar I2C).
* Configuración de Rutas predefinidas base requeridas (Como verificar la creación o falta de permisos en el anidado de `public/` y alertar a consola mediante logs crudos y primitivos).