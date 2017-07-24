# -*- coding: utf-8 -*-

import sys
import socket
import struct 

HOST = '127.0.0.1'
PORT =  51515
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
dest = (HOST, PORT)
tcp.connect(dest)

while True:
	try:
		tcp.settimeout(5.0)
		print struct.unpack('>I',tcp.recv(4))[0]
		num = int(raw_input("Please enter a number: "))
		tcp.send(struct.pack('>I', num))		
	except socket.timeout:
		print "Tempo excedido"
		continue 