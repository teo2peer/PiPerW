<div align="center">
  <!-- Puedes agregar un logo aquí -->
  <h1>🏴‍☠️ PiPerW 🏴‍☠️</h1>
  <p><b>El Framework Definitivo de Auditoría Inalámbrica y Pentesting Físico para Raspberry Pi</b></p>
  
  <p>
    <img src="https://img.shields.io/badge/OS-Kali%20Linux-blue?style=for-the-badge&logo=kali-linux" alt="Kali Linux" />
    <img src="https://img.shields.io/badge/Hardware-RPi%20Zero%202%20W-c2185b?style=for-the-badge&logo=raspberry-pi" alt="Raspberry Pi" />
    <img src="https://img.shields.io/badge/Python-3.9%2B-yellow?style=for-the-badge&logo=python" alt="Python 3" />
  </p>
</div>

---

## 📖 Índice
- [Acerca del Proyecto](#-acerca-del-proyecto)
- [Módulos Soportados](#-módulos-soportados)
- [Requisitos Previos](#-requisitos-previos)
- [Guía de Instalación](#-guía-de-instalación)
- [Aviso Legal](#-aviso-legal)

---

## 🎯 Acerca del Proyecto

**PiPerW** transforma tu **Raspberry Pi Zero 2 W** (y placas compatibles) en una navaja suiza de seguridad ofensiva portátil. Diseñado para operar de forma desatendida o mediante interfaces ligeras, consolida múltiples vectores de ataque en un único framework cohesivo, permitiendo su uso rápido y automatizado en auditorías de campo.

## ⚡ Módulos Soportados

- 📡 **WiFi:** Desautenticación, escáner, Beacon Flooding, captura de Handshakes (requiere adaptador en modo monitor).
- 🔵 **Bluetooth:** Escaneo, análisis y ataques a dispositivos BLE y clásicos.
- 📻 **Sub-GHz:** Interacción con frecuencias sub-gigahercio utilizando transceptores externos limitados de forma eficiente (como el CC1101).
- 💳 **RFID/NFC:** Lectura, clonación y emulación de tarjetas en múltiples bandas.
- 🦆 **BadUSB:** Inyección de *keystrokes* (estilo DuckyScript) aprovechando el puerto OTG (USB Gadget) de la Raspberry.
- 🛠️ **Utilidades:** Monitorización del sistema, generación de contraseñas, resiliencia de hilos y configuraciones ad-hoc.

---

## 📋 Requisitos Previos

Para garantizar la máxima compatibilidad con scripts de inyección, drivers de monitorización y conectividad de bajo nivel, **PiPerW** está construido y probado exclusivamente sobre sistemas **Kali Linux ARM**.

1. **Lee detenidamente la Documentación Oficial:**
   Revisa la [guía de Kali Linux para la Raspberry Pi Zero 2 W](https://www.kali.org/docs/arm/raspberry-pi-zero-2-w/).
2. **Descarga la Imagen Oficial:**
   Obtén la ISO ("image") para tu hardware directamente de su web:
   [Descargar Kali Linux ARM Platforms](https://www.kali.org/get-kali/#kali-platforms).

---

## ⚙️ Guía de Instalación

### 1️⃣ Preparación de la MicroSD
Utiliza tu software de flasheo preferido para grabar la imagen descargada en tu tarjeta MicroSD. Algunas herramientas recomendadas:
- [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
- [Balena Etcher](https://balena.io/etcher/)
- [Rufus](https://rufus.ie/)

### 2️⃣ Primer Arranque y Acceso
Inserta la tarjeta MicroSD en la Raspberry Pi, conéctale alimentación y un monitor/teclado.
Una vez que el sistema operativo complete el arranque, inicia sesión:

- **Usuario:** `kali`
- **Contraseña:** `kali`

Dado que la instalación y administración de redes requiere privilegios, escala directamente a *superusuario*:
```bash
sudo su
```

### 3️⃣ Configuración de Red (Internet)
Deberás conectar tu Raspberry Pi a la red WiFi local usando el administrador de líneas de comandos `nmcli`.

```bash
# 1. Asegúrate de encender las capacidades de red y permitir la interfaz wlan0
nmcli networking on
nmcli dev set wlan0 managed yes

# 2. Lista las redes WiFi disponibles en tu rango
nmcli dev wifi list

# 3. Conéctate a tu red elegida (reemplaza <SSID> por el nombre de tu red)
nmcli dev wifi connect "<SSID>" --ask
``` 
*(Nota: La consola te solicitará la contraseña para el SSID indicado).*

### 4️⃣ Actualización del Sistema
Antes de intentar descargar e instalar cualquier framework, **debes actualizar Kali**. Esto previene incompatibilidades de empaquetado y evita errores con las cabeceras del kernel (linux-headers).
```bash
apt update -y && apt upgrade -y
```

### 5️⃣ Instalación de PiPerW
Ya puedes continuar directamente en la placa o si lo prefieres, usando **SSH** desde otro ordenador (recomendado para pegar comandos).
*Si usas SSH, conéctate con `ssh kali@<IP_RASPBERRY>`, y luego vuelve a ejecutar `sudo su`.*

```bash
# 1. Clona este repositorio en tu Raspberry Pi
git clone https://github.com/TU-USUARIO/PiPerW.git
cd PiPerW

# 2. Concede permisos y ejecuta el script de instalación automática
chmod +x install.sh
./install.sh
```

> 🔥 **Importante:** El instalador `install.sh` se encargará de instalar dependencias APT, generar entornos virtuales de Python (PIP), reconfigurar LightDM para autologin de usuario, habilitar el I2C/SPI y establecer el modo **OTG USB** (Gadget). 
> 
> **La placa se reiniciará automáticamente al terminar para aplicar los módulos de Kernel.**

---

## ⚖️ Aviso Legal

> **Disclaimer:** *PiPerW* ha sido desarrollado única y exclusivamente para propósitos educativos, auditorías de seguridad autorizadas y experimentación de pentesting legal. Los creadores y contribuidores no se hacen responsables de ningún daño, perjuicio o uso ilícito de esta herramienta. **Utiliza PiPerW bajo tu propia responsabilidad y asegúrate siempre de tener permiso por escrito antes de auditar infraestructuras ajenas.**
