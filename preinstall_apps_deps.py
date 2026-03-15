import os
import sys
import subprocess
import toml
from PiPerW.helpers import Log

def preinstall_all():
    Log.info("Scanning all manifests to pre-install dependencies...")
    cache_file = ".cache_install.toml"
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
                Log.exception(f"Error reading manifest {manifest_path}: {e}")
    
    # Remove duplicates
    cache["apt"] = list(set(cache["apt"]))
    cache["pip"] = list(set(cache["pip"]))
    cache["github"] = list(set(cache["github"]))

    # Install APT
    for pkg in cache["apt"]:
        Log.info(f"Installing APT package: {pkg}")
        subprocess.run(['sudo', 'apt-get', 'install', '-y', pkg], check=False)

    # Install PIP
    for pkg in cache["pip"]:
        Log.info(f"Installing PIP package: {pkg}")
        subprocess.run([sys.executable, '-m', 'pip', 'install', pkg], check=False)

    # Install GitHub
    for repo_url in cache["github"]:
        repo_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
        target_path = os.path.join('lib', repo_name)
        if not os.path.exists(target_path):
            Log.info(f"Cloning GitHub repo: {repo_name}")
            os.makedirs('lib', exist_ok=True)
            subprocess.run(['git', 'clone', repo_url, target_path], check=False)
        else:
            Log.info(f"GitHub repo {repo_name} already exists, pulling latest...")
            subprocess.run(['git', '-C', target_path, 'pull'], check=False)

    # Save to cache
    Log.info("Saving cache file...")
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            toml.dump(cache, f)
    except Exception as e:
        Log.exception(f"Error saving cache: {e}")

    Log.info("Pre-installation complete.")

if __name__ == "__main__":
    preinstall_all()
