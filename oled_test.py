import board 
import busio 
import time
import digitalio


i2c = busio.I2C(board.SCL, board.SDA)
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont

# Create the SSD1306 OLED class.
# The first two parameters are the pixel width and pixel height.  Change these
# to the right size for your display!
oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
# Alternatively you can change the I2C address of the device with an addr parameter:
#display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, addr=0x31)

# Clear the display.  Always call show after changing pixels to make the display
# update visible!
oled.fill(0)

oled.show()

'''Basic pixel operaitons'''
# # Set a pixel in the origin 0,0 position.
# oled.pixel(0, 0, 1)
# # Set a pixel in the middle 64, 16 position.
# oled.pixel(64, 16, 1)
# # Set a pixel in the opposite 127, 31 position.
# oled.pixel(127, 31, 1)
# oled.show()

'''Clock example'''
# Create blank image for drawing.
image = Image.new("1", (oled.width, oled.height))
draw = ImageDraw.Draw(image)

# Load a font in 2 different sizes.
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
font2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)

offset = 0  # flips between 0 and 32 for double buffering

while True:
    # write the current time to the display after each scroll
    draw.rectangle((0, 0, oled.width, oled.height * 2), outline=0, fill=0)
    text = time.strftime("%X")
    draw.text((0, 0), text, font=font, fill=255)
    text = time.strftime("%a %e %b %Y")
    draw.text((0, 14), text, font=font, fill=255)
    text = time.strftime("%X")
    draw.text((0, 30), text, font=font, fill=255)
    oled.image(image)
    oled.show()

    time.sleep(1)

    for i in range(0, oled.height // 2):
        offset = (offset + 1) % oled.height
        print(oled.height, offset)
        oled.write_cmd(adafruit_ssd1306.SET_DISP_START_LINE | offset)
        # oled.scroll(delta_x=0, delta_y=-offset)
        oled.show()
        time.sleep(0.001)

'''Pill time logo '''

# # Load a font in 2 different sizes.
# font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
# font2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
# width = oled.width
# height = oled.height
# image = Image.new("1", (oled.width, oled.height))
# draw = ImageDraw.Draw(image)
# # Draw some shapes.
# # First define some constants to allow easy resizing of shapes.
# padding = 2
# shape_width = 40
# top = padding
# bottom = height - padding
# # Move left to right keeping track of the current x position for drawing shapes.
# x = padding
# # Draw an ellipse.
# while(True):
#     draw.ellipse((x, top, x + shape_width, bottom), outline=255, fill=0)
#     text = "PILL"
#     text2= "TIME"
#     draw.text((8, 5), text, font=font, fill=255)
#     draw.text((60, 0), text, font=font2, fill=255)
#     draw.text((60, 15), text2, font=font2, fill=255)
#     # Display image.
#     oled.image(image)
#     oled.show()
#     time.sleep(1)
#     oled.fill(0)
#     oled.show()
#     time.sleep(0.1)