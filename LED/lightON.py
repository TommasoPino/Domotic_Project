# lightON.py
import RPi.GPIO as GPIO
import os
GPIO.setwarnings(False)

GPIO.setmode(GPIO.BCM)

ledpin = 17

GPIO.setup(ledpin, GPIO.OUT)

GPIO.output(ledpin, 1)

file = open('lightON','w')
file.close()
