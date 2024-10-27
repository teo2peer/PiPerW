from PIL import Image, ImageDraw, ImageFont
from PiPerW.helpers import DirFilter 
from PiPerW.helpers import Log
from PiPerW.helpers import Config
from PiPerW.driver.pheripherals import Pheripherals
from PiPerW.driver.display import Display
import os
import re

# FIXME: This is a workaround for avoiding passiing the width and height to the Menu class. Need to find a better solution instead of importing Display

Pheripheral = Pheripherals()

display = Display()
class Menu:
    
    def __init__(self, texts, icons=None, pattern=None, font=ImageFont.load_default(), horizontal_margin=10, vertical_margin=10, item_padding = 10, background_color=0, accent_color=255):
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
        
        self.width = display.width
        self.height = display.height
        self.item_height = display.item_height
        self.font = font
        self.horizontal_margin = horizontal_margin
        self.vertical_margin = vertical_margin
        self.padding = item_padding
        
        self.selected_item_padding = 6
        self.selected_item_border_thickness = 2
        
        self.background_color = background_color
        self.accent_color = accent_color
        
        self.max_items_on_screen = (self.height - 2 * self.vertical_margin) // (self.item_height + self.padding)
        self.items =  []
        self.icons = icons
        self.texts =  texts
        
        
        self.start_index = 0
        self.index = 0
        
        # remove all items that start with __
        self.texts = [text for text in self.texts if not text.startswith("__")]
        
        if pattern:
            Log.info("Filtering items")
            self.filter(pattern)
        
        if len(self.texts) < 1:
            texts = ["Empty"]
        
        Log.info("Creating menu items")
        for i in range(len(self.texts)):
            Log.info(f"Creating item {i}")
            self.items.append(self.create_item(self.texts[i], self.icons[i] if self.icons else None))
        
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
        
        icon_offset_x = 0  # Initial offset for the icon
        icon_size = self.item_height  # Assuming the icon is a square of item height
        
        # Calculate the text position based on whether there's an icon
        text_x = icon_offset_x + (icon_size + 4 if icon else 0)  # Initial offset for the text
        print(text_x)
        
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
        
        border_thickness = self.selected_item_border_thickness
        padding = self.selected_item_padding
        
        # Create a new image for the border, slightly larger than the item
        border_width = self.width - self.horizontal_margin
        border_height = item.height + padding * 2
        
        border = Image.new('1', (border_width, border_height+padding), 0)
        draw = ImageDraw.Draw(border)
        
        # Rounded rectangle parameters
        border_radius = 8
        rect_x0 = 0
        rect_y0 = 0
        rect_x1 = self.width - self.horizontal_margin 
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
        Ensure the next item is partially visible if there are more items available.
        The last item is fully displayed only if it is the selected item.
        '''
        
        img = Image.new('1', (self.width, self.height), background_color)
        draw = ImageDraw.Draw(img)

        # Adjust the start_index if necessary
        if self.index >= self.start_index + self.max_items_on_screen:
            self.start_index = self.index - self.max_items_on_screen + 1
        elif self.index < self.start_index:
            self.start_index = self.index

        # Calculate the y position of the first item
        y = self.vertical_margin
        x = 0

        # Determine how many items to draw (add one extra to partially show the next item)
        end_index = min(self.start_index + self.max_items_on_screen + 1, len(self.items))

        # Draw the menu items
        

        # Handle the last item being fully displayed only if selected
        if self.index == len(self.items) - 1 and  end_index >= len(self.items) and len(self.items) > self.max_items_on_screen:
            last_item_y = self.height - self.padding - self.item_height - self.vertical_margin
            
            
            # The last item is selected, display it fully
            img.paste(self.selected_item(self.items[-1]), (0, last_item_y))
            # the previous item is not selected, display it partially
            img.paste(self.items[-2], (x, last_item_y - (self.item_height + self.padding)))
            
            
            # print the rest of the items in the menu from down to up
            for i in range(end_index - 3, self.start_index - 1, -1):
                item = self.items[i]
                img.paste(item, (x, last_item_y - (self.item_height + self.padding) * (end_index - i - 1)))
                
            
        else:
            for i in range(self.start_index, end_index):
                item = self.items[i]

                # Draw the selected item with a rounded rectangle
                if i == self.index:
                    item = self.selected_item(item)
                    img.paste(item, (0, y))
                else:
                    img.paste(item, (x, y + 6))

                y += self.item_height + self.padding
        return img
        
    
    def add_item(self, text, icon=None):
        '''
        Add an item to the menu
        
        :param text: str: Text of the item
        :param icon: Image: Icon of the item
        '''
        
        self.items.append(self.create_item(text, icon))
        
    def filter(self, regex):
        '''
        Filter the items based on regex pattern

        :param text: str: Text to filter
        '''
        pattern = re.compile(regex)
        self.texts = [text for text in self.texts if pattern.match(text)]
    
    def show(self):
        '''
        Show the menu
        '''
        
        display.draw(self.generate())
    
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
    
    def choose(self):
        '''
        Choose the selected item
        '''
        print(self.texts)
        self.show()
        while True:
            key = Pheripheral.get_key()
            if key in ("up", "down"):
                self.__handle_menu_navigation(key)
            elif key == "select":
                return self.get_selected()
            elif key == "back" or key == "exit":
                return None
        
        
        
    def __handle_key_press(key):
        '''
        Handle the key press
        
        :param key: str: The key pressed
        :param menu: Menu: The menu object
        '''
        if key in ("up", "down", "select"):
            self.__handle_menu_navigation(key)
        elif key == "back":
            return

    def __handle_menu_navigation(key):
        '''
        Handle the menu navigation
        
        :param key: str: The key pressed
        :param menu: Menu: The menu object
        '''
        if key == "up":
            self.previous()
        elif key == "down":
            self.next()
        self.show()
        


class MenuBase(Menu):
    
    def __init__(self, items, folder, show_icons=False, pattern=None, font=ImageFont.load_default(), horizontal_margin=10, vertical_margin=10, item_padding=10, background_color=0, accent_color=255):
        
        self.folder = folder
        
        icons = None
        if show_icons:
            icons = []
            for item in items:
                icon_path = f"{folder}/{item}/icon.bmp" if os.path.isdir(f"{folder}/{item}") else f"{folder}/{item}.bmp"
                icon = Image.open(icon_path) if os.path.exists(icon_path) else Image.open(f"PiPerW/themes/{Config['general']['theme']}/resources/no.bmp")
                icons.append(icon)
        
        super().__init__(items, icons, pattern, font, horizontal_margin, vertical_margin, item_padding, background_color, accent_color)
    
    def get_full_path(self):
        return f"{self.folder}/{self.get_selected()}"

class MenuFolder(MenuBase):
    
    def __init__(self, parent_folder, show_icons=False, pattern=None, font=ImageFont.load_default(), horizontal_margin=10, vertical_margin=10, item_padding=10, background_color=0, accent_color=255):
        
        folders = DirFilter(parent_folder).folders()
        super().__init__(folders, parent_folder, show_icons, pattern, font, horizontal_margin, vertical_margin, item_padding, background_color, accent_color)


class MenuFolderFiles(MenuBase):
    
    def __init__(self, folder, show_icons=False, pattern=None, font=ImageFont.load_default(), horizontal_margin=10, vertical_margin=10, item_padding=10, background_color=0, accent_color=255):
        
        files = DirFilter(folder).files()
        super().__init__(files, folder, show_icons, pattern, font, horizontal_margin, vertical_margin,item_padding, background_color, accent_color)


class MenuFromDataFolder(MenuBase):
    
    def __init__(self, folder, type_items="file", show_icons=False, pattern=None, font=ImageFont.load_default(), horizontal_margin=10, vertical_margin=10, item_padding=10, background_color=0, accent_color=255):
        
        folder = f"data/{folder.strip('/')}"
        os.makedirs(folder, exist_ok=True)
        
        items = DirFilter(folder).files() if type_items == "file" else DirFilter(folder).folders()
        super().__init__(items, folder, show_icons, pattern, font, horizontal_margin, vertical_margin, item_padding, background_color, accent_color)