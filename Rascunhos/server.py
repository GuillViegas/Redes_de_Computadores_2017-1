# -*- coding: utf-8 -*-

import socket
import struct 
import sys

HOST = ''
PORT = 51515
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
orig = (HOST, PORT)
tcp.bind(orig)
tcp.listen(1)

con, cliente = tcp.accept()	
con.send(struct.pack('>I', 0))
while True: 
	num = struct.unpack('>I', con.recv(4))[0]
	print num
	raw_input("Please enter a number: ")
	con.send(struct.pack('>I', num))
	
