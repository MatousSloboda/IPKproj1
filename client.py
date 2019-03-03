import socket
import sys
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.connect(('localhost', int(sys.argv[1])))


response_proto = 'GET '
response_status = '/hostname'
response_status_text = ' HTTP/1.1'

sock.send('%s %s %s\r\n' % (response_proto, '/hostname', response_status_text))
sock.send('%s %s %s\r\n' % (response_proto, '/load', response_status_text))


data = sock.recv(1024)
print data
sock.close()

print 'end'
