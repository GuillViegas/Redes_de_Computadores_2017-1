import sys
import struct

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

SYNC1, SYNC2, CHECKSUM, LENGTH, ID, FLAG = struct.unpack('>IIHHBB',QUADRO)

print 'Check SYNC'
print SYNC2 == 0xDCC023C2
print 'Check CHECKSUM'
print CHECKSUM == 0
print 'Check LENGTH'
print LENGTH == 65535
print 'Check ID'
print ID == 1
print 'Check FLAG'
print FLAG == int('10000000', 2)