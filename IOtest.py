#!/usr/bin/env python

import RPi.GPIO as GPIO
import pygame
from mfrc522 import SimpleMFRC522


pygame.mixer.init()
reader = SimpleMFRC522()

def write():
    try:
            text = input('New data:')
            print("Now place your tag to write")
            reader.write(text)
            print("Written")
    finally:
            GPIO.cleanup()
def read():
    try:
        id, text = reader.read()
        print(id)
        print(text)                   
            
        if id==665322504066:
            print("if 1")
            pygame.mixer.music.load("stomach.wav")
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy() == True:
                continue
        if id ==494783076233:
            print("if 2")
            pygame.mixer.music.load("head.wav")
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy() == True:
                continue
    except KeyboardInterrupt:
        GPIO.cleanup()
   
    finally:
        
        GPIO.cleanup()
        
    

      
read()    


