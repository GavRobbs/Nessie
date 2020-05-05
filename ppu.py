from peripheral import *

class PPU(Peripheral):
    def __init__(self):
        Peripheral.__init__(self)
        self.romdata = []
        self.ramdata = []
    def writeByte(self, location, value):
        pass
    def readByte(self, location):
        pass
    def readWord(self, location):
        pass
    def writeWord(self, location):
        pass
    def populate(self, header, filedata):
        temp = list(filedata.read(header.CHRRomSize))
        self.romdata = [int(i) for i in temp]
    def dump(self):
        print("The CHR ROM is:")
        print(self.romdata)
        print("The CHR RAM is:")
        print(self.ramdata)