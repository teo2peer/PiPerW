from PiPerW.helpers import Config
import os


class Execute:
    def __init__(self):
        ''' 
        After wifi modules are unload, reset the wifi card, stop monitor mode and reload the wifi modules
        '''
        
        os.system("sudo airmon-ng stop {}mon".format(Config['network']['interface']))
        os.system("sudo systemctl restart NetworkManager")