import socket
import sys
import re
import os

def handleRequest(connection, client_address, i):
    data = connection.recv(1024)
    if not data: 
        print 'I am returning %d. connection' %i
        return
    data = splitRequest(data)
    requestType = getRequestType(data[0])

    if requestType != "GET":
        response_proto = 'HTTP/1.1'
        response_status = '405 '
        response_status_text = 'Method Not Allowed' # this can be random
        connection.send('%s %s %s\r\n' % (response_proto, response_status, \
                                                        response_status_text))
        connection.send('\r\n')
        connection.close()
    else:     
        response_proto = 'HTTP/1.1'
        response_status = '200'
        response_status_text = 'OK'

        msg = 'Spravne'

        response_headers = {
            'Content-Type': 'text/html; encoding=utf8',
            'Content-Length': len(msg),
        }
        response_headers_raw = ''.join('%s: %s\n' % (k, v) for k, v in \
                                                response_headers.iteritems())
        print 'posielam %d' %i
        connection.send('%s %s %s\r\n' % (response_proto, response_status, \
                                                        response_status_text))
        connection.send(response_headers_raw)
        connection.send('\r\n') # to separate headers from body
        connection.send(msg)
        connection.close()


def splitRequest(data):
    return data.splitlines()
    return data

def getRequestType(line):
    line = re.split("/",line)
    return line[0].replace(" ", "")



# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = int(sys.argv[1])

try:
    sock.bind( ('', port) )
except:
    print 'Port is taken'
    sys.exit()

sock.listen(100)

connectionServed = 0

while True:
    print 'waiting for a connection'
    connection, client_address = sock.accept()
    connectionServed = connectionServed + 1

    newpid = os.fork()
    if newpid > 0:
        print connectionServed
        connection.close()
        continue
    elif newpid == 0:
        handleRequest(connection, client_address, connectionServed)
        sys.exit(0)
    else:
        print 'error'
        #error in creating child, handling a request by parent then waits for another connection
        handleRequest(connection, client_address, connectionServed)
