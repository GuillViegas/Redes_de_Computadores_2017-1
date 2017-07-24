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

    QUADRO = SYNC+SYNC+CHECKSUM+LENGTH+ID+FLAG+MSG
    
    return QUADRO

def DesmontaCabec(CABEC):
    SYNC1, SYNC2, CHECK, LENGTH, ID, FLAG = struct.unpack('>IIHHBB', CABEC)

    if (SYNC1 == 0xDCC023C2 and
        SYNC2 == 0xDCC023C2):
        SYNC = True
    else: SYNC = False

    return FLAG, int(ID), int(LENGTH), SYNC, CHECK

    #I = 4 bytes = 32bits
    #H = 2 bytes = 16bits
    #B = 1 byte  = 8bits