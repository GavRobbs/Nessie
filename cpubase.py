class CPUBase:
    def __init__(self):
        self.RAM = [0] * 2048
        self.flags = None
        self.mapper = None
        self.pc = 0
        self.sp = 0x1FF
        self.a = 0
        self.x = 0
        self.y = 0

    def pushStack(self, value):
        self.RAM[self.sp] = value
        self.sp -= 1

    def popStack(self):
        self.sp += 1
        value = self.RAM[self.sp]
        self.RAM[self.sp] = 0
        return value

    def writeByte(self, location, value):
        pass

    def readByte(self, location):
        pass

    def readWord(self, location):
        pass

    def execute(self):
        pass


#The NES memory map is as follows:
#0x0000 - 0x7FF - 2kb internal ram
#0x7FF to 0x1FFF - mirror of the 2kb
#0x2000 to 0x2007 - NES PPU registers
#0x2008 to 0x3FFF - Mirrors of the PPU register
#0x4000 to 0x4017 - Input and APU
#0x4018 to 0x401F - CPU Test
#0x4020 to 0xFFFF - cartridge space and mapper registers
#The written byte needs to be checked and hijacked appropriately