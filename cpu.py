import romutils
import opcodes
import datetime
from cpubase import *

class NESCPU(CPUBase):
    #This is the CPU base plus the memory mapped peripherals
    def __init__(self):
        self.RAM = [0] * 2048
        self.cycleSpeed = 1770000 #NTSC and 1790000 for PAL, to be configurable
        self.microsPerCycle = (1/cycleSpeed) * 1000000
        self.cycleDeltaSum = 0
        self.ROMData = None
        self.PPU = None
        self.LIDC = 0 #Last instruction duration in cycles
        self.APUAndInputManager = None
        self.flags = None
        self.mapper = None
        self.pc = 0
        self.sp = 0

    def loadROM(self, filename):
        #This loads the ROM via its filename,
        #sets the initial state of the processor
        #populates the data and sets the appropriate mapper

        (self.ROMData, romfile) = romutils.loadROM(filename, True)

        if self.ROMData.NESVersion == "NES2.0":
            raise Exception("NES2.0 ROMs are not yet supported.")

        romfile.seek(0,0)
        if (self.ROMData.hasTrainer):
            #Skip the trainer
            romfile.seek(528)
        else:
            romfile.seek(512)

        for i in range(0, self.ROMData.PRGRomSize, 16384):
            romfile.seek(i, 1) #Relative seek
            mapper.data[i % 16384] = list(romfile.read(16384))
            #Remember that lists are mutable and strings are not

        for i in range(0, self.ROMData.CHRRomSize, 8192):
            #I should consider putting this data in the PPU instead
            romfile.seek(i, 1)
            mapper.data[i % 16384] = list(romfile.read(16384))

        romfile.close()
        pass

    def pushStack(self, value):
        pass

    def popStack(self):
        pass

    def writeByte(self, location, value):
        #This writebyte function is important
        #because we don't want to access memory directly
        #since the NES has memory mapping, we may want specific effects when reading or
        #writing data. If the location is less than 0x4020, the specific location is
        #delegated - whether APU, PPU, work memory etc - above 0x4020, the mapper
        #handles 

        #Remember that the Python range function is inclusive of the first,
        #but exclusive of the last value

        if location in range(0x0, 0x800):
            #Work memory
            self.RAM[location] = value
        elif location in range(0x800, 0x2000):
            #Work memory mirror
            self.RAM[location % 0x800] = value
        elif location in range(0x2000, 0x2008):
            #PPU memory map
            self.PPU.write(location, value)
        elif location in range(0x2008, 0x4000):
            #PPU memory map mirror
            self.PPU.write(0x2000 + (location % 8), value)
        elif location in range(0x4000, 0x4018):
            #Input and APU
            self.APUAndInputManager.write(location, value)
        elif location in range(0x4018, 0x4020):
            #The test location, unsure of what to do here
            pass
        else:
            #This means it's definitely referring to the memory map
            self.mapper.write(location, value)

    def readByte(self, location):
        #The explanation works as above

        if location in range(0x0, 0x800):
            #Work memory
            return self.RAM[location]
        elif location in range(0x800, 0x2000):
            #Work memory mirror
            return self.RAM[location % 800]
        elif location in range(0x2000, 0x2008):
            #PPU memory map
            return self.PPU.read(location)
        elif location in range(0x2008, 0x4000):
            #PPU memory map mirror
            return self.PPU.read(0x2000 + (location % 8))
        elif location in range(0x4000, 0x4018):
            #Input and APU
            return self.APUAndInputManager.read(location)
        elif location in range(0x4018, 0x4020):
            #The test location, unsure of what to do here
            pass
        else:
            #This means it's definitely referring to the memory map
            self.mapper.readByte(location)

    def readWord(self, location):
        #The explanation works as above

        if location in range(0x0, 0x800):
            #Work memory
            return (self.RAM[location+1] << 8) + self.RAM[location]
        elif location in range(0x800, 0x2000):
            #Work memory mirror
            return (self.RAM[(location % 800)+1] << 8) + self.RAM[location % 800]
        elif location in range(0x2000, 0x2008):
            #PPU memory map
            return self.PPU.readWord(location)
        elif location in range(0x2008, 0x4000):
            #PPU memory map mirror
            return self.PPU.readWord(0x2000 + (location % 8))
        elif location in range(0x4000, 0x4018):
            #Input and APU
            return self.APUAndInputManager.readWord(location)
        elif location in range(0x4018, 0x4020):
            #The test location, unsure of what to do here
            pass
        else:
            #This means it's definitely referring to the memory map
            self.mapper.readWord(location)

    def execute(self):
        #This command fetches and runs the current opcode based off where the program
        #counter is, increments the program counter accordingly, then returns the
        #duration of the command that was just executed in cycles
        currentOp = opcodes.code_dict[mycpu.RAM[mycpu.pc]]
        advance, duration = self._executeOpcode(currentOp)
        self.pc += advance
        return duration        

    def run(self):
        #This is the simplest event loop possible ignoring input and interrupts
        #It gets the starting time initially, then gets a time for every iteration
        #of the loop. The difference between those is the delta. The duration of the
        #last instruction executed (in cycles) is stored. If the delta time between two
        #iterations of the loop is more than or equal to the length of the last instruction
        #the last instruction should have taken, then you can move on, otherwise wait
        start = datetime.now()
        while True:
            newtime = datetime.now()
            delta_us = newtime - start()
            if delta_us >= (self.LIDC * self.microsPerCycle):
                start = newtime
                LIDC = self.execute()
            else:
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