import socket
import sys
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.connect(('localhost', 10000))
time.sleep(13)
data = sock.recv(1024)
print data
sock.close()
