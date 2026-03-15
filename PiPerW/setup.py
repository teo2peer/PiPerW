from PiPerW.helpers import Config, Log, DirFilter, Selector, save_config
import os
import psutil
import bluetooth


def install():
    
    # create tmp folder if not exists
    if not os.path.exists("PiPerW/tmp"):
        os.makedirs("PiPerW/tmp")
    
    # ---------------------------
    #     Theme Configurator
    # ---------------------------
    Log.info("Searching for themes")
    themes_dir = DirFilter("PiPerW/themes")
    Log.info("Themes found: {}".format(themes_dir.dirs()))
    
    selector = Selector(themes_dir.dirs(), "Select a theme")
    selected = selector.select()
    Log.info("Selected theme: {}".format(selected))
    
    Config['general']['theme'] = selected
    
    
    
    # Check if is a raspberry pi and if is using WaveShare OLED HAT
    if os.path.exists("/proc/device-tree/model") and "raspberry" in open("/proc/device-tree/model").read().lower():
        Log.warning("Raspberry Pi detected")
        Log.info("Are you using WaveShare oled HAT with buttons?")
        res = input("y/N: ")
        
        Log.info("Configuring for WaveShare OLED HAT")
        Config['display']['driver'] = 'sh1106'
        Config['display']['rotate'] = 180
        Config['pheripherals']['controllers'].append("waveshare_hat")
        
    else:
        #---------------------------
        #     Display driver
        #---------------------------
        Log.info("Searching for display drivers")
        display_dir = DirFilter("PiPerW/driver/display")
        Log.info("Display drivers found: {}".format(display_dir.dirs()))
        
        selector = Selector(display_dir.dirs(), "Select a display driver")
        selected = selector.select()
        Log.info("Selected display driver: {}".format(selected))
        
        # if want display inverted
        inverted = input("\nInvert display? (y/N): ")
        if inverted.lower() == "y":
            Config['display']['rotate'] = 180
        else:
            Config['display']['rotate'] = 0
        
        Config['display']['driver'] = selected
    
    
    #---------------------------
    #     Wireless Interface
    #---------------------------
    if Config['network']['ask_interface'] == True:
        Log.info("Searching for wireless interfaces")
        
        addrs = list(psutil.net_if_addrs().keys())
        interfaces = []
        Log.info("Wireless interfaces found: {}".format(addrs))
        
        selector = Selector(addrs, "Select a wireless interface")
        selected = selector.select()
        Log.info("Selected wireless interface: {}".format(selected))
        
        Config['network']['interface'] = selected
        Config['network']['ask_interface'] = False
    
    #---------------------------
    #     BLuetooth Interface
    #---------------------------
    
    if Config['bluetooth']['ask_interface'] == True:
        Log.info("Searching for bluetooth interfaces")
        
        interfaces = bluetooth.discover_devices(duration=2, lookup_names=True)

        if not interfaces:
            Log.error("No bluetooth interfaces found")
            selected = None
        else:
            addrs = [x[0] for x in interfaces]
            Log.info("Bluetooth interfaces found: {}".format(addrs))
            
            selector = Selector(addrs, "Select a bluetooth interface")
            selected = selector.select()
        Log.info("Selected bluetooth interface: {}".format(selected))
        
        Config['bluetooth']['interface'] = selected
        Config['bluetooth']['ask_interface'] = False
    
    Config['general']['first_run'] = False
    save_config()
    
    
    
    
