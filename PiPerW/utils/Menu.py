from PIL import Image, ImageDraw, ImageFont
from PiPerW.helpers import DirFilter 
from PiPerW.helpers import Log
import os


class Menu:
    
    def __init__(self, width, height, texts, icons=None, font=ImageFont.load_default(), horizontal_margin=10, vertical_margin=10, item_height=16, item_padding = 10, background_color=0, accent_color=255):
        '''
        Initialize the menu
        
        :param width: int: Width of the display
        :param height: int: Height of the display
        :param font: ImageFont: Font to use for the menu
        :param horizontal_margin: int: Horizontal margin for the menu
        :param vertical_margin: int: Vertical margin for the menu
        :param item_height: int: Height of each item in the menu
        '''
        
        Log.warning("Initializing menu")
        
        self.width = width
        self.height = height
        self.font = font
        self.horizontal_margin = horizontal_margin
        self.vertical_margin = vertical_margin
        self.item_height = item_height
        self.padding = item_padding
        self.background_color = background_color
        self.accent_color = accent_color
        
        self.items =  []
        self.icons = icons
        self.texts =  texts
        
        self.index = 0
        
        Log.info("Creating menu items")
        for i in range(len(texts)):
            Log.info(f"Creating item {i}")
            self.items.append(self.create_item(texts[i], icons[i] if icons else None))
        
        Log.info("Menu initialized")
        
        
    
    def create_item(self, text, icon=None):
        '''
        Create a menu item
        
        :param text: str: Text of the item
        :param selected: bool: Whether the item is selected
        '''
        
        item = Image.new('1', (self.width-self.horizontal_margin, self.item_height), 0)
        draw = ImageDraw.Draw(item)
        
        # Draw the background for the item
        draw.rectangle((0, 0, self.width, self.item_height), outline=0, fill=self.background_color)
        
        icon_offset_x = self.horizontal_margin  # Initial offset for the icon
        icon_size = self.item_height  # Assuming the icon is a square of item height
        
        # Calculate the text position based on whether there's an icon
        text_x = icon_offset_x + (icon_size + 4 if icon else 16)
        
        # Calculate text height for vertical centering
        text_bbox = self.font.getbbox(text)  # Measure the text, not the draw object
        text_height = text_bbox[3] - text_bbox[1]
        text_y = (self.item_height - text_height) // 2  # Center the text vertically
        
        # Draw the icon if available
        if icon is not None:
            # icon = icon.convert('1')
            # resize icon to item height
            wpercent = (icon_size/float(icon.size[0]))
            hsize = int((float(icon.size[1])*float(wpercent)))
            icon = icon.resize((icon_size,hsize),  Image.LANCZOS)
            
            icon = icon.convert('1')
            
            item.paste(icon, (icon_offset_x, (self.item_height - icon_size) // 2), icon)
            
        # Draw the text
        draw.text((text_x, text_y), text, font=self.font, fill=self.accent_color)
        
        return item
        
    def selected_item(self, item):
        '''
        Draw a rounded border around the selected item and return the resulting image.

        :param item: Image: The image of the menu item
        :param y: int: The y-coordinate where the item is drawn
        :return: Image: The image with the selected item highlighted
        '''
        
        border_thickness = 2
        padding = 6
        
        # Create a new image for the border, slightly larger than the item
        border_width = self.width - self.horizontal_margin
        border_height = item.height + padding * 2
        
        border = Image.new('1', (border_width, border_height+padding), 0)
        draw = ImageDraw.Draw(border)
        
        # Rounded rectangle parameters
        border_radius = 8
        rect_x0 = padding
        rect_y0 = 0
        rect_x1 = border_width - padding 
        rect_y1 = border_height
        
        # Draw rounded rectangle around the selected item
        draw.rounded_rectangle(
            [rect_x0, rect_y0, rect_x1, rect_y1],
            radius=border_radius,
            outline=self.accent_color,
            width=border_thickness
        )
        
        # Paste the item into the border
        border.paste(item, (padding+border_thickness, padding))
        
        return border
        
    def generate(self, icons=None, color=255, background_color=0):
        '''
        Generate a menu with selectable items and rounded borders for the selected item.

        :param icons: list: List of icons for each item
        :param color: int: Color of the text (single channel, e.g., 255 for white)
        :param background_color: int: Background color of the menu (single channel, e.g., 0 for black)
        '''

        img = Image.new('1', (self.width, self.height), background_color)
        draw = ImageDraw.Draw(img)
        
        # Calculate the y position of the first item
        y = self.vertical_margin
        x = self.horizontal_margin
        # Draw the background for the menu
        draw.rectangle((0, 0, self.width, self.height), outline=0, fill=background_color)
        
        # Draw the menu items
        for i in range(len(self.items)):
            item = self.items[i]
            
            # Draw the selected item with a rounded rectangle
            if i == self.index:
                item = self.selected_item(item)
                img.paste(item, (x, y))
            else:
                # Paste the item into the menu with margin
                img.paste(item, (x, y+6))
            
            y += self.item_height + self.padding
        
        
        # rerturn the image
        return img
        
        
    def next(self):
        '''
        Move the selection to the next item
        '''
        
        self.index += 1
        if self.index >= len(self.items):
            self.index = 0
            
    def previous(self):
        '''
        Move the selection to the previous item
        '''
        
        self.index -= 1
        if self.index < 0:
            self.index = len(self.items) - 1
        
    def get_selected(self):
        '''
        Get the selected item
        
        :return: str: Selected item
        '''
        
        return self.texts[self.index]
    
    def get_index(self):
        '''
        Get the selected item index
        
        :return: int: Selected item index
        '''
        
        return self.index
        
class MenuFolder(Menu):
    
    def __init__(self, width, height, parent_folder, font=ImageFont.load_default(), horizontal_margin=10, vertical_margin=10, item_height=16, item_padding = 10, background_color=0, accent_color=255):
        '''
        Initialize the menu
        
        :param width: int: Width of the display
        :param height: int: Height of the display
        :param font: ImageFont: Font to use for the menu
        :param horizontal_margin: int: Horizontal margin for the menu
        :param vertical_margin: int: Vertical margin for the menu
        :param item_height: int: Height of each item in the menu
        '''
        
        # get all files in the folder
        folders = DirFilter(parent_folder).folders()
        
        # get the icon of each folder
        icons = []
        for folder in folders:
            # check if icon exists
            
            if not os.path.exists(f"{parent_folder}/{folder}/icon.bmp"):
                Log.warning(f"Icon not found for folder {folder}")
                icon = Image.open("PiPerW/display/no.bmp")
            else:
                icon = Image.open(f"{parent_folder}/{folder}/icon.bmp")
            icons.append(icon)
            
        
        
        super().__init__(width, height, folders, icons, font, horizontal_margin, vertical_margin, item_height, item_padding, background_color, accent_color)

        
    
class MenuFolderFile(Menu):
    
    def __init__(self, width, height, folder, show_icons, font=ImageFont.load_default(), horizontal_margin=10, vertical_margin=10, item_height=16, item_padding = 10, background_color=0, accent_color=255):
        '''
        Initialize the menu
        
        :param width: int: Width of the display
        :param height: int: Height of the display
        :param font: ImageFont: Font to use for the menu
        :param horizontal_margin: int: Horizontal margin for the menu
        :param vertical_margin: int: Vertical margin for the menu
        :param item_height: int: Height of each item in the menu
        '''
        
        files = DirFilter(folder).files()
        if show_icons:
            icons = []
            for file in files:
                icon = Image.open(f"{folder}/{file}.bmp")
                icons.append(icon)
        else:
            icons = None
        
        
        super().__init__(width, height, files, icons, font, horizontal_margin, vertical_margin, item_height, item_padding, background_color, accent_color)
    
    