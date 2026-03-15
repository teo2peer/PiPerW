from PiPerW.interfaces.app_interface import AppInterface
from PiPerW.driver.pheripherals import Pheripherals
from PiPerW.driver.display import Display
from PiPerW.helpers import Log
from PiPerW.utils.Menu import Menu
import os
import sys
import subprocess
import toml
import time

display = Display()
pheripherals = Pheripherals()

class App(AppInterface):
    def __init__(self):
        super().__init__()
        self.cache_file = ".cache_install.toml"

    def load_cache(self):
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    cache = toml.load(f)
            else:
                cache = {"apt": [], "pip": [], "github": []}
                
            for key in ["apt", "pip", "github"]:
                if key not in cache:
                    cache[key] = []
            return cache
        except Exception as e:
            Log.error(f"Error loading cache: {e}")
            return {"apt": [], "pip": [], "github": []}

    def save_cache(self, cache):
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                toml.dump(cache, f)
        except Exception as e:
            Log.error(f"Error saving cache: {e}")

    def scan_all_manifests(self):
        cache = {"apt": [], "pip": [], "github": []}
        apps_dir = "apps"
        for root, dirs, files in os.walk(apps_dir):
            if "manifest.toml" in files:
                manifest_path = os.path.join(root, "manifest.toml")
                try:
                    with open(manifest_path, "r", encoding="utf-8") as f:
                        manifest = toml.load(f)
                        reqs = manifest.get("requirements", {})
                        if "apt" in reqs:
                            cache["apt"].extend(reqs["apt"])
                        if "pip" in reqs:
                            cache["pip"].extend(reqs["pip"])
                        if "github" in reqs:
                            cache["github"].extend(reqs["github"])
                except Exception as e:
                    Log.error(f"Error reading manifest {manifest_path}: {e}")
        
        # Remove duplicates
        cache["apt"] = list(set(cache["apt"]))
        cache["pip"] = list(set(cache["pip"]))
        cache["github"] = list(set(cache["github"]))
        return cache

    def run_command(self, cmd, msg=""):
        display.clear()
        display.text(f"Running:\n{msg}")
        try:
            subprocess.run(cmd, check=True)
            display.text(f"Success:\n{msg}")
        except subprocess.CalledProcessError as e:
            Log.error(f"Command failed: {cmd} - {e}")
            display.text(f"Failed!\nCheck logs.")
        time.sleep(1)

    def do_action(self, action_type, cache):
        # action_type can be "update_pip", "update_apt", "update_github", "reinstall", "scan_all"
        apt_pkg = cache.get("apt", [])
        pip_pkg = cache.get("pip", [])
        git_pkg = cache.get("github", [])

        if action_type in ["update_apt", "update_all", "reinstall"]:
            for pkg in apt_pkg:
                if self.is_stopped(): return
                msg = f"APT: {pkg[:15]}"
                if action_type == "reinstall":
                    self.run_command(['sudo', 'apt-get', 'install', '--reinstall', '-y', pkg], msg)
                else:
                    self.run_command(['sudo', 'apt-get', 'install', '--only-upgrade', '-y', pkg], msg)

        if action_type in ["update_pip", "update_all", "reinstall"]:
            for pkg in pip_pkg:
                if self.is_stopped(): return
                msg = f"PIP: {pkg[:15]}"
                if action_type == "reinstall":
                    self.run_command([sys.executable, '-m', 'pip', 'install', '--force-reinstall', pkg], msg)
                else:
                    self.run_command([sys.executable, '-m', 'pip', 'install', '--upgrade', pkg], msg)

        if action_type in ["update_github", "update_all", "reinstall"]:
            for repo_url in git_pkg:
                if self.is_stopped(): return
                repo_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
                target_path = os.path.join('lib', repo_name)
                msg = f"GIT: {repo_name[:15]}"
                if action_type == "reinstall":
                    if os.path.exists(target_path):
                        import shutil
                        shutil.rmtree(target_path)
                    self.run_command(['git', 'clone', repo_url, target_path], "Clone " + msg)
                else:
                    if os.path.exists(target_path):
                        self.run_command(['git', '-C', target_path, 'pull'], "Pull " + msg)
                    else:
                        self.run_command(['git', 'clone', repo_url, target_path], "Clone " + msg)

    def run(self):
        while not self.is_stopped():
            options = [
                "Update PIP", 
                "Update APT", 
                "Update GitHub", 
                "Update All", 
                "Reinstall All", 
                "Scan all Manifests", 
                "Clear Cache", 
                "Exit"
            ]
            menu = Menu(options, "Dependency Mgr")
            selected = menu.select()
            
            if selected is None or selected == len(options) - 1:
                break
                
            cache = self.load_cache()

            if selected == 0:
                self.do_action("update_pip", cache)
            elif selected == 1:
                self.do_action("update_apt", cache)
            elif selected == 2:
                self.do_action("update_github", cache)
            elif selected == 3:
                self.do_action("update_all", cache)
            elif selected == 4:
                self.do_action("reinstall", cache)
            elif selected == 5:
                # Scan all manifests and write to cache
                new_cache = self.scan_all_manifests()
                self.save_cache(new_cache)
                display.clear()
                display.text("Cache built\nfrom all apps.")
                time.sleep(2)
            elif selected == 6:
                # Clear Cache
                self.save_cache({"apt": [], "pip": [], "github": []})
                display.clear()
                display.text("Cache file\ncleared.")
                time.sleep(2)
                
            display.clear()
