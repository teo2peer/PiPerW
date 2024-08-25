from PiPerW.utils import Config, Log, DirFilter, Selector, save_Config
import os
import psutil


Log = Logging()

def install():
    
    
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
    
    
    
    #---------------------------
    #     Display driver
    #---------------------------
    Log.info("Searching for display drivers")
    display_dir = DirFilter("PiPerW/display")
    Log.info("Display drivers found: {}".format(display_dir.dirs()))
    
    selector = Selector(display_dir.dirs(), "Select a display driver")
    selected = selector.select()
    Log.info("Selected display driver: {}".format(selected))
    
    # if want display inverted
    inverted = input("\nInvert display? (y/N): ")
    if inverted.lower() == "y":
        Config['display']['invert'] = True
    else:
        Config['display']['invert'] = False
    
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
        
        addrs = list(psutil.net_if_addrs().keys())
        interfaces = []
        Log.info("Bluetooth interfaces found: {}".format(addrs))
        
        selector = Selector(addrs, "Select a bluetooth interface")
        selected = selector.select()
        Log.info("Selected bluetooth interface: {}".format(selected))
        
        Config['bluetooth']['interface'] = selected
        Config['bluetooth']['ask_interface'] = False
    
    Config['general']['first_run'] = False
    save_Config()
    
    
    
    