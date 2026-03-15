# Directorio: lib/ (y tmp/)

Dentro de PiPerW estas carpetas actúan como lugares de almacenamiento intermedio global expuesto a subprocesos o recursos foráneos no controlados directamente por el ecosistema de Python normal.

## `lib/` (Librerías Nativas y Clones)

1. **`gadget/hid_script`**: Un área vital de modificación de kernel. Este archivo `.sh` interactúa con el framework de subsistema USB para crear un `USB Gadget` en Linux tipo "Composite Device". Literalmente modifica las banderas a nivel de SO y re-enlaza módulos virtuales (como `dwc2` y `libcomposite`) a registros locales (/sys/kernel/config/usb_gadget/piperw/) para falsificar identidades USB frente a otro ordenador (Logrando que la Raspberry engañe a un Windows identificándose como si en realidad usted hubiese pinchado un Teclado + Ratón + Interfaz RNDIS). Usado extensivamente por la utilidad `pico-badusb` y funciones Rubber Ducky.
2. **Autodescarga Git**: Gracias al Dependency Manager guiado por los `manifest.toml`, cualquier requerimiento que sea marcado explicitamente como de un array de "Github", clonará un subrepositorio de git directamente aquí, logrando compartición del path sin requerir instalaciones estáticas globales.

---

## `tmp/` (Temporales Volátiles)

El basurero temporal de software de hacking. A veces utilidades desarrolladas para sistemas Linux (como el pack `aircrack-ng` o escaneres SubGhz) no poseen bindings por Python nativos. 
1. **Delegación de Submódulos**: Por ende, una app como *Deauth* o *Handshake Capture* delegará un demonio `Popen` invocando `sudo airodump-ng ... -w PiPerW/tmp/scan` mientras tu App en Python aguarda dormida observando la interfaz para luego procesar los resultados `.csv` expuestos aquí temporalmente.
2. **Volatilidad**: El código prevé que el contenido de esta carpeta esté sujeto a continua pérdida de estado. Los programadores saben que no debe guardarse información maestra en `tmp/`.