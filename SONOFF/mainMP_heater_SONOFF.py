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

def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

def get_random_time():
    num = translate(urandom.getrandbits(16), 0, 65535, 0, 10000)
    integer  = math.floor(num)/1000 # the translate function returns a float, which we gotta deal with somehow
    return integer

def log(message):
    print(message)

def get_ip_address():
    log('get local ip')
    ip_address = ''
    sta_if = net.WLAN(net.STA_IF)
    temp = sta_if.ifconfig()
    ip_address = temp[0]
    return ip_address

def toggle(p):
    log('toggle pin')
    p.value(not p.value())

def stripInMessage(inline):
    inline = str(inline)
    inline = inline.replace('b\'','')
    outline = inline.replace('\'','')
    return outline

def checkFileAndCreate(dir,filename):
    dirfilename = dir+'/'+filename
    log('check file ' + dirfilename)
    listfile = os.listdir(dir)
    if not (filename in listfile):
        log('file ' + dirfilename + ' not found, it will created')
        file = open(dirfilename,'w')
        file.close()

def FileGetServerIP(filename):
    log('getting SERVER IP from file: ' + filename)
    global ServerIP
    file = open(filename,'r')
    strServerIP = file.readline()
    file.close()
    if strServerIP!='':
        log('SERVER IP found: ' + strServerIP)
        elements = strServerIP.split(',')
        ServerIP[0] = elements[0]
        ServerIP[1] = int(elements[1])
        log('And set')
    return ServerIP

def FileSetServerIP(IP,filename):
    log('putting SERVER IP to file: ' + filename)
    try:
        file = open(filename,'w')
        file.write(IP[0]+','+str(IP[1]))
        file.close()
        log('done')
    except Exception as ex:
        log(str(ex))
    

def statusPin(pins,idpin):
    log('Getting status pin')
    pinval = pins[idpin].value()
    if pinval==0:
        message = mac + ',PIN,' + elements[1] + ',OFF'
    elif pinval==1:
        message = mac + ',PIN,' + elements[1] + ',ON'
    return message

def closeSocketServer():
    global sockServer
    log('Closing socket to receive form server')
    try:       
        sockServer.close()
        sockServer = None
        sockServer = sock.socket(sock.AF_INET,sock.SOCK_STREAM)
        sockServer.settimeout(0.1)
    except Exception as ex:
        log(str(ex))

def bindSocketServer():
    global sockServer
    global ServerIP
    log('Opening socket to receive form server at: ' + str(ServerIP))
    try:
        closeSocketServer()
        sockServer.bind(('',ServerIP[1]))
        sockServer.listen(1)
    except Exception as ex:
        log(str(ex))

def sendSocketBroadcast(message):
    global ServerIP
    try:
        log('Try to send message to the server: '+ message + ' at : ' + str((ServerIP[0],BROADCASTPORT)))  
        sockBroadCast.sendto(message,(ServerIP[0],BROADCASTPORT))
        log('Sent message to the server: '+ message)  
    except Exception as ex:
        log(str(ex))

def changeMainPin(p):
    time.sleep(0.50)
    toggle(pins[0])
    toggle(pins[2])


log('start initialization')
mac = ubinascii.hexlify(net.WLAN().config('mac'),':').decode()
ip  = get_ip_address()

ServerIP = ['',0]

filedata = 'serverip.data'
dirdata = 'data'
checkFileAndCreate(dirdata,filedata)
IPfile = dirdata + '/' + filedata
ServerIP = FileGetServerIP(IPfile)
sockServerRun = False

boardKind = 'H'

BROADCASTPORT = 51082
sockBroadCast=sock.socket(sock.AF_INET,sock.SOCK_DGRAM)
sockBroadCast.settimeout(0.1)
sockBroadCast.bind(('',BROADCASTPORT))

ip  = get_ip_address()
message = 'D,' + mac+','+ip+','+boardKind


sockServer=sock.socket(sock.AF_INET,sock.SOCK_STREAM)
sockServer.settimeout(0.1)

if ServerIP[1]!=0:
    bindSocketServer()
    sendSocketBroadcast(message)

pins = [machine.Pin(12, machine.Pin.OUT),
        machine.Pin(0, machine.Pin.IN),
        machine.Pin(13,machine.Pin.OUT)]

pins[0].on()
pins[2].on()

pins[1].irq(trigger=machine.Pin.IRQ_FALLING, handler=changeMainPin)


sec2millis = 1000
min2sec    = 60
min2millis = min2sec*sec2millis

millis_old = 0
waitTime = 0
log('start main loop')
while True:
    # time.sleep(0.5)
    try:
        millis_new = int(round(time.time()*sec2millis))
        millis_pass = millis_new-millis_old
        if (millis_pass/min2millis>=waitTime):
            millis_old = millis_new
            waitTime = 1
            ip  = get_ip_address()
            message = 'D,' + mac+','+ip+','+boardKind
            sendSocketBroadcast(message)
        try:
            m=sockBroadCast.recvfrom(1024)
            line = stripInMessage(m[0])
            log('Recived message from broadcast: ' + line)
            elements = list(line.split(','))
            
            if elements[0].strip()=='S':
                waitTime = get_random_time()
                log('New waiting time: ' + str(waitTime))
                if (ServerIP[0] != elements[1]):
                    log('build SERVERIP')
                    ServerIP[0] = elements[1]
                    ServerIP[1] = int(elements[2])

                    FileSetServerIP(ServerIP,IPfile)

                    bindSocketServer()
                else:
                    log('nothong change, server ip is: ' +str(ServerIP[0]))
                    log('nothong change, server port is: ' +str(ServerIP[1]))
                    
        except Exception as ex:
            pass
            # if str(ex)=='[Errno 110] ETIMEDOUT':
            #     pass
            # if str(ex)=='[Errno 22] EINVAL':
            #     pass
            # else:
            #     log('loop1')
            #     log(str(ex))

        try:
            conn, addr = sockServer.accept()
            conn.settimeout(1)
            log('Connection address:' + str(addr))
            # time.sleep(0.01)
            while 1:
                try:
                    temp = conn.recv(1024)
                    if not temp:
                        break
                    messageFromServer = stripInMessage(temp)
                    log('Recived message from server: ' + messageFromServer)
                    elements = messageFromServer.split(',')
                    messageToServer = 'ERROR'
                    if elements[0]=='PIN':
                        idpin = int(elements[1])
                        if(len(pins)-1>=idpin):
                            if elements[2]=='ON':
                                pins[idpin].on()
                                pins[2].on()
                                messageToServer = statusPin(pins,idpin)
                            elif elements[2]=='OFF':
                                pins[idpin].off()
                                pins[2].off()
                                messageToServer = statusPin(pins,idpin)
                            elif elements[2]=='STAT':
                                messageToServer = statusPin(pins,idpin)
                    conn.send(messageToServer)
                    break
                except Exception as ex:
                    pass
            conn.close()
        except Exception as ex:
            pass
            # if str(ex).strip()=='[Errno 110] ETIMEDOUT':
            #     pass
            # if str(ex).strip()=='[Errno 22] EINVAL':
            #     pass
            # else:
            #     log('loop2')
            #     log(str(ex))
            

    except KeyboardInterrupt:
        log('Detected KeyboardInterrupt')
        break
    except Exception as ex:
        if str(ex)=='[Errno 110] ETIMEDOUT':
            pass
        if str(ex)=='[Errno 11] EAGAIN':
            pass
        if str(ex)=='[Errno 22] EINVAL':
            pass
        else:
            log('loop3')
            log(str(ex))
    
    time.sleep_ms(20)

sockBroadCast.close()
closeSocketServer()
log('Exiting')
