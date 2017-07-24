# -*- coding: utf-8 -*-
import socket 
import struct
import sys

consts = {
	'HOST' : '127.0.0.1',
	'PORT' : 5001,
	'RESP_LEN': 204,
	'stimeout': 4
}

msg_types = {
	'CLIREQ' : 1,
	'RESPONSE' : 3
}

def do_query(udp, MSG, s_adress):
	udp.sendto(MSG, s_address)
	has_received = False 

	while True:
		try:
			(MSG, ADDRESS) = udp.recvfrom(consts['RESP_LEN'])
			IP, PORT = ADDRESS
			msg_type = struct.unpack_from('>H', MSG, 0)[0]

			if (msg_type == 3):
				key, value = MSG[2:].split('\t')
				print "(" + IP + ":" + str(PORT) + ") - " + "KEY: " + key + "\tVALUE: " + value 

			else:
				print "Error: invalid message type."

			has_received = True

		except socket.timeout:
			return has_received


udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp.bind((consts["HOST"], consts["PORT"]))
CLIREQ = struct.pack('>H', msg_types['CLIREQ'])
HOST, PORT = sys.argv[1].split(":")
s_address = (HOST, int(PORT))
udp.settimeout(consts['stimeout'])

while True:
	key = raw_input("Enter the key you want to search for: ")
	MSG = CLIREQ + key.strip() + '\0'
	
	# First attempt
	if do_query(udp, MSG, s_address):
		continue

	# Retransmission 
	if not do_query(udp, MSG, s_address): 
		print "Key not found!"