from cpubase import *
from flags import *

class LocationNotAvailableError(Exception):
    pass

class TestCPU(CPUBase):
    def __init__(self):
        CPUBase.__init__(self)
        self.flags = Flags()
    
    def writeByte(self, location, value):
        if location in range(0x0, 0x800):
            self.RAM[location] = value
        elif location in range(0x800, 0x2000):
            self.RAM[location % 0x800] = value
        else:
            raise LocationNotAvailableError

    def readByte(self, location):
        #The explanation works as above

        if location in range(0x0, 0x800):
            #Work memory
            return self.RAM[location]
        elif location in range(0x800, 0x2000):
            #Work memory mirror
            return self.RAM[location % 800]
        else:
            raise LocationNotAvailableError

    def readWord(self, location):
        #The explanation works as above

        if location in range(0x0, 0x800):
            #Work memory
            return (self.RAM[location + 1] << 8) + self.RAM[location]
        elif location in range(0x800, 0x2000):
            #Work memory mirror
            return (self.RAM[(location%800) + 1] << 8) + self.RAM[location%800]
        else:
            raise LocationNotAvailableError

    def execute(self):
        pass

    def printRegisters(self):
        print("A:", self.a)
        print("X:", self.x)
        print("Y:", self.y)
        print("SP:", self.sp)
        print("PC:", self.pc)

    def printStack(self):
        print("The values on the stack are:")
        print(self.RAM[0x100:0x200])

    def printFlags(self):
        print("Zero:", True if self.flags.getZero() == 1 else False)   
        print("Carry:", True if self.flags.getCarry() == 1 else False)
        print("Overflow:", True if self.flags.getOverflow() == 1 else False)
        print("Interrupt Disable:", True if self.flags.getInterruptDisable() == 1 else False)
        print("Negative", True if self.flags.getNegative() == 1 else False)

    def printMemorySlice(self, start, end):
        if start > 2048 or end > 2048:
            raise LocationNotAvailableError
        print("Looking at the values in work RAM from", start, "to", end)
        print(self.RAM[start:end])