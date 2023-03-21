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

modebutton = Rect(20, 190, 80, 30, fill=0x000000)#sets start coordinates, width, height, and fill color of the rectangle that will be the button to change screen modes
splash.append(modebutton) #adds to splash

mode_label = displayio.Group(scale=2, x=37, y=203) #sets size and start position of message
text = "MODE"
text_area = label.Label(terminalio.FONT, text=text, color=0xAFAFAF) #adds text to label button created previously to display group
mode_label.append(text_area)  #subgroup for text scaling
splash.append(mode_label) #adds to splash

colorbutton = Rect(80, 80, 160, 80, fill=0x000000)#sets start coordinates, width, height, and fill color of the rectangle that will be the button to trigger the color-change of the background
splash.append(colorbutton) #adds to splash

text_group = displayio.Group(scale=3, x=100, y=115) #sets size and start position of message
text = "Random!"
text_area = label.Label(terminalio.FONT, text=text, color=0xAFAFAF) #adds text to label button created previously to display group
text_group.append(text_area)  #subgroup for text scaling
splash.append(text_group) #adds to splash

line_bitmap = displayio.Bitmap(230, 170, 1)

paint_mode = False
color_mode = True
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
            if y >= 80 and y <= 160 and x >= 80 and x <= 240 and color_mode==True:
                random_color = random.choice(color_list)
                color_palette[0] = random_color #chooses a random color from the list of colors and sets it to the color of the background sprite
                time.sleep(1)

            if y >= 190 and y <= 220 and x >= 20 and x <= 100 and color_mode==True and paint_mode==False:
                if(time.monotonic() - last_mode_time < 1):
                    continue
                last_mode_time = time.monotonic()
                for i in range(len(splash)-1, 2, -1): #goes through the contents of splash backwards until it reaches position [1], which is the second thing in the list. This ensures that it doesn't remove the background, mode button, or mode button label
                     splash.pop(i) #goes through splash and removes everything else from display, saves memory, important to do so code can run indefinitely
                modebutton.hidden = True #hides mode button for a smoother transition between modes
                mode_label.hidden = True #hides mode button label for smoother transition between modes
                time.sleep(.1)
                modebutton.hidden = False #shows mode button for a smoother transition between modes
                mode_label.hidden = False #shows mode button label for smoother transition between modes
                color_palette[0] = 0xAFAFAF #changes the color of the background
                divider = Rect(0, 165, 320, 3,  fill=0x000000)
                splash.append(divider)
                print("entering paint mode!")
                color_mode = False
                paint_mode = True

            if paint_mode==True and y < 155:
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
                ''' if (time.monotonic() - last_touch_time <= 2): #and last_touch[0] - x <= 2 and last_touch[1] - y <= 2:
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
                    splash.append(polygon)'''
            
            if y >= 190 and y <= 220 and x >= 20 and x <= 100 and color_mode==False and paint_mode==True:
                if(time.monotonic() - last_mode_time < 1):
                    continue
                last_mode_time = time.monotonic()
                for i in range(len(splash)-1, 2, -1): #goes through the contents of splash backwards until it reaches postition [1], which is the second thing in the list. This ensures that it doesn't remove the background, mode button, or mode button label
                     splash.pop(i) #goes through splash and removes everything else from display, saves memory, important to do so code can run indefinitely
                modebutton.hidden = True #hides mode button for a smoother transition between modes
                mode_label.hidden = True #hides mode button label for smoother transition between modes
                time.sleep(.1)
                modebutton.hidden = False #shows mode button for a smoother transition between modes
                mode_label.hidden = False #shows mode button label for smoother transition between modes
                colorbutton = Rect(80, 80, 160, 80, fill=0x000000)#sets start coordinates, width, height, and fill color of the rectangle that will be the button to trigger the color-change of the background
                splash.append(colorbutton) #adds to splash
                text_group = displayio.Group(scale=3, x=100, y=115) #sets size and start position of message
                text = "Random!"
                text_area = label.Label(terminalio.FONT, text=text, color=0xAFAFAF) #adds text to label button to display group
                text_group.append(text_area)  #subgroup for text scaling
                splash.append(text_group) #adds to splash
                print("entering color mode!")
                color_mode = True
                paint_mode = False
            #last_touch_time = time.monotonic()
    except OSError as error:
        pass
   # except MemoryError as error:
       # displayio.remove(splash)
        
