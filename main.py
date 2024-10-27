# -*- coding: utf-8 -*-
# Author: Teo2Peer
# Date: 2021
# Description: PiPerW 

from PiPerW.helpers import Config, WThread, Log
from PiPerW.utils.Menu import MenuFolder
from PiPerW.driver.display import Display
import importlib
import multiprocessing
import os
import sys
import time

last_activity = 0
Display = Display()
Pheripheral = None

def first_run():
    '''
    First run setup
    '''
    
    Log.warning("First run detected")
    try:
        setup = importlib.import_module("PiPerW.setup")
        Log.info("Setup script imported")
        instrall_func = WThread(target=setup.install)
        instrall_func.start()
        instrall_func.join()
        
        # Install packages
        Log.info("Installing packages")
        # os.system("sudo apt update && sudo apt upgrade -y")
        Log.warning("SKIPPING")
        
        
        # Restart program
        Log.info("Restarting PiPerW")
        os.system("sudo python3 main.py")
        
    except Exception as e:
        Log.exception(f"Error running setup script: {e}")
        sys.exit(1)


def initialize_display():
    '''
    Initialize the display
    '''
    
    try:
        Display.init()
    except Exception as e:
        Log.exception(f"Error initializing display driver: {e}")
        sys.exit(1)
    return Display

def initialize_web_server():
    '''
    Initialize the web server to cast the display
    '''
    if Config['display_cast']['default']:
        Log.warning("Initializing web server")
        try:
            web = importlib.import_module("PiPerW.utils.Web").web_server
            multiprocessing.Process(target=web.run).start()
        except Exception as e:
            Log.exception(f"Error initializing web server: {e}")
            sys.exit(1)

def initialize_peripherals():
    ''' 
    Initialize the peripherals like keyboard, wave share hat, etc
    '''
    global Pheripheral
    Log.warning("Initializing peripherals")
    try:
        Pheripheral = importlib.import_module("PiPerW.driver.pheripherals").Pheripherals()
    except Exception as e:
        Log.exception(f"Error initializing peripherals: {e}")
        sys.exit(1)

def init():
    '''
    Initialize the PiPerW
    '''
    
    Log.info("Initializing PiPerW")
    
    # cehck if is windows
    if os.name == "nt":
        Log.error("PiPerW is not compatible with Windows, but development can be done with limited functionality")

    else:
        if  'SUDO_UID' not in os.environ.keys():
            Log.error("Not running as root, exiting")
            sys.exit(1)
        

    if Config['general']['first_run']:
        first_run()

    initialize_display()
    Display.clear()
    Display.progress_bar(20, "Loading PiPerW", True)

    initialize_web_server()
    Display.progress_bar(40, "Loading PiPerW", True)

    initialize_peripherals()
    Display.progress_bar(60, "PiPerW")

    Log.info("PiPerW initialized")
    menu = MenuFolder("apps", True)
    menu.show()

    while True:
        if check_last_activity():
            menu.show()
        
        key = Pheripheral.await_key()
        handle_key_press(key, menu)
        if key == "back":
            break

def check_last_activity():
    '''
    Check if the last activity was more than the timeout
    and display the splashscreen
    '''
    
    global last_activity
    if time.time() - Pheripheral.timestamp > Config['display']['timeout']:
        Log.warning("Screen timeout")
        Display.splashscreen()
        Pheripheral.await_any_key_press()
        Log.info("Screen wakeup")
        last_activity = time.time()
        Display.stop_animation()
        return True
    return False

def handle_key_press(key, menu):
    '''
    Handle the key press
    
    :param key: str: The key pressed
    :param menu: Menu: The menu object
    '''
    if key in ("up", "down", "select"):
        handle_menu_navigation(key, menu)
    elif key == "back":
        return

def handle_menu_navigation(key, menu):
    '''
    Handle the menu navigation
    
    :param key: str: The key pressed
    :param menu: Menu: The menu object
    '''
    if key == "up":
        menu.previous()
    elif key == "down":
        menu.next()
    elif key == "select":
        app_finder(menu.get_selected())
    menu.show()

def app_finder(folder):
    '''
    Find the app in the folder
    
    :param folder: str: The folder to search
    '''

    apps_menu = MenuFolder(f"apps/{folder}", True)
    apps_menu.show()
    while True:
        key = Pheripheral.await_key()
        if key in ("up", "down"):
            handle_menu_navigation(key, apps_menu)
        elif key == "select":
            execute_app(apps_menu.get_selected(), folder)
            apps_menu.show()
        elif key == "back" or key == "exit":
            break

def execute_app(app, folder):
    '''
    Execute the app in a new thread
    
    :param app: str: The app to execute
    :param folder: str: The folder of the app
    '''
    try:
        app_module = importlib.import_module("apps.{}.{}".format(folder,app)).App()

        t = WThread(target=app_module.run)
        t.start()
        t.join()
    except Exception as e:
        Log.exception(f"App crashed\n{app}: {e}")
        Display.text(f"Error running app\n{app}\n\nLog in output.log\n\nPress any key to continue")
        Pheripheral.await_any_key_press()
        
    # check if exist in folder __on_exit__.py
    try:
        Display.text("Executing on exit script")
        on_exit = importlib.import_module(f"apps.{folder}.__on_exit__").Execute()
        on_exit.__init__()
    except ImportError:
        pass

def stop_app():
    '''
    Stop the app
    '''
    Display.stop_animation()
    Display.text("Stopping PiPerW")
    Pheripheral.stop()
    
    Display.clear()
    

if __name__ == "__main__":
    try:
        init()
    except KeyboardInterrupt:
        Log.info("Exiting PiPerW")
        
        stop_app()
        
        sys.exit(0)
    except Exception as e:
        Log.exception(f"Error initializing PiPerW: {e}")
        sys.exit(1)
