from PiPerW.apps.app_interface import AppInterface
from PiPerW.driver.pheripherals import Pheripherals
from PiPerW.driver.display import Display
from PiPerW.helpers import Log, Config, download_lib_from_github, select_number
from PiPerW.utils.Menu import Menu, MenuFromDataFolder
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
        
        display.text("This app is to test RPI RF emulation capabilities")
        time.sleep(2)
        
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
                    self.wait_for_input(getattr(self, 'process', None))
                    raise SystemError("Failed to install libsndfile1-dev")
                
                
                display.text("Downloading rpitx... \n (2/3)")
                Log.warning("Downloading rpitx")
                # remove path if exists
                if os.path.exists(self.lib_path):
                    res = os.system("rm -rf "+self.lib_path)
                    if res != 0:
                        Log.error("Failed to remove rpitx")
                        display.text("Failed to remove rpitx")
                        self.wait_for_input(getattr(self, 'process', None))
                        raise SystemError("Failed to remove rpitx")
                
                download_lib_from_github("https://github.com/F5OEO/rpitx", "rpitx")
                
                
                # compile PiFmRds
                Log.warning("Compiling rpitx")
                res = os.system("cd PiPerW/lib/rpitx && ./install.sh")
                
                if res != 0:
                    Log.error("Failed to compile rpitx")
                    display.text("Failed to compile rpitx")
                    self.wait_for_input(getattr(self, 'process', None))
                    raise SystemError("Failed to compile rpitx")
                
                Log.info("rpitx installed, reboot needed")
                display.text("rpitx installed, reboot needed")
            except Exception as e:
                raise SystemError("Failed to install rpitx: " + str(e))
                return
    
        
        
        Log.info(f"Executable: {self.executable_root}")
        
        
        
        
        # play music
        display.text("Select a option, press any key to continue")
        
        # regex pattern to filter music files like mp3, wav, etc
        options =[
            "Carrier",  
            "Chirp",
            "Spectrum",
            "AM audio",
            "SendIQ"
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
        elif option == "AM audio":
            self.play_am_audio()
        elif option == "SendIQ":
            self.send_iq()
    
    
    def play_carrier(self):
        '''
        Play carrier wave
        '''
        display.text("Select frequency to generate the carier music")
        self.frequency = select_number(display, pheripherals, start_number=self.frequency, title="Select frequency", decimals = 2,  min=400, max=500)

        
        display.text("Playing carrier wave\nPress any key to stop")
        Log.info("Playing carrier wave with frequency: "+str(self.frequency))
        
        # # Run the executable with Popen
        self.start_process(self.executable_root+"/tune", ["-f", str(self.frequency)+"e6"])
        
        self.wait_for_input(getattr(self, 'process', None))
        
        display.text("Stopping Carrier")
        Log.info("Stopping carrier wave")
        
        self.stop_process()
            
    

    def play_chirp(self):
        '''
        Play chirp wave
        '''
        display.text("Select frequency to generate the chirp music")
        # self.select_frequency()
        self.frequency = select_number(display, pheripherals, start_number=self.frequency, title="Select frequency", decimals = 2,  min=400, max=500)

        
        bandwith = select_number(display, pheripherals, title="Select bandwith", scale=100,  min=50000, max=100000)
        
        display.text("Playing chirp wave\nPress any key to stop")
        Log.info("Playing chirp wave with frequency: "+str(self.frequency))
        
        # # Run the executable with Popen
        self.start_process(self.executable_root+"/pichirp", [str(self.frequency)+"e6", str(bandwith), "5"] )
        
        self.wait_for_input(getattr(self, 'process', None))
        
        display.text("Stopping Chirp")
        Log.info("Stopping chirp wave")
        
        self.stop_process()
        
    def play_spectrum(self):
        ''' 
        Show a spectrum image
        '''
        display.text("Select frequency to generate the spectrum")
        self.frequency = select_number(display, pheripherals, start_number=self.frequency, title="Select frequency", decimals = 2,  min=400, max=500)
        
        display.text("Select image to show")
        # png, jpg, bmp, etc regex pattern
        image_menu = MenuFromDataFolder("Sub-GHz/RPImodulation", type_items="file", pattern=r".*\.(png|jpg|bmp)")
        image = image_menu.choose()
        image =image_menu.get_full_path()
        
        display.text("Showing spectrum image at frequency: "+str(self.frequency)+" MHz\nPress any key to stop")
        # pillow convert image to 320x256        
        os.system(f"convert {image} -resize 320x256 -flip -quantize YUV -dither FloydSteinberg -colors 4 -interlace partition /tmp/spectrum.yuv")
        self.start_process(self.executable_root+"/spectrumpaint", ["/tmp/spectrum.yuv", str(self.frequency)+"e6", "100000"])
        self.wait_for_input(getattr(self, 'process', None))
        self.stop_process()
        
    def play_am_audio(self):
        '''
        Play AM audio
        '''
        display.text("Select frequency to generate the AM audio")
        self.frequency = select_number(display, pheripherals, start_number=self.frequency, title="Select frequency", decimals = 2,  min=400, max=500)
        
        display.text("Select audio file to play\nFile: wav, mp3, etc in MONO")
        # wav, mp3, etc regex pattern
        audio_menu = MenuFromDataFolder("Sub-GHz/RPImodulation", type_items="file", pattern=r".*\.(wav|mp3)")
        audio_file = audio_menu.choose()
        audio_file = audio_menu.get_full_path()
        
        display.text("Playing AM audio at frequency: "+str(self.frequency)+" MHz\nPress any key to stop")
        Log.info("Playing AM audio at frequency: "+str(self.frequency)+" MHz")
        
        # comand to execute
        # (while true; do cat "$2"; done) | csdr convert_i16_f \
#   | csdr gain_ff 4.0 | csdr dsb_fc \
#   | sudo ./rpitx -i - -m IQFLOAT -f "$1" -s 48000

        self.start_process("bash", ["-c", f"(while true; do cat '{audio_file}'; done) | csdr convert_i16_f | csdr gain_ff 4.0 | csdr dsb_fc | {self.executable_root}/sendiq -s 48000 -f {self.frequency}e6 -t i16 -i -"])
        self.wait_for_input(getattr(self, 'process', None))
        self.stop_process()
        
        
    def send_iq(self):
        '''
        Send IQ data
        '''
        
        display.text("Select frequency to send the IQ file")
        self.frequency = select_number(display, pheripherals, start_number=self.frequency, title="Select frequency", decimals = 2,  min=400, max=500)
        
        display.text("Select IQ file to send\nFile: /816bit, sample rate 10000-250000")
        Log.warning("FORMAT FILE: *-(u8|i16)-[0-9]+.(wav|iq)  -> example: myiq-i16-10000.iq, myiq-u8-250000.wav")
        # wav, iq, etc regex pattern with name, format and sample rate
        iq_menu = MenuFromDataFolder("Sub-GHz/RPImodulation", type_items="file", pattern=".*-(u8|i16)-[0-9]+.(wav|iq)")
        iq_file = iq_menu.choose()
        iq_file = iq_menu.get_full_path()
        
        display.text("Sending IQ file at frequency: "+str(self.frequency)+" MHz\nPress any key to stop")
        Log.info("Sending IQ file at frequency: "+str(self.frequency)+" MHz")
        
        # get type and sample rate
        tipe_file, sample_rate = iq_file.split("-")[-2:]
        sample_rate = sample_rate.split(".")[0]
        
        self.start_process(self.executable_root+"/sendiq", ["-s", sample_rate, "-f", str(self.frequency)+"e6", "-t", tipe_file, "-i", iq_file])
        self.wait_for_input(getattr(self, 'process', None))
        self.stop_process()
