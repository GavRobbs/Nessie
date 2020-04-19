import romutils
import opcodes0
import opcodes1
from cpubase import *

class CPU(CPUBase):
    def __init__(self):
        self.RAM = [0] * 2048
        self.ROMData = None
        self.PPU = None
        self.APUAndInputManager = None
        self.flags = None
        self.mapper = None
        self.pc = 0
        self.sp = 0
        self.opcodeList = {0 : opcodes0.code_dict, 1 : opcodes1.code_dict}

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
        #This reads code at the program counter location
        #It then looks up the appropriate opcode
        #It checks the length of the command, then subtracts 1 for the code itself
        #It then populates the params dictionary by reading length - 1 subsequent bytes
        #It passes this to the handler function where the relevant processing is done
        #The handler function returns an index to the duration tuple which
        #shows how long it actually took to process the function

        #The important thing is that the program counter is modified here
        #and not in the client functions, to avoid confusion - but I may
        #have to hack this a bit when it comes to the JMP functions.

        #IMPORTANT - I also need to add in code to check when the 256 byte page
        #boundary is crossed, for jumps and indexed addressing - may end up delegating to client
        code = self.readByte(pc)
        (code_high, code_low) = ((code & 0b11110000) >> 4, code & 0b00001111)
        params = {}
        for i in range(0, self.opcodeList[code_high][code_low].length - 1):
            params.update({i: self.readByte(pc + 1 + i)})
        result = self.opcodeList[code_high][code_low].function(params)

        #Write some conditional code that stops this if jump is set
        self.pc += self.opcodeList[code_high][code_low].length
        return self.opcodeList[code_high][code_low].duration[result]


#The NES memory map is as follows:
#0x0000 - 0x7FF - 2kb internal ram
#0x7FF to 0x1FFF - mirror of the 2kb
#0x2000 to 0x2007 - NES PPU registers
#0x2008 to 0x3FFF - Mirrors of the PPU register
#0x4000 to 0x4017 - Input and APU
#0x4018 to 0x401F - CPU Test
#0x4020 to 0xFFFF - cartridge space and mapper registers
#The written byte needs to be checked and hijacked appropriately