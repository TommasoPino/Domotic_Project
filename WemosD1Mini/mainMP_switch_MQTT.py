# Questo script e' il core del codice che faccimo girare sulle schede wifi con micropython
# il sistema 

import network as net
import socket as sock
import machine 
import os
import time
import ubinascii
import urandom
import math
import broadcastManager as BCman
from umqtt.simple import MQTTClient

def log(message):
    print(message)

def stripInMessage(inline):
    inline = str(inline)
    inline = inline.replace('b\'','')
    outline = inline.replace('\'','')
    return outline

def statusPin(pins,idpin):
    log('Getting status pin')
    pinval = pins[idpin].value()
    if pinval==0:
        message = mac + ',PIN,' + str(idpin) + ',ON'
    elif pinval==1:
        message = mac + ',PIN,' + str(idpin) + ',OFF'
    return message

log('start initialization')

bcman = BCman.BroadcastManager(dirdata = 'data',filedata = 'serverip.data',boardKind = 'I',portBroadCast = 51082)
bcman.init_bc_sock()

RecievedMessage = ""
CurrentStatus = "on"
RecievedNEWMessage = False

def sub_cb(topic, msg):
    global RecievedMessage
    global RecievedNEWMessage
    RecievedMessage = str(msg)
    RecievedNEWMessage = True

mac = ubinascii.hexlify(net.WLAN().config('mac'),':').decode()
clientID = mac#.replace(":","")
topic = clientID
mqttc = MQTTClient(clientID,bcman.ServerIP[0])
mqttc.connect()
mqttc.set_callback(sub_cb)
mqttc.subscribe(topic)

pins = [machine.Pin(2, machine.Pin.OUT)]
pins[0].on()


log('start main loop')
while True:
    try:
        bcman.check_bc_msg()
        mqttc.check_msg()
        if RecievedNEWMessage:
            RecievedNEWMessage = False
            try:
                messageFromServer = RecievedMessage.decode('ASCII') 
            except:
                messageFromServer = RecievedMessage
            messageFromServer = stripInMessage(messageFromServer)
            log('Recived message from server: ' + messageFromServer)
            elements = messageFromServer.split(',')
            print(elements)
            messageToServer = 'ERROR'
            if elements[0]=='PIN':
                idpin = int(elements[1])
                if(len(pins)-1>=idpin):
                    if elements[2]=='ON':
                        print('on')
                        pins[idpin].off()
                        messageToServer = statusPin(pins,idpin)
                        mqttc.publish(topic+"/status",messageToServer)
                    elif elements[2]=='OFF':
                        print('off')
                        pins[idpin].on()
                        messageToServer = statusPin(pins,idpin)
                        mqttc.publish(topic+"/status",messageToServer)
                    elif elements[2]=='STAT':
                        print('status')
                        messageToServer = statusPin(pins,idpin)
                        mqttc.publish(topic+"/status",messageToServer)

            
    except KeyboardInterrupt:
        log('Detected KeyboardInterrupt')
        break
    except Exception as ex:
        log(str(ex))

mqttc.disconnect()
bcman.closesock()
log('Exiting')
