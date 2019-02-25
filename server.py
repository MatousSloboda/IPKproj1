import socket
import sys
import re
import os
import errno
import time

def handleRequest(connection, client_address, i):
    timeout = time.time()
    print timeout
    print 'rozdiel:'
    print time.time() - timeout
    possibleRequests = 21
    while(1):
        if (time.time() - timeout) > 10:
            print 'Time ran out!'
            connection.close()
            return
        try:
            data = connection.recv(1024)
            if not data: 
                print 'I should return %d. connection' %i
                connection.close()
                return
        except socket.timeout, e:
            err = e.args[0]
            print err
            continue
        except socket.error, e:
            err = e.args[0]
            print err
            connection.close()
            return
        else:
            print 'data %s' %data
            data = splitRequest(data)
            requestType = getRequestType(data[0])
            print data

            if requestType != "GET":
                response_proto = 'HTTP/1.1'
                response_status = '405 '
                response_status_text = 'Method Not Allowed' # this can be random
                connection.send('%s %s %s\r\n' % (response_proto, response_status, \
                                                                response_status_text))
                connection.send('\r\n')
                connection.close()
                return

            else:     
                possibleRequests = possibleRequests - 1
                #a tu budem riesit tie vsetky moznosti
                #urob non blocking read
                #po akom dlhom case treba vypnut perzistente spojenie, ak client neodpoveda?
                #1. ci je v hlavicke HTTP 1.1 deafultne persistent connection
                #hlavicka accept a chyba ak ja to nepodporujem pozor */* znamena vsetko
                #nacitanie zo suboru
                response_proto = 'HTTP/1.1'
                response_status = '200'
                response_status_text = 'OK'

                msg = 'Sprava cislo %d \n' %i

                response_headers = {
                    'Content-Type': 'text/plain; encoding=utf8',
                    'Content-Length': len(msg),
                    #'Refresh' : '3'
                }
                response_headers_raw = ''.join('%s: %s\n' % (k, v) for k, v in \
                                                        response_headers.iteritems())
                connection.send('%s %s %s\r\n' % (response_proto, response_status, \
                                                                response_status_text))
                connection.send(response_headers_raw)
                connection.send('\r\n')
                connection.send(msg)

                #connection.close()


def splitRequest(data):
    return data.splitlines()
    return data

def getRequestType(line):
    line = re.split("/",line)
    return line[0].replace(" ", "")



# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock,set
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
