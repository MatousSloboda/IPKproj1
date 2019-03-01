import socket
import sys
import re
import os
import errno
import time

def handleRequest(connection, client_address, i):
    timeout = time.time()
    possibleRequests = 20
    while(1):
        if (time.time() - timeout) > 10:
            print 'Time ran out!'
            connection.close()
            return
        try:
            data = connection.recv(1024)
            if not data: 
                print 'I close %d. connection' %i
                connection.close()
                return
        except socket.timeout:
            continue
        except socket.error, e:
            err = e.args[0]
            print err
            connection.close()
            return

######################DATA SECTION######################
        else:
            data = splitHTTP(data)
            requestLine = splitRequestLine(data[0])

            if len(requestLine) != 3:
                print 'ERROR in HTTP request'
                connection.close()
                return
            
            if requestLine[0] != "GET":
                response_proto = 'HTTP/1.1'
                response_status = '405 '
                response_status_text = 'Method Not Allowed' # this can be random

                try:
                    connection.send('%s %s %s\r\n' % (response_proto, response_status, \
                                                                    response_status_text))
                    connection.send('\r\n')
                except socket.error, e:
                    err = e.args[0]
                    print err

                connection.close()
                return

            else:    
                #Ak mam hlavicku 1.0 a tam mam connection keep alive tak drzim, inak nie
                #nacitanie zo suboru
                accepts = recieverAccepts(returnHeadderLine('Accept', data))
                if accepts == 'text':
                    print 'accepts text'
                elif accepts == 'json':
                    print 'accepts json'
                else:
                    print 'Nepodporovany format'
                    connection.close()
                    return

                if requestLine[1] == '/hostname':
                    print 'hostname'

                elif requestLine[1] == '/cpu-name':
                    print returnHeadderLine('Accept', data)

                else:
                    print returnHeadderLine('Accept', data)
                    #pories si load a refresh + vypocet


                response_proto = 'HTTP/1.1'
                response_status = '200'
                response_status_text = 'OK'

                msg = 'PETO ZACNI SA UCIT!\n'

                response_headers = {
                    'Content-Type': 'text/plain; encoding=utf8',
                    'Content-Length': len(msg),
                    'Keep-Alive' : 'timeout=10, max=%d' %possibleRequests,
                    'Refresh' : '1'
                }
                response_headers_raw = ''.join('%s: %s\n' % (k, v) for k, v in \
                                                        response_headers.iteritems())
                connection.send('%s %s %s\r\n' % (response_proto, response_status, \
                                                                response_status_text))
                connection.send(response_headers_raw)
                connection.send('\r\n')
                connection.send(msg)
                possibleRequests = possibleRequests - 1
                if possibleRequests < 0:
                    connection.close()
                    return
                timeout = time.time()


def splitHTTP(data):
    return data.splitlines()
    return data

def splitRequestLine(line):
    line = re.split(" ",line)
    return line

def returnHeadderLine(option, data):
    for i in data:
        i = re.split(":",i)
        if i[0].lower() == option.lower():
            return i[1].lower()
    return None

def recieverAccepts(line):
    if line.find('*/*') > 0:
        return 'text'
    elif line.find('text/plain') > 0:
        return 'text'
    elif line.find('application/json') > 0:
        return 'json'




# Create a TCP/IP socket
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except:
    print 'Error creating socket!'
    sys.exit()

port = int(sys.argv[1])

try:
    sock.bind( ('', port) )
except:
    print 'Port is taken!'
    sys.exit()

sock.listen(100)

connectionServed = 0

while True:
    print 'waiting for a connection'
    connection, client_address = sock.accept()
    connection.settimeout(1)
    connectionServed = connectionServed + 1

    newpid = os.fork()
    if newpid > 0:
        connection.close()
        continue
    elif newpid == 0:
        handleRequest(connection, client_address, connectionServed)
        break
    else:
        print 'Error creating new process. Main process will handle your request. Not possible to handle parallel requests now!'
        #error in creating child, handling a request by parent then waits for another connection
        handleRequest(connection, client_address, connectionServed)
