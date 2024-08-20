from PiPerW.utils import config, Logging, WThread
import sys, os


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
        try:
            t = WThread(target=PiPerW.setup.install)
            t.start()
            t.join()
        except Exception as e:
            log.exception("Error running setup script: {}".format(e))
            sys.exit(1)
        







if __name__ == "__main__":
    init()