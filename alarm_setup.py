#!/usr/bin/env python3
########################################################################
# Filename    : MatrixKeypad.py
# Description : obtain the key code of 4x4 Matrix Keypad
# Author      : freenove
# modification: 2018/08/03
########################################################################
import RPi.GPIO as GPIO
import Keypad       #import module Keypad

import board 
import busio 
import time
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont
import os, pickle
import interface

ROWS = 4        # number of rows of the Keypad
COLS = 4        #number of columns of the Keypad
keys =  [   '1','2','3','A',    #key code
            '4','5','6','B',
            '7','8','9','C',
            '*','0','#','D'     ]
rowsPins = [18,23,24,25]        #connect to the row pinouts of the keypad
colsPins = [10,22,27,17]        #connect to the column pinouts of the keypad

IDLE, MENU, SCHEDULE, SETTINGUP = 0,1,2,3
states = [IDLE, MENU, SCHEDULE, SETTINGUP]


saved_path = './medication_schedule.pkl'
def load_med_hist():
    if(os.path.exists(saved_path)):
        with open(saved_path,'rb') as f:
            med_hist = pickle.load(f)
    else:
        med_hist = dict() 
    return med_hist

def save_med_hist(med_hist):
    with open(saved_path,'wb') as f:
        pickle.dump(med_hist, f)




# Load a font in 2 different sizes.
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
font2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)

time_4d = ['0','0','0','0']
curr_digit = 0
amount = 0

curr_menu_pg, curr_sched_pg, curr_setup_pg = 0, 0, 0



def clr_alarm():
    global time_4d, curr_digit, amount
    curr_digit=0
    amount = 0
    time_4d = ['0','0','0','0']

def next_state(state, button="#", timeout=False, med_hist=None): 
    global curr_menu_pg, curr_sched_pg, curr_setup_pg, time_4d, curr_digit, amount
    if(timeout):
        return IDLE
    if(state==IDLE):
        return MENU
    elif(state == MENU):
        if button=="1":
            curr_menu_pg = 0
            return SCHEDULE
        elif button=="A":
            curr_setup_pg = 0
            return SETTINGUP
        elif button=="B":
            curr_setup_pg = 1
            return SETTINGUP
        elif button=="C":
            curr_setup_pg = 2
            return SETTINGUP
        elif button=="D":
            curr_setup_pg = 3
            return SETTINGUP
        elif button=='0':
            print("Going to idle")
            return IDLE
        elif button== '*' or button=='#':
            curr_menu_pg = 1-curr_menu_pg
            return MENU
    elif(state == SCHEDULE):
        if button== '*':
            curr_sched_pg+=1
            if(curr_sched_pg>3):
                curr_sched_pg = 0
        elif button=="#":
            curr_sched_pg-=1
            if(curr_sched_pg<0):
                curr_sched_pg = 3 
        return SCHEDULE
    elif(state == SETTINGUP):
        if(button=='*'):
            clr_alarm()    
            curr_digit=0
            return SETTINGUP
        elif(button=="#"):
            curr_digit=0 
            med_hist[curr_setup_pg] = [time_4d,amount]
            clr_alarm()
            return MENU
        else: 
            if curr_digit>=0 and curr_digit<=3:
                time_4d[curr_digit] = button 
                curr_digit+=1
            elif curr_digit ==4: 
                amount = int(button)
                curr_digit = 0 
            return SETTINGUP
    return state

def clear(oled):
    oled.fill(0)
    oled.show()
    return oled

def initialize():
    i2c = busio.I2C(board.SCL, board.SDA)
    oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
    clear(oled)
    # Create blank image for drawing.
    image = Image.new("1", (oled.width, oled.height))
    draw = ImageDraw.Draw(image)

    state = IDLE

    return oled, image, draw, state


def display(oled, image):
    oled.image(image) 
    oled.show() 


def show_time(oled, image, draw, clr=False):
    if clr:
        oled = clear(oled)
    # write the current time to the display after each scroll
    draw.rectangle((0, 0, oled.width, oled.height * 2), outline=0, fill=0)
    text = time.strftime("%X")
    draw.text((0, 0), text, font=font, fill=255)
    text = time.strftime("%a %e %b %Y")
    draw.text((0, 14), text, font=font, fill=255)
    # text = time.strftime("%X")
    # draw.text((0, 36), text, font=font2, fill=255)
    display(oled, image)

def show_setting(oled, image, draw):
    draw.rectangle((0, 0, oled.width, oled.height * 2), outline=0, fill=0)
    message_row1 = "Set alarm for"
    message_row2 = "%c%c : %c%c"%(time_4d[0],time_4d[1],time_4d[2],time_4d[3])
    draw.text((0,0), message_row1, font=font, fill=255)
    draw.text((0,14), message_row2, font=font2, fill=255)
    display(oled, image)


def loop(oled, image, draw, state, med_hist=None):
    last_display_time = time.time_ns()
    keypad = Keypad.Keypad(keys,rowsPins,colsPins,ROWS,COLS)    #creat Keypad object
    keypad.setDebounceTime(50)      #set the debounce time
    while(True):
        if(state == IDLE and time.time_ns()-last_display_time>= 1e9):
            last_display_time = time.time_ns()
            show_time(oled, image, draw)
        key = keypad.getKey()       #obtain the state of keys
        if(key != keypad.NULL):     #if there is key pressed, print its key code.
            print ("You Pressed Key : %c "%(key))
            state = next_state(state, button=key, med_hist=med_hist)
            if(state==MENU):
                interface.menu_page(draw,curr_menu_pg)
                display(oled, image)
            elif(state==SCHEDULE):
                if(curr_sched_pg in med_hist):
                    interface.med_schedule_page(draw, curr_sched_pg, med_hist[curr_sched_pg][0],med_hist[curr_sched_pg][1])
                else:
                    interface.med_schedule_page(draw, pillId=curr_sched_pg, set=False)
                display(oled, image)
            elif(state==SETTINGUP):
                interface.alarm_setup_page(draw,curr_setup_pg,time_4d,amount)
                display(oled,image)
            print("Current state:", state)
                
        
            
if __name__ == '__main__':     #Program start from here
    print ("Program is starting ... ")
    med_hist = load_med_hist()
    oled, image, draw, state = initialize()
    # interface.alarm_setup_page(draw)
    # display(oled, image)
    # time.sleep(10)
    # interface.menu_page(draw, 1)
    # display(oled, image)
    # time.sleep(10)
    print("now looping")
    print("medication schedule:\n", med_hist)
    try:
        state = loop(oled, image, draw, state, med_hist=med_hist)
    except KeyboardInterrupt:  #When 'Ctrl+C' is pressed, exit the program.
        GPIO.cleanup()
    finally:
        save_med_hist(med_hist)
