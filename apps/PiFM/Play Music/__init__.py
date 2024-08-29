from PiPerW.apps.app_interface import AppInterface
from PiPerW.pheripherals import Pheripherals
from PiPerW.display import Display
from PiPerW.helpers import Log, Config, download_lib_from_github
from PiPerW.utils.Menu import MenuFolderFiles
import os, time, subprocess, multiprocessing


display = Display()
pheripherals = Pheripherals()



class App(AppInterface):
    
    def __init__(self):
        self.name = "Play Music"
        self.version = "1.0"
        self.description = "Play music from your Pi"
        self.author = "Teo2Peer"
        
        super().__init__(self.name, self.version)
        
        # get this path
        self.path = "PiPerW/lib/PiFmRds"
        # check if PiFmRds is installed 
        
        if not os.path.exists(self.path + "/PiFmRds") or not os.path.exists(self.path + "/PiFmRds/src/pi_fm_rds"):
            Log.error("PiFmRds is not installed. Installing...")
            display.text("PiFmRds is not installed. Installing...")
            
            
            
            # try to install PiFmRds
            try:
                Log.warning("Installing libsndfile1-dev")
                res = os.system("sudo apt install libsndfile1-dev -y")
                
                if res != 0:
                    Log.error("Failed to install libsndfile1-dev")
                    display.text("Failed to install libsndfile1-dev")
                    pheripherals.await_any_key_press()
                    raise SystemError("Failed to install libsndfile1-dev")
                
                
                Log.warning("Downloading PiFmRds")
                # remove path if exists
                if os.path.exists(self.path):
                    res = os.system("rm -rf "+self.path)
                    if res != 0:
                        Log.error("Failed to remove PiFmRds")
                        display.text("Failed to remove PiFmRds")
                        pheripherals.await_any_key_press()
                        raise SystemError("Failed to remove PiFmRds")
                
                download_lib_from_github("https://github.com/ChristopheJacquet/PiFmRds.git", "PiFmRds")
                self.fix_makefile_pi_zerow()
                
                # compile PiFmRds
                Log.warning("Compiling PiFmRds")
                res = os.system("cd PiPerW/lib/PiFmRds/src && make clean && make")
                
                if res != 0:
                    Log.error("Failed to compile PiFmRds")
                    display.text("Failed to compile PiFmRds")
                    pheripherals.await_any_key_press()
                    raise SystemError("Failed to compile PiFmRds")
                
                Log.info("PiFmRds installed")
            except Exception as e:
                raise SystemError("Failed to install PiFmRds: " + str(e))
                return
    
        self.executable = self.path + "src/pi_fm_rds"
        self.frequency = 100.0
        
    
    def fix_makefile_pi_zerow(self):
        '''
            Fix makefile for Pi Zero W
        '''
    
        # patch makefile
        makefile = self.path + "/src/Makefile"
        # replace ARCH_CFLAGS = -O3 to ARCH_CFLAGS = -march=armv7-a -O3 -mtune=arm1176jzf-s -mfloat-abi=hard -mfpu=vfp -ffast-math
        # use regex to replace
        
        with open(makefile, "r") as f:
            lines = f.readlines()
            
        with open(makefile, "w") as f:
            for line in lines:
                if "ARCH_CFLAGS = -O3" in line:
                    line = "	ARCH_CFLAGS = -march=armv7-a -O3 -mtune=arm1176jzf-s -mfloat-abi=hard -mfpu=vfp -ffast-math\n"
                if "TARGET = other" in line:
                    line = "	TARGET = 2\n
                f.write(line)
            
        
    def run(self):
        
        
        # play music
        display.text("Select a music file to play, press any key to continue")
        
        menu = MenuFolderFiles(self.path+"/music")
        menu.show()
        
        while True:
            key = pheripherals.get_key()
            if key == "up":
                menu.previous()
            elif key == "down":
                menu.next()
            elif key == "select":
                play_music(menu.get_selected())
            elif key == "back" or key == "exit":
                break
            
    
    def select_frequency(self):
        '''
        Select frequency to play music
        '''
        
        display.text("Select frequency to play music")
        display.text("Press up or down to change frequency")
        display.text("Press select to play music")
        
        while True:
            key = pheripherals.await_key()
            text = "Select frequency\n"
            if key == "right":
                self.frequency += 0.1
            elif key == "left":
                self.frequency -= 0.1
            elif key == "up":
                self.frequency += 1.0
            elif key == "down":
                self.frequency -= 1.0
            elif key == "select":
                break
            elif key == "back":
                return
            
            text += "Frequency: {:.1f}".format(self.frequency)
            display.text(text)
        return self.frequency
    
    def play_music(self, file):
        '''
        Play music file into another process
        
        :param file: music file path
        '''
        
        display.text("Playing {}".format(file)+"\nPress any key to stop")
        process = multiprocessing.Process(target=self.executable, args=(self.path+"/music/"+file,))
        process.start()
        
        pheripherals.await_any_key_press()
        
        process.terminate()
        
        
        