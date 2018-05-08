import socket
import sys
import time

def get_ip_address():
    ip_address = ''
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8",80))
    ip_address = s.getsockname()[0]
    s.close()
    return ip_address

socket.setdefaulttimeout(0.1)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)# UDP
sock.bind(('',51082))

sock.sendto('test',('192.168.2.6',51082))
time.sleep(0.05)
message = sock.recvfrom(1024)

print(message[0])


