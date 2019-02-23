import socket
import sys
import re


def splitRequest(data):
    data = data.splitlines()
    print 'DATA: %s' %data
    return data

def removeSpaces(line):
    print 'Linia pred %s' %line
    print 'Linia je rozdelena na %s' % re.split("/",line)
    line = re.split("/",line)
    return line[0].replace(" ", "")

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = int(sys.argv[1])

#sock.bind = (socket.gethostname(), port )
print 'starting up on localhost port %s' %  port
try:
    sock.bind(('', port))
except:
    print 'Port is taken'
    sys.exit()

sock.listen(10)

while True:
    print 'waiting for a connection'
    connection, client_address = sock.accept()
    print 'connection from', client_address

    data = connection.recv(1024)
    data = splitRequest(data)
    requestType = removeSpaces(data[0])

    if requestType == "GET":
        '''
        response_proto = 'HTTP/1.1'
        response_status = '200'
        response_status_text = 'OK' # this can be random

        response_headers = {
            'Content-Type': 'text/html; encoding=utf8',
            'Connection': 'close',
        }
        response_headers_raw = ''.join('%s: %s\n' % (k, v) for k, v in \
                                                response_headers.iteritems())

        # sending all this stuff
        connection.send('%s %s %s' % (response_proto, response_status, \
                                                        response_status_text))
        connection.send(response_headers_raw)
        print "Je to GET miamor!"
        '''
        response_proto = 'HTTP/1.1'
        response_status = '200'
        response_status_text = 'SKUSKA' # this can be random

        response_headers = {
            'Content-Type': 'text/html; encoding=utf8',
            'Content-Length': len('ODPOVED'),
        }
        response_headers_raw = ''.join('%s: %s\n' % (k, v) for k, v in \
                                                response_headers.iteritems())

        connection.send('%s %s %s' % (response_proto, response_status, \
                                                        response_status_text))
        connection.send(response_headers_raw)
        connection.send('\n') # to separate headers from body
        connection.send('ODPOVED')
    else:
        response_proto = 'HTTP/1.1'
        response_status = '400'
        response_status_text = 'BAD' # this can be random
        connection.send('%s %s %s' % (response_proto, response_status, \
                                                        response_status_text))
        print "Nauc vratit chybnu hlasku"

    
    connection.close()
