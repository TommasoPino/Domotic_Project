import network as net
import socket as sock
import machine 
import os
import time
import ubinascii
import urandom
import math
from umqtt.simple import MQTTClient


RecievedMessage = ""
CurrentStatus = "on"
RecievedNEWMessage = False

def sub_cb(topic, msg):
    global RecievedMessage
    global RecievedNEWMessage
    RecievedMessage = str(msg)
    RecievedNEWMessage = True

clientID = ubinascii.hexlify(net.WLAN().config('mac'),':').decode().replace(":","")
topic = clientID+"/PIN2"
mqttc = MQTTClient(clientID,bcman.ServerIP[0])
mqttc.connect()
mqttc.subscribe(clientID)