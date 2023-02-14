import random
import time

import adafruit_focaltouch
import adafruit_ili9341
import adafruit_rgb_display.ili9341 as ili9341
import board
import busio
import displayio
import terminalio
from adafruit_display_shapes.rect import Rect
from adafruit_display_text import label
from adafruit_rgb_display import color565

displayio.release_displays() #set up for screen by releasing all used pins for new display
# Use Hardware SPI
spi = board.SPI()

tft_cs = board.D10
tft_dc = board.D9

display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs)
display = adafruit_ili9341.ILI9341(display_bus, width=320, height=240)

# Make the display context
splash = displayio.Group()
display.show(splash)

# Draw a grey background
color_bitmap = displayio.Bitmap(320, 240, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0xAFAFAF  #grey

bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)

splash.append(bg_sprite)

colorbutton = Rect(80, 80, 160, 80, fill=0x000000)#sets start coordinates, width, height, and fill color of the rectangle that will be the button to trigger the color-change of the background
splash.append(colorbutton) #adds to splash

text_group = displayio.Group(scale=3, x=100, y=110) #sets size and start position of message
text = "Random!"
text_area = label.Label(terminalio.FONT, text=text, color=0xAFAFAF) #adds text to label button created previously to display group
text_group.append(text_area)  #subgroup for text scaling
splash.append(text_group) #adds to splash

i2c = busio.I2C(board.SCL, board.SDA)
ft = adafruit_focaltouch.Adafruit_FocalTouch(i2c)

# color codes and list compiling colors for randomization
red = 0xFF0000
orange = 0xFF8F00
yellow = 0xFFE700
green = 0x70FF00
teal = 0x00FFA4
blue = 0x00C6FF
indigo = 0x0029FF
purple = 0xAF00FF
pink = 0xFF00D4
color_list = [red, orange, yellow, green, teal, blue, indigo, purple, pink]

while True:
    try:
        if ft.touched: #sometimes returns empty brackets, has code ignore these instances to continue running when this happens
            ts = ft.touches
            print(ts)
            try:
                point = ts[0]  # the shield only supports one point!
            except:
                pass
            #perform transformation to get into display coordinate system! 
            # While the TFT shield uses one corner and orientation, focal touch views the screen as if it's rotated 90 degrees, then puts the origin at the top left corner
            # The next two lines of code must be done in order to have focal touch and the TFT screen use the same origin
            y = point["x"]
            x = 320 - point["y"] 
            print(f"{x} , {y}")
            if y >= 80 and y <= 160 and x >= 80 and x <= 240:
                random_color = random.choice(color_list)
                splash.remove(bg_sprite) #removes from display, saves storage space, important to do so code can run indefinitely
                splash.remove(colorbutton) #removes from display, saves storage space, important to do so code can run indefinitely
                splash.remove(text_group) #removes from display, saves storage space, important to do so code can run indefinitely
                color_bitmap = displayio.Bitmap(320, 240, 1)
                color_palette = displayio.Palette(1)
                color_palette[0] = random_color #chooses a random color from the list of colors and sets it to the color of the background sprite
                bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
                splash.append(bg_sprite)
                colorbutton = Rect(80, 80, 160, 80, fill=0x000000)#sets start coordinates, width, height, and fill color of the rectangle that will be the button to trigger the color-change of the background
                splash.append(colorbutton) #adds to splash
                text_group = displayio.Group(scale=3, x=100, y=110) #sets size and start position of message
                text = "Random!"
                text_area = label.Label(terminalio.FONT, text=text, color=0xAFAFAF) #adds text to label button to display group
                text_group.append(text_area)  #subgroup for text scaling
                splash.append(text_group) #adds to splash
                time.sleep(1)
    except OSError as error:
        pass