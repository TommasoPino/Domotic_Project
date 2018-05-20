# lightSTAT.py
import RPi.GPIO as GPIO
import os

GPIO.setwarnings(False)

GPIO.setmode(GPIO.BCM)

ledpin = 18

GPIO.setup(ledpin, GPIO.IN)
value = GPIO.input(ledpin)

if value==1:
    print('true')
else:
    print('false')

# filename = os.path.join('/home/pi/.DomoticPythonServer', 'lightON')

# if os.path.isfile(filename):
#     print('true')
# else:
#     print('false')


