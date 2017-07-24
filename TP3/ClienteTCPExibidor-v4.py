# Cliente TCP - Emissor
# Recebe como parametro o identificador

import socket
import struct
import sys

#TipoMensagem: 2BYTES
#IdentificadorOrigem: 2BYTES
#IdentificadorDestino: 2BYTES
#NumeroSequencia: 2BYTES
def MontaMensagem(msg, numSeq, tipoMSG, idtOrigem, idtDestino):
  
    TipoMensagem = int(hex(tipoMSG), 16)
    TipoMensagem = struct.pack('>H', TipoMensagem)
    IdentificadorOrigem = int(hex(idtOrigem), 16) 
    IdentificadorOrigem = struct.pack('>H', IdentificadorOrigem)
    IdentificadorDestino = int(hex(idtDestino), 16) 
    IdentificadorDestino = struct.pack('>H', IdentificadorDestino)
    NumeroSequencia = int(hex(numSeq), 16) 
    NumeroSequencia = struct.pack('>H', NumeroSequencia)

    return TipoMensagem + IdentificadorOrigem + IdentificadorDestino + NumeroSequencia + msg

def EnviaMSGCabecalho(msg):
    tcp.send(msg)

def RecebePrimeiroOKouERRO():
    msg = tcp.recv(8) #O cabecalho possui 8 bytes
    tipoMensagem, identificadorOrigem, identificadorDestino, numeroSequencia = struct.unpack('>HHHH', msg)

    if (tipoMensagem == 1): return identificadorDestino
    else: return 0

def ExibeOrigem(idtOrg):
    print("O identificador de Origem deste Exibidor eh: "+ str(idtOrg))

def EnviaOI():
    msg = MontaMensagem('', 0, 3, 0, 65535) #destino eh o servidor
    EnviaMSGCabecalho(msg)
    idtOrg = RecebePrimeiroOKouERRO()
    if (idtOrg == 0): idtOrg = EnviaOI()
    else: ExibeOrigem(idtOrg)
    return idtOrg

def EnviaOK(numSeq, idtOrigem, idtDestino):
    OK = MontaMensagem('', numSeq, 1, idtOrigem, idtDestino)
    EnviaMSGCabecalho(OK)

def FechaConexao():
    tcp.close()
    
def RecebeFLW(numSeq, idtOrigem, idtDestino):
    EnviaOK(numSeq, idtDestino, idtOrigem)
    FechaConexao()

def DesmontaCabec(cabec):
  
    TipoMensagem, IdentificadorOrigem, IdentificadorDestino, NumeroSequencia = struct.unpack('>HHHH', cabec)
    
    return TipoMensagem, IdentificadorOrigem, IdentificadorDestino, NumeroSequencia

def ExibeMensagem(idtOrigem, msg):
    print("Mensagem de "+str(idtOrigem)+": "+msg)

def RecebeeMSGUsu(numSeq, idtOrigem, idtDestino):
    qtdChar = struct.unpack('>H', tcp.recv(2))
    qtdChar = qtdChar[0]
    print ("qtdCHAR = "+str(qtdChar))
    
    msg = tcp.recv(qtdChar)
    ExibeMensagem(idtOrigem, msg)
    
    EnviaOK(numSeq, idtDestino, idtOrigem)

def ExibeLista(listaCliente):
    print ("Cliente Conectados:")
    for client in listaCliente:
        print client 

def RecebeCLIST(numSeq, idtOrigem, idtDestino):
    listaCConnect = []
    qtdCConnect = int(struct.unpack('>H', tcp.recv(2))[0]) #Recebe o numero de clientes conectados
    
    i=0
    while (i < qtdCConnect):
        listaCConnect.append(int(struct.unpack('>H', tcp.recv(2))[0]))
        i += 1
             
    EnviaOK(numSeq, idtDestino, idtOrigem)
    ExibeLista(listaCConnect)
    
    
#------------------------- INICIO DO PROGRAMA -------------------------#

#Confere se os argumentos cliente-emissor estao sendo informados
if len(sys.argv)>=1:
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    IPPAS, PORT = sys.argv[1].split(':')
    dest = (IPPAS, int(PORT))
    tcp.connect(dest)

    idtOrg = EnviaOI()
    recebeMSG = True
    #loop
    while(recebeMSG):
        #recebo msg
        cabec = tcp.recv(8)
        TipoMensagem, idtOrigem, idtDestino, numSeq = DesmontaCabec(cabec)
        #eh msg
        if (TipoMensagem == 5):
            RecebeeMSGUsu(numSeq, idtOrigem, idtDestino)
        #eh FLW
        elif (TipoMensagem == 4):
            RecebeFLW(numSeq, idtOrigem, idtDestino)
            recebeMSG = False
        #eh CLIST
        elif (TipoMensagem == 7):
            RecebeCLIST(numSeq, idtOrigem, idtDestino)
            
        else: sys.stderr.write("Tipo de mensagem recebida esta fora do esperado")
else: sys.stderr.write("Erro ao executar cliente, argumento nao informado")
#----------------------------------------------------------------------#
