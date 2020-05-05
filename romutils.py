#We intend to be able to read NES 2.0 rom data, but for the purposes of emulation,
#we only want to play NES 1.0 roms

class ROMHeader:
    def __init__(self):
        self.NESConst = ""
        self.PRGRomSize = 0
        self.CHRRomSize = 0
        self.CHRRamSize = 0
        self.mirrorMode = ""
        self.hasSaveMem = False
        self.hasTrainer = False
        self.mapperNumber = 0
        self.subMapperNumber = 0
        self.NESVersion = 0
        self.consoleType = ""
        self.PRGRamSize = 0
        self.tvSystem = ""
        self.hasBusConflict = False
        self.PRGNVRamSize = 0
        self.PRGVRamSize = 0
        self.CHRNVRamSize = 0
        self.CHRVRamSize = 0
        self.timingMode = ""


def loadROM(filename, get_file_handle=False):
    myrom = open(filename, "rb")
    header = None
    try:
        header = _processHeader(myrom)
    except Exception as error:
        print(error)
    finally:
        if get_file_handle == False:
            myrom.close()
            return header
        else:
            return (header, myrom)

def printHeader(header):
    print("NES Header:", header.NESConst)
    print("NES Version:", header.NESVersion)

    print("PRG ROM Size:", header.PRGRomSize, "bytes")
    if header.NESVersion == "NES2.0":
        print("PRG NVRAM Size:", header.PRGNVRamSize, "kb")
        print("PRG VRAM Size:", header.PRGVRamSize, "kb")
    else:
        print("PRG RAM Size:", header.PRGRamSize, "bytes")

    print("CHR ROM Size:", header.CHRRomSize, "bytes")
    if header.NESVersion == "NES2.0":
        print("CHR NVRAM Size:", header.CHRNVRamSize, "kb")
        print("CHR VRAM Size:", header.CHRVRamSize, "kb")
    else:
        print("CHR RAM Size:", header.CHRRamSize, "bytes")

    print("Mirroring Mode:", header.mirrorMode)

    if header.hasSaveMem == True:
        print("Cartridge has save memory.")
    else:
        print("Cartridge does not have memory for saves.")

    if header.hasTrainer == True:
        print("Cartridge has trainer.")
    else:
        print("Cartridge does not have a trainer.")

    print("Console type:", header.consoleType)
    print("Mapper number:", header.mapperNumber)
    print("TV System:", header.tvSystem)

    if header.NESVersion == "NES2.0":
        print("Timing Mode", header.timingMode)
        
def _processHeader(romfile):
    romfile.seek(0, 0)
    head = ROMHeader()
    header_str = romfile.read(16)
    head.NESConst = header_str[0:4]
    head.PRGRomSize = header_str[4] * 16384
    
    if header_str[6] & 0x08 != 0:
        head.mirrorMode = "FOUR SCREEN"
    else:
        if header_str[6] & 0x1 == 0:
            head.mirrorMode = "HORIZONTAL"
        else:
            head.mirrorMode = "VERTICAL"

    head.hasSaveMem = True if header_str[6] & 0x2 != 0 else False
    head.hasTrainer = True if header_str[6] & 0x4 != 0 else False

    if header_str[7] & 0x0C == 0x08:
        head.NESVersion = "NES2.0"

        if header_str[5] == 0:
            head.CHRRomSize = 0
        else:
            head.CHRRomSize = header_str[5] * 8192

        consoleVal = header_str[7] & 0x3
        if consoleVal == 0:
            head.consoleType = "NES"
        elif consoleVal == 1:
            head.consoleType = "UNISYSTEM"
        elif consoleVal == 2:
            head.consoleType = "PLAYCHOICE 10"
        else:
            head.consoleType = "EXTENDED"

        head.mapperNumber = ((header_str[6] & 0b11110000) >> 4) + (header_str[7] & 0b11110000) + ((header_str[8] & 0b00001111) << 8)
        head.subMapperNumber = (header_str[8] & 0b11110000) >> 4

        PRGLSB = header_str[4]
        PRGMSB = header_str[9] & 0b00001111

        if PRGMSB == 15:
            multiplier = PRGLSB & 0x3
            exponent = (PRGLSB & 0b11111100) >> 2
            head.PRGRomSize = 2 * exponent + (multipler * 2 + 1)
        else:
            head.PRGRomSize = ((PRGMSB << 8) + PRGLSB) * 16

        CHRLSB = header_str[5]
        CHRMSB = (header_str[9] & 0b11110000) >> 4

        if CHRMSB == 15:
            multiplier = CHRLSB & 0x3
            exponent = (CHRLSB & 0b11111100) >> 2
            head.CHRRomSize = 2 * exponent + (multipler * 2 + 1)
        else:
            head.CHRRomSize = ((CHRMSB << 8) + CHRLSB) * 8

        PRGVRAMCNT = header_str[10] & 0b00001111
        PRGNVRAMCNT = (header_str[10] & 0b11110000) >> 4

        if PRGVRAMCNT == 0:
            head.PRGVRamSize = 0
        else:
            head.PRGVRamSize = 64 << PRGVRAMCNT
        
        if PRGNVRAMCNT == 0:
            head.PRGNVRamSize = 0
        else:
            head.PRGNVRamSize = 64 << PRGNVRAMCNT

        CHRVRAMCNT = header_str[11] & 0b00001111
        CHRNVRAMCNT = (header_str[11] & 0b11110000) >> 4

        if CHRVRAMCNT == 0:
            head.CHRVRamSize = 0
        else:
            head.CHRVRamSize = 64 << CHRVRAMCNT
        
        if CHRNVRAMCNT == 0:
            head.CHRNVRamSize = 0
        else:
            head.CHRNVRamSize = 64 << CHRNVRAMCNT

        tmode = header_str[12] & 0x03
        if tmode == 0:
            head.timingMode = "RP2C02"
        elif tmode == 1:
            head.timingMode = "RP2C07"
        elif tmode == 2:
            head.timingMode = "MR"
        else:
            head.timingMode = "UMC6527P"

    elif header_str[7] & 0x0C == 0 and header_str[12:16] == b'\x00\x00\x00\x00':

        head.NESVersion = "NES1.0"

        if header_str[5] == 0:
            head.CHRRomSize = 0
            head.CHRRamSize = 8192
        else:
            head.CHRRomSize = header_str[5] * 8192

        if header_str[7] == 0:
            head.mapperNumber = (header_str[6] & 0b11110000) >> 4
            head.consoleType = "NES"
        else:
            head.consoleType = "UNISYSTEM" if header_str[7] & 0x1 == 1 else "NES"
            head.mapperNumber = (header_str[7] & 0b11110000) + ((header_str[6] & 0b11110000) >> 4)

        head.PRGRamSize = header_str[8] * 8192 if header_str[8] != 0 else 8192

        if header_str[9] == 0:
            head.tvSystem = "UNSPECIFIED or NTSC"
        else:
            head.tvSystem = "PAL"
    else:
        head.NESVersion = "Archaic iNES"

    return head

if __name__ == '__main__':
    import sys
    romHeader = loadROM(sys.argv[1])
    printHeader(romHeader)