import socket
import time

TCP_IP = '192.168.1.114'
TCP_PORT = 51083
BUFFER_SIZE = 1024
MESSAGE = "Hello, World!"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(0.1)
try:
    s.connect((TCP_IP, TCP_PORT))
    for i in range(3):
        try:
            s.send(MESSAGE)
            data = s.recv(BUFFER_SIZE)
            print "received data:", data
            break
        except Exception as ex:
            print(i)
            print(str(ex))
            time.sleep(0.1)

    s.close()
except Exception as ex:
    print(str(ex))
    pass