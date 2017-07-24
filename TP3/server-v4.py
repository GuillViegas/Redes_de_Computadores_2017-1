# -*- coding: utf-8 -*-
import socket 
import struct 
import sys
import select 

NUM_CLIENTS = 255

sockets = []

emissores = dict()
exibidores = dict()
emissores_exibidores = dict()

IDENTIFICADORES_EMISSORES = 1
IDENTIFICADORES_EXIBIDORES = 4096
IDENTIFICADOR_SERVIDOR = 65535

tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcp.bind(('', int(sys.argv[1])))

tcp.listen(NUM_CLIENTS)

sockets.append(tcp)

while True:
	try:
		inputready, outputready, exceptready = select.select(sockets, [], [])
	except select.error as e:
		break
	except socket.error as e:
		break
	for s in inputready:
		try:
			if s == tcp:
				con, address = tcp.accept()
				sockets.append(con)
                         
			else:
				data = s.recv(8)

				if len(data) == 0:
					sockets.remove(s)
					s.close()
					continue

				TIPO, ID_ORIG, ID_DEST, SNUM = struct.unpack('>HHHH', data)
				if TIPO == 3:
					if ID_ORIG != 0:
						if(IDENTIFICADORES_EMISSORES < 4096):
							if ID_ORIG >= 4096 and ID_ORIG < 8192:
								if exibidores.has_key(ID_ORIG):
									emissores_exibidores[IDENTIFICADORES_EMISSORES] = ID_ORIG
									emissores[IDENTIFICADORES_EMISSORES] = s
									s.send(struct.pack('>H', int(hex(1), 16)) + struct.pack('>H', int(hex(IDENTIFICADOR_SERVIDOR), 16)) + struct.pack('>H', int(hex(IDENTIFICADORES_EMISSORES), 16)) + struct.pack('>H', int(hex(SNUM), 16)))
									IDENTIFICADORES_EMISSORES += 1
								else:
									s.send(struct.pack('>H', int(hex(2), 16)) + struct.pack('>H', int(hex(IDENTIFICADOR_SERVIDOR), 16)) + struct.pack('>H', int(hex(ID_ORIG), 16)) + struct.pack('>H', int(hex(SNUM), 16)))
							else:
								emissores[IDENTIFICADORES_EMISSORES] = s
								s.send(struct.pack('>H', int(hex(1), 16)) + struct.pack('>H', int(hex(IDENTIFICADOR_SERVIDOR), 16)) + struct.pack('>H', int(hex(IDENTIFICADORES_EMISSORES), 16)) + struct.pack('>H', int(hex(SNUM), 16)))
								IDENTIFICADORES_EMISSORES += 1
						else:
							s.send(struct.pack('>H', int(hex(2), 16)) + struct.pack('>H', int(hex(IDENTIFICADOR_SERVIDOR), 16)) + struct.pack('>H', int(hex(ID_ORIG), 16)) + struct.pack('>H', int(hex(SNUM), 16)))
					else:
						if(IDENTIFICADORES_EXIBIDORES < 8192):
							exibidores[IDENTIFICADORES_EXIBIDORES] = s 
							s.send(struct.pack('>H', int(hex(1), 16)) + struct.pack('>H', int(hex(IDENTIFICADOR_SERVIDOR), 16)) + struct.pack('>H', int(hex(IDENTIFICADORES_EXIBIDORES), 16)) + struct.pack('>H', int(hex(SNUM), 16)))
							IDENTIFICADORES_EXIBIDORES += 1
						else:
							s.send(struct.pack('>H', int(hex(2), 16)) + struct.pack('>H', int(hex(IDENTIFICADOR_SERVIDOR), 16)) + struct.pack('>H', int(hex(ID_ORIG), 16)) + struct.pack('>H', int(hex(SNUM), 16)))
				elif TIPO == 5:
					data = s.recv(2)
					LENGTH = struct.unpack('>H', data)[0]
					MSG = s.recv(LENGTH)
					if ID_DEST == 0:
						if len(exibidores) != 0:
							s.send(struct.pack('>H', int(hex(1), 16)) + struct.pack('>H', int(hex(IDENTIFICADOR_SERVIDOR), 16)) + struct.pack('>H', int(hex(ID_ORIG), 16)) + struct.pack('>H', int(hex(SNUM), 16)))

							for ID_EXIBIDOR in exibidores:
								exibidores[ID_EXIBIDOR].send(struct.pack('>H', int(hex(5), 16)) + struct.pack('>H', int(hex(ID_ORIG), 16))  + struct.pack('>H', int(hex(ID_DEST), 16))  + struct.pack('>H', int(hex(SNUM), 16)) + struct.pack('>H', int(hex(LENGTH), 16)) + MSG)
						else:
							s.send(struct.pack('>H', int(hex(2), 16)) + struct.pack('>H', int(hex(IDENTIFICADOR_SERVIDOR), 16)) + struct.pack('>H', int(hex(ID_ORIG), 16)) + struct.pack('>H', int(hex(SNUM), 16)))

					elif ID_DEST > 0 and ID_DEST < 4096:
						if emissores.has_key(ID_DEST):
							if emissores_exibidores.has_key(ID_DEST):
								if exibidores.has_key(emissores_exibidores[ID_DEST]):
									s.send(struct.pack('>H', int(hex(1), 16)) + struct.pack('>H', int(hex(IDENTIFICADOR_SERVIDOR), 16)) + struct.pack('>H', int(hex(ID_ORIG), 16)) + struct.pack('>H', int(hex(SNUM), 16)))
									exibidores[emissores_exibidores[ID_DEST]].send(struct.pack('>H', int(hex(5), 16)) + struct.pack('>H', int(hex(ID_ORIG), 16))  + struct.pack('>H', int(hex(ID_DEST), 16))  + struct.pack('>H', int(hex(SNUM), 16)) + struct.pack('>H', int(hex(LENGTH), 16)) + MSG)
								else:
									s.send(struct.pack('>H', int(hex(2), 16)) + struct.pack('>H', int(hex(IDENTIFICADOR_SERVIDOR), 16)) + struct.pack('>H', int(hex(ID_ORIG), 16)) + struct.pack('>H', int(hex(SNUM), 16)))

							else:
								s.send(struct.pack('>H', int(hex(2), 16)) + struct.pack('>H', int(hex(IDENTIFICADOR_SERVIDOR), 16)) + struct.pack('>H', int(hex(ID_ORIG), 16)) + struct.pack('>H', int(hex(SNUM), 16)))
						else:
							s.send(struct.pack('>H', int(hex(2), 16)) + struct.pack('>H', int(hex(IDENTIFICADOR_SERVIDOR), 16)) + struct.pack('>H', int(hex(ID_ORIG), 16)) + struct.pack('>H', int(hex(SNUM), 16)))

					else:
						if exibidores.has_key(ID_DEST):
							s.send(struct.pack('>H', int(hex(1), 16)) + struct.pack('>H', int(hex(IDENTIFICADOR_SERVIDOR), 16)) + struct.pack('>H', int(hex(ID_ORIG), 16)) + struct.pack('>H', int(hex(SNUM), 16)))
							exibidores[ID_DEST].send(struct.pack('>H', int(hex(5), 16)) + struct.pack('>H', int(hex(ID_ORIG), 16))  + struct.pack('>H', int(hex(ID_DEST), 16))  + struct.pack('>H', int(hex(SNUM), 16)) + struct.pack('>H', int(hex(LENGTH), 16)) + MSG)
						else:
							s.send(struct.pack('>H', int(hex(2), 16)) + struct.pack('>H', int(hex(IDENTIFICADOR_SERVIDOR), 16)) + struct.pack('>H', int(hex(ID_ORIG), 16)) + struct.pack('>H', int(hex(SNUM), 16)))
				elif TIPO == 4:
					s.send(struct.pack('>H', int(hex(1), 16)) + struct.pack('>H', int(hex(IDENTIFICADOR_SERVIDOR), 16)) + struct.pack('>H', int(hex(ID_ORIG), 16)) + struct.pack('>H', int(hex(SNUM), 16)))
					sockets.remove(s)
					s.close()

					if ID_ORIG < 4096:
						del emissores[ID_ORIG]

						if emissores_exibidores.has_key(ID_ORIG):
							exibidores[emissores_exibidores[ID_ORIG]].send(struct.pack('>H', int(hex(4), 16)) + struct.pack('>H', int(hex(IDENTIFICADOR_SERVIDOR), 16)) + struct.pack('>H', int(hex(emissores_exibidores[ID_ORIG]), 16)) + struct.pack('>H', int(hex(SNUM), 16)))
							del exibidores[emissores_exibidores[ID_ORIG]]
							del emissores_exibidores[ID_ORIG]
					else:
						for exibidores in emissores_exibidores:
							if emissores_exibidores[exibidores] == ID_ORIG:
								del emissores_exibidores[exibidores]
						del exibidores[ID_ORIG]
				elif TIPO == 6:
					if ID_DEST == 0:
						if len(exibidores) != 0:
							s.send(struct.pack('>H', int(hex(1), 16)) + struct.pack('>H', int(hex(IDENTIFICADOR_SERVIDOR), 16)) + struct.pack('>H', int(hex(ID_ORIG), 16)) + struct.pack('>H', int(hex(SNUM), 16)))

							for ID_EXIBIDOR in exibidores:
								exibidores[ID_EXIBIDOR].send(struct.pack('>H', int(hex(7), 16)) + struct.pack('>H', int(hex(IDENTIFICADOR_SERVIDOR), 16))  + struct.pack('>H', int(hex(ID_DEST), 16))  + struct.pack('>H', int(hex(SNUM), 16)) + struct.pack('>H', int(hex(len(emissores) + len(exibidores)), 16)))
								for i in emissores:
									exibidores[ID_EXIBIDOR].send(struct.pack('>H', i))
								for j in exibidores:
									exibidores[ID_EXIBIDOR].send(struct.pack('>H', j))
						else:
							s.send(struct.pack('>H', int(hex(2), 16)) + struct.pack('>H', int(hex(IDENTIFICADOR_SERVIDOR), 16)) + struct.pack('>H', int(hex(ID_ORIG), 16)) + struct.pack('>H', int(hex(SNUM), 16)))
					elif ID_DEST < 0 and ID_DEST < 4096:
						if emissores_exibidores.has_key(ID_DEST):
							s.send(struct.pack('>H', int(hex(1), 16)) + struct.pack('>H', int(hex(IDENTIFICADOR_SERVIDOR), 16)) + struct.pack('>H', int(hex(ID_ORIG), 16)) + struct.pack('>H', int(hex(SNUM), 16)))
							exibidores[emissores_exibidores[ID_DEST]].send(struct.pack('>H', int(hex(7), 16)) + struct.pack('>H', int(hex(IDENTIFICADOR_SERVIDOR), 16))  + struct.pack('>H', int(hex(ID_DEST), 16))  + struct.pack('>H', int(hex(SNUM), 16)) + struct.pack('>H', int(hex(len(emissores) + len(exibidores)), 16)))
							for i in emissores:
								exibidores[ID_DEST].send(struct.pack('>H', i))
							for j in exibidores:
								exibidores[ID_DEST].send(struct.pack('>H', j))
						else:
							s.send(struct.pack('>H', int(hex(2), 16)) + struct.pack('>H', int(hex(IDENTIFICADOR_SERVIDOR), 16)) + struct.pack('>H', int(hex(ID_ORIG), 16)) + struct.pack('>H', int(hex(SNUM), 16)))
					elif ID_DEST >= 4096 and ID_DEST < 8192:
						if exibidores.has_key(ID_DEST):
							s.send(struct.pack('>H', int(hex(1), 16)) + struct.pack('>H', int(hex(IDENTIFICADOR_SERVIDOR), 16)) + struct.pack('>H', int(hex(ID_ORIG), 16)) + struct.pack('>H', int(hex(SNUM), 16)))
							exibidores[ID_DEST].send(struct.pack('>H', int(hex(7), 16)) + struct.pack('>H', int(hex(IDENTIFICADOR_SERVIDOR), 16))  + struct.pack('>H', int(hex(ID_DEST), 16))  + struct.pack('>H', int(hex(SNUM), 16)) + struct.pack('>H', int(hex(len(emissores) + len(exibidores)), 16)))
							for i in emissores:
								exibidores[ID_DEST].send(struct.pack('>H', i))
							for j in exibidores:
								exibidores[ID_DEST].send(struct.pack('>H', j))
						else:
							s.send(struct.pack('>H', int(hex(2), 16)) + struct.pack('>H', int(hex(IDENTIFICADOR_SERVIDOR), 16)) + struct.pack('>H', int(hex(ID_ORIG), 16)) + struct.pack('>H', int(hex(SNUM), 16)))
					else:
						s.send(struct.pack('>H', int(hex(2), 16)) + struct.pack('>H', int(hex(IDENTIFICADOR_SERVIDOR), 16)) + struct.pack('>H', int(hex(ID_ORIG), 16)) + struct.pack('>H', int(hex(SNUM), 16)))
				else:
					s.send(struct.pack('>H', int(hex(2), 16)) + struct.pack('>H', int(hex(IDENTIFICADOR_SERVIDOR), 16)) + struct.pack('>H', int(hex(ID_ORIG), 16)) + struct.pack('>H', int(hex(SNUM), 16)))
		except socket.error as e:
			break
