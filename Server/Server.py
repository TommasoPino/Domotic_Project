#!/usr/bin/env python
import socket as sock
import time
import os.path
import datetime
import sys


def log(message):
    file = open(filelog, 'r+')
    lines = file.readlines()
    if message == None:
        file.write('\n')
        file.write('\n')
    else:
        file.write(str(datetime.datetime.now()) + ': ' + message)
        file.write('\n')

    file.close()


def readtable(filename):
    C = {}
    try:
        file = open(filename, 'r')
        log('Reading ' + filename + ' to populate the dictionary')
        lines = file.readlines()
        nel = 0
        for line in lines:
            if not(line[0] is '#'):
                elements = line.split(',')
                listel = []
                for el in elements[1:]:
                    element = el.strip()
                    try:
                        element = float(element)
                        pass
                    except:
                        pass
                    listel.append(element)

                nel = nel + 1
                C[elements[0].strip()] = listel

        log('Found ' + str(nel) + ' device in the file')
        file.close()
    except:
        pass
    return C


def composemessage(elementsin):
    message = elementsin[0]
    elementsinlen = len(elementsin)
    for i in range(1, elementsinlen):
        message = message + ',' + elementsin[i]
    return message


def add2table(input, filename):
    file = open(filename, 'r+')
    lines = file.readlines()
    file.write('%15s' % (str(input[0])))
    for value in input[1:]:
        file.write(', %15s' % (str(value)))
    file.write('\n')
    log('Added new elements to the Device Table')
    file.close()


def stripInMessage(inline):
    inline = str(inline)
    inline = inline.replace('b\'', '')
    outline = inline.replace('\'', '')
    return outline


def get_ip_address():
    ip_address = ''
    s = sock.socket(sock.AF_INET, sock.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip_address = s.getsockname()[0]
    s.close()
    return ip_address


def listenLocal():
    sockServer = sock.socket(sock.AF_INET,  # Internet
                             sock.SOCK_STREAM)  # TCP
    global DeviceDict
    try:
        conn, addr = sockLocal.accept()
        time.sleep(0.01)
        while 1:
            message = conn.recv(BUFFER_SIZE)
            if not message:
                break
            log('Received internal message ' + message)
            elements = message.split(',')
            try:
                device = DeviceDict[elements[0]]
                log('Found device with id: ' + elements[0])
                messagetosend = composemessage(elements[1:])
                log(str(device))
                try:
                    IPSEND = (device[0][0], IPPORT)

                    sockServer.connect(IPSEND)
                except:
                    IPSEND = (device[0], IPPORT)
                    sockServer.connect(IPSEND)
                log('Opened connection with: ' + str(IPSEND))
                for i in range(4):
                    try:
                        sockServer.send(messagetosend)
                        log('Message sent to Device')
                        messagerecived = sockServer.recv(BUFFER_SIZE)
                        log('Message recieve from Device: ' + messagerecived)
                        log('Connection Closed')
                        break
                    except Exception as ex:
                        log('An error occours: ' + ex.message)
                sockServer.close()
                elementsin = messagerecived.split(',')
                if elements[0] == elementsin[0]:
                    log('Match ' + elementsin[0])
                conn.send(messagerecived)
                log('Resent message')
            except sock.error as ex:
                log(str(ex))
                conn.send('Error')
            except KeyError:
                log('Key ' + elements[0] + ' not found!')
                conn.send('Not Found')
            except Exception as ex:
                conn.send('Error')
                log(ex.message)
        log('Closed connection')
        conn.close()
    except sock.timeout:
        pass
    return


def checkFileAndCreate(filename):
    if not os.path.isfile(filename):
        file = open(filename, 'w')
        file.close()


def listenBroadcast():
    global DeviceDict
    try:
        message = sockBroad.recvfrom(1024)
        log('Recived External message: "' +
            str(message[0]) + '" ; from: ' + str(message[1]))

        elements = stripInMessage(message[0]).split(',')
        if elements[0] == 'D':
            log('Message from a device')
            try:
                Device = DeviceDict[elements[1]]
                log('Device already present on table')
            except KeyError:
                DeviceDict[elements[1]] = [elements[2:]]
                add2table(elements[1:], FileDataDevice)
        elif elements[0] == 'S':
            log('Message from Server ignored')
        else:
            log('Message ignored')
    except sock.timeout:
        pass


# start the program
DeviceDict = {}
pathusr = '/home/pi/.DomoticPythonServer/'
FileDataDevice = pathusr + 'DeviceList.csv'
filelog = pathusr + 'Server.log'

# check the existance of the file log
checkFileAndCreate(filelog)
log(None)
log('Server Turned on, start initialization')

# check the existance of the Devices file
log('Check existance of ' + FileDataDevice)
checkFileAndCreate(FileDataDevice)

# Build the device dictionary
log('Build table from file')
DeviceDict = readtable(FileDataDevice)


# Define Ip of server and its listen port
IPSERVER = get_ip_address()
IPPORT = 51083
sock.setdefaulttimeout(0.2)

# questo script e' il server principale che mette in comunicazione
# tutti i device wireless con il core homekit, ascolta sulla porta
# 51081 tutte le comunicazioni TCP che arrivano in locale dal
# dispositivo che lo lancia.
localSocket = ('127.0.0.1', 51081)  # Server solo sul loop interno
sockLocal = sock.socket(sock.AF_INET,  # Internet
                        sock.SOCK_STREAM)  # TCP
sockLocal.bind(localSocket)
# il socket inizia ad ascoltare
sockLocal.listen(5)

# una volta ogni 10 minuti o se arriva una comunicazione interna
# con scritto 'broadcast' viene lanciato un segnale in broadcast
# con le informazioni di contatto del server. Viene fatto un confronto
# con i dati presenti su un file di registro e nel caso ci sia un nuovo
# dispositivo, questo viene aggiunto alla lista, nel caso un dispositivo
# non rispondesse viene aggiunto un # ad inizio linea e viene considerato
# rimosso (da valutare l'idea di contattarlo per altre 3 volte nell'ora
# successiva, per poi decretarlo disperso)

# socket di invio messaggi
broadcastwaitTime = 1  # minute
BROADCASTIP = '255.255.255.255'
BROADCASTPORT = 51082
broadcastSocket = (BROADCASTIP, BROADCASTPORT)
sockBroad = sock.socket(sock.AF_INET,  # Internet
                        sock.SOCK_DGRAM)  # UDP
sockBroad.setsockopt(sock.SOL_SOCKET, sock.SO_BROADCAST, 1)
sockBroad.bind(('', BROADCASTPORT))
# il messaggio che viene inviato in broadcast e' l'ip del server e la porta
# del server TCP, inoltre comunica su quale porta i dispositivi devono aprire
# il socket server

broadcastMessage = 'S,' + IPSERVER + ',' + str(IPPORT)


# sockServer = sock.socket(sock.AF_INET, # Internet
#                          sock.SOCK_STREAM) # TCP
# sockServer.bind(('',IPPORT))
# sockServer.listen(5)

# alcune variabili utili
BUFFER_SIZE = 1024
sec2millis = 1000
min2sec = 60
min2millis = min2sec*sec2millis

log('Server start main loop')
millis_old = 0
while True:
    millis_new = int(round(time.time()*sec2millis))
    millis_pass = millis_new-millis_old
    try:
        # manda il messaggio broadcast ogni volta che passa broadcastwaitTime
        if ((millis_pass/min2millis) >= broadcastwaitTime):
            millis_old = millis_new
            sockBroad.sendto(broadcastMessage, broadcastSocket)
            log('Sent "'+broadcastMessage+'" to the broadcast')

        # prova a ricevere un messaggio dal server interno
        listenLocal()

        # prova a ricevere messggi broadcast
        listenBroadcast()

    except KeyboardInterrupt:
        print('Keybord interruption detected')
        log('Server shuted down by KeybordInterruption')
        break
    except Exception as ex:
        log(ex.message)
        break

sockLocal.close()
sockBroad.close()
