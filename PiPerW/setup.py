from PiPerW.utils import config, Logging
import os

def install():
    # search for themes in PiPerW/themes
    me.info("Searching for themes")
    themes = os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'themes'))
    
    