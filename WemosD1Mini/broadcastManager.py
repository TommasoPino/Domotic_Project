# This class create the instance to manage the serverIP and the relative broadcast management

import network as net
import socket as sock
import machine 
import os
import time
import ubinascii
import urandom
import math

def get_ip_address():
    ip_address = ''
    sta_if = net.WLAN(net.STA_IF)
    temp = sta_if.ifconfig()
    ip_address = temp[0]
    return ip_address

class BroadcastManager:

    def __init__(self,
                dirdata = "data",
                filedata = "serverip.data",
                boardKind = "I",
                portBroadCast = 51082):
        self.dirdata = dirdata
        self.filedata = filedata
        self.portBroadCast = portBroadCast
        self.mac = ubinascii.hexlify(net.WLAN().config('mac'),':').decode()
        self.boardKind = boardKind
        self.build_bc_msg()
        self.checkFileAndCreate(self.dirdata,self.filedata)
        self.IPfile = self.dirdata + '/' + self.filedata
        self.ServerIP = []
        self.FileGetServerIP()
        self.sec2millis = 1000
        self.min2sec    = 60
        self.min2millis = self.min2sec*self.sec2millis
        self.millis_old = int(round(time.time()*self.sec2millis))
        self.waitTime = 1
        self.sockBroadCast = []


    def init_bc_sock(self):
        self.sockBroadCast=sock.socket(sock.AF_INET,sock.SOCK_DGRAM)
        self.sockBroadCast.settimeout(0.1)
        self.sockBroadCast.bind(('',self.portBroadCast))

    def build_bc_msg(self):
        self.ip = get_ip_address()
        self.message = 'D,' + self.mac+','+self.ip+','+self.boardKind

    def stripInMessage(self,inline):
        inline = str(inline)
        inline = inline.replace('b\'','')
        outline = inline.replace('\'','')
        return outline

    def check_bc_msg(self):
        millis_new = int(round(time.time()*self.sec2millis))
        millis_pass = millis_new-self.millis_old
        if (millis_pass/self.min2millis>=self.waitTime):
            self.log('inside if')
            self.millis_old = millis_new
            self.waitTime = 1
            self.log('Build message')
            self.build_bc_msg()
            self.send_bc_msg()
        try:
            m=self.sockBroadCast.recvfrom(1024)
            line = self.stripInMessage(m[0])
            self.log('Recived message from broadcast: ' + line)
            elements = list(line.split(','))
            
            if elements[0].strip()=='S':
                self.waitTime = self.get_random_time()
                self.log('New waiting time: ' + str(self.waitTime))
                if (self.ServerIP[0] != elements[1]):
                    self.log('build SERVERIP')
                    self.ServerIP[0] = elements[1]
                    self.ServerIP[1] = int(elements[2])

                    self.FileSetServerIP()
                else:
                    self.log('nothong change, server ip is: ' +str(self.ServerIP[0]))
                    self.log('nothong change, server port is: ' +str(self.ServerIP[1])) 
        except Exception as ex:
            if str(ex)=='[Errno 110] ETIMEDOUT':
                pass
            elif str(ex)=='[Errno 11] EAGAIN':
                pass
            elif str(ex)=='[Errno 22] EINVAL':
                pass
            else:
                self.log(str(ex))
            

    def get_random_time(self):
        num = self.translate(urandom.getrandbits(16), 0, 65535, 0, 10000)
        integer  = math.floor(num)/1000 # the translate function returns a float, which we gotta deal with somehow
        return integer

    def translate(self,value, leftMin, leftMax, rightMin, rightMax):
        # Figure out how 'wide' each range is
        leftSpan = leftMax - leftMin
        rightSpan = rightMax - rightMin
        # Convert the left range into a 0-1 range (float)
        valueScaled = float(value - leftMin) / float(leftSpan)
        # Convert the 0-1 range into a value in the right range.
        return rightMin + (valueScaled * rightSpan)

    def checkFileAndCreate(self,dir,filename):
        dirfilename = dir+'/'+filename
        self.log('check file ' + dirfilename)
        listfile = os.listdir(dir)
        if not (filename in listfile):
            self.log('file ' + dirfilename + ' not found, it will created')
            file = open(dirfilename,'w')
            file.close()
    
    

    def log(self,message):
        print(message)
    
    def FileGetServerIP(self):
        self.log('getting SERVER IP from file: ' + self.IPfile)
        file = open(self.IPfile,'r')
        strServerIP = file.readline()
        file.close()
        if strServerIP!='':
            self.log('SERVER IP found: ' + strServerIP)
            elements = str(strServerIP).split(',')
            self.ServerIP[0] = elements[0]
            self.ServerIP[1] = int(elements[1])
            self.log('And set')
        else:
            self.ServerIP = ['192.168.1.11',51083]
            self.log('SERVER IP NOT found: ' + str(self.ServerIP))
            

    def FileSetServerIP(self):
        self.log('putting SERVER IP to file: ' + self.IPfile)
        try:
            file = open(self.IPfile,'w')
            file.write(self.ServerIP[0]+','+str(self.ServerIP[1]))
            file.close()
            self.log('done')
        except Exception as ex:
            self.log(str(ex))

    def send_bc_msg(self):
        self.log('inside sendSocketBroadcast')
        try:
            self.log('Try to send message to the server: '+ self.message + ' at : ' + str((self.ServerIP[0],self.portBroadCast)))  
            self.sockBroadCast.sendto(self.message,(self.ServerIP[0],self.portBroadCast))
            self.log('Sent message to the server: '+ self.message)  
        except Exception as ex:
            self.log(str(ex))


    def closesock(self):
        self.sockBroadCast.close()