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
    
def EnviaOK(numSeq, idtOrigem, idtDestino):
    OK = MontaMensagem('', numSeq, 1, idtOrigem, idtDestino)
    EnviaMSGCabecalho(OK)

def FechaConexao():
    #tcp.close()
    pass
    
def RecebePrimeiroOKouERRO():
    msg = tcp.recv(8) #O cabecalho possui 8 bytes
    tipoMensagem, identificadorOrigem, identificadorDestino, numeroSequencia = struct.unpack('>HHHH', msg)
    if (tipoMensagem == 1): return identificadorDestino
    else: return 0
    
def RecebeUltimoOK():
    msg = tcp.recv(8) #O cabecalho possui 8 bytes
    tipoMensagem, identificadorOrigem, identificadorDestino, numeroSequencia = struct.unpack('>HHHH', msg)

    if (tipoMensagem == 1): return True
    else: return False

def RecebeOKouERRO():
    msg = tcp.recv(8) #O cabecalho possui 8 bytes
    tipoMensagem, identificadorOrigem, identificadorDestino, numeroSequencia = struct.unpack('>HHHH', msg)

    if (tipoMensagem == 1): print ('Mensagem enviada com sucesso')
    else: print ('Erro ao encontrar o exibidor de destino')

def RecebeOK():
    msg = tcp.recv(8) #O cabecalho possui 8 bytes
    tipoMensagem, identificadorOrigem, identificadorDestino, numeroSequencia = struct.unpack('>HHHH', msg)

    if (tipoMensagem == 1): print ('CREQ enviado com sucesso')
    else: print ('Erro ao enviar CREQ')

def ExibeOrigem(idtOrg):
    print("O identificador de Origem deste Emissor eh: "+ str(idtOrg))

def EnviaOI(idtExibidor):
    if (idtExibidor == 0): idtExibidor = 1 #Se eu nao recebi um exibidor para associar envio 1
    
    msg = MontaMensagem('', 0, 3, idtExibidor, 65535) #destino eh o servidor
    EnviaMSGCabecalho(msg)
    idtOrg = RecebePrimeiroOKouERRO()
    if (idtOrg == 0): idtOrg = EnviaOI(1)
    else: ExibeOrigem(idtOrg)
    return idtOrg
    
def EnviaFLW(numSeq, idtOrg):
    msg = MontaMensagem('', numSeq, 4, idtOrg, 65535) #destino eh o servidor
    EnviaMSGCabecalho(msg)
    FIM = RecebeUltimoOK()
    if (FIM): FechaConexao()
    else: EnviaFLW(numSeq, idtOrg)

def EnviaMSGUsu(msg, numSeq, idtOrg, idtDst):
    tamMSG = int(hex(len(msg)), 16)
    tamMSG = struct.pack('>H', tamMSG)
    newMSG = tamMSG + msg
    msg = MontaMensagem(newMSG, numSeq, 5, idtOrg, idtDst)
    EnviaMSGCabecalho(msg)
    RecebeOKouERRO()
    

def EnviaCREQ(numSeq, idtOrg, idtDst): #destino recebe lista de clientes
    msg = MontaMensagem('', numSeq, 6, idtOrg, idtDst)
    EnviaMSGCabecalho(msg)
    RecebeOK()    
    
#------------------------- INICIO DO PROGRAMA -------------------------#

#Confere se os argumentos cliente-emissor estao sendo informados
print("o tamanho da lista de argumentos eh: "+str(len(sys.argv)))
i = 0
if (len(sys.argv)>=2):
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    IPPAS, PORT = sys.argv[1].split(':')
    dest = (IPPAS, int(PORT))
    tcp.connect(dest)
    if (len(sys.argv)>=3): idtExibidor = int(sys.argv[2])
    else: idtExibidor = 0
    #EnviaOI(idtExibidor)
    idtOrg = EnviaOI(idtExibidor)
    enviaMSG = True
    numSeq = 0
    #loop
    while(enviaMSG):
        #ExibeDestino(s)
        #EnviaCREQ(numSeq, idtOrg, idtOrg) #Envio a solicitacao para receber a lista de clientes conectados
        #listaCliente = RecebeCLIST(numSeq, idtOrigem, idtDestino)
        #ExibeLista(listaCliente)
        #Deseja enviar mensagem para um unico destino?
        answer = 'J'
        while(answer != 'S' and answer != 'N'):
            answer = raw_input('Deseja enviar mensagem para um unico destino? (S)im ou (N)ao: ')
            if (answer != 'S' and answer != 'N'):
                sys.stderr.write("Resposta incorreta, responda com S ou N")

        #UNICAST
        if(answer == 'S'):
            destino = int(raw_input("Digite o destino: "))
            msg = raw_input("Digite a mensagem ou CRER(para lista de clientes conectados ao servidor): ")
            if msg == "CREQ":
                EnviaCREQ(numSeq, idtOrg, destino)
            else:
                EnviaMSGUsu(msg, numSeq, idtOrg, destino)

        #BROADCAST
        else:
            msg = raw_input("Digite a mensagem ou CREQ(para lista de clientes conectados ao servidor): ")
            if msg == "CREQ":
                EnviaCREQ(numSeq, idtOrg, 0)
            else:
                EnviaMSGUsu(msg, numSeq, idtOrg, 0)

        #Deseja enviar nova mensagem?
        answer = 'J'
        while(answer != 'S' and answer != 'N'):
            answer = raw_input('Deseja enviar nova mensagem? (S)im ou (N)ao: ')
            if (answer != 'S' and answer != 'N'):
                sys.stderr.write("Resposta incorreta, responda com S ou N")

        if(answer == 'N'):
            EnviaFLW(numSeq, idtOrg)
            enviaMSG = False
        numSeq = numSeq + 1
else: sys.stderr.write("Erro ao executar cliente, argumento nao informado")
#----------------------------------------------------------------------#
