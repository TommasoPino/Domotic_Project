import socket
from get_ip_addr import *

MAC_ADR = 'C2:A7:1C:F0:0D:37'
UDP_IP = str(get_ip_address())
UDP_IP_PORT = 50002
UDP_BC = '255.255.255.255'
UDP_BC_PORT = 12345
MESSAGE = 'S,' + UDP_IP + ',' + str(UDP_IP_PORT)
print "UDP target IP:", UDP_BC
print "UDP target port:", UDP_BC_PORT
print "message:", MESSAGE

sock = socket(AF_INET, # Internet
              SOCK_DGRAM) # UDP

sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
              
sock.sendto('PIN,0,STAT', (UDP_BC, UDP_IP_PORT))

print "message sent"