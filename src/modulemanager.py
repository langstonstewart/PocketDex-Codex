import subprocess, sys
from .banner import banner

class ModuleManager:
    def __init__(self):
        self.module_list = ["PyQt6"]

    def module_check(self):
        from importlib import import_module
        
        banner()
        # check if user has modules, install prompt if not
        print("Checking for modules, please wait...")
        
        for module in self.module_list:
            try:
                import_module(module.replace("-", ""))

            except ModuleNotFoundError:
                        self.installer(module)
            
        banner()

        print("Modules imported.")

        return True
        
    def installer(self, package):
        print(f"installing {package}..")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])