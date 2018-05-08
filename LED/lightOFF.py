# lightOFF.py
import RPi.GPIO as GPIO
GPIO.setwarnings(False)

GPIO.setmode(GPIO.BCM)

ledpin = 17

GPIO.setup(ledpin, GPIO.OUT)

GPIO.output(ledpin, 0)