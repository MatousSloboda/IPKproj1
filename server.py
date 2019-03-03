import socket
import sys
import re
import os
import errno
import time
from itertools import groupby #from many spaces makes one
import platform

def handleRequest(connection, client_address, i):
    timeout = time.time()
    possibleRequests = 20
    print 'NEW PROCESS: %d' %i
    while(1):
        if possibleRequests < 0:
            print 'Too many requests'
            connection.close()
            return
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
            print 'Error sock rcv'
            connection.close()
            return

######################DATA SECTION######################
        else:
            data = splitHTTP(data)
            requestLine = splitRequestLine(data[0])

            if len(requestLine) != 3:
                sendNegativeResponse('400','Bad HTTP request', connection)
                connection.close()
                print 'Bad HTTP request'
                return
            
            if requestLine[0] != "GET":
                sendNegativeResponse('405','Method Not Allowed', connection)
                connection.close()
                print 'Method Not Allowed'
                return

            else:    
                #Ak mam hlavicku 1.0 a tam mam connection keep alive tak drzim, inak nie
                #nacitanie zo suboru
                print data
                accepts = recieverAccepts(returnHeadderLine('Accept', data))
                keepAlive = recieverKeepAlive(returnHeadderLine('Connection', data))

                if requestLine[1] == '/hostname':
                    sendPositiveAnswer(accepts, possibleRequests, False, 0, socket.gethostname(), connection )

                elif requestLine[1] == '/cpu-name':
                    sendPositiveAnswer(accepts, possibleRequests, False, 0, platform.processor(), connection )

                elif requestLine[1] == '/load':
                    sendPositiveAnswer(accepts, possibleRequests, False, 0, 'load', connection )

                elif requestLine[1][:14] == '/load?refresh=':
                    try:
                        refreshTime = int(requestLine[1][14:])
                        sendPositiveAnswer(accepts, possibleRequests, True, refreshTime, 'loadRefresh', connection )
                    except:
                        sendNegativeResponse('405','Method Not Allowed', connection)
                        connection.close()
                        return
                else:
                    sendNegativeResponse('405','Method Not Allowed', connection)
                    connection.close()
                    print 'Bad path'
                    return
                
                possibleRequests = possibleRequests - 1
                timeout = time.time()



def sendPositiveAnswer(contentType, possibleRequests, refresh, refreshTime, message, connection):
    response_proto = 'HTTP/1.1'
    response_status = '200'
    response_status_text = 'OK'

    if contentType == 'text/plain':
        msg = message + '\n'
    else:
        msg = message
    #else:
    #    msg = message.toJson()
    if refresh:
        response_headers = {
            'Content-Type': contentType + ' encoding=utf8',
            'Content-Length': len(msg),
            'Keep-Alive' : 'timeout=10, max=%d' %possibleRequests,
            'Refresh' : refreshTime
        }
    else:
        response_headers = {
            'Content-Type': contentType + ' encoding=utf8',
            'Content-Length': len(msg),
            'Keep-Alive' : 'timeout=10, max=%d' %possibleRequests,
        }

    response_headers_raw = ''.join('%s: %s\n' % (k, v) for k, v in \
                                            response_headers.iteritems())
    connection.send('%s %s %s\r\n' % (response_proto, response_status, response_status_text))
    connection.send(response_headers_raw)
    connection.send('\r\n')
    connection.send(msg)

def splitHTTP(data):
    return data.splitlines()
    return data

def splitRequestLine(line):
    line = ''.join(' ' if is_space else ''.join(chars) for is_space, chars in groupby(line, str.isspace))
    line = re.split(" ",line)
    return line

def returnHeadderLine(option, data):
    for i in data:
        i = re.split(":",i)
        if i[0].lower() == option.lower():
            return i[1].lower()
    return None

def recieverAccepts(line):
    if not line:
        return 'text/plain'
    if line.find('*/*') > 0:
        return 'text/plain'
    elif line.find('text/plain') > 0 or line.find('text/*') > 0:
        return 'text/plain'
    elif line.find('application/json') > 0 or line.find('application/*') > 0:
        return 'application/json'
    return 'text/plain'

def recieverKeepAlive(line):
    if not line:
        return True    #tu sa to este ale moze zmenit v zavislosti od HTTP dotazu
    elif line.find('keep-alive') > 0:
        return True
    else:
        return False

def sendNegativeResponse(status, statusText, connection):
    response_proto = 'HTTP/1.1'
    response_status = status + ' '
    response_status_text = statusText

    try:
        connection.send('%s %s %s\r\n' % (response_proto, response_status, response_status_text))
        connection.send('\r\n')
    except socket.error, e:
        print 'Error'
        err = e.args[0]
        print err

    return



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
