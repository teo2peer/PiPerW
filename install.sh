#!/bin/bash

# Check if the script is being run as root
if [[ $EUID -ne 0 ]]; then
    echo "Please run the script as root."
    exit 1
fi


# Update the package list and install required packages
echo "Updating package list and installing required packages..."
sudo apt-get update

echo "Installing re4son kernel..."
echo "deb http://http.re4son-kernel.com/re4son/ kali-pi main" > /etc/apt/sources.list.d/re4son.list
wget -O - https://re4son-kernel.com/keys/http/archive-key.asc | apt-key add -
sudo apt update
sudo apt install -y kalipi-kernel kalipi-bootloader kalipi-re4son-firmware kalipi-kernel-headers libraspberrypi0 libraspberrypi-dev libraspberrypi-doc libraspberrypi-bin

echo "Installing dependencies..."

sudo apt-get install python3 python3-dev python3-pip python3-virtualenv  -y
sudo apt-get install ifstat libffi-dev libssl-dev direnv ondir virtualenv -y
sudo apt-get install libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev libopenjp2-7 i2c-tools fonts-dejavu bluez libgfortran5 libopenblas0-pthread -y
sudo apt install git libgmp3-dev gawk qpdf bison flex make autoconf libtool texinfo -y

# install python packages modules
echo "Installing python packages..."
sudo apt-get install python3-numpy python3-pil  python3-dev python3-smbus python3-venv python3-bluez python3-toml  -y

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
echo "Setting the default systemd target to 3..."
sudo systemctl set-default multi-user.target
sudo systemctl isolate multi-user.target


# Enable SPI, I2C, and Serial through raspi-config
echo "Enabling SPI, I2C, and Serial interfaces using raspi-config..."
sudo raspi-config nonint do_spi 0
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_serial 0

# Create and configure a swap file
echo "Creating and configuring a swap file..."

# check if the file exists
if [ -f /kali.swap ]; then
    echo "kali.swap already exists."
else
    sudo dd if=/dev/zero of=/kali.swap.tmp bs=1024 count=2097152
    sudo mv /kali.swap.tmp /kali.swap
    sudo chmod 600 /kali.swap

    # Setting up the swap space
    echo "Setting up the swap space..."
    sudo mkswap /kali.swap
    sudo swapon /kali.swap
    sudo echo "/kali.swap none swap sw 0 0" >> /etc/fstab
fi



# adding otg support for bad_usb
echo "Adding OTG support for BadUSB..."

# check if the line exists in the file
if grep -q "dtoverlay=dwc2" /boot/config.txt; then
    echo "dtoverlay=dwc2 already exists in /boot/config.txt."
else
    echo "dtoverlay=dwc2" | sudo tee -a /boot/config.txt
fi

if grep -q "dwc2" /etc/modules; then
    echo "dwc2 already exists in /etc/modules."
else
    echo "dwc2" | sudo tee -a /etc/modules
fi

if grep -q "libcomposite" /etc/modules; then
    echo "libcomposite already exists in /etc/modules."
else
    echo "libcomposite" | sudo tee -a /etc/modules
fi


echo "Creating a 4GB file for the USB drive..."
# Create a 4gb file for the USB drive

# check if the file exists
if [ -f /PiPerW.img ]; then
    echo "PiPerW.img already exists."
else
    FILE=/PiPerW.img
    MNTPOINT=/mnt/usb_piperw

    dd if=/dev/zero of=$FILE bs=1M count=4096
    mkdosfs $FILE
fi



echo "Setting up the USB drive, keyboard, mouse... (MAY NOT WORK IF NOT REBOOTED. IF ERROR, REBOOT AND REEXECUTE THE SCRIPT)"
sudo chmod +x ./PiPerW/lib/pheripherals/hid_script
LOCAL_PATH=$(pwd)

echo "Adding the startup script to crontab..."
# Add the script to crontab

# check if the line exists in the file
if grep -q "@reboot root $LOCAL_PATH/PiPerW/lib/gadget/hid_script" /etc/crontab; then
    echo "The script is already added to crontab."
else
    echo "@reboot root $LOCAL_PATH/PiPerW/lib/gadget/hid_script" | sudo tee -a /etc/crontab
fi


# https://www.piwheels.org/simple/numpy/numpy-2.1.2-cp311-cp311-linux_armv6l.whl#sha256=bc15ed0e1459a24de8f46d54edad0c6a04314e51e59cc9385bb6107549fd00e5

add pip whells
echo "Adding pip wheels..."
touch /etc/pip.conf
echo "[global]" >> /etc/pip.conf
echo "extra-index-url=https://www.piwheels.org/simple" >> /etc/pip.conf


#------------------------------------------------
# !               UNABLE TO USE VENV BECAUSE NUMPY NOT POSIBLE TO BUILD 
#------------------------------------------------

# # Create a Python virtual environment in this directory
# echo "Creating a Python virtual environment in this directory..."
# sudo python3 -m venv env

# # Install the required Python packages
# echo "Installing the required Python packages..."
# sudo env/bin/python -m pip install --upgrade pip
# sudo env/bin/python -m pip install -r requirements.txt
#------------------------------------------------
# !               END VENV TRY
#------------------------------------------------

# normal
# remove issue pip externally-managed-environment
echo "Removing issue pip externally-managed-environment..."
echo "break-system-packages = true" >> /etc/pip.conf

# Install the required Python packages
echo "Installing the required Python packages..."
sudo python3 -m pip install --upgrade pip
sudo python3 -m pip install -r requirements.txt


# Indicate that the script execution is complete
echo "Script execution completed."

