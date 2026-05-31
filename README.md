<div align="center">
  <h1>PiPerW</h1>
  <p><b>El Framework Definitivo de Auditoría Inalámbrica y Pentesting Físico para Raspberry Pi</b></p>
  
  <p>
    <img src="https://img.shields.io/badge/OS-Kali%20Linux-blue?style=for-the-badge&logo=kali-linux" alt="Kali Linux" />
    <img src="https://img.shields.io/badge/Hardware-RPi%20Zero%202%20W-c2185b?style=for-the-badge&logo=raspberry-pi" alt="Raspberry Pi" />
    <img src="https://img.shields.io/badge/Python-3.9%2B-yellow?style=for-the-badge&logo=python" alt="Python 3" />
  </p>
</div>

---

## Índice
- [Acerca del Proyecto](#acerca-del-proyecto)
- [Módulos Soportados](#módulos-soportados)
- [Requisitos Previos](#requisitos-previos)
- [Guía de Instalación](#guía-de-instalación)
- [Aviso Legal](#aviso-legal)

---

## Acerca del Proyecto

**PiPerW** transforma su **Raspberry Pi Zero 2 W** (y placas compatibles) en una plataforma de seguridad ofensiva portátil. Diseñado para operar de forma desatendida o mediante interfaces ligeras, consolida múltiples vectores de ataque en un único framework cohesivo, permitiendo su uso rápido y automatizado en auditorías de campo.

## Módulos Soportados

- **WiFi:** Desautenticación, escaneo, Beacon Flooding, captura de Handshakes (requiere adaptador en modo monitor).
- **Bluetooth:** Escaneo, análisis y pruebas de concepto en dispositivos BLE y clásicos.
- **Sub-GHz:** Interacción con frecuencias sub-gigahercio utilizando transceptores externos (como el CC1101).
- **RFID/NFC:** Lectura, clonación y emulación de tarjetas en múltiples bandas.
- **BadUSB:** Inyección de pulsaciones de teclado (compatible con DuckyScript) aprovechando el puerto OTG (USB Gadget) de la Raspberry.
- **Utilidades:** Monitorización del sistema, generación de contraseñas, resiliencia de hilos y configuraciones avanzadas.

---

## Requisitos Previos

Para garantizar la máxima compatibilidad con scripts de inyección, drivers de monitorización y conectividad de bajo nivel, **PiPerW** está construido y verificado sobre sistemas **Kali Linux ARM**.

1. **Documentación Oficial:**
   Consulte la [guía de Kali Linux para la Raspberry Pi Zero 2 W](https://www.kali.org/docs/arm/raspberry-pi-zero-2-w/).
2. **Descarga de la Imagen Oficial:**
   Obtenga la ISO correspondiente para su hardware desde el sitio web oficial:
   [Descargar Kali Linux para plataformas ARM](https://www.kali.org/get-kali/#kali-platforms).

---

## Guía de Instalación

### 1. Preparación de la MicroSD
Utilice su software de flasheo preferido para grabar la imagen descargada en su tarjeta MicroSD. Algunas herramientas recomendadas:
- [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
- [Balena Etcher](https://balena.io/etcher/)
- [Rufus](https://rufus.ie/)

### 2. Primer Arranque y Acceso
Inserte la tarjeta MicroSD en la Raspberry Pi, conecte la alimentación y periféricos básicos mínimos.
Una vez que el sistema operativo complete el arranque, inicie sesión:

- **Usuario:** `kali`
- **Contraseña:** `kali`

Dado que la instalación y administración de redes requiere privilegios, escale a superusuario:
```bash
sudo su
```

### 3. Configuración de Red
Conecte su Raspberry Pi a la red WiFi local usando el administrador de red de consola `nmcli`.

```bash
# Habilitar las capacidades de red y permitir la interfaz wlan0
nmcli networking on
nmcli dev set wlan0 managed yes

# Listar las redes WiFi disponibles
nmcli dev wifi list

# Conectar a la red seleccionada (reemplace <SSID> por el nombre de su red)
nmcli dev wifi connect "<SSID>" --ask
``` 
*(Nota: La consola solicitará la contraseña para el SSID indicado).*

### 4. Actualización del Sistema
Antes de intentar descargar e instalar el framework, **es indispensable actualizar el sistema**. Esto previene incompatibilidades de paquetes y conflictos con las cabeceras del kernel.
```bash
apt update -y && apt upgrade -y
```

### 5. Instalación de PiPerW
Puede proceder directamente desde la placa o mediante **SSH** desde otro equipo (recomendado para facilitar las tareas operativas).
*Si utiliza SSH, conecte mediante `ssh kali@<IP_RASPBERRY>`, y luego vuelva a ejecutar `sudo su`.*

```bash
# Clonar este repositorio en la Raspberry Pi
git clone https://github.com/TU-USUARIO/PiPerW.git
cd PiPerW

# Conceder permisos y ejecutar el script de instalación automática
chmod +x install.sh
./install.sh
```

> **Aviso Importante:** El instalador `install.sh` se encargará de gestionar las dependencias de APT, configurar los entornos virtuales de Python (PIP), ajustar LightDM para autologin, habilitar las interfaces I2C/SPI y establecer el modo **OTG USB** (Gadget). 
> 
> **El sistema se reiniciará automáticamente al concluir para aplicar los módulos del núcleo.**

---

## Aviso Legal

**Descargo de Responsabilidad:** *PiPerW* ha sido desarrollado estricta y exclusivamente para propósitos educativos, auditorías de seguridad autorizadas y experimentación de pentesting legal. Los desarrolladores y contribuidores no se hacen responsables de ningún daño, perjuicio o uso indebido de esta herramienta. **El uso de PiPerW es bajo su propia responsabilidad; asegúrese siempre de contar con autorización por escrito antes de auditar infraestructuras de terceros.**
