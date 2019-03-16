import socket
import sys
import re
import os
import errno
import time
from itertools import groupby #from many spaces in text makes one
import platform


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

def occursInAccepts(line):
    if not line:
        return 'text/plain'
    elif line.find('*/*') > 0:
        return 'text/plain'
    elif line.find('text/plain') > 0 or line.find('text/*') > 0:
        return 'text/plain'
    elif line.find('application/json') > 0 or line.find('application/*') > 0:
        return 'application/json'
    return None

def occursKeepAlive(line):
    if not line:
        return True
    elif line.find('keep-alive') > 0:
        return True
    else:
        return False

def calculateCpuStat(start, stop):
    Total = stop['total']
    PrevTotal = start['total']

    Idle = stop['idle']
    PrevIdle = start['idle']

    return (((Total-PrevTotal)-(Idle-PrevIdle))/(Total-PrevTotal)*100)

def readCPUstat():
    cpu_infos = {}
    stats  = open('/proc/stat', 'r')
    line = stats.readline()
    stats.close()
    line = ''.join(' ' if is_space else ''.join(chars) for is_space, chars in groupby(line, str.isspace))
    cpuLoad = re.split(" ",line)

    cpu_id,user,nice,system,idle,iowait,irq,softrig,steal,guest,guest_nice,daco = cpuLoad

    Idle=float(idle)+float(iowait)
    NonIdle=float(user)+float(nice)+float(system)+float(irq)+float(softrig)+float(steal)

    Total=float(Idle)+float(NonIdle)
    cpu_infos.update({'total':Total,'idle':Idle})

    return cpu_infos



def sendPositiveAnswer(attributes):
    response_proto = 'HTTP/1.1'
    response_status = '200'
    response_status_text = 'OK'

    bodyText            = str(attributes['body'])
    contentType         = attributes['accepts']
    keepAlive           = attributes['keepAlive']
    possibleRequests    = attributes['possibleRequests'] 
    refreshAllowed      = attributes['refreshAllowed']
    connection          = attributes['connection']

    #creating body
    if contentType == 'application/json':
        if attributes['type'] == 'load':
            msg ="{\"%s\": \"%s%%\"}" % (attributes['type'], bodyText)
        else:
            msg ="{\"%s\": \"%s\"}" % (attributes['type'], bodyText)
    else:
        if attributes['type'] == 'load':
            msg = bodyText + '%\n'
        else:
            msg = bodyText + '\n'
            
    #creating headder
    if keepAlive:
        if refreshAllowed:
            response_headers = {
                'Content-Type': contentType + ' encoding=utf8',
                'Content-Length': len(msg),
                'Keep-Alive' : 'timeout=10, max=%d' %possibleRequests,
                'Refresh' : attributes['refreshTime']
            }
        else:
            response_headers = {
                'Content-Type': contentType + ' encoding=utf8',
                'Content-Length': len(msg),
                'Keep-Alive' : 'timeout=10, max=%d' %possibleRequests,
            }
    else:   
    #client send connection : close
        if refreshAllowed:
            response_headers = {
                'Content-Type': contentType + ' encoding=utf8',
                'Content-Length': len(msg),
                'Refresh' : attributes['refreshTime'],
                'Connection' : 'close'
            }
        else:
            response_headers = {
                'Content-Type': contentType + ' encoding=utf8',
                'Content-Length': len(msg),
                'Connection' : 'close'
            }

    response_headers_raw = ''.join('%s: %s\n' % (k, v) for k, v in \
                                            response_headers.iteritems())
    try:    #prevention if client closed socket
        connection.send('%s %s %s\r\n' % (response_proto, response_status, response_status_text))
        connection.send(response_headers_raw)
        connection.send('\r\n')
        connection.send(msg)
        return 0
    except socket.error, e:
            err = e.args[0]
            print err
            print 'Error sock send'
            return 1
    



def sendNegativeResponse(status, statusText, connection):
    response_proto = 'HTTP/1.1'
    response_status = status + ' '
    response_status_text = statusText

    try:
        connection.send('%s %s %s\r\n' % (response_proto, response_status, response_status_text))
        connection.send('\r\n')
        return 0
    except socket.error, e:
        print 'Error sock send'
        err = e.args[0]
        print err
        return 1


def handleRequest(connection, client_address):
    timeout = time.time()
    possibleRequests = 20
    while(1):
        if possibleRequests < 0:
            print 'Too many requests'
            connection.close()
            return
        if (time.time() - timeout) > 10:
            print 'Time ran out!'
            connection.close()
            return
######################DATA SECTION######################
        try:
            data = connection.recv(1024)
            if not data: 
                print 'I close connection'
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
###################### I recieved data ######################            
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
                accepts = occursInAccepts(returnHeadderLine('Accept', data))
                keepAlive = occursKeepAlive(returnHeadderLine('Connection', data)) #True if 'Connection : keep-alive' or Connection is not mentioned in socket

                if accepts == None:
                    sendNegativeResponse('406','Not Acceptable', connection)
                    connection.close()
                    print 'Unsupported method'
                    return

                if requestLine[1] == '/hostname':
                    messageFeatures = {
                        'keepAlive'         : keepAlive,
                        'accepts'           : accepts,
                        'possibleRequests'  : possibleRequests,
                        'refreshAllowed'    : False,
                        'body'              : socket.gethostname(),
                        'connection'        : connection,
                        'type'              : 'hostname'
                    }
                    if sendPositiveAnswer(messageFeatures) == 1:
                        connection.close()
                        return
                    if not keepAlive:
                        connection.close()
                        return

                elif requestLine[1] == '/cpu-name':
                    messageFeatures = {
                        'keepAlive'         : keepAlive,
                        'accepts'           : accepts,
                        'possibleRequests'  : possibleRequests,
                        'refreshAllowed'    : False,
                        'body'              : platform.processor(),
                        'connection'        : connection,
                        'type'              : 'cpu-name'
                    }

                    if sendPositiveAnswer(messageFeatures) == 1:
                        connection.close()
                        return
                    if not keepAlive:
                        connection.close()
                        return

                elif requestLine[1] == '/load':

                    start = readCPUstat()
                    time.sleep(1)
                    stop = readCPUstat()

                    messageFeatures = {
                        'keepAlive'         : keepAlive,
                        'accepts'           : accepts,
                        'possibleRequests'  : possibleRequests,
                        'refreshAllowed'    : False,
                        'body'              : round(calculateCpuStat(start, stop),2),
                        'connection'        : connection,
                        'type'              : 'load'
                    }

                    if sendPositiveAnswer(messageFeatures) == 1:
                        connection.close()
                        return
                    if not keepAlive:
                        connection.close()
                        return

                elif requestLine[1][:14] == '/load?refresh=':
                    try:
                        refreshTime = int(requestLine[1][14:])
                    except:
                        sendNegativeResponse('406','Not Acceptable', connection)
                        connection.close()
                        return

                    start = readCPUstat()
                    time.sleep(1)
                    stop = readCPUstat()

                    messageFeatures = {
                        'keepAlive'         : keepAlive,
                        'accepts'           : accepts,
                        'possibleRequests'  : possibleRequests,
                        'refreshAllowed'    : True,
                        'refreshTime'       : refreshTime,
                        'body'              : round(calculateCpuStat(start, stop),2),
                        'connection'        : connection,
                        'type'              : 'load'
                    }

                    if sendPositiveAnswer(messageFeatures) == 1:
                        connection.close()
                        return
                    if not keepAlive:
                        connection.close()
                        return

                else:
                    sendNegativeResponse('404','Not Found', connection)
                    connection.close()
                    print 'Bad path'
                    return
                
                possibleRequests = possibleRequests - 1
                timeout = time.time()






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


while True:
    connection, client_address = sock.accept()
    connection.settimeout(1)

    newpid = os.fork()
    if newpid > 0:
        connection.close()
        continue
    elif newpid == 0:
        handleRequest(connection, client_address)
        break
    else:
        print 'Error creating new process. Main process will handle your request. Not possible to handle parallel requests now!'
        handleRequest(connection, client_address)
