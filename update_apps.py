import os
import re
from PiPerW.interfaces.app_interface import AppInterface
from PiPerW.helpers import Log

apps_dir = "apps"

for root, dirs, files in os.walk(apps_dir):
    if "__init__.py" in files:
        init_file = os.path.join(root, "__init__.py")
        manifest_file = os.path.join(root, "manifest.toml")
        
        with open(init_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Try finding name and version in super().__init__("Name", "Version") or similar
        match = re.search(r'(super\(\)\.__init__|AppInterface\.__init__|App\.__init__|self\.__init__)\s*\(\s*(?:self\s*,)?\s*[\'"]([^\'"]+)[\'"]\s*,\s*[\'"]([^\'"]+)[\'"]\s*\)', content)
        if match:
            name, version = match.group(2), match.group(3)
            # Create manifest if it doesn't exist
            if not os.path.exists(manifest_file):
                with open(manifest_file, "w", encoding="utf-8") as mf:
                    mf.write(f'name = "{name}"\nversion = "{version}"\n')
            
            # Replace the init call with one that takes zero parameters (or just self)
            call_type = match.group(1)
            if "super" in call_type:
                new_content = re.sub(r'super\(\)\.__init__\([^)]*\)', 'super().__init__()', content)
            elif "AppInterface" in call_type:
                new_content = re.sub(r'AppInterface\.__init__\(\s*self\s*[^)]*\)', 'AppInterface.__init__(self)', content)
            else:
                new_content = re.sub(re.escape(match.group(0)), call_type + '(self)', content)
                
            if new_content != content:
                with open(init_file, "w", encoding="utf-8") as f:
                    f.write(new_content)
                Log.info(f"Updated {init_file}")
