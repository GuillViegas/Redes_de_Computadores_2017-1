# -*- coding: utf-8 -*-

import socket
import struct
import sys
import time

#Monta o quadro em str
#000-031: SYNC
#032-063: SYNC
#064-079: CHECKSUM
#080-095: LENGTH
#096-103: ID
#104-111: FLAG
#112-112+LENGHT: DADOS
def MontaQuadro(MSG, last_id, flag):
    SYNC = 0xDCC023C2
    SYNC = struct.pack('>I', SYNC)

    CHECKSUM = struct.pack('>H', 0)

    LENGTH = int(hex(len(MSG)), 16)
    LENGTH = struct.pack('>H', LENGTH)

    if last_id == 0: ID = struct.pack('>B', 1)
    else: ID = struct.pack('>B', 0)
    
    if   flag == 'ACK': FLAG = struct.pack('>B', int('10000000', 2))
    elif flag == 'END': FLAG = struct.pack('>B', int('01000000', 2))
    else              : FLAG = struct.pack('>B', int('00111111', 2))

    CHECKSUM = checksum(SYNC+SYNC+CHECKSUM+LENGTH+ID+FLAG+MSG)
    CHECKSUM = struct.pack('>H', CHECKSUM)

    QUADRO = SYNC+SYNC+CHECKSUM+LENGTH+ID+FLAG+MSG
    
    return QUADRO

def DesmontaCabec(CABEC):  
    SYNC1, SYNC2, CHECKSUM, LENGTH, ID, FLAG = struct.unpack('>IIHHBB', CABEC)

    if (SYNC1 == 0xDCC023C2 and
        SYNC2 == 0xDCC023C2):
        SYNC = 0xDCC023C2
    else: SYNC = False

    return FLAG, ID, LENGTH, SYNC, CHECKSUM

def ProximoQuadroDados(INPUT, last_id):
    MSG = INPUT.read(100)
    #Se a linha lida não tem dado (ou seja, arquivo vazio)
    if len(MSG) < 100:
        if (len(MSG)%2) != 0: MSG = MSG + " "
        QUADRO = MontaQuadro(MSG, last_id, 'END')
        END = True
        INPUT.close()
    else:
        QUADRO = MontaQuadro(MSG, last_id, '---')
        END = False
    return QUADRO, END

def EnviaQuadro(QUADRO):
    if sys.argv[1] == '-s': con.send(QUADRO)
    else: tcp.send(QUADRO)

def RecebeQuadro(tamanho):
    try:
        TIMEOUT = False
        if sys.argv[1] == '-s': 
            con.settimeout(1.0)
            QUADRO = con.recv(tamanho)
            con.settimeout(None)
        else:
            tcp.settimeout(1.0)
            QUADRO = tcp.recv(tamanho)
            tcp.settimeout(None)
    except socket.timeout:
        TIMEOUT = True
        QUADRO = None

    return TIMEOUT, QUADRO

def carry_around_add(a, b):
    c = a + b
    return(c &0xffff)+(c >>16)

def checksum(msg):
    s =0
    for i in range(0, len(msg),2):
        w = ord(msg[i])+(ord(msg[i+1])<<8)
        s = carry_around_add(s, w)
    return~s &0xffff

def VerificaChecksum(SYNC1, SYNC2, CHECKSUM, LENGTH, ID, FLAG, MSG):
    
    if CHECKSUM == checksum(struct.pack('>IIHHBB%dc' % len(MSG), SYNC1, SYNC2, 0, LENGTH, ID, FLAG, *MSG)): CHECK = True
    else: CHECK = False

    return CHECK

#---------------------------- INICIO DO PROGRAMA ----------------------------#

#Confere se os argumentos cliente/servidor estao sendo informados
if len(sys.argv)>=5:

    #Inicia a conexao
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if sys.argv[1] == '-s' or sys.argv[1] == '-c':

        # -*- SERVIDOR -*-
        if sys.argv[1] == '-s':
            HOST = ''

            if int(sys.argv[2]) >= 51000 and int(sys.argv[2]) <= 55000:
            	PORT = sys.argv[2]
            else:
            	print >> sys.stderr, 'Numero de porto invalido!'
            	sys.exit()

            orig = (HOST, int(PORT))
            tcp.bind(orig)
            tcp.listen(1)
            con, cliente = tcp.accept()
                
        # -*- CLIENTE -*-
        else:
            if (int(sys.argv[2].split(':')[1]) >= 51000) and (int(sys.argv[2].split(':')[1]) <= 55000):
            	IPPAS, PORT = sys.argv[2].split(':')
            else:
            	print >> sys.stderr, 'Numero de porto invalido!'
            	sys.exit()

            dest = (IPPAS, int(PORT))
            tcp.connect(dest)
	

        #Variáveis de controle para o fim da transmissão
        end_receber_dados = False
        end_receber_ack = False
        
        #Ultimos ids recebidos = 1 pois o primeiro eh sempre 0
        last_ack_id = 1
        last_data_id = 1
        last_checksum = 0
        

        #flag de controle que indica que o proximo ACK e o ultimo
        flag_controle = False
        
        #Envio do primeiro pacote do INPUT
        #Abre o arquivo 
        INPUT = open(sys.argv[3], 'r')
        #Li os primeiros caracteres do arquivo
        QUADRO, END = ProximoQuadroDados(INPUT, 1)
        EnviaQuadro(QUADRO)

        #Gravo último ACK e pacote enviado
        last_packet_sent = QUADRO
        last_ACK_sent = None
        last_is_packet = True
            
        #Se o primeiro quadro for o ultimo quadro de dados eu recebo o ultimo ACK e paro de enviar dados
        if END: flag_controle = True
   
        #Abre o arquivo de saida
        OUTPUT = open(sys.argv[4], 'w')

        #Enquanto eu nao tiver recebido todos os dados ou enquanto eu noo tiver recebido todos os ACKS
        while (not end_receber_dados or not end_receber_ack):

            #Recebo o cabecalho 112 bits = 14 bytes
            TIMEOUT, CABEC = RecebeQuadro(14)

            if TIMEOUT:
                if last_is_packet:
                    EnviaQuadro(last_packet_sent)
                else:
                    EnviaQuadro(last_ACK_sent)
        
            else:
                FLAG, ID, LENGTH, SYNC, CHECKSUM = DesmontaCabec(CABEC)
                
                #Verifica se o inicio do pacote esta correto'
                if SYNC == 0xDCC023C2:
                
                    #Se nao e flag de END'
                    if FLAG != int('01000000', 2):
                        
                        #Se eh quadro de ACK'
                        if FLAG == int('10000000', 2):

                            #Verifica CHECKSUM'
                            if VerificaChecksum(SYNC, SYNC, CHECKSUM, LENGTH, ID, FLAG, ''): 

                                #Se ACK ID é diferente do ID do último pacote recebido'
                                if ID != last_data_id:
                                    
                                    #Se esse for o ultimo ACK a receber'
                                    if flag_controle:
                                        end_receber_ack = True                          
                                    
            
                                        #Se a recepcao de dados tambem ja acabou'
                                        if end_receber_dados:                                            
                                            tcp.close()
            
                                    #Se nao eh o ultimo ACK'
                                    else:
                                        #Envio o proximo quadro de dados
                                        QUADRO, END = ProximoQuadroDados(INPUT, ID)
                                        last_packet_sent = QUADRO
                                        last_is_packet = True
                                        EnviaQuadro(QUADRO)                                        
            
                                        #Se esse eh o ultimo quadro de dados avisa que ACK que vai ser o ultimo
                                        if END: flag_controle = True
            
                                    #Inverte o ID do ACK
                                    last_ack_id = ID

                                #Se AKC ID diferente, AKC recebido não é do último pacote enviado
                                else:
                                    EnviaQuadro(last_packet_sent)

                                
                        #Se eh quadro de DADOS
                        else:
                            TIMEOUT, MSG = RecebeQuadro(LENGTH)

                            if TIMEOUT:
                                EnviaQuadro(last_ACK_sent)

                            else:
                                #Verifica CHECKSUM
                                if VerificaChecksum(SYNC, SYNC, CHECKSUM, LENGTH, ID, FLAG, MSG): 
            
                                    #Se eh um quadro de dados repetido
                                    if ID == last_data_id and CHECKSUM == last_checksum:
                                        
                                        #Envio ACK de confirmação
                                        QUADRO = MontaQuadro('', last_data_id, 'ACK')
                                        last_ACK_sent = QUADRO
                                        last_is_packet = False
                                        EnviaQuadro(QUADRO)                                    
                
                                    #Se eh um novo quadro de dados
                                    else:
                                        
                                        #Recebo os dados e gravo                            
                                        OUTPUT.write(MSG)
                                       
                                        #Envio quadro de confirmação
                                        QUADRO = MontaQuadro('', last_data_id, 'ACK')
                                        last_ACK_sent = QUADRO
                                        last_is_packet = False
                                        EnviaQuadro(QUADRO)                                    
                
                                        #inverto o ID de dados e o ultimo checksum
                                        last_data_id = ID
                                        last_checksum = CHECKSUM
        
                    #Se eu recebi um flag de END
                    else:
        
                        #Se o quadro tem DADOS
                        if LENGTH > 0:
                            TIMEOUT, MSG = RecebeQuadro(LENGTH)

                            if TIMEOUT:
                                EnviaQuadro(last_ACK_sent)
                                
                            else:
                                #Verifica CHECKSUM
                                if VerificaChecksum(SYNC, SYNC, CHECKSUM, LENGTH, ID, FLAG, MSG): 

                                    #Se o quadro eh repetido
                                    if ID == last_data_id and CHECKSUM == last_checksum:
                                        
                                        #Envia ultimo ACK de confirmação
                                        QUADRO = MontaQuadro('', last_data_id, 'ACK')
                                        last_ACK_sent = QUADRO
                                        last_is_packet = False
                                        EnviaQuadro(QUADRO)

                                        end_receber_dado = True
                                        if end_receber_ack:                                            
                                            tcp.close()

                                        
                                    #Se eh um novo quadro de dados
                                    else:
                
                                        #Recebo os dados e gravo                            
                                        OUTPUT.write(MSG)
                                        #Fecho o arquivo, pq acabou os dados
                                        OUTPUT.close()
                                        
                                        #Envia ultimo quadro de confirmação
                                        QUADRO = MontaQuadro('', last_data_id, 'ACK')
                                        last_ACK_sent = QUADRO
                                        last_is_packet = False
                                        EnviaQuadro(QUADRO)

                                        end_receber_dados = True
                                        
                                        if end_receber_ack:
                                            tcp.close()

                                        #inverto o ID de dados e o ultimo checksum
                                        last_data_id = ID
                                        last_checksum = CHECKSUM
                                
                        #Se não tem DADO
                        else:
                            
                            #Verifica CHECKSUM
                            if VerificaChecksum(SYNC, SYNC, CHECKSUM, LENGTH, ID, FLAG, ''): 

                                #Envia ultimo quadro de confirmação
                                QUADRO = MontaQuadro('', last_data_id, 'ACK')
                                last_ACK_sent = QUADRO
                                last_is_packet = False
                                EnviaQuadro(QUADRO)

                                end_receber_dados = True
                                
                                if end_receber_ack:
                                    tcp.close()

                #Se o inicio do pacote esta errado
                else:
                    print >> sys.stderr, 'Inicio do pacote apresenta erro'
              
    # -*- ARGUMENTO INVÁLIDO -*-
    else:
	   print >> sys.stderr, 'Entrada invalida!'
else:
    print >> sys.stderr, 'Parametro nao informado'


