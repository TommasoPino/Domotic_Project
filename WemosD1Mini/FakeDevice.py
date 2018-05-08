# import network as net
import socket as sock
# import machine 
import os
import time
# import ubinascii

def log(message):
    print(message)

def get_ip_address():
    ip_address = ''
    s = sock.socket(sock.AF_INET, sock.SOCK_DGRAM)
    s.connect(("8.8.8.8",80))
    ip_address = s.getsockname()[0]
    s.close()
    return ip_address

BROADCASTIP = '255.255.255.255'
BROADCASTPORT = 51082
broadcastSocket = (BROADCASTIP,BROADCASTPORT)
sockBroad = sock.socket(sock.AF_INET, # Internet
                        sock.SOCK_DGRAM) # UDP
sockBroad.setsockopt(sock.SOL_SOCKET, sock.SO_BROADCAST, 1)
sockBroad.settimeout(0.1)
sockBroad.bind(('',BROADCASTPORT))

MAC = 'C2:A7:1C:F0:0D:37'
IP = get_ip_address()
boardKind = 'I'
sockBroad.sendto('D,' + MAC + ',' + IP + ',' + boardKind,(BROADCASTIP,BROADCASTPORT))

sockServer = sock.socket(sock.AF_INET, # Internet
                         sock.SOCK_STREAM) # UDP
sockServer.settimeout(0.1)
sockServer.bind(('',51083))
sockServer.listen(3)

print('start loop')
while 1:
    try:
        conn, addr = sockServer.accept()
        print('Connection address:' + str(addr))
        time.sleep(0.01)
        while 1:
            data = conn.recv(1024)
            if not data:
                break
            print "received data:", data
            conn.send(data)  # echo
        conn.close()
    except KeyboardInterrupt:
        break
    except Exception as ex:
	pass

sockServer.close()