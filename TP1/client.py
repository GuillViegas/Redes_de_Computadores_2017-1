# -*- coding: utf-8 -*-

import sys
import socket
import struct 

HOST = '127.0.0.1'
PORT =  51515
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
dest = (HOST, PORT)
tcp.connect(dest)

if sys.argv[1] == 'inc':
	arg = '+'
elif sys.argv[1] == 'dec': 
	arg = '-'
else:
	arg = '*'
	print >> sys.stderr, 'Entrada inválida!'

tcp.send(arg)
tcp.settimeout(5.0)
count = struct.unpack('>I', tcp.recv(4))[0]
tcp.settimeout(None)
u = count%10
d = count%100//10
c = count//100
tcp.send(str(c))
tcp.send(str(d))
tcp.send(str(u))
tcp.close()