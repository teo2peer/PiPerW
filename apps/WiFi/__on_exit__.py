from PiPerW.helpers import Config
import os


class Execute:
    def __init__(self):
        ''' 
        After wifi modules are unload, reset the wifi card, stop monitor mode and reload the wifi modules
        '''
        
        os.system("sudo airmon-ng stop {}mon".format(Config['network']['interface']))
        os.system("sudo ifconfig {} down".format(Config['network']['interface']))
        os.system("sudo iwconfig {} mode managed".format(Config['network']['interface']))
        os.system("sudo ifconfig {} up".format(Config['network']['interface']))
        os.system("sudo service NetworkManager start")