from opcode import *

BPL = Opcode("BPL r8", 0x10, 2, (3, 2, 4), jump = True)
def BPLFunc(cpu, args):
    relative = args[0]
    if cpu.flags.getNegative == 1:
        cpu.pc += 2
        return 1 #branch not taken, so 2 cycles
    else:
        newAddr = cpu.pc + relative
        if (cpu.pc // 256) != (newAddr // 256):
            #This means that the jump instruction has brought us to a different page
            cpu.pc = newAddr
            return 2
        else:
            cpu.pc = newAddr
            return 0
BPL.function = BPLFunc

ORAIndY = Opcode("ORA (a8), Y", 0x11, 2, (5, 6))
def ORAIndYFunc(cpu, args):
    #Indirect Indexed OR - just painful
    initial_address = cpu.readWord(args[0])
    y_offset = cpu.y
    final_address = initial_address + y_offset
    fetched_value = cpu.readByte(final_address)
    value = clampResult(fetched_value | cpu.a)
    cpu.flags.checkNegative(value)
    cpu.flags.checkZero(value)
    cpu.a = value
    if (initial_address // 256) != (final_address // 256):
        return 1
    else:
        return 0
ORAIndY.function = ORAIndYFunc

ORAZPX = Opcode("ORA a8, X", 0x15, 2, (4))
def ORAZPXFunc(cpu, args):
    #Zero page X
    address = (args[0] + cpu.x) & 0b11111111
    value = clampResult(cpu.readByte(address) | cpu.a)
    cpu.flags.checkNegative(value)
    cpu.flags.checkZero(value)
    cpu.a = value
    return 0
ORAZPX.function = ORAZPXFunc

ASLZPX = Opcode("ASL a8, X", 0x16, 2, (6))
def ASLZPXFunc(cpu, args):
    address = (args[0] + cpu.x) & 0b11111111
    value = cpu.readByte(address)
    topBit  = 1 if (0b10000000 & value) != 0 else 0
    value = clampResult(value << 1)
    cpu.flags.checkNegative(value)
    cpu.flags.checkZero(value)
    cpu.flags.setCarry(topBit)
    cpu.a = value
    return 0
ASLZPX.function = ASLZPXFunc

CLC = Opcode("CLC", 0x18, 1, (2))
def CLCFunc(cpu, args):
    cpu.flags.setCarry(0)
    return 0
CLC.function = CLCFunc

ORAAbsoluteY = Opcode("ORA a16, Y", 0x19, 3, (4, 5))
def ORAAbsoluteYFunc(cpu, args):
    initial_address = (args[1] << 8) + args[0]
    final_address = initial_address + cpu.y
    value = clampResult(cpu.readByte(final_address) | cpu.a)
    cpu.a = value
    cpu.flags.checkNegative(value)
    cpu.flags.checkZero(value)
    if (initial_address // 256) != (final_address // 256):
        return 1
    else:
        return 0
ORAAbsoluteY.function = ORAAbsoluteYFunc

ORAAbsoluteX = Opcode("ORA a16, X", 0x1D, 3, (4, 5))
def ORAAbsoluteXFunc(cpu, args):
    initial_address = (args[1] << 8) + args[0]
    final_address = initial_address + cpu.x
    value = clampResult(cpu.readByte(final_address) | cpu.a)
    cpu.a = value
    cpu.flags.checkNegative(value)
    cpu.flags.checkZero(value)
    if (initial_address // 256) != (final_address // 256):
        return 1
    else:
        return 0
ORAAbsoluteX.function = ORAAbsoluteXFunc

ASLAbsoluteX = Opcode("ASL a16, X", 0x1E, 3, (7))
def ASLAbsoluteXFunc(cpu, args):
    initial_address = (args[1] << 8) + args[0]
    final_address = initial_address + cpu.x
    value = cpu.readByte(final_address)
    topBit  = 1 if (0b10000000 & value) != 0 else 0
    value = clampResult(value << 1)
    cpu.flags.checkNegative(value)
    cpu.flags.checkZero(value)
    cpu.flags.setCarry(topBit)
    cpu.a = value
    return 0
ASLAbsoluteX.function = ASLAbsoluteXFunc
