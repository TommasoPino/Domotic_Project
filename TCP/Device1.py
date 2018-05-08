import socket
import sys

def get_ip_address():
    ip_address = ''
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8",80))
    ip_address = s.getsockname()[0]
    s.close()
    return ip_address

socket.setdefaulttimeout(0.01)

sock = socket.socket(socket.AF_INET, # Internet
              socket.SOCK_DGRAM) # UDP
sock.bind(('',51082))

while True:
    try:
        message = sock.recvfrom(1024)
        print(message[0]) 
        sock.sendto(message[0],(message[1][0],51082))
    except KeyboardInterrupt:
        print('Keybord interruption detected')
        break
    except:
        pass


