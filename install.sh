#!/bin/bash


RED="\e[31m"
GREEN="\e[32m"
YELLOW="\e[33m"
BLUE="\e[34m"
ENDCOLOR="\e[0m"



# Check if the script is being run as root
if [[ $EUID -ne 0 ]]; then
    echo -e "${RED}Please run the script as root.${ENDCOLOR}"
    exit 1
fi

#---------------------------
#     Updating and instaling packages
#---------------------------
# Update the package list and install required packages
echo -e "${BLUE}Updating package list and installing required packages...${ENDCOLOR}"
sudo apt-get update

echo -e "${BLUE}Installing re4son kernel...${ENDCOLOR}"
echo "deb http://http.re4son-kernel.com/re4son/ kali-pi main" > /etc/apt/sources.list.d/re4son.list
wget -O - https://re4son-kernel.com/keys/http/archive-key.asc | apt-key add -
sudo apt update
sudo apt install -y kalipi-kernel kalipi-bootloader kalipi-re4son-firmware kalipi-kernel-headers libraspberrypi0 libraspberrypi-dev libraspberrypi-doc libraspberrypi-bin

echo -e "${BLUE}Installing dependencies...${ENDCOLOR}"

sudo apt-get install python3 python3-dev python3-pip python3-virtualenv  -y
sudo apt-get install ifstat libffi-dev libssl-dev direnv ondir virtualenv util-linux-extra -y
sudo apt-get install libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev libopenjp2-7 i2c-tools fonts-dejavu bluez libgfortran5 libopenblas0-pthread -y
sudo apt install git libgmp3-dev gawk qpdf bison flex make autoconf libtool texinfo -y

# install python packages modules
echo -e "${BLUE}Installing python packages...${ENDCOLOR}"
sudo apt-get install python3-numpy python3-pil  python3-dev python3-smbus python3-venv python3-bluez python3-toml  -y


#---------------------------
#     Autologin
#---------------------------

# Enable autologin by editing lightdm.conf
echo -e "${BLUE}Enabling autologin by editing lightdm.conf..."

# Ensure autologin-user=kali and autologin-user-timeout=0 exist under [SeatDefaults]
SEAT_DEFAULTS_FOUND=$(grep -q "^\[SeatDefaults\]" /etc/lightdm/lightdm.conf && echo "yes" || echo "no")

if [[ "$SEAT_DEFAULTS_FOUND" == "yes" ]]; then
    echo -e "${BLUE}[SeatDefaults] found. Checking autologin settings...${ENDCOLOR}"

    AUTOL_LOGIN_USER=$(grep -q "^autologin-user=kali" /etc/lightdm/lightdm.conf && echo "yes" || echo "no")
    AUTOLOGIN_USER_TIMEOUT=$(grep -q "^autologin-user-timeout=0" /etc/lightdm/lightdm.conf && echo "yes" || echo "no")

    if [[ "$AUTOL_LOGIN_USER" == "no" ]]; then
        echo -e "${RED}autologin-user=kali not found. Adding it...${ENDCOLOR}"
        sudo sed -i "/^\[SeatDefaults\]/a autologin-user=kali" /etc/lightdm/lightdm.conf
    else
        echo -e "${YELLOW}autologin-user=kali already exists.${ENDCOLOR}"
    fi

    if [[ "$AUTOLOGIN_USER_TIMEOUT" == "no" ]]; then
        echo -e "${RED}autologin-user-timeout=0 not found. Adding it...${ENDCOLOR}"
        sudo sed -i "/^\[SeatDefaults\]/a autologin-user-timeout=0" /etc/lightdm/lightdm.conf
    else
        echo -e "${YELLOW}autologin-user-timeout=0 already exists.${ENDCOLOR}"
    fi
else
    echo -e "${RED}[SeatDefaults] section not found. Adding it with autologin settings...${ENDCOLOR}"
    echo -e "\n[SeatDefaults]\nautologin-user=kali\nautologin-user-timeout=0" | sudo tee -a /etc/lightdm/lightdm.conf
fi

# Restart the lightdm service to apply changes
echo -e "${BLUE}Restarting lightdm service..."
sudo service lightdm restart


#---------------------------
#     Enabling console mode
#---------------------------

# Set the default systemd target to multi-user
echo -e "${BLUE}Setting the default systemd target to 3...${ENDCOLOR}"
sudo systemctl set-default multi-user.target
sudo systemctl isolate multi-user.target


#---------------------------
#     Enabling I2C, SPI, and Serial
#---------------------------
# Enable SPI, I2C, and Serial through raspi-config
echo -e "${BLUE}Enabling SPI, I2C, and Serial interfaces using raspi-config...${ENDCOLOR}"
sudo raspi-config nonint do_spi 0
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_serial 0



#---------------------------
#     Creating a swap file
#---------------------------
# Create and configure a swap file
echo -e "${BLUE}Creating and configuring a swap file...${ENDCOLOR}"

# check if the file exists
if [ -f /kali.swap ]; then
    echo -e "${RED}kali.swap already exists.${ENDCOLOR}"
else
    sudo dd if=/dev/zero of=/kali.swap.tmp bs=1024 count=2097152
    sudo mv /kali.swap.tmp /kali.swap
    sudo chmod 600 /kali.swap

    # Setting up the swap space
    echo -e "${BLUE}Setting up the swap space...${ENDCOLOR}"
    sudo mkswap /kali.swap
    sudo swapon /kali.swap
    sudo echo "/kali.swap none swap sw 0 0" >> /etc/fstab
fi





#---------------------------
#     HardwareClock
#---------------------------
# enabling hardware clock
echo -e "${BLUE}Adding support for hardware clock...${ENDCOLOR}"
# check if the line exists in the file
if grep -q "i2c-bcm2708" /etc/modules; then
    echo -e "${YELLOW}i2c-bcm2708 already exists in /etc/modules.${ENDCOLOR}"
else
    echo "i2c-bcm2708" | sudo tee -a /etc/modules
fi

if grep -q "i2c-dev" /etc/modules; then
    echo -e "${YELLOW}i2c-dev already exists in /etc/modules.${ENDCOLOR}"
else
    echo "i2c-dev" | sudo tee -a /etc/modules
fi

if grep -q "rtc-ds1307" /etc/modules; then
    echo -e "${YELLOW}rtc-ds1307 already exists in /etc/modules.${ENDCOLOR}"
else
    echo "rtc-ds1307" | sudo tee -a /etc/modules
fi


# echo "Adding the RTC device..."
# check if the line exists in the file
if grep -q "ds1307 0x68" /etc/rc.local; then
    echo -e "${YELLOW}ds1307 0x68 already exists in /etc/rc.local.${ENDCOLOR}"
else
    echo "echo ds1307 0x68 > /sys/class/i2c-adapter/i2c-1/new_device" | sudo tee -a /etc/rc.local
fi

# initialize
hwclock --systohc -D --noadjfile --utc


# Adding in rc.local
if grep -q "echo ds1307 0x68 > /sys/class/i2c-adapter/i2c-1/new_device" /etc/rc.local; then
    echo -e "${YELLOW}echo ds1307 0x68 > /sys/class/i2c-adapter/i2c-1/new_device already exists in /etc/rc.local.${ENDCOLOR}"
else
    echo "echo ds1307 0x68 > /sys/class/i2c-adapter/i2c-1/new_device" | sudo tee -a /etc/rc.local
fi

if grep -q "hwclock -s" /etc/rc.local; then
    echo -e "${YELLOW}hwclock -s already exists in /etc/rc.local.${ENDCOLOR}"
else
    echo "hwclock -s" | sudo tee -a /etc/rc.local
fi



#---------------------------
#     SWAP
#---------------------------

echo -e "${BLUE}Creating a 4GB file for the USB drive...${ENDCOLOR}"
# Create a 4gb file for the USB drive

# check if the file exists
if [ -f /PiPerW.img ]; then
    echo -e "${RED}PiPerW.img already exists.${ENDCOLOR}"
else
    FILE=/PiPerW.img
    MNTPOINT=/mnt/usb_piperw

    dd if=/dev/zero of=$FILE bs=1M count=4096
    mkdosfs $FILE
fi

#---------------------------
#     PIPERW GDGET
#---------------------------


# adding otg support for bad_usb
echo -e "${BLUE}Adding OTG support for BadUSB...${ENDCOLOR}"

# check if the line exists in the file
if grep -q "dtoverlay=dwc2" /boot/config.txt; then
    echo -e "${YELLOW}dtoverlay=dwc2 already exists in /boot/config.txt.${ENDCOLOR}"
else
    echo "dtoverlay=dwc2" | sudo tee -a /boot/config.txt
fi

if grep -q "dwc2" /etc/modules; then
    echo -e "${YELLOW}dwc2 already exists in /etc/modules.${ENDCOLOR}"
else
    echo "dwc2" | sudo tee -a /etc/modules
fi

if grep -q "libcomposite" /etc/modules; then
    echo -e "${YELLOW}libcomposite already exists in /etc/modules.${ENDCOLOR}"
else
    echo "libcomposite" | sudo tee -a /etc/modules
fi

echo -e "${BLUE}Setting up the USB drive, keyboard, mouse... ${RED}(MAY NOT WORK IF NOT REBOOTED. IF ERROR, REBOOT AND REEXECUTE THE SCRIPT)${ENDCOLOR}"
# create the gadget script
sudo chmod +x ./PiPerW/lib/gadget/hid_script
LOCAL_PATH=$(pwd)

echo -e "${BLUE}Adding the startup script to crontab...${ENDCOLOR}"
# Add the script to crontab

# check if the line exists in the file
if grep -q "@reboot root $LOCAL_PATH/PiPerW/lib/gadget/hid_script" /etc/crontab; then
    echo -e "${WARNING}The script is already added to crontab.${ENDCOLOR}"
else
    echo "@reboot root $LOCAL_PATH/PiPerW/lib/gadget/hid_script" | sudo tee -a /etc/crontab
fi


#---------------------------
#     PIP configure
#---------------------------
# add pip whells
echo -e "${BLUE}Adding pip wheels...${ENDCOLOR}"
touch /etc/pip.conf
if grep -q "[global]" /etc/pip.conf; then
    echo -e "${YELLOW}[global] already exists in /etc/pip.conf.${ENDCOLOR}"
else
    echo "[global]" | sudo tee -a /etc/pip.conf
fi

if grep -q "extra-index-url=https://www.piwheels.org/simple" /etc/pip.conf; then
    echo -e "${YELLOW}extra-index-url=https://www.piwheels.org/simple already exists in /etc/pip.conf.${ENDCOLOR}"
else
    echo "extra-index-url=https://www.piwheels.org/simple" | sudo tee -a /etc/pip.conf
fi




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
echo -e "${BLUE}Removing issue pip externally-managed-environment...${ENDCOLOR}"
if grep -q "break-system-packages = true" /etc/pip.conf; then
    echo -e "${YELLOW}break-system-packages = true already exists in /etc/pip.conf.${ENDCOLOR}"
else
    echo "break-system-packages = true" | sudo tee -a /etc/pip.conf
fi


# Install the required Python packages
echo -e "${BLUE}Installing the required Python packages...${ENDCOLOR}"
sudo python3 -m pip install --upgrade pip
sudo python3 -m pip install -r requirements.txt


# Indicate that the script execution is complete
echo -e "${GREEN}Script execution completed.${ENDCOLOR}\n"

# press any key to reboot
echo -e "${BLUE}Press any key to reboot...${ENDCOLOR}\n"
read -n 1 -s -r -p ""
sudo reboot

