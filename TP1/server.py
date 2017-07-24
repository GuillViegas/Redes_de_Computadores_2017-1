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

count = 0
tmp = count
aux = ''

while True: 

	# -- estabelecida uma nova conexão com um cliente

	con, cliente = tcp.accept()
	
	# -- servidor recebe 1 byte do cliente com a indicação do que fazer: 
	#    '+' incrementar contador global (count)
	#    '-' decrementar contador global 
	#     Qualquer outro argumento mantém o contador global

	con.settimeout(5.0)
	arg = con.recv(1)
	con.settimeout(None)
	
	if arg == '+':            
		if count < 999:     # se argumento recebido é '+' e count menor do que 999, valor de count deve ser incrementado.
			tmp += 1       
		else:               # se argumento recebido é '+' e count igual a 999, valor de count deve retornar a 0.
			tmp = 0         

	elif arg == '-':
		if count > 0:       # se argumento recebido é '-' e count maior do que 0, valor de count deve ser decrementado. 
			tmp -= 1
		else:               # se argumento recebido é '-' e count igual a 0, valor de count deve ir para 999.
			tmp = 999

	# se argumento recebido é diferente de '+' ou '-'. valor de count deve se manter igual. 

	else: 
		sys.stderr.write('Argumento enviado pelo cliente é inválido!\n')
	

	# --- Envia mensagem para cliente com o próximo valor do contador global.
	#     É utlizada uma váriavel de apoio 'tmp' para isso. 
	#     Somente após receber a confirmação pelo cliente que o contador é atualizado.

	con.send(struct.pack('>I', tmp))

	# -- Recebe 3 bytes de confirmação pelo cliente do contador global.
	#    Cada caractere possui 1 byte, servidor recebe 3 caracteres. 
	#    Os caracteres são concatenados e formam a string aux. 

	for i in range(0, 3):
		con.settimeout(5.0)
		aux += con.recv(1)
		con.settimeout(None)

	# -- Caso a mensagem seja confirmada, ou seja, caso a mensagem recebida esteja de acordo com o valor
	#    do contador global incrementado, decrementado ou igual, o valor do mesmo é atualizado (count = int(aux)).
	#    Caso contrário, uma mensagem de erro é exibida informando sobre a falha na confirmação.

	if arg == '+':
		if count < 999:
			if int(aux) == count + 1:
				count = int(aux)
			else:
				sys.stderr.write('Falha na confirmação! - Mensagem recebida do cliente não confere com mensagem enviado.\n')
		else:
			if int(aux) == 0:
				count = int(aux)
			else:
				sys.stderr.write('Falha na confirmação! - Mensagem recebida do cliente não confere com mensagem enviado.\n')
	elif arg == '-':
		if count > 0:
			if int(aux) == count - 1:
				count = int(aux)
			else:
				sys.stderr.write('Falha na confirmação! - Mensagem recebida do cliente não confere com mensagem enviado.\n')
		else:
			if int(aux) == 999:
				count = int(aux)
			else:
				sys.stderr.write('Falha na confirmação! - Mensagem recebida do cliente não confere com mensagem enviado.\n')
	else:
		if int(aux) == count:
			count = int(aux)
		else:
			sys.stderr.write('Falha na confirmação! - Mensagem recebida do cliente não confere com mensagem enviado.\n')

	print count

	# -- tmp e aux são atualizadas para seu valor default.

	tmp = count
	aux = ''

	# -- conexão com o cliente é finalizada 

	con.close()
