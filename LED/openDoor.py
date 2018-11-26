# lightSwitch.py
import RPi.GPIO as GPIO
import os
import time
import sys

def switch(doorpin):
	GPIO.output(doorpin, 1)
	time.sleep(0.5)
	GPIO.output(doorpin,0)

MESSAGE = sys.argv[1]

GPIO.setwarnings(False)

GPIO.setmode(GPIO.BCM)
doorpin = 23
GPIO.setup(doorpin, GPIO.OUT)

status = 1

if MESSAGE=='ON':
	switch(doorpin)

#GPIO.output(ledpin, 1)

#time.sleep(0.05)

#GPIO.output(ledpin,0)

# filename = os.path.join('/home/pi/.DomoticPythonServer', 'lightON')

# file = open(filename,'w')
# file.close()
