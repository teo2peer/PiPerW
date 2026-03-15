#!/bin/bash
# PiPerW Setup Script
# Exit on any error, unless in an if statement
set -e

RED="\e[31m"
GREEN="\e[32m"
YELLOW="\e[33m"
BLUE="\e[34m"
MAGENTA="\e[35m"
ENDCOLOR="\e[0m"

# Helper functions for better UI
info() { echo -e "\n${BLUE}[*] $1${ENDCOLOR}"; }
success() { echo -e "${GREEN}[+] $1${ENDCOLOR}"; }
warning() { echo -e "${YELLOW}[!] $1${ENDCOLOR}"; }
error() { echo -e "${RED}[X] $1${ENDCOLOR}"; exit 1; }

# Check for root privileges
if [[ $EUID -ne 0 ]]; then
    error "This script must be run as root. Try: sudo ./install.sh"
fi

info "Welcome to PiPerW Installer"

info "Updating package lists..."
apt-get update -y

info "Installing kernel headers..."
apt-get install -y linux-headers-rpi-v7 linux-headers-rpi-v7l || warning "Could not install all kernel headers. Continuing anyway..."

info "Installing core APT dependencies..."
apt-get install -y python3 python3-dev python3-pip python3-virtualenv python3-venv python3-bluez python3-toml
apt-get install -y ifstat libffi-dev libssl-dev direnv ondir virtualenv util-linux-extra
apt-get install -y libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev libopenjp2-7 i2c-tools fonts-dejavu bluez libgfortran5 libopenblas0-pthread
apt-get install -y git libgmp3-dev gawk qpdf bison flex make autoconf libtool texinfo
apt-get install -y python3-numpy python3-pil python3-smbus

#---------------------------
#     Autologin
#---------------------------
info "Configuring LightDM Autologin for user kali..."
if [ -f /etc/lightdm/lightdm.conf ]; then
    if ! grep -q "^\[SeatDefaults\]" /etc/lightdm/lightdm.conf; then
        echo -e "\n[SeatDefaults]" >> /etc/lightdm/lightdm.conf
    fi
    sed -i "/^\[SeatDefaults\]/a autologin-user=kali\nautologin-user-timeout=0" /etc/lightdm/lightdm.conf
    # Clean duplicates if appended multiple times
    sed -i "/^autologin-user=/d" /etc/lightdm/lightdm.conf
    sed -i "/^autologin-user-timeout=/d" /etc/lightdm/lightdm.conf
    sed -i "/^\[SeatDefaults\]/a autologin-user=kali\nautologin-user-timeout=0" /etc/lightdm/lightdm.conf
    systemctl restart lightdm || true
    success "Autologin configured."
else
    warning "LightDM config not found. Skipping autologin setup."
fi

info "Setting default systemd target to CLI (multi-user.target)..."
systemctl set-default multi-user.target > /dev/null 2>&1 || true

#---------------------------
#     Hardware Interfaces
#---------------------------
info "Enabling SPI, I2C, and Serial via raspi-config..."
if command -v raspi-config > /dev/null; then
    raspi-config nonint do_spi 0
    raspi-config nonint do_i2c 0
    raspi-config nonint do_serial 0
    success "Hardware interfaces enabled."
else
    warning "raspi-config not found. Are you on a Raspberry Pi? Skipping..."
fi

#---------------------------
#     Swap Configuration
#---------------------------
if [ ! -f /kali.swap ]; then
    info "Creating 2GB swap file..."
    dd if=/dev/zero of=/kali.swap bs=1M count=2048 status=progress
    chmod 600 /kali.swap
    mkswap /kali.swap
    swapon /kali.swap
    if ! grep -q "kali.swap" /etc/fstab; then
        echo "/kali.swap none swap sw 0 0" >> /etc/fstab
    fi
    success "Swap configured."
else
    success "Swap file already exists."
fi

#---------------------------
#     Hardware Clock (RTC)
#---------------------------
info "Configuring Hardware Clock Modules (DS1307)..."
for mod in i2c-bcm2708 i2c-dev rtc-ds1307; do
    if ! grep -q "^$mod$" /etc/modules; then
        echo "$mod" >> /etc/modules
    fi
done

if ! grep -q "ds1307" /etc/rc.local; then
    sed -i -e "$i \echo ds1307 0x68 > /sys/class/i2c-adapter/i2c-1/new_device\n" /etc/rc.local
fi

if ! grep -q "hwclock -s" /etc/rc.local; then
    sed -i -e "$i \hwclock -s\n" /etc/rc.local
fi
success "RTC Clock persistence injected."

#---------------------------
#     Storage & Gadget
#---------------------------
if [ ! -f /PiPerW.img ]; then
    info "Creating 4GB FAT32 USB Image for Composite Gadget..."
    dd if=/dev/zero of=/PiPerW.img bs=1M count=4096 status=progress
    mkdosfs /PiPerW.img
    success "Drive image created."
else
    success "USB Drive image already exists."
fi

info "Configuring USB OTG Gadget Engine..."
if [ -f /boot/config.txt ]; then
    if ! grep -q "dtoverlay=dwc2" /boot/config.txt; then
        echo "dtoverlay=dwc2" >> /boot/config.txt
    fi
fi
for mod in dwc2 libcomposite; do
    if ! grep -q "^$mod$" /etc/modules; then
        echo "$mod" >> /etc/modules
    fi
done
chmod +x ./PiPerW/lib/gadget/hid_script || true

if ! grep -q "hid_script" /etc/crontab; then
    echo "@reboot root $(pwd)/PiPerW/lib/gadget/hid_script" >> /etc/crontab
fi
success "USB Gadget configured in system crontab."

#---------------------------
#     Python Env settings
#---------------------------
info "Configuring PIP settings..."
mkdir -p /etc
touch /etc/pip.conf
if ! grep -q "\[global\]" /etc/pip.conf; then
    echo "[global]" >> /etc/pip.conf
fi
if ! grep -q "extra-index-url=" /etc/pip.conf; then
    echo "extra-index-url=https://www.piwheels.org/simple" >> /etc/pip.conf
fi
if ! grep -q "break-system-packages" /etc/pip.conf; then
    echo "break-system-packages = true" >> /etc/pip.conf
fi

info "Installing PIP Core requirements..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt || warning "Some PIP requirements failed depending on your CPU arch."


echo -e "\n${MAGENTA}------------------------------------------------${ENDCOLOR}"
echo -e "${YELLOW}Deseas pre-instalar las dependencias de las Aplicaciones ahora?${ENDCOLOR}"
echo -e "${YELLOW}(Si eliges n, se instalaran en tiempo real la primera vez que abras el app).${ENDCOLOR}"
read -p "[Y/n]: " response
if [[ "$response" =~ ^([yY][eE][sS]|[yY]|)$ ]]; then
    info "Iniciando Pre-instalacion de Dependencias APPs..."
    python3 preinstall_apps_deps.py
else
    info "Omitido. Las dependencias se resolveran on-demand en la Placa."
fi


success "PiPerW Setup Completed Successfully!"
info "Please reboot to apply kernel, display and I2C changes."
read -n 1 -s -r -p "Press any key to REBOOT now... (or CTRL+C to cancel)"
reboot
