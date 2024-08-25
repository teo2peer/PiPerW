# -_- coding: utf-8 -_-
# Author: Teo2Peer
# Date: 2021
# Description: PiPerW 

from PiPerW.helpers import Config, WThread, Log
from PiPerW.utils.Menu import MenuFolder
import PiPerW.utils.Logging
import sys, os, time
import importlib
import multiprocessing


last_activity = 0

def first_run():
    
    Log.warning("First run detected")
    # improt setup script
    setup = importlib.import_module("PiPerW.setup")
    Log.info("Setup script imported")
    
    # run setup script
    try:
        t = WThread(target=setup.install)
        t.start()
        t.join()
        
        # install packages
        Log.info("Installing packages")
        os.system("sudo apt update")    
        os.system("sudo apt upgrade -y")
        os.system("./install.sh")
        
        # restart program
        Log.info("Restarting PiPerW")
        os.system("sudo python3 main.py")
        
    except Exception as e:
        Log.exception("Error running setup script: {}".format(e))
        sys.exit(1)
    

def init():
    
    Log.info("Initializing PiPerW")
    Log.info("Config file loaded")
    
    if Config['general']['first_run']:
        first_run()

    #---------------------------
    #     Init display
    #---------------------------
    Log.warning("Init display driver")
    try:
        display = importlib.import_module("PiPerW.display.{}".format(Config['display']['driver'])).Driver
        display.init()
    except Exception as e:
        Log.exception("Error initializing display driver: {}".format(e))
        sys.exit(1)
    
    display.clear()
    display.progress_bar(20, "Loading PiPerW", True)
   
    
    #---------------------------
    #     Init web server
    #---------------------------
    if Config['display_cast']['default']:
        Log.warning("Init web server")
        try:
            web = importlib.import_module("PiPerW.utils.Web").web_server
            multiprocessing.Process(target=web.run).start()
        except Exception as e:
            Log.exception("Error initializing web server: {}".format(e))
            sys.exit(1)
    
    display.progress_bar(40, "Loading PiPerW", True)
    
    #---------------------------
    #     Pheripherals
    #---------------------------
    
    Log.warning("Init pheripherals")
    try:
        pheripherals = importlib.import_module("PiPerW.pheripherals").Pheripherals()
    except Exception as e:
        Log.exception("Error initializing pheripherals: {}".format(e))
        sys.exit(1)
    
    
    display.progress_bar(60, "PiPerW")

    # wait for pheripherals to start
    # pheripherals_thread.join()
        
    Log.info("PiPerW initialized")
    menu = MenuFolder(display.width, display.height, "apps")
    display.draw(menu.generate())
    
    # time.sleep(1) # This solvs the issue of the first key press not being registered? 
    # Maybe a mutex is needed?
    
    while True:
        check_last_activity(pheripherals, display)
        key = pheripherals.get_key()
        # print(key)   # FIXME: Issue when not printing key

        if(key == "up"):
            menu.previous()
            display.draw(menu.generate())
        elif(key == "down"):
            menu.next()
            display.draw(menu.generate())
        elif(key == "select"):
            app_finder(menu.get_selected(), display, pheripherals)
            display.draw(menu.generate())
        elif(key == "back"):
            break
        
        
        
        key = None
        
    
    
def check_last_activity(pheripherals, display):
    global last_activity
    if time.time() - pheripherals.timestamp > Config['display']['timeout']:
        Log.warning("Screen timeout")
        display.splashscreen()
        pheripherals.await_key()
        Log.info("Screen wakeup")
        last_activity = time.time()
        display.stop_animation()
        return True
    return False

def app_finder(folder, display, pheripherals):
    apps = []
    apps_menu = MenuFolder(display.width, display.height, "apps/{}".format(folder))
    display.draw(apps_menu.generate())
    while True:
        key = pheripherals.get_key()
        if(key == "up"):
            apps_menu.previous()
            display.draw(apps_menu.generate())
        elif(key == "down"):
            apps_menu.next()
            display.draw(apps_menu.generate())
        elif(key == "select"):
            display.text("Loading\n{}".format(apps_menu.get_selected()))
        elif(key == "back"):
            break
        
        key = None

def execute_app(app):
    importlib.import_module("PiPerW.apps.{}".format(app)).app
    
    try:
        app = importlib.import_module("PiPerW.apps.{}".format(app)).app
        WThread(target=app.run).start()
    except Exception as e:
        Log.exception("Error running app {}: {}".format(app,e))
        display.text("Error running app {}: ".format(app))
        pheripherals.await_key()
        sys.exit(1)



if __name__ == "__main__":
    try:
        init()
    # check for ctrl+c
    except KeyboardInterrupt:
        Log.info("Exiting PiPerW")
        
        # stop all processes
        # multiprocessing.Process.terminate()
        sys.exit(0)
    except Exception as e:
        Log.exception("Error initializing PiPerW: {}".format(e))
        sys.exit(1)
        