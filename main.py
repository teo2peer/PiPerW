# -*- coding: utf-8 -*-
# Author: Teo2Peer
# Date: 2021
# Description: PiPerW 

from PiPerW.helpers import Config, WThread, Log
from PiPerW.utils.Menu import MenuFolder
from PiPerW.display import Display
import importlib
import multiprocessing
import os
import sys
import time

last_activity = 0
Display = Display()

def first_run():
    Log.warning("First run detected")
    try:
        setup = importlib.import_module("PiPerW.setup")
        Log.info("Setup script imported")
        instrall_func = WThread(target=setup.install)
        instrall_func.start()
        instrall_func.join()
        
        # Install packages
        Log.info("Installing packages")
        os.system("sudo apt update && sudo apt upgrade -y")
        
        
        # Restart program
        Log.info("Restarting PiPerW")
        os.system("sudo python3 main.py")
        
    except Exception as e:
        Log.exception(f"Error running setup script: {e}")
        sys.exit(1)

def initialize_display():
    try:
        Display.init()
    except Exception as e:
        Log.exception(f"Error initializing display driver: {e}")
        sys.exit(1)
    return Display

def initialize_web_server():
    if Config['display_cast']['default']:
        Log.warning("Initializing web server")
        try:
            web = importlib.import_module("PiPerW.utils.Web").web_server
            multiprocessing.Process(target=web.run).start()
        except Exception as e:
            Log.exception(f"Error initializing web server: {e}")
            sys.exit(1)

def initialize_peripherals():
    Log.warning("Initializing peripherals")
    try:
        pheripherals = importlib.import_module("PiPerW.pheripherals").Pheripherals()
    except Exception as e:
        Log.exception(f"Error initializing peripherals: {e}")
        sys.exit(1)
    return pheripherals

def init():
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

    pheripherals = initialize_peripherals()
    Display.progress_bar(60, "PiPerW")

    Log.info("PiPerW initialized")
    menu = MenuFolder(Display.width, Display.height, "apps")
    Display.draw(menu.generate())

    while True:
        if check_last_activity(pheripherals):
            Display.draw(menu.generate())
        
        key = pheripherals.get_key()
        handle_key_press(key, menu, pheripherals)
        if key == "back":
            break

def check_last_activity(pheripherals):
    global last_activity
    if time.time() - pheripherals.timestamp > Config['display']['timeout']:
        Log.warning("Screen timeout")
        Display.splashscreen()
        pheripherals.await_any_key_press()
        Log.info("Screen wakeup")
        last_activity = time.time()
        Display.stop_animation()
        return True
    return False

def handle_key_press(key, menu, pheripherals):
    if key in ("up", "down", "select"):
        handle_menu_navigation(key, menu, pheripherals)
    elif key == "back":
        return

def handle_menu_navigation(key, menu, pheripherals):
    if key == "up":
        menu.previous()
    elif key == "down":
        menu.next()
    elif key == "select":
        app_finder(menu.get_selected(), pheripherals)
    Display.draw(menu.generate())

def app_finder(folder, pheripherals):
    apps_menu = MenuFolder(Display.width, Display.height, f"apps/{folder}")
    Display.draw(apps_menu.generate())
    while True:
        key = pheripherals.get_key()
        if key in ("up", "down"):
            handle_menu_navigation(key, apps_menu, pheripherals)
        elif key == "select":
            execute_app(apps_menu.get_selected(), folder, pheripherals)
            Display.draw(apps_menu.generate())
        elif key == "back":
            break

def execute_app(app, folder, pheripherals):
    try:
        app_module = importlib.import_module("apps.{}.{}".format(folder,app)).App()

        t = WThread(target=app_module.run)
        t.start()
        t.join()
    except Exception as e:
        Log.exception(f"App crashed\n{app}: {e}")
        Display.text(f"Error running app\n{app}\n\nLog in output.log\n\nPress any key to continue")
        pheripherals.await_any_key_press()
        
    # check if exist in folder __on_exit__.py
    try:
        Display.text("Executing on exit script")
        on_exit = importlib.import_module(f"apps.{folder}.__on_exit__").Execute()
        on_exit.__init__()
    except ImportError:
        pass
        

if __name__ == "__main__":
    try:
        init()
    except KeyboardInterrupt:
        Log.info("Exiting PiPerW")
        sys.exit(0)
    except Exception as e:
        Log.exception(f"Error initializing PiPerW: {e}")
        sys.exit(1)
