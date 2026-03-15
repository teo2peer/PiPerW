from PiPerW.helpers import Config
import os
import subprocess

class Execute:
    def __init__(self):
        '''
        After wifi modules are unload, reset the wifi card, stop monitor mode and reload the wifi modules
        '''
        interface = Config['network']['interface']
        subprocess.run(["sudo", "airmon-ng", "stop", f"{interface}mon"], capture_output=True)
        subprocess.run(["sudo", "airmon-ng", "stop", interface], capture_output=True)
        
        # Ensure it comes back to normal
        subprocess.run(["sudo", "ifconfig", interface, "down"], capture_output=True)
        subprocess.run(["sudo", "iwconfig", interface, "mode", "managed"], capture_output=True)
        subprocess.run(["sudo", "ifconfig", interface, "up"], capture_output=True)
        
        # Restart the networking managers
        subprocess.run(["sudo", "service", "NetworkManager", "start"], capture_output=True)
        subprocess.run(["sudo", "service", "wpa_supplicant", "start"], capture_output=True)