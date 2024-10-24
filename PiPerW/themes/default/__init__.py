from PiPerW.themes.theme_interface import ThemeInterface

class Theme(ThemeInterface):
    def __init__(self):
        super(Theme, self).__init__()
        self.name = "default"

        # get all the frames from the frames/default folder'
        self.frameArray = self.get_frames('default')
