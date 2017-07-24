import sys
import struct

def carry_around_add(a, b):
    c = a + b
    return(c &0xffff)+(c >>16)

def checksum(msg):
    s =0
    for i in range(0, len(msg),2):
        w = ord(msg[i])+(ord(msg[i+1])<<8)
        s = carry_around_add(s, w)
    return~s &0xffff

SYNC = struct.pack('>I', 0xDCC023C2)
#SYNC = struct.unpack('>I', SYNC)
#print SYNC[0] == 0xDCC023C2

CHECKSUM = struct.pack('>H', 0)

LENGTH = struct.pack('>H', int(hex(65535), 16))
#LENGTH = struct.unpack('>H', LENGTH)
#print LENGTH[0] == 65535

ID = struct.pack('>B', 1)
#ID = struct.unpack('>B', ID)
#print ID[0] == 1

FLAG = struct.pack('>B', int('10000000', 2))
#FLAG = struct.unpack('>B', FLAG)
#print FLAG[0] == int('10000000', 2)

QUADRO = SYNC+SYNC+CHECKSUM+LENGTH+ID+FLAG

CHECKSUM = checksum(SYNC+SYNC+CHECKSUM+LENGTH+ID+FLAG)
CHECKSUM = struct.pack('>H', CHECKSUM)
QUADRO = SYNC+SYNC+CHECKSUM+LENGTH+ID+FLAG

SYNC1, SYNC2, CHECKSUM, LENGTH, ID, FLAG = struct.unpack('>IIHHBB',QUADRO)

if CHECKSUM == checksum(struct.pack('>IIHHBB', SYNC1, SYNC2, 0, LENGTH, ID, FLAG)): CHECK = True
else: CHECK = False

print 'Check SYNC'
print SYNC2 == 0xDCC023C2
print 'Check CHECKSUM'
print CHECK
print 'Check LENGTH'
print LENGTH == 65535
print 'Check ID'
print ID == 1
print 'Check FLAG'
print FLAG == int('10000000', 2)
