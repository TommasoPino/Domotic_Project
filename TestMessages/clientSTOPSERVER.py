import socket
from get_ip_addr import *

UDP_IP = str(get_ip_address())
UDP_IP_PORT = 50002
UDP_BC = '255.255.255.255'
UDP_BC_PORT = 12345
MESSAGE = 'stopserver'

print "UDP target IP:", UDP_BC
print "UDP target port:", UDP_BC_PORT
print "message:", MESSAGE

sock = socket(AF_INET, # Internet
              SOCK_DGRAM) # UDP

sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
              
sock.sendto(MESSAGE, (UDP_BC, UDP_BC_PORT))

print "message sent"