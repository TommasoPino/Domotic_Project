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
from umqtt.robust import MQTTClient
import connectWiFi as wifi

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
        message = mac + ',PIN,' + str(idpin) + ',OFF'
    elif pinval==1:
        message = mac + ',PIN,' + str(idpin) + ',ON'
    return message

def toggle(p):
    log('toggle pin')
    p.value(not p.value())

def changeMainPin(p):
    time.sleep(0.50)
    toggle(pins[0])
    toggle(pins[2])
    
log('start initialization')

time.sleep(1)
wifi.do_connect()
bcman = BCman.BroadcastManager(dirdata = 'data',filedata = 'serverip.data',boardKind = 'H',portBroadCast = 51082)
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

pins = [machine.Pin(12, machine.Pin.OUT),
        machine.Pin(0, machine.Pin.IN),
        machine.Pin(13,machine.Pin.OUT)]

pins[0].on()
pins[2].on()

pins[1].irq(trigger=machine.Pin.IRQ_FALLING, handler=changeMainPin)

bcman.send_bc_msg()
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
                        pins[idpin].on()
                        pins[2].on()
                        messageToServer = statusPin(pins,idpin)
                        mqttc.publish(topic+"/status",messageToServer)
                    elif elements[2]=='OFF':
                        print('off')
                        pins[idpin].off()
                        pins[2].off()
                        messageToServer = statusPin(pins,idpin)
                        mqttc.publish(topic+"/status",messageToServer)
                    elif elements[2]=='STAT':
                        print('status')
                        messageToServer = statusPin(pins,idpin)
                        mqttc.publish(topic+"/status",messageToServer)

            
    except KeyboardInterrupt:
        log('Detected KeyboardInterrupt')
        break
    # except Exception as ex:
    #     if str(ex)=='[Errno 103] ECONNABORTED':
    #         mqttc = MQTTClient(clientID,bcman.ServerIP[0])
    #         mqttc.connect()
    #         mqttc.set_callback(sub_cb)
    #         mqttc.subscribe(topic)
    #     log(str(ex))

mqttc.disconnect()
bcman.closesock()
log('Exiting')

