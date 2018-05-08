# Questo script e' il core del codice che faccimo girare sulle schede wifi con micropython
# il sistema 

# import network as net
import socket as sock
# import machine 
import os
import time
# import ubinascii

def log(message):
    print(message)

# def get_ip_address():
#     log('get local ip')
#     ip_address = ''
#     sta_if = net.WLAN(net.STA_IF)
#     temp = sta_if.ifconfig()
#     ip_address = temp[0]
#     return ip_address

def get_ip_address():
    ip_address = ''
    s = sock.socket(sock.AF_INET, sock.SOCK_DGRAM)
    s.connect(("8.8.8.8",80))
    ip_address = s.getsockname()[0]
    s.close()
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
    except Exception as ex:
        log(str(ex))

def statusPin(pins,idpin):
    log('Getting status pin')
    pinval = 0#pins[idpin].value()
    if pinval==0:
        message = mac + ',PIN,' + elements[1] + ',ON'
    elif pinval==1:
        message = mac + ',PIN,' + elements[1] + ',OFF'
    return message

def closeSocketServer():
    try:
        global sockServerRun
        global sockServer
        if (sockServerRun):
            log('Closed socket to receive form server')
            sockServer.close()
            sockServerRun = False
    except Exception as ex:
        log(str(ex))

def bindSocketServer():
    global sockServerRecivBind
    log('Opened socket to receive form server at: ' + str(ServerIP))
    try:
        sockServer.bind(('',ServerIP[1]))
        sockServer.listen(1)
        sockServerRun = True
    except Exception as ex:
        log(str(ex))

# def sendSocketServer(message):
#     try:
#         global ServerIP
#         log('Try to send message to the server: '+ message)  
#         sockServerSend.sendto(message,(ServerIP[0],ServerIP[1]))
#         log('Sent message to the server: '+ message)  
#     except Exception as ex:
#         log(str(ex))

def sendSocketBroadcast(message):
    try:
        global ServerIP
        log('Try to send message to the server: '+ message)  
        sockBroadCast.sendto(message,(ServerIP[0],BROADCASTPORT))
        log('Sent message to the server: '+ message)  
    except Exception as ex:
        log(str(ex))

log('start initialization')
mac = 'ec:fa:bc:87:77:bd'#ubinascii.hexlify(net.WLAN().config('mac'),':').decode()
ip  = get_ip_address()

ServerIP = ['',0]

filedata = 'serverip.data'
dirdata = 'data'
checkFileAndCreate(dirdata,filedata)
IPfile = dirdata + '/' + filedata
ServerIP = FileGetServerIP(IPfile)

boardKind = 'I'

BROADCASTPORT = 51082
sockBroadCast=sock.socket(sock.AF_INET,sock.SOCK_DGRAM)
sockBroadCast.setblocking(False)
sockBroadCast.bind(('',BROADCASTPORT))

ip  = get_ip_address()
message = 'D,' + mac+','+ip+','+boardKind
sendSocketBroadcast(message)

sockServer=sock.socket(sock.AF_INET,sock.SOCK_STREAM)
# sockServer.setblocking(False)
sockServer.settimeout(0.1)
sockServerRun = False

# pins = [machine.Pin(2, machine.Pin.OUT)]
# pins[0].on()

pins = [1]

sec2millis = 1000
min2sec    = 60
min2millis = min2sec*sec2millis

millis_old = 0
waitTime = 0
log('start main loop')
while True:
    try:
        millis_new = int(round(time.time()*1000))
        millis_pass = millis_new-millis_old
        try:
            if (millis_pass>=waitTime):
                m=sockBroadCast.recvfrom(1024)
                line = stripInMessage(m[0])
                log('Recived message from broadcast: ' + line)
                elements = list(line.split(','))
                waitTime = 0*sec2millis
                if elements[0].strip()=='S':
                    log('build SERVERIP')
                    ServerIP[0] = elements[1]
                    ServerIP[1] = int(elements[2])

                    FileSetServerIP(ServerIP,IPfile)

                    ip  = get_ip_address()
                    message = 'D,' + mac+','+ip+','+boardKind
                    sendSocketBroadcast(message)

                    closeSocketServer()

                    bindSocketServer()
                    
        except Exception as ex:
            if str(ex)=='[Errno 110] ETIMEDOUT':
                pass
            else:
                log(str(ex))

        # try:
        #     if (not sockServerRecivBind):
        #         sockServerReciv.bind((ServerIP[0],ServerIP[1]))
        #         ip  = get_ip_address()
        #         sockServerSend.sendto(mac+','+ip+','+boardKind,(ServerIP[0],ServerIP[1]))
        #         sockServerRecivBind = True
        # except:
        #     pass

        try:
            conn, addr = sockServer.accept()
            log('Connection address:' + str(addr))
            time.sleep(0.01)
            while 1:
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
                            # pins[idpin].off()
                            messageToServer = statusPin(pins,idpin)
                        elif elements[2]=='OFF':
                            # pins[idpin].on()
                            messageToServer = statusPin(pins,idpin)
                        elif elements[2]=='STAT':
                            messageToServer = statusPin(pins,idpin)
                conn.send(messageToServer)
            conn.close()
        except Exception as ex:
            if str(ex)=='[Errno 110] ETIMEDOUT':
                pass
            else:
                log(str(ex))
            
        millis_old = millis_new
            # if (millis_new-millis_old>=500):
            #     toggle(pin)
            #     # time.sleep_messageFromServer(1000)
            #     sS.sendto('the value is ' + str(pin.value()), (ServerIP[0],12345))
    except KeyboardInterrupt:
        log('Detected KeyboardInterrupt')
        break
    except Exception as ex:
        if str(ex)=='[Errno 110] ETIMEDOUT':
            pass
        if str(ex)=='[Errno 11] EAGAIN':
            pass
        else:
            log(str(ex))

sockBroadCast.close()
closeSocketServer()
log('Exiting')