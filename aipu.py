from peripheral import *

class AIPU(Peripheral):
    def __init__(self):
        Peripheral.__init__(self)
        self.data = []
    def writeByte(self, location, value):
        pass
    def readByte(self, location):
        pass
    def readWord(self, location):
        pass
    def writeWord(self, location):
        pass
    def populate(self, header, filedata):
        pass
    def dump(self):
        pass