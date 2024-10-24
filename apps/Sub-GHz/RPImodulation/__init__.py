from PiPerW.interfaces.app_interface import AppInterface
from PiPerW.pheripherals import Pheripherals
from PiPerW.display import Display
from PiPerW.helpers import Log, Config, download_lib_from_github, select_number
from PiPerW.utils.Menu import Menu
import os, sys, time
import subprocess


display = Display()
pheripherals = Pheripherals()



class App(AppInterface):
    
    def __init__(self):
        self.name = "RPI rpitx interface"
        self.version = "1.0"
        self.description = "Emmit RF signals with your RPI with the gpio 4 with rpitx"
        self.author = "Teo2Peer"
        
        super().__init__(self.name, self.version)
        
        # get this path
        self.path = os.path.dirname(os.path.realpath(__file__)) 
        # get root program path
        self.root_path = os.path.dirname(os.path.dirname(os.path.dirname(self.path)))
        self.lib_path = "PiPerW/lib/rpitx"
        
        self.executable_root= self.root_path +'/'+ self.lib_path
        self.frequency = 433.00
        self.process = None
        
        # check if PiFmRds is installed 
        if not os.path.exists(self.lib_path) or not os.path.exists(self.lib_path + "/spectrumpaint"):
            Log.error("rpitx is not installed. Installing...")
            display.text("rpitx  is not installed. Installing...")
            time.sleep(2)
            
            
            
            # try to install PiFmRds
            try:
                display.text("Installing libsndfile1-dev... \n (1/3)")
                Log.warning("Installing libsndfile1-dev")
                res = os.system("sudo apt install libsndfile1-dev -y")
                
                if res != 0:
                    Log.error("Failed to install libsndfile1-dev")
                    display.text("Failed to install libsndfile1-dev")
                    pheripherals.await_any_key_press()
                    raise SystemError("Failed to install libsndfile1-dev")
                
                
                display.text("Downloading rpitx... \n (2/3)")
                Log.warning("Downloading rpitx")
                # remove path if exists
                if os.path.exists(self.lib_path):
                    res = os.system("rm -rf "+self.lib_path)
                    if res != 0:
                        Log.error("Failed to remove rpitx")
                        display.text("Failed to remove rpitx")
                        pheripherals.await_any_key_press()
                        raise SystemError("Failed to remove rpitx")
                
                download_lib_from_github("https://github.com/F5OEO/rpitx", "rpitx")
                
                
                # compile PiFmRds
                Log.warning("Compiling rpitx")
                res = os.system("cd PiPerW/lib/rpitx && ./install.sh")
                
                if res != 0:
                    Log.error("Failed to compile rpitx")
                    display.text("Failed to compile rpitx")
                    pheripherals.await_any_key_press()
                    raise SystemError("Failed to compile rpitx")
                
                Log.info("rpitx installed, reboot needed")
                display.text("rpitx installed, reboot needed")
            except Exception as e:
                raise SystemError("Failed to install rpitx: " + str(e))
                return
    
        
        
        print("Executable: ", self.executable_root)

        
        
    def run(self):
        
        
        
        
        # play music
        display.text("Select a option, press any key to continue")
        
        # regex pattern to filter music files like mp3, wav, etc
        options =[
            "Carrier",  
            "Chirp",
            "Spectrum",
            "SSB",
        ]
        
        menu = Menu(options)
        
        while True:
            
            menu.show()
            key = pheripherals.await_key()
            if key == "up":
                menu.previous()
            elif key == "down":
                menu.next()
            elif key == "select":
                self.exec(menu.get_selected())
            elif key == "back" or key == "exit":
                break
            
    
    
    def select_frequency(self):
        '''
        Select frequency to play music
        '''
        
        display.text("Move to change frequency\nPress select to confirm")
        multiplier = 10
        while True:
            key = pheripherals.await_key()
            text = "Select frequency\n"
            if key == "right":
                self.frequency += (0.01 * multiplier)
            elif key == "left":
                self.frequency -= (0.01 * multiplier)
            elif key == "up":
                multiplier = multiplier * 10 if multiplier < 1000 else 1000
            elif key == "down":
                multiplier = multiplier/ 10 if multiplier > 1 else 1
            elif key == "select":
                break
            elif key == "back":
                sys.exit(0)
            
            self.frequency = round(self.frequency, 2)
            text += "Frequency: {:.2f} MHz\n".format(self.frequency)
            text += "Multiplier: {}\n ↕ to modify".format(multiplier)
            display.text(text)
    
    
    def start_process(self, executable, args):
        '''
        Start a process using Popen
        
        :param executable: executable path
        :param args: arguments to pass to the executable
        '''
        Log.warning("Starting process: "+executable+" "+str(args))
        args = [str(arg) for arg in args]
        self.process = subprocess.Popen([executable] + args)

        
    def stop_process(self):
        '''
        Stop the process
        '''
        if self.process is not None:
            self.process.terminate()
        
        if self.process.poll() is None:
            self.process.kill()
            
        self.process.wait()
        self.process = None
        
    
    def exec(self, option):
        '''
        Execute the selected option
        
        :param option: selected option
        '''
        
        if option == "Carrier":
            self.play_carrier()
        elif option == "Chirp":
            self.play_chirp()
        elif option == "Spectrum":
            self.play_spectrum()
        elif option == "SSB":
            self.play_ssb()
    
    
    def play_carrier(self):
        '''
        Play carrier wave
        '''
        display.text("Select frequency to generate the carier music")
        self.select_frequency()
        
        display.text("Playing carrier wave\nPress any key to stop")
        Log.info("Playing carrier wave with frequency: "+str(self.frequency))
        
        # # Run the executable with Popen
        self.start_process(self.executable_root+"/tune", ["-f", str(self.frequency)+"e6"])
        
        pheripherals.await_any_key_press()
        
        display.text("Stopping Carrier")
        Log.info("Stopping carrier wave")
        
        self.stop_process()
            
    

    def play_chirp(self):
        '''
        Play chirp wave
        '''
        display.text("Select frequency to generate the chirp music")
        self.select_frequency()
        
        bandwith = select_number(display, pheripherals, title="Select bandwith", scale=100,  min=50000, max=100000)
        
        display.text("Playing chirp wave\nPress any key to stop")
        Log.info("Playing chirp wave with frequency: "+str(self.frequency))
        
        # # Run the executable with Popen
        self.start_process(self.executable_root+"/pichirp", [str(self.frequency)+"e6", str(bandwith), "5"] )
        
        pheripherals.await_any_key_press()
        
        display.text("Stopping Chirp")
        Log.info("Stopping chirp wave")
        
        self.stop_process()
        