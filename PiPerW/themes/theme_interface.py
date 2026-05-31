from PIL import Image, ImageDraw, ImageFont, ImageOps

class ThemeInterface:
    def __init__(self):
        '''
        Initialize the theme
        
        :param width: int: Width of the display
        :param height: int: Height of the display
        '''
        self.name = "base_theme"
        self.frame_index = 0
        self.max_frames = 0

        self.frameArray = [] # Array to store the frames from frames/{theme} folder
        
        
    def next_frame(self):
        '''
        Loop through the frames
        
        :return: Image: The next frame
        '''
        if self.frame_index == self.max_frames:
            self.frame_index = 0
        
        frame = self.frameArray[self.frame_index]
        self.frame_index += 1
        return frame
    
    def get_frames(self, theme):
        '''
        Get all the frames from the frames/{theme} folder
        
        :param theme: str: The theme to get the frames from
        :return: list: List of frames
        '''
        frames = []
        for i in range(0, 100):
            try:
                frame = Image.open('PiPerW/themes/{}/frames/{}.bmp'.format(theme, i))
                frames.append(frame)
            except Exception:
                self.max_frames = i
                break
        return frames