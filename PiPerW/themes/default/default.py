import _base_theme_

class Theme(_base_theme_.BaseThreme):
    def __init__(self, width, height):
        super(Theme, self).__init__(width, height)
        self.name = "default"

        # get all the frames from the frames/default folder'
        self.frameArray = self.get_frames('default')
