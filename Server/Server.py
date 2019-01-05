#!/usr/bin/env python
import socket as sock
import time
import os.path
import datetime
import sys
import logging
import logging.handlers as handlers

#class Unbuffered(object):
#   def __init__(self, stream):
#       self.stream = stream
#   def write(self, data):
#       self.stream.write(data)
#       self.stream.flush()
#   def writelines(self, datas):
#       self.stream.writelines(datas)
#       self.stream.flush()
#   def __getattr__(self, attr):
#       return getattr(self.stream, attr)

# def log(message):
#     file = open(filelog, 'r+')
#     lines = file.readlines()
#     if message == None:
#         file.write('\n')
#         file.write('\n')
#     else:
#         file.write(str(datetime.datetime.now()) + ': ' + message)
#         file.write('\n')
# 	#sys.stdout = Unbuffered(sys.stdout)
# 	print(str(datetime.datetime.now()) + ': ' + message)
#     file.close()


def readtable(filename):
    C = {}
    try:
        file = open(filename, 'r')
        logger.info('Reading ' + filename + ' to populate the dictionary')
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

        logger.info('Found ' + str(nel) + ' device in the file')
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
    logger.info('Added new elements to the Device Table')
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
            logger.info('Received internal message ' + message)
            elements = message.split(',')
            try:
                device = DeviceDict[elements[0]]
                logger.info('Found device with id: ' + elements[0])
                messagetosend = composemessage(elements[1:])
                logger.debug(str(device))
                # try:
                #     IPSEND = (device[0][0], IPPORT)
                #     sockServer.connect(IPSEND)
                # except:
                IPSEND = (device[0], IPPORT)
                logger.info('Try opening connection with: ' + str(IPSEND))
                sockServer.connect(IPSEND)
                logger.info('Opened connection with: ' + str(IPSEND))
                for i in range(4):
                    try:
                        sockServer.send(messagetosend)
                        logger.debug('Message sent to Device')
                        messagerecived = sockServer.recv(BUFFER_SIZE)
                        logger.info('Message recieve from Device: ' + messagerecived)
                        logger.debug('Connection Closed')
                        break
                    except Exception as ex:
                        logger.warning('An error occours: ' + ex.message)
                        time.sleep(0.1)
                sockServer.close()
                elementsin = messagerecived.split(',')
                if elements[0] == elementsin[0]:
                    logger.debug('Match ' + elementsin[0])
                    conn.send(messagerecived)
                logger.debug('Resent message')
            except sock.error as ex:
                logger.warning(str(ex))
                conn.send('Error')
            except KeyError:
                logger.warning('Key ' + elements[0] + ' not found!')
                conn.send('Not Found')
            except Exception as ex:
                conn.send('Error')
                logger.warning(ex.message)
        logger.debug('Closed connection')
        conn.close()

        try:
            logger.debug('Connection Closing')
            sockServer.close()
        except:
            pass
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
        logger.info('Recived External message: "' +
            str(message[0]) + '" ; from: ' + str(message[1]))

        elements = stripInMessage(message[0]).split(',')
        if elements[0] == 'D':
            logger.info('Message from a device')
            try:
                Device = DeviceDict[elements[1]]
                logger.info('Device already present on table, checking for updates')
                if Device[0]!=elements[2]:
                    logger.info('changed ip from ' + str(Device[0]) + ' to ' + str(elements[2]))
                    DeviceDict[elements[1]] = elements[2:]
                    updatetable(DeviceDict,FileDataDevice)
            except KeyError:
                DeviceDict[elements[1]] = elements[2:]
                add2table(elements[1:], FileDataDevice)
        elif elements[0] == 'S':
            logger.debug('Message from Server ignored')
        else:
            logger.warning('Message ignored')
    except sock.timeout:
        pass

def updatetable(devicedict,filename):
    logger.info('updating table')
    try:
        file = open(filename, 'w')
        file.close()
        for deviceID in devicedict:
            logger.debug(str(deviceID + devicedict[0]))
            add2table([deviceID] + devicedict[deviceID],filename)
        logger.debug('done')
    except Exception as ex:
        logger.warning(str(ex))
        
    


# start the program
DeviceDict = {}
# pathusr = '/home/pi/.DomoticPythonServer/'
pathusr = '/home/pi/.DomoticPythonServer/'
FileDataDevice = pathusr + 'DeviceList.csv'
FileLogPath = pathusr + 'DomoticServer.log'
logname = 'DomoticServer'
logger = logging.getLogger(logname)
# logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)
# logging
# Here we define our formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logHandler = handlers.TimedRotatingFileHandler(FileLogPath, when='midnight', interval=1, backupCount=3)
logHandler.suffix = "%Y%m%d"
# logHandler.setLevel(logging.INFO)
logHandler.setLevel(logging.DEBUG)
# Here we set our logHandler's formatter
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

# add ch to logger
# ch = logging.StreamHandler()
# ch.setLevel(logging.DEBUG)
# ch.setFormatter(formatter)
# logger.addHandler(ch)



# filelog = pathusr + 'Server.log'
# # check the existance of the file log
# checkFileAndCreate(filelog)
#sys.stdout = Unbuffered(sys.stdout)
logger.info('\n\n')
logger.info('Server Turned on, start initialization')

# check the existance of the Devices file
logger.info('Check existance of ' + FileDataDevice)
checkFileAndCreate(FileDataDevice)

# Build the device dictionary
logger.info('Build table from file')
DeviceDict = readtable(FileDataDevice)


# Define Ip of server and its listen port
IPSERVER = get_ip_address()
IPPORT = 51083
sock.setdefaulttimeout(1)

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
broadcastwaitTime = 5  # minute
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

logger.info('Server start main loop')
millis_old = 0
while True:
    millis_new = int(round(time.time()*sec2millis))
    millis_pass = millis_new-millis_old
    try:
        # manda il messaggio broadcast ogni volta che passa broadcastwaitTime
        if ((millis_pass/min2millis) >= broadcastwaitTime):
            millis_old = millis_new
            sockBroad.sendto(broadcastMessage, broadcastSocket)
            logger.info('Sent "'+broadcastMessage+'" to the broadcast')

        # prova a ricevere un messaggio dal server interno
        listenLocal()

        # prova a ricevere messggi broadcast
        listenBroadcast()

    except KeyboardInterrupt:
        logger.warning('Server shuted down by KeybordInterruption')
        break
    except Exception as ex:
        logger.warning(ex.message)
        break

sockLocal.close()
sockBroad.close()
