# -*- coding: utf-8 -*-
import socket 
import struct
import sys

consts = {
	'REQ_LEN' : 55,
	'HOST' : '127.0.0.1',
	'count': 0,
	'TTL_INIT': 3
}

msg_types = {
	'CLIREQ' : 1,
	'QUERY' : 2,
	'RESPONSE' : 3
}

# Loads a kv_table from a file
def load_dict_by_file (inpath):

	kv_table = dict() 

	with open(inpath) as f:
		for line in f.readlines():
			line = line.strip()
			
			# Skipping comment line
			if not line or (line[0] == '#'):
				continue

			# Reading key/value pair and store in dictionary kv_table
			line = line.split(' ', 1)
			if len(line) != 2:

				print "ERROR! Invalid input format!"
				continue
			
			key, value = line
			kv_table[key] = value.strip()

	return kv_table

# Loads the list of neighboring servents 
def load_neighborhood(neighbors):

	neighbors = [n.split(':') for n in neighbors]
	return [(p[0], int(p[1])) for p in neighbors]

#---------------------------- INITIALIZING SERVENT ----------------------------#
old_msg = dict()
inpath = sys.argv[2]
kv_table = load_dict_by_file(inpath)

neighbors = load_neighborhood(sys.argv[3:])

udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
HOST = consts['HOST']
PORT = int(sys.argv[1])
udp.bind((HOST, PORT))

count = consts['count']
old_queries = set()

while True:

	(MSG, ADDRESS) = udp.recvfrom(consts['REQ_LEN'])
	msg_type = struct.unpack_from('>H', MSG, 0)[0] 

	(ip_source, port_source) = ADDRESS
	print "Received a message from: " + ip_source + ":" + str(port_source)
	
	ip_source = struct.pack('>4s', socket.inet_aton(ip_source))
	port_source = struct.pack('>H', port_source)

	# Received a message from client
	if(msg_type == msg_types['CLIREQ']):

		MSG_SIGN = ADDRESS[0] + str(ADDRESS[1]) + str(count) + MSG[2:].strip().strip('\0')
		old_queries.add(MSG_SIGN)

		msg_type = struct.pack('>H', msg_types['QUERY'])
		TTL = struct.pack('>H', consts['TTL_INIT'])
		NSEQ = struct.pack('>L', count)
		count += 1
		key = MSG[2:].strip().strip('\0')
		MSG = msg_type + TTL + ip_source + port_source + NSEQ + key + '\0'

		# Send a message to all neighbors
		for neighbor in neighbors:
			udp.sendto(MSG, neighbor)

		# If the servent has the key, send a reponse to the client with key and value
		if kv_table.has_key(key):
			msg_type = struct.pack('>H', msg_types['RESPONSE'])
			MSG = msg_type + key + '\t' + kv_table[key] + '\0'
			udp.sendto(MSG, ADDRESS)

	# Received a message from servent
	elif(msg_type == msg_types['QUERY']):
		TTL = struct.unpack_from('>H', MSG, 2)[0]
		ip_source = struct.unpack_from('>4s', MSG, 4)[0]
		port_source = struct.unpack_from('>H', MSG, 8)[0]
		NSEQ = struct.unpack_from('>L', MSG, 10)[0]
		key = MSG[14:].strip().strip('\0')

		MSG_SIGN = socket.inet_ntoa(ip_source) + str(port_source) + str(NSEQ) + key

		# If message has already been received, do nothing.
		if MSG_SIGN in old_queries:
			continue
		
		old_queries.add(MSG_SIGN)

		if (TTL > 1):
			TTL = struct.pack('>H', TTL - 1)
			MSG = MSG[:2] + TTL + MSG[4:]

			for neighbor in neighbors:
				udp.sendto(MSG, neighbor)

		# If the servent has the key, send a reponse to the client with key and value
		if kv_table.has_key(key):
			msg_type = struct.pack('>H', msg_types['RESPONSE'])
			MSG = msg_type + key + '\t' + kv_table[key] + '\0'
			udp.sendto(MSG, (socket.inet_ntoa(ip_source), port_source))

	else:

		print "Error: invalid message type."
		pass
