#!/bin/bash

# Update the package list and install required packages
echo "Updating package list and installing required packages..."
sudo apt-get update

echo "Installing re4son kernel..."
echo "deb http://http.re4son-kernel.com/re4son/ kali-pi main" > /etc/apt/sources.list.d/re4son.list
wget -O - https://re4son-kernel.com/keys/http/archive-key.asc | apt-key add -
apt update
apt install -y kalipi-kernel kalipi-bootloader kalipi-re4son-firmware kalipi-kernel-headers libraspberrypi0 libraspberrypi-dev libraspberrypi-doc libraspberrypi-bin

echo "Installing dependencies..."

sudo apt-get install python3-dev python3-pip libffi-dev libssl-dev -y
sudo apt-get install python3-numpy -y
sudo apt-get install ifstat -y
sudo apt-get install python3 python3-pip python3-pil libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev libopenjp2-7   python3-dev python3-smbus i2c-tools python3-pip python3-venv fonts-dejavu -y
sudo apt install git libgmp3-dev gawk qpdf bison flex make autoconf libtool texinfo -y
sudo pip3 install --upgrade pip
sudo pip3 install -r requirements.txt


# Enable autologin by editing lightdm.conf
echo "Enabling autologin by editing lightdm.conf..."

# Ensure autologin-user=kali and autologin-user-timeout=0 exist under [SeatDefaults]
SEAT_DEFAULTS_FOUND=$(grep -q "^\[SeatDefaults\]" /etc/lightdm/lightdm.conf && echo "yes" || echo "no")

if [[ "$SEAT_DEFAULTS_FOUND" == "yes" ]]; then
    echo "[SeatDefaults] found. Checking autologin settings..."

    AUTOL_LOGIN_USER=$(grep -q "^autologin-user=kali" /etc/lightdm/lightdm.conf && echo "yes" || echo "no")
    AUTOLOGIN_USER_TIMEOUT=$(grep -q "^autologin-user-timeout=0" /etc/lightdm/lightdm.conf && echo "yes" || echo "no")

    if [[ "$AUTOL_LOGIN_USER" == "no" ]]; then
        echo "autologin-user=kali not found. Adding it..."
        sudo sed -i "/^\[SeatDefaults\]/a autologin-user=kali" /etc/lightdm/lightdm.conf
    else
        echo "autologin-user=kali already exists."
    fi

    if [[ "$AUTOLOGIN_USER_TIMEOUT" == "no" ]]; then
        echo "autologin-user-timeout=0 not found. Adding it..."
        sudo sed -i "/^\[SeatDefaults\]/a autologin-user-timeout=0" /etc/lightdm/lightdm.conf
    else
        echo "autologin-user-timeout=0 already exists."
    fi
else
    echo "[SeatDefaults] section not found. Adding it with autologin settings..."
    echo -e "\n[SeatDefaults]\nautologin-user=kali\nautologin-user-timeout=0" | sudo tee -a /etc/lightdm/lightdm.conf
fi

# Restart the lightdm service to apply changes
echo "Restarting lightdm service..."
sudo service lightdm restart

# Set the default systemd target to multi-user
echo "Setting the default systemd target to multi-user..."
sudo systemctl set-default multi-user.target

# Enable SPI, I2C, and Serial through raspi-config
echo "Enabling SPI, I2C, and Serial interfaces using raspi-config..."
sudo raspi-config nonint do_spi 0
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_serial 0

# Create and configure a swap file
echo "Creating and configuring a swap file..."
sudo dd if=/dev/zero of=/name.swap.tmp bs=1024 count=2097152
sudo mv /name.swap.tmp /name.swap
sudo chmod 600 /name.swap

# Setting up the swap space
echo "Setting up the swap space..."
sudo mkswap /name.swap
sudo swapon /name.swap


# Indicate that the script execution is complete
echo "Script execution completed."
