# lightSwitch.py
import RPi.GPIO as GPIO
import os
import time
import sys

def switch(ledpin):
	GPIO.output(ledpin, 1)
	time.sleep(0.05)
	GPIO.output(ledpin,0)

MESSAGE = sys.argv[1]

GPIO.setwarnings(False)

GPIO.setmode(GPIO.BCM)
ledpin = 27
readpin = 22
GPIO.setup(ledpin, GPIO.OUT)
GPIO.setup(readpin,GPIO.IN)
status = GPIO.input(readpin)

if MESSAGE=='STATUS':
	if status==1:
		print('True')
	else:
		print('False')
elif MESSAGE=='ON':
	if status==1:
		switch(ledpin)

elif MESSAGE=='OFF':
	if status==0:
		switch(ledpin)

#GPIO.output(ledpin, 1)

#time.sleep(0.05)

#GPIO.output(ledpin,0)

# filename = os.path.join('/home/pi/.DomoticPythonServer', 'lightON')

# file = open(filename,'w')
# file.close()
