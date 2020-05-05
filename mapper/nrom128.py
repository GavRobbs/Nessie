from mapper import mapper

class NROM128Mapper(mapper.Mapper):
    def __init__(self):
        mapper.Mapper.__init__(self)
        self.romdata = []

    def __translateMirroredAddress__(self, address):
        return (address - 0x4000 if address >= 0xC000 else address)

    def readByte(self, location):
        return self.romdata[self.__translateMirroredAddress__(location)]

    def writeByte(self, location, value):
        self.romdata[self.__translateMirroredAddress__(location)] = value

    def readWord(self, location):
        highbyte = self.romdata[self.__translateMirroredAddress__(location + 1)]
        lobyte  = self.romdata[self.__translateMirroredAddress__(location)]
        return (highbyte << 8) | lobyte

    def writeWord(self, location, value):
        self.romdata[self.__translateMirroredAddress__(location)] = value & 0xFF
        self.romdata[self.__translateMirroredAddress__(location + 1)] = value & 0xFF00

    def populate(self, header, filedata):
        temp = list(filedata.read(header.PRGRomSize))
        self.romdata = [int(i) for i in temp]

    def dump(self):
        print("The PRG ROM data is:")
        print(self.romdata)