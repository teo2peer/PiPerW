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
import subprocess
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
        Log.error(f"Error running setup script: {e}")
        sys.exit(1)


def initialize_display():
    '''
    Initialize the display
    '''
    
    try:
        Display.init()
    except Exception as e:
        Log.error(f"Error initializing display driver: {e}")
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
            multiprocessing.Process(target=web.run, daemon=True).start()
        except Exception as e:
            Log.error(f"[Degraded Mode] Web server failed to start: {e}. Running without WebCast.")
            # We removed sys.exit(1) to allow the rest of PiPerW to continue working locally

def initialize_peripherals():
    ''' 
    Initialize the peripherals like keyboard, wave share hat, etc
    '''
    global Pheripheral
    Log.warning("Initializing peripherals")
    try:
        Pheripheral = importlib.import_module("PiPerW.driver.pheripherals").Pheripherals()
    except Exception as e:
        Log.error(f"Error initializing peripherals: {e}")
        sys.exit(1)

def initialize_telemetry():
    '''
    Initialize the hardware telemetry loop to prevent overheating
    '''
    Log.info("Initializing hardware telemetry")
    try:
        telemetry_module = importlib.import_module("PiPerW.utils.telemetry")
        telemetry = telemetry_module.HardwareTelemetry()
        telemetry.start()
    except Exception as e:
        Log.warning(f"Failed to start hardware telemetry: {e}")

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

    initialize_telemetry()

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

    if len(apps_menu.texts) == 0:
        Display.text("No hay aplicaciones\nen esta carpeta.\n\n[BACK] para salir")
        Pheripheral.await_any_key_press()
        return

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

def resolve_dependencies(app_name, apt_reqs, pip_reqs, git_reqs, force_reinstall=False, update=False):
    has_installed_something = False
    total_reqs = len(apt_reqs) + len(pip_reqs) + len(git_reqs)
    current_req = 0
    cache_file = ".cache_install.toml"

    # Load cache
    try:
        import toml
        if os.path.exists(cache_file):
            with open(cache_file, "r", encoding="utf-8") as f:
                cache = toml.load(f)
        else:
            cache = {"apt": [], "pip": [], "github": []}
        
        # Ensure keys exist
        for key in ["apt", "pip", "github"]:
            if key not in cache:
                cache[key] = []
    except Exception:
        cache = {"apt": [], "pip": [], "github": []}

    def save_cache():
        try:
            import toml
            with open(cache_file, "w", encoding="utf-8") as f:
                toml.dump(cache, f)
        except Exception as e:
            Log.error(f"Error saving cache: {e}")

    def update_progress(msg):
        nonlocal current_req
        current_req += 1
        pct = int(15 + (45 * (current_req / max(1, total_reqs))))
        Display.progress_bar(pct, msg)

    # Check APT
    for pkg in apt_reqs:
        if pkg in cache["apt"] and not force_reinstall and not update:
            update_progress(f"Cached APT:\n{pkg[:15]}")
            continue
            
        try:
            result = subprocess.run(['dpkg', '-s', pkg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if result.returncode != 0 or force_reinstall or update:
                update_progress(f"Instalando APT:\n{pkg[:15]}")
                Log.info(f"Installing APT dependency for {app_name}: {pkg}")
                
                cmd = ['sudo', 'apt-get', 'install', '-y', pkg]
                if force_reinstall:
                    cmd = ['sudo', 'apt-get', 'install', '--reinstall', '-y', pkg]
                elif update:
                    cmd = ['sudo', 'apt-get', 'install', '--only-upgrade', '-y', pkg]
                    
                subprocess.run(cmd)
                has_installed_something = True
                
                if pkg not in cache["apt"]:
                    cache["apt"].append(pkg)
            else:
                update_progress(f"Check APT: {pkg[:10]}")
                if pkg not in cache["apt"]:
                    cache["apt"].append(pkg)
        except FileNotFoundError:
            Log.warning(f"dpkg not found, skipping apt dependency: {pkg}")

    # Check PIP
    for pkg in pip_reqs:
        if pkg in cache["pip"] and not force_reinstall and not update:
            update_progress(f"Cached PIP:\n{pkg[:15]}")
            continue
            
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'show', pkg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if result.returncode != 0 or force_reinstall or update:
                update_progress(f"Instalando PIP:\n{pkg[:15]}")
                Log.info(f"Installing PIP dependency for {app_name}: {pkg}")
                
                cmd = [sys.executable, '-m', 'pip', 'install', pkg]
                if force_reinstall:
                    cmd = [sys.executable, '-m', 'pip', 'install', '--force-reinstall', pkg]
                elif update:
                    cmd = [sys.executable, '-m', 'pip', 'install', '--upgrade', pkg]
                    
                subprocess.run(cmd)
                has_installed_something = True
                
                if pkg not in cache["pip"]:
                    cache["pip"].append(pkg)
            else:
                update_progress(f"Check PIP: {pkg[:10]}")
                if pkg not in cache["pip"]:
                    cache["pip"].append(pkg)
        except FileNotFoundError:
            Log.warning(f"pip not found, skipping pip dependency: {pkg}")

    # Check GitHub
    for repo_url in git_reqs:
        try:
            repo_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
            if repo_url in cache["github"] and not force_reinstall and not update:
                update_progress(f"Cached GIT:\n{repo_name[:15]}")
                continue
                
            target_path = os.path.join('lib', repo_name)
            if not os.path.exists(target_path) or force_reinstall:
                update_progress(f"Clonando:\n{repo_name[:15]}")
                Log.info(f"Cloning GIT dependency for {app_name}: {repo_url}")
                os.makedirs('lib', exist_ok=True)
                if force_reinstall and os.path.exists(target_path):
                    import shutil
                    shutil.rmtree(target_path)
                subprocess.run(['git', 'clone', repo_url, target_path])
                has_installed_something = True
                
                if repo_url not in cache["github"]:
                    cache["github"].append(repo_url)
            elif update:
                update_progress(f"Update GIT:\n{repo_name[:15]}")
                Log.info(f"Updating GIT dependency for {app_name}: {repo_url}")
                subprocess.run(['git', '-C', target_path, 'pull'])
                has_installed_something = True
            else:
                update_progress(f"Check GIT: {repo_name[:10]}")
                if repo_url not in cache["github"]:
                    cache["github"].append(repo_url)
        except FileNotFoundError:
            Log.warning(f"git not found, skipping git dependency: {repo_url}")

    save_cache()

    if has_installed_something:
        Display.progress_bar(60, "Configurando...")
        time.sleep(1)

def execute_app(app, folder):
    '''
    Execute the app in a new thread

    :param app: str: The app to execute
    :param folder: str: The folder of the app
    '''
    try:
        # Prevent multiple loadings or confusing delays by showing immediate feedback
        Display.progress_bar(0, "Cargando metadatos...")

        # Módulo de carga de Metadatos escalable (Manifiesto TOML externo)
        manifest_path = f"apps/{folder}/{app}/manifest.toml"
        app_name = app
        app_version = "1.0"
        app_req_apt = []
        app_req_pip = []
        app_req_git = []

        if os.path.exists(manifest_path):
            try:
                import toml
                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest = toml.load(f)
                    app_name = manifest.get('app', {}).get('name', app)
                    app_version = manifest.get('app', {}).get('version', '1.0')
                    reqs = manifest.get('requirements', {})
                    app_req_apt = reqs.get('apt', [])
                    app_req_pip = reqs.get('pip', [])
                    app_req_git = reqs.get('github', [])
            except Exception as e:
                Log.error(f"[SRE] Error leyendo manifest.toml en {app}: {e}")

        Display.progress_bar(15, "Chequeando deps...")
        # Resolver dependencias ANTES de cargar el módulo para evitar crash
        resolve_dependencies(app_name, app_req_apt, app_req_pip, app_req_git)

        Display.progress_bar(60, "Importando librerias")
        Log.info(f"Loaded App: {app_name} v{app_version}")
        if app_req_apt or app_req_pip or app_req_git:
            Log.info(f"[{app_name}] Requisitos -> APT: {app_req_apt} | PIP: {app_req_pip} | GIT: {app_req_git}")

        module_name = f"apps.{folder}.{app}"

        Display.progress_bar(90, "Iniciando app...")
        # Hot-reload support: if module is already loaded, reload it.
        if module_name in sys.modules:
            app_module_base = importlib.reload(sys.modules[module_name])
        else:
            app_module_base = importlib.import_module(module_name)

        app_module = app_module_base.App()

        # Short-press EXIT keys are ignored while inside the app (apps should only exit via long-press EXIT)
        Pheripheral.suppress_exit = True

        t = WThread(target=app_module.run)
        app_module._thread = t
        t.start()

        # Non-blocking wait to keep main thread responsive
        while t.is_alive():
            if getattr(Pheripheral, 'force_app_kill', False):
                Log.error(f"[SRE] Dead Man's Switch Triggered! Forcibly abandoning unrensponsive app: {app}")
                t.stop() # set stop event
                Pheripheral.force_app_kill = False
                break # Regain UI Control immediately
            t.join(0.1)

        if hasattr(t, 'exc') and t.exc:
            raise t.exc

    except Exception as e:
        Log.exception(f"App crashed\n{app}: {e}")
        Display.text(f"Error running app\n{app}\n\nLog in output.log\n\nPress any key to continue")
        Pheripheral.await_any_key_press()
    finally:
        # Restore EXIT handling after app exits
        Pheripheral.suppress_exit = False

    # check if exist in folder __on_exit__.py
    try:
        Display.text("Executing on exit script")
        on_exit_module_name = f"apps.{folder}.__on_exit__"
        
        # Hot-reload support for the exit script
        if on_exit_module_name in sys.modules:
            on_exit_base = importlib.reload(sys.modules[on_exit_module_name])
        else:
            on_exit_base = importlib.import_module(on_exit_module_name)
            
        try:
            cleanup_thread = WThread(target=on_exit_base.Execute)
            cleanup_thread.start()
            cleanup_thread.join(timeout=3.0) # Abort drastically after 3 seconds timeout
            
            if cleanup_thread.is_alive():
                Log.error("Cleanup script timed out! Forcefully continuing.")
        except Exception as e_exit:
            Log.error(f"Error inside on exit script: {e_exit}")
            
    except ImportError:
        pass
    except Exception as e:
        Log.error(f"Failed to load on exit script: {e}")

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
