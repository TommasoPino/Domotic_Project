# lightON.py
import RPi.GPIO as GPIO
import os
GPIO.setwarnings(False)

GPIO.setmode(GPIO.BCM)

ledpin = 17

GPIO.setup(ledpin, GPIO.OUT)

GPIO.output(ledpin, 1)

# filename = os.path.join('/home/pi/.DomoticPythonServer', 'lightON')

# file = open(filename,'w')
# file.close()
