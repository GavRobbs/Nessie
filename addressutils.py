def readAbsoluteAddress(cpu, args):
    return (args[1] << 8) | args[0]
#The following 3 functions all do the same thing
#but I kept them different for semantics

def readZeroPageAddress(cpu, args):
    return args[0]

def readRelativeAddress(cpu, args):
    return args[0]

def readImmediateAddress(cpu, args):
    return args[0]

def readIndirectAddress(cpu, args):
    #This is only used by the JMP command, but kept here for clarity
    src = readAbsoluteAddress(cpu, args)
    return cpu.readWord(src)

def readIAbsoluteIndexedAddressX(cpu, args):
    #If a page boundary is crossed, the instruction takes one extra cycle
    #The opcode itself is at pc+0
    #The low byte of the absolute address is at pc+1
    #The high byte of the absolute address is at pc+2
    #What this means is that if pc + 1 at pc + 2 are on 2 different pages
    #Then pc+1 // 256 != pc+2 // 256
    init_address = readAbsoluteAddress(cpu, args) 
    final_address = init_address + cpu.x
    if (final_address & 0xFF00) != (init_address & 0xFF00):
        return (final_address, True) #Page boundary crossed
    else:
        return (final_address, False) #Page boundary not crossed

def readZeroPageXAddress(cpu, args):
    src = (cpu.readByte(args[0]) + cpu.x) & 0xFF
    return src, False

def readIAbsoluteIndexedAddressY(cpu, args):
    #If a page boundary is crossed, the instruction takes one extra cycle
    init_address = readAbsoluteAddress(cpu, args) 
    final_address = init_address + cpu.y
    if (final_address & 0xFF00) != (init_address & 0xFF00):
        return (final_address, True) #Page boundary crossed
    else:
        return (final_address, False) #Page boundary not crossed

def readIZeroPageIndexedAddressX(cpu, args):
    src = readZeroPageAddress(cpu, args)
    return 0xFF & (src + cpu.x)

def readIZeroPageIndexedAddressY(cpu, args):
    src = readZeroPageAddress(cpu, args)
    return 0xFF & (src + cpu.y)

def readIndexedIndirectAddress(cpu, args):
    initial = cpu.x + cpu.readByte(args[0])
    final = initial & 0xFF
    return cpu.readWord(final)

def readIndirectIndexedAddress(cpu, args):
    #If a page boundary is crossed, the instruction takes one extra cycle
    first_address = cpu.readWord(args[0])
    final_address = first_address + cpu.y

    if (first_address & 0xFF00) != (final_address & 0xFF00):
        return (final_address, True) #Page boundary crossed
    else:
        return (final_address, False) #Page boundary not crossed