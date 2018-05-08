from socket import *
s=socket(AF_INET, SOCK_DGRAM)
s.bind(('',51082))
while True:
    m=s.recvfrom(1024)
    print m[0]