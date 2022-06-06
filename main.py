#!/usr/bin/env python3
########################################################################
# Filename    : MatrixKeypad.py
# Description : obtain the key code of 4x4 Matrix Keypad
# Author      : freenove
# modification: 2018/08/03
########################################################################
import RPi.GPIO as GPIO
from numpy import save
import Keypad       #import module Keypad

import board 
import busio 
import time
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont
import os, pickle, subprocess, signal
import interface
import pygame
from mfrc522 import SimpleMFRC522
from datetime import datetime


import threading 

ROWS = 4        # number of rows of the Keypad
COLS = 4        #number of columns of the Keypad
keys =  [   '1','2','3','A',    #key code
            '4','5','6','B',
            '7','8','9','C',
            '*','0','#','D'     ]
rowsPins = [18,23,24,12]        #connect to the row pinouts of the keypad
colsPins = [13,22,27,17]        #connect to the column pinouts of the keypad

IDLE, MENU, SCHEDULE, SETTINGUP, ALARM, AUDIO_RECORD = 0,1,2,3,4,5
states = [IDLE, MENU, SCHEDULE, SETTINGUP, ALARM, AUDIO_RECORD]

audio_path = './alarm_audio'
saved_path = './medication_schedule.pkl'
idle_timer = time.time_ns() 
IDLE_STATE_TIMER = 10e9


## TO-DO:
 # add menu: clear all history 

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
        print("Current med hist: ", med_hist)

def write():
    reader = SimpleMFRC522()
    try:
            text = input('New data:')
            print("Now place your tag to write")
            reader.write(text)
            print("Written")
    finally:
            GPIO.cleanup()
def read():
    #rint("in READ")
    reader = SimpleMFRC522()
    while(True):
        
        try:
            
            id, text = reader.read_no_block()
            if (text is not None):
                print(id)
                print(text)
                with open(os.path.join(audio_path,'temp_id.txt'), 'w') as f:
                    f.write(str(id))
                
            if id==665322504066: 
                print("if 1")
                # pygame.mixer.music.load("stomach.wav")
                # pygame.mixer.music.play()
                # while pygame.mixer.music.get_busy() == True:
                #     continue
            if id ==494783076233:
                print("if 2")
                # pygame.mixer.music.load("head.wav")
                # pygame.mixer.music.play()
                # while pygame.mixer.music.get_busy() == True:
                #     continue
        finally:
            print("out read")
            pass


# Load a font in 2 different sizes.
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
font2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)

time_4d = ['0','0','0','0']
curr_digit = 0
amount = 0

curr_menu_pg, curr_sched_pg, curr_setup_pg = 0, 0, 0

curr_audio, curr_id = [None, None], None

def check_alarm(): 
    #TO-DO:
    #1. show "pill time display" 
    #2. show current time 
    #3. show remaining pill time 
    # Press "#" or when pill is swiped to stop the process
    current_time = datetime.now()
    now = current_time.strftime("%H:%M:%S")
    print("Checking alarm, current time: ", now)
    for k, v in med_hist.items():
        time_str = ''.join(v[0])
        time_str = "%s:%s"%(time_str[:2], time_str[2:])
        if time_str == now[:5] and int(now[6:7]) <= 10 : 
            print("PILL TIME FOR PILL %s"%k)
            return True
    return False

def record_audio_start(page): 
    pillIds = ["A", "B", "C", "D"]
    file_name = os.path.join(audio_path, "pill_%s.wav"%(pillIds[page]))
    print("Start recording audio")
    p = subprocess.Popen(['arecord', '--format=S16_LE', '--rate=16000', '--file-type=wav', file_name])
    return file_name, p

def record_audio_terminate(file_name, p):
    global curr_id
    os.kill(p.pid, signal.SIGINT)  # Send the signal to all the process groups
    print("Audio terminated")
    temp_id_file = os.path.join(audio_path, "temp_id.txt")
    with open(temp_id_file) as f:
        temp_id = f.read()
        print("Recorded id is: ", temp_id)
        os.remove(temp_id_file)
    curr_id = temp_id 
    med_hist[curr_setup_pg].append(curr_id)
    med_hist[curr_setup_pg].append(file_name)
    print("Audio completed")



def clr_alarm():
    global time_4d, curr_digit, amount
    curr_digit=0
    amount = 0
    time_4d = ['0','0','0','0']

def next_state(state, button="#", timeout=False, med_hist=None, alarming = False): 
    global curr_menu_pg, curr_sched_pg, curr_setup_pg, time_4d, curr_digit, amount, curr_audio
    if(alarming):
        return ALARM
    if(timeout):
        return IDLE
    if(state==IDLE):
        return MENU
    elif (button in ["A","B", "C", "D"]) and (state in list(range(1,4))): 
        if button=="A":
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
    elif(state == MENU):
        if button=="1":
            curr_menu_pg = 0
            return SCHEDULE
        elif button=='0':
            print("Going to idle")
            return IDLE
        elif button== '*' or button=='#':
            curr_menu_pg = 1-curr_menu_pg
            return MENU
    elif(state == SCHEDULE):
        if button== '#':
            curr_sched_pg+=1
            if(curr_sched_pg>3):
                curr_sched_pg = 0
        elif button=="*":
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
            curr_audio[0],curr_audio[1] = record_audio_start(curr_setup_pg)
            return AUDIO_RECORD
        else: 
            if curr_digit>=0 and curr_digit<=3:
                time_4d[curr_digit] = button 
                curr_digit+=1
            elif curr_digit ==4: 
                amount = int(button)
                curr_digit = 0 
            return SETTINGUP
    elif(state == ALARM):
        if(button=="#"):
            return IDLE
    elif(state == AUDIO_RECORD):
        if(button=="#"):
            print("Terminating audio")
            record_audio_terminate(*curr_audio)
            save_med_hist(med_hist = med_hist)
            return MENU
            
    return state

def clear(oled):
    oled.fill(0)
    oled.show()
    return oled

def initialize():
    GPIO.setmode(GPIO.BCM)
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
    global idle_timer
    last_display_time = time.time_ns()
    keypad = Keypad.Keypad(keys,rowsPins,colsPins,ROWS,COLS)    #creat Keypad object
    keypad.setDebounceTime(50)      #set the debounce time
    while(True):
        if(time.time_ns()-last_display_time>= 1e9):
            last_display_time = time.time_ns()
            if((state != ALARM) and check_alarm()):
                state = next_state(state, alarming = True)
                continue
            elif(state == IDLE):
                last_display_time = time.time_ns()
                show_time(oled, image, draw)

        if((state not in [IDLE, AUDIO_RECORD, ALARM]) and (time.time_ns()- idle_timer >= IDLE_STATE_TIMER)):
            state = next_state(state, timeout=True)
            idle_timer = time.time_ns()  
            print("Current state:", state)
            continue
        key = keypad.getKey()       #obtain the state of keys
        if(key != keypad.NULL):     #if there is key pressed, print its key code.
            print ("You Pressed Key : %c "%(key))
            idle_timer = time.time_ns()
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
            elif(state==ALARM):
                interface.alarm_page(draw)
                display(oled, image) 
            elif(state== AUDIO_RECORD):
                interface.recording_audio_page(draw, curr_setup_pg)
                display(oled, image) 
            print("Current state:", state)
                
class myThread1 (threading.Thread):
   def __init__(self, threadID, name, oled, image, draw, state, med_hist):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.oled = oled
      self.image = image
      self.draw = draw
      self.state = state
      self.med_hist = med_hist
   def run(self):
    try:
        self.state = loop(self.oled, self.image, self.draw, self.state, self.med_hist)
    except KeyboardInterrupt:  #When 'Ctrl+C' is pressed, exit the program.
        print("Thread 1 ending, cleaning it up")
        GPIO.cleanup()
    finally:
        print("Saving medication history")
        save_med_hist(self.med_hist)

class myThread2 (threading.Thread):
   def __init__(self, threadID, name):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
   def run(self):
        try:
            read()
        except KeyboardInterrupt: 
            print("Thread 2 ending, cleaning it up")
            GPIO.cleanup()
        finally:
            print("Saving medication history in thread 2")
            # save_med_hist(self.med_hist)
        
if __name__ == '__main__':     #Program start from here
    print ("Program is starting ... ")
    pygame.mixer.init()
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
        thread1 = myThread1(1, "oled", oled, image, draw, state, med_hist=med_hist)
        thread2 = myThread2(2, "speaker")
        thread2.start()
        thread1.start()
 #   try:
   #     state = loop(oled, image, draw, state, med_hist=med_hist)
    except KeyboardInterrupt:  #When 'Ctrl+C' is pressed, exit the program.
        GPIO.cleanup()

    finally:
        save_med_hist(med_hist)
        print("Main loop ending, saving again???")
