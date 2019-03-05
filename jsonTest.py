import json
import sys
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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

sock.listen(10)


connection, client_address = sock.accept()


msg = json.loads(msg)

data = connection.recv(1024)

response_headers = {
                'Content-Type': 'application/json' + ' encoding=utf8',
                'Content-Length': len(msg),
                'Keep-Alive' : 'timeout=10, max=20',
            }
response_headers_raw = ''.join('%s: %s\n' % (k, v) for k, v in \
                            response_headers.iteritems())
response_proto = 'HTTP/1.1'
response_status = '200'
response_status_text = 'OK'
connection.send('HTTP/1.1 200 OK\r\n')
connection.send(response_headers_raw)
connection.send('\r\n')
connection.send(msg)


m ='{"id": 2, "name": "abc"}'
jsonObj = json.loads(m)

print m
print ''
print jsonObj