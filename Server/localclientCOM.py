import socket
import sys

def get_ip_address():
    ip_address = ''
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8",80))
    ip_address = s.getsockname()[0]
    s.close()
    return ip_address

def StatusSwitch(message):
    elements = message.split(',')
    if elements[-1]=='ON':
        print('true')
    else:
        print('false')

# 'ec:fa:bc:87:77:bd,PIN,0,OFF'
# 'C2:A7:1C:F0:0D:37,PIN,0,OFF'
ServerIP = ('127.0.0.1',51081)

MESSAGE = sys.argv[1]

sock = socket.socket(socket.AF_INET, # Internet
               socket.SOCK_STREAM) # UDP

sock.connect(ServerIP)
sock.send(MESSAGE)
message = sock.recv(1024)
#print(message)
if len(sys.argv)==2:
    kind = 'I'
else:
    kind = sys.argv[2]

if kind=='I':
    StatusSwitch(message)
