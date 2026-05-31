from PiPerW.interfaces.app_interface import AppInterface
from PiPerW.driver.pheripherals import Pheripherals
from PiPerW.driver.display import Display
from PiPerW.helpers import Log, Config, download_lib_from_github, select_number
from PiPerW.utils.Menu import Menu, MenuFromDataFolder
import os, sys, time, shutil
import subprocess


def _safe_path(path):
    """Resolve path. Reject traversal/shell metachars."""
    if not path:
        raise ValueError("Empty path")
    resolved = os.path.realpath(path)
    if not os.path.exists(resolved):
        raise FileNotFoundError(resolved)
    bad = set('`$;&|<>\n\r"\\')
    if any(c in bad for c in resolved):
        raise ValueError(f"Refusing unsafe path: {resolved!r}")
    return resolved


display = Display()
pheripherals = Pheripherals()



class App(AppInterface):
    
    def __init__(self):
        self.name = "RPI rpitx interface"
        self.version = "1.0"
        self.description = "Emmit RF signals with your RPI with the gpio 4 with rpitx"
        self.author = "Teo2Peer"
        
        super().__init__()
        
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
                res = subprocess.run(["sudo", "apt", "install", "libsndfile1-dev", "-y"]).returncode

                if res != 0:
                    Log.error("Failed to install libsndfile1-dev")
                    display.text("Failed to install libsndfile1-dev")
                    self.wait_for_input(getattr(self, 'process', None))
                    raise SystemError("Failed to install libsndfile1-dev")
                
                
                display.text("Downloading rpitx... \n (2/3)")
                Log.warning("Downloading rpitx")
                # remove path if exists
                if os.path.exists(self.lib_path):
                    try:
                        shutil.rmtree(self.lib_path)
                    except Exception as e:
                        Log.error(f"Failed to remove rpitx: {e!r}")
                        display.text("Failed to remove rpitx")
                        self.wait_for_input(getattr(self, 'process', None))
                        raise SystemError("Failed to remove rpitx")
                
                download_lib_from_github("https://github.com/F5OEO/rpitx", "rpitx")
                
                
                # compile PiFmRds
                Log.warning("Compiling rpitx")
                res = subprocess.run(["./install.sh"], cwd="PiPerW/lib/rpitx").returncode
                
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
        Stop the process (or pipeline). self.process may be a Popen
        or a list of Popen (pipeline).
        '''
        if self.process is None:
            return
        procs = self.process if isinstance(self.process, list) else [self.process]
        for p in procs:
            try:
                if p.poll() is None:
                    p.terminate()
            except Exception as e:
                Log.warning(f"terminate failed: {e!r}")
        for p in procs:
            try:
                p.wait(timeout=2)
            except Exception:
                try:
                    p.kill()
                except Exception as e:
                    Log.warning(f"kill failed: {e!r}")
        self.process = None

    def start_pipeline(self, stages):
        """Start a pipeline of argv lists. No shell. Returns list of Popen."""
        procs = []
        prev_stdout = None
        for i, argv in enumerate(stages):
            is_last = (i == len(stages) - 1)
            p = subprocess.Popen(
                argv,
                stdin=prev_stdout,
                stdout=None if is_last else subprocess.PIPE,
            )
            if prev_stdout is not None:
                prev_stdout.close()
            prev_stdout = p.stdout
            procs.append(p)
        self.process = procs
        return procs
        
    
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
        try:
            image = _safe_path(image)
        except Exception as e:
            Log.error(f"Rejected image path: {e!r}")
            display.text("Invalid image path")
            return
        res = subprocess.run([
            "convert", image,
            "-resize", "320x256",
            "-flip",
            "-quantize", "YUV",
            "-dither", "FloydSteinberg",
            "-colors", "4",
            "-interlace", "partition",
            "/tmp/spectrum.yuv",
        ]).returncode
        if res != 0:
            Log.error(f"convert failed rc={res}")
            display.text("convert failed")
            return
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

        try:
            audio_file = _safe_path(audio_file)
        except Exception as e:
            Log.error(f"Rejected audio path: {e!r}")
            display.text("Invalid audio path")
            return

        # Pipeline (no shell): convert_i16_f | gain_ff | dsb_fc | sendiq
        # First stage stdin is fed by a Python loop that re-reads the file.
        import threading
        conv = subprocess.Popen(
            ["csdr", "convert_i16_f"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        )
        gain = subprocess.Popen(
            ["csdr", "gain_ff", "4.0"],
            stdin=conv.stdout, stdout=subprocess.PIPE,
        )
        conv.stdout.close()
        dsb = subprocess.Popen(
            ["csdr", "dsb_fc"],
            stdin=gain.stdout, stdout=subprocess.PIPE,
        )
        gain.stdout.close()
        send = subprocess.Popen(
            [self.executable_root + "/sendiq", "-s", "48000",
             "-f", f"{self.frequency}e6", "-t", "i16", "-i", "-"],
            stdin=dsb.stdout,
        )
        dsb.stdout.close()
        self.process = [conv, gain, dsb, send]

        stop_feed = threading.Event()
        def _feeder():
            try:
                while not stop_feed.is_set() and conv.poll() is None:
                    with open(audio_file, "rb") as f:
                        while not stop_feed.is_set():
                            chunk = f.read(8192)
                            if not chunk:
                                break
                            try:
                                conv.stdin.write(chunk)
                            except (BrokenPipeError, ValueError):
                                return
            finally:
                try:
                    conv.stdin.close()
                except Exception:
                    pass
        feeder = threading.Thread(target=_feeder, daemon=True)
        feeder.start()
        try:
            self.wait_for_input(send)
        finally:
            stop_feed.set()
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
        
        try:
            iq_file = _safe_path(iq_file)
        except Exception as e:
            Log.error(f"Rejected IQ path: {e!r}")
            display.text("Invalid IQ path")
            return

        # get type and sample rate
        tipe_file, sample_rate = iq_file.split("-")[-2:]
        sample_rate = sample_rate.split(".")[0]
        if tipe_file not in ("u8", "i16"):
            Log.error(f"Unknown IQ type: {tipe_file}")
            display.text("Unknown IQ type")
            return
        if not sample_rate.isdigit():
            Log.error(f"Invalid sample rate: {sample_rate}")
            display.text("Invalid sample rate")
            return

        self.start_process(self.executable_root+"/sendiq", ["-s", sample_rate, "-f", str(self.frequency)+"e6", "-t", tipe_file, "-i", iq_file])
        self.wait_for_input(getattr(self, 'process', None))
        self.stop_process()
