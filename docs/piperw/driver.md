# Directorio: driver/

La capa `driver/` traduce las llamadas estandarizadas definidas en las `interfaces` a una ejecución lógica para hardware real por parte del procesador de periférico correspondiente.

Está internamente segmentada en carpetas que representan el "tipo" de hardware que se está impulsando:

## 1. `display/`
Motores de renderizado encargados de empujar los buffers de imagen hacia la pantalla.
- **`sh1106/`** y **`ssd1306/`**: Exitosos controladores monocromáticos para las mini-pantallas OLED I2C de 1.3" y 0.96".
- **`st7735S/`**: Para pantallas LCD SPI a color (típicas en diversos HATs de Raspberry o pantallas TFT).
- **`only_web/`**: Este es un **driver virtual**. De inmensa utilidad para los programadores. Si el sistema se arranca en un PC, no intentará buscar I2C, sino que dirigirá en tiempo real el buffer interno a un servidor Flask (alojado en `utils/Web`) para que la pantalla del PiPerW pueda ser probada gráficamente abriendo `localhost` en tu navegador.

## 2. `pheripherals/`
Controladores encargados de atrapar las interrupciones o cambios de estado físicos de los controles y transformarlos en eventos legibles.
- **`keyboard/`**: Mapea físicamente las pulsaciones del teclado del PC del programador a eventos lógicos (flechas y enter al framework).
- **`waveshare_hat/`**: Diseñado para el popular addon de Raspberry Pi. Contiene el mapeo de resistencias *pull-up/pull-down* del joystick omnidireccional y los botones laterales (KEY1, KEY2) hacia los controles estándar del menú (arriba, abajo, seleccionar).

## 3. `SubGHz/`
Controladores de transceptores de radio externos.
- **`CC1101/`**: Lógica de interacción SPI para este famoso chip transceptor de ultra-baja potencia. Posee un script **`reg.py`** ultra-detallado que documenta y mapea en hexadecimal los registros requeridos para reescribir la memoria del chip que lo sintoniza en diferentes frecuencias (433MHz, 868MHz, 915MHz) para los ataques domóticos y de clonación de garajes presentes en la carpeta de aplicaciones `Sub-GHz`.