class Display():
    def __init__(self):
        pass
    
    def init(self):
        pass
    
    def reset(self):
        pass
    
    def show_image(self, buffer):
        pass
    
    def clear(self):
        pass
    
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