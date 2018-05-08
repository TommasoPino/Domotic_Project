import socket
from get_ip_addr import *

MAC_ADR = 'ec:fa:bc:87:77:bd'
UDP_IP = str(get_ip_address())
UDP_IP_PORT = 50003
UDP_BC = '255.255.255.255'
UDP_BC_PORT = 12345
# MESSAGE = MAC_ADR + ',' + UDP_IP + ',' + 'test'
# MESSAGE = MAC_ADR + ',PIN,0,ON'
MESSAGE = MAC_ADR + ',PIN,0,OFF'

print "UDP target IP:", UDP_IP
print "UDP target port:", UDP_IP_PORT
print "message:", MESSAGE

sockR = socket(AF_INET, # Internet
              SOCK_DGRAM) # UDP

sockR.bind(('127.0.0.1',50002))

sockS = socket(AF_INET, # Internet
              SOCK_DGRAM) # UDP

sockS.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

sockS.sendto(MESSAGE, ('127.0.0.1', 50001))

message = sockR.recvfrom(1024)
              
print message[0]

print "message sent"