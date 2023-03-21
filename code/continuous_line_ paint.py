#type: ignore

import gc
import random
import time

import adafruit_focaltouch
import adafruit_ili9341
import board
import busio
import displayio
import terminalio
from math import sqrt
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.polygon import Polygon
from adafruit_display_text import label

displayio.release_displays() #set up for screen by releasing all used pins for new display

spi = busio.SPI(clock=board.D13, MOSI=board.D11, MISO=board.D12)

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

divider = Rect(0, 165, 320, 3,  fill=0x000000)
splash.append(divider)

line_bitmap = displayio.Bitmap(230, 170, 1)

last_mode_time = -10
last_touch_time = 0
last_touch = (0, 0)

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
            #print(ts)
            try:
                point = ts[0]  # the shield only supports one point!
            except:
                pass
            #perform transformation to get into display coordinate system! 
            # While the TFT shield uses one corner and orientation, focal touch views the screen as if it's rotated 90 degrees, then puts the origin at the top left corner
            # The next two lines of code must be done in order to have focal touch and the TFT screen use the same origin
            y = point["x"]
            x = 320 - point["y"] 

            #print(f"{x} , {y}")
            if y < 155:
                gc.collect()
                rect_allowed = True #creates a variable to determine if a pixel has already been placed at a coordinate set, prevents unnecessary pixel placement
                #random_color = random.choice(color_list)
                for obj in splash:
                    if obj.y == y and obj.x == x:
                        rect_allowed = False
                        break
                if rect_allowed:
                    rect = Rect(x-3, y-3, 6, 6, fill=red)
                    last_touch = (x-3, y-3)
                    splash.append(rect)
                if (time.monotonic() - last_touch_time <= 2): #and last_touch[0] - x <= 2 and last_touch[1] - y <= 2:
                    #lots of geometry here to find points for polygon/connection line!
                    slope = (y - last_touch[1])/(x - last_touch[0])
                    perp_slope = -1/slope
                    offset_vector = (1/(sqrt(1 + perp_slope**2)), perp_slope/(sqrt(1 + perp_slope**2)))
                    offset = (int(offset_vector[0] * 3), int(offset_vector[1] * 3))
                    polygon = Polygon(
                        [
                            (x + offset[0], y + offset[1]),
                            (x - offset[0], y - offset[1]),
                            (last_touch[0] - offset[0], last_touch[1] - offset[1]),
                            (last_touch[0] + offset[0], last_touch[1] + offset[1])
                        ],
                        outline = red,
                        fill = red
                    )
                    splash.append(polygon)
                last_touch_time = time.monotonic()
    except OSError as error:
        pass
   # except MemoryError as error:
       # displayio.remove(splash)
        
