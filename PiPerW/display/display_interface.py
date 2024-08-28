from PiPerW.utils.Singleton import Singleton
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import importlib
from PiPerW.helpers import WThread, Config, Log 
import os, time



class DisplayInterface(metaclass=Singleton):
    def __init__(self, width, height, item_height=16, horizontal_margin=10, vertical_margin=10, type="b"):
        self.width = width
        self.height = height
        
        # item height and margins 
        self.item_height = item_height
        self.horizontal_margin = horizontal_margin
        self.vertical_margin = vertical_margin
        self.type = type
        
        # invert image x degr
        self.rotate = Config['display']['rotate']
        
        # load default font
        self.font = ImageFont.load_default()
        
        try:
            self.theme = importlib.import_module("PiPerW.themes.{}".format(Config['general']['theme'])).Theme()
        except Exception as e:
            Log.exception("Error loading theme: {}".format(e))
            sys.exit(1)
        
        
        self.trhead = None
        
        
    
    
    
    def init(self):
        pass
    
    def reset(self):
        pass
    
    
    # DO NOT MODIFY
    def draw(self, image):
        print("Drawing image")
        # check if image is a buffer, pillow or normal image
        if type(image) == np.ndarray:
            image = Image.fromarray(image)
        elif type(image) != Image.Image:
            raise ValueError("Image must be a buffer, pillow or normal image")
        
        # Resize with same aspect ratio
        if(self.type == "RGB"):
            image = self.convert_to_rgb(image)
            
        
        # replace or create image in PiPerW/tmp
        # create tmp folder if not exists
        if not os.path.exists("PiPerW/tmp"):
            os.makedirs("PiPerW/tmp")
        image.save("PiPerW/tmp/display.png")
        
        # rotate image if necessary
        if self.rotate != 0:
            image = image.rotate(self)
        
        self.show(image)
        
    def image(self, image):
        '''
        Display an image
        
        :param image: Image: Image to display
        '''
        
        if type(image) == str:
            image = Image.open(image)
        
        # Resize with same aspect ratio
        if image.size != (self.width, self.height):
            image.thumbnail((self.width, self.height))
            
        # convert to bmp
        image = image.convert('1')
        
        # Display the image
        self.draw(image)
            
    
    def show(self, image):
        pass
    
    def clear(self):
        pass
    
    def splashscreen(self):
        '''
        Display the splashscreen
        '''
        self.thread = WThread(target=self.loop_splashscreen)
        self.thread.start()
        
        
    
    def loop_splashscreen(self):
        '''
        Loop through the frames of the splashscreen
        
        :param theme: Theme: The theme to display
        '''

        while True:
            
            # check if thread is stopped
            if self.thread.stopped():
                break
                
            frame = self.theme.next_frame()
            
            
            # resize the image to cover the whole screen
            frame = frame.resize((self.width, self.height))
            
            
            self.image(frame)
            time.sleep(0.05)
            
    def stop_animation(self):
        '''
        Stop the splashscreen animation
        '''
        if self.thread:
            self.thread.stop()
            self.thread.join()
            self.thread = None
    
    def progress_bar(self, progress, message="", text_on_top = False, color=255):
        ''' 
        Display a progress bar in the middle of the screen
        
        :param progress: int: Progress in percent
        :param message: str: Message to display
        :param color: int: Color of the progress bar (hexadecimal color code)
        '''
        
        height_Bar = 16
        
        # Create a new image with white background
        img = Image.new('1', (self.width, self.height), 0)
        draw = ImageDraw.Draw(img)

        # Draw the background for the progress bar
        draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
        draw.rectangle((10, self.height / 2 - (2 + height_Bar / 2), self.width - 10, self.height / 2 + 12), outline=0, fill=255)
        
        # Calculate the filled width of the progress bar
        filled_width = ((self.width-24) * progress / 100)+12
        draw.rectangle((12, self.height / 2 - (height_Bar / 2), filled_width, self.height / 2 + 10), outline=0, fill=0)
        
        # Calculate text size and position
        text_bbox = draw.textbbox((0, 0), message, font=self.font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_x = (self.width - text_width) / 2
        
        if text_on_top:
            text_y = self.height / 2 - 25
        else:
            text_y = self.height / 2 + 20
        
        # Draw the message below the progress bar
        draw.text((text_x, text_y), message, font=self.font, fill=color)
        
        # Resize image if necessary (usually not needed if dimensions are already correct)
        img = img.resize((self.width, self.height))

        # Display the image
        self.draw(img)
        
        
    def text(self, text):
        '''
        Display a text in the middle of the screen
        
        :param text: str: Text to display
        '''
        
        # Create a new image with black background
        img = Image.new('1', (self.width, self.height), 0)
        draw = ImageDraw.Draw(img)
        
        # Calculate text size and position
        text_bbox = draw.textbbox((0, 0), text, font=self.font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_x = (self.width - text_width) / 2
        text_y = (self.height - text_height) / 2
        
        # Draw the text in the middle of the screen
        draw.text((text_x, text_y), text, font=self.font, fill=255)
        
        # Resize image if necessary (usually not needed if dimensions are already correct)
        img = img.resize((self.width, self.height))
        
        # Display the image
        self.draw(img)
        
        
        
        
    
        
        
    
    def get_buffer(self, image):
        """Convert image to buffer."""
        buf = np.full((self.width // 8) * self.height, 0xFF, dtype=np.uint8)
        image_monocolor = image.convert('1')
        imwidth, imheight = image_monocolor.size
        pixels = np.array(image_monocolor)

        if imwidth == self.width and imheight == self.height:
            for y in range(imheight):
                for x in range(imwidth):
                    if pixels[y, x] == 0:
                        buf[x + (y // 8) * self.width] &= ~(1 << (y % 8))
        elif imwidth == self.height and imheight == self.width:
            for y in range(imheight):
                for x in range(imwidth):
                    newx = y
                    newy = self.height - x - 1
                    if pixels[y, x] == 0:
                        buf[newx + (newy // 8) * self.width] &= ~(1 << (y % 8))
        return buf
    
    def convert_to_rgb(self, image):
        '''Convert image to RGB
        
        :param image: Image: Image to convert
        :return: Image: Converted image
        '''
        image = image.convert('RGB')
        return image
    