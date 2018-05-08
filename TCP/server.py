#!/usr/bin/env python

import socket
import time
import sys

TCP_IP = ''#'127.0.0.1'
TCP_PORT = 51083
BUFFER_SIZE = 1024  # Normally 1024, but we want fast response

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(0.1)
# s.setblocking(1)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
while 1:
    try:
        conn, addr = s.accept()
        print('Connection address: ' + str(addr))
        time.sleep(0.01)
        while 1:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                break
            print("received data:" + data)
            conn.send(data)  # echo
        conn.close()
    except KeyboardInterrupt:
        print('')
        break
    except socket.timeout:
        pass
    except Exception as ex:
        print(ex)
s.close()
