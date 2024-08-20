from PiPerW.utils import config, Logging
import os


log = Logging(config['general']['debug'], os.path.dirname(os.path.abspath(__file__)))


    

def init():
    
    log.info("Initializing PiPerW")
    log.info("Config file loaded")
    
    
    
    
    if config['general']['first_run']:
        log.warning("First run detected")
        
        # improt setup script
        import PiPerW.setup 
        log.info("Setup script imported")
        
        # run setup script
        PiPerW.setup.install()
        







if __name__ == "__main__":
    init()