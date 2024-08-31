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
        self.path = os.path.dirname(os.path.realpath(__file__)) 
        # get root program path
        self.root_path = os.path.dirname(os.path.dirname(os.path.dirname(self.path)))
        self.lib_path = "PiPerW/lib/PiFmRds"
        # check if PiFmRds is installed 
        
        if not os.path.exists(self.lib_path) or not os.path.exists(self.lib_path + "/src/pi_fm_rds"):
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
                if os.path.exists(self.lib_path):
                    res = os.system("rm -rf "+self.lib_path)
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
    
        self.executable = self.root_path +'/'+ self.lib_path + "/src/pi_fm_rds"
        self.frequency = 100.0
        
        print("Executable: ", self.executable)

        
    
    def fix_makefile_pi_zerow(self):
        '''
            Fix makefile for Pi Zero W
        '''

        Log.warning("Fixing makefile for Pi Zero W")
        
        # patch makefile
        makefile = self.lib_path + "/src/Makefile"
        # replace makefile with this one
        text = '''
CC = gcc
STD_CFLAGS = -Wall -std=gnu99 -c -g


# Determine hardware platform and set proper compilation flags based on user choice

ARCH_CFLAGS = -march=armv7-a -O3 -mtune=arm1176jzf-s -mfloat-abi=hard -mfpu=vfp -ffast-math
TARGET = 2

CFLAGS = $(STD_CFLAGS) $(ARCH_CFLAGS) -DRASPI=$(TARGET)

ifneq ($(TARGET), 4)

app: rds.o waveforms.o pi_fm_rds.o rds_strings.o fm_mpx.o control_pipe.o mailbox.o
	$(CC) $(LDFLAGS) -o pi_fm_rds rds.o rds_strings.o waveforms.o mailbox.o pi_fm_rds.o fm_mpx.o control_pipe.o -lsndfile -lm

endif


rds_wav: rds.o rds_strings.o waveforms.o rds_wav.o fm_mpx.o
	$(CC) $(LDFLAGS) -o rds_wav rds_wav.o rds.o rds_strings.o waveforms.o fm_mpx.o -lsndfile -lm

rds_strings.o: rds_strings.c rds_strings.h
	$(CC) $(CFLAGS) rds_strings.c

rds_strings_test: rds_strings.o rds_strings_test.c
	$(CC) -Wall -std=gnu99 -o rds_strings_test rds_strings.o rds_strings_test.c
	./rds_strings_test

rds.o: rds.c waveforms.h rds_strings.o
	$(CC) $(CFLAGS) rds.c

control_pipe.o: control_pipe.c control_pipe.h rds.h
	$(CC) $(CFLAGS) control_pipe.c

waveforms.o: waveforms.c waveforms.h
	$(CC) $(CFLAGS) waveforms.c

mailbox.o: mailbox.c mailbox.h
	$(CC) $(CFLAGS) mailbox.c

pi_fm_rds.o: pi_fm_rds.c control_pipe.h fm_mpx.h rds.h mailbox.h
	$(CC) $(CFLAGS) pi_fm_rds.c

rds_wav.o: rds_wav.c
	$(CC) $(CFLAGS) rds_wav.c

fm_mpx.o: fm_mpx.c fm_mpx.h
	$(CC) $(CFLAGS) fm_mpx.c

clean:
	rm -f *.o *_test
'''
        with open(makefile, "w") as f:
            f.write(text)
            
        
    def run(self):
        
        
        display.text("Select frequency to play music")
        self.select_frequency()
        
        # play music
        display.text("Select a music file to play, press any key to continue")
        
        menu = MenuFolderFiles(self.path+"/music")
        
        while True:
            
            menu.show()
            key = pheripherals.await_key()
            if key == "up":
                menu.previous()
            elif key == "down":
                menu.next()
            elif key == "select":
                self.play_music(menu.get_selected())
            elif key == "back" or key == "exit":
                break
            
    
    def select_frequency(self):
        '''
        Select frequency to play music
        '''
        
        display.text("Move to change frequency\nPress select to confirm")
        
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
    
    def run_executable(self, executable, args):
        args = [str(arg) for arg in args]
        subprocess.run([executable] + args)
    
    def play_music(self, file):
        '''
        Play music file into another process
        
        :param file: music file path
        '''
        
        display.text("Playing {}".format(file)+"\nPress any key to stop")
        process = multiprocessing.Process(
            target=self.run_executable,
            args=[self.executable, ["-freq", self.frequency, "-audio", self.path+"/music/"+file]]
        )
        process.start()
        
        pheripherals.await_any_key_press()
        
        # get process id
        pid = process.pid
        
        # terminate process
        process.terminate()
        
        # make sure process is terminated with kill
        os.system("kill -9 "+str(pid))
        
        # wait for process to finish
        process.join()
        
        
        
        
        
        