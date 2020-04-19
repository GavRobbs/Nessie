from opcode import *

BRK = Opcode("BRK", 0x0, 2, (7))
def BRKFunc(cpu, args):
    #This should cause a NMI then return to PC+2 - needs some work
    return 0
BRK.function = BRKFunc

ORAIndirectX = Opcode("ORA (a8, X)", 0x1, 2, (6))
def ORAIXFunc(cpu, args):
    lookup_address = (args[0] + cpu.x) & 0b11111111
    value = cpu.readWord(lookup_address)
    result = cpu.a | value
    cpu.flags.checkNegative(result)
    cpu.flags.checkZero(result)
    cpu.a = clampResult(result)
    return 0
ORAIndirectX.function = ORAIXFunc

ORAZeroPage = Opcode("ORA a8", 0x5, 2, (3))
def ORAZPFunc(cpu, args):
    result = cpu.readByte(args[0]) | cpu.a
    cpu.flags.checkNegative(result)
    cpu.flags.checkZero(result)
    cpu.a = clampResult(result)
    return 0
ORAZeroPage.function = ORAZPFunc

ASLZP = Opcode("ASL a8", 0x6, 2, (5))
def ASLZPFunc(cpu, args):
    value = cpu.readByte(args[0])
    topBit  = 1 if (0b10000000 & value) != 0 else 0
    value = clampResult(value << 1)
    cpu.flags.checkNegative(value)
    cpu.flags.checkZero(value)
    cpu.flags.setCarry(topBit)
    cpu.a = value
    return 0
ASLZP.function = ASLZPFunc

PHP = Opcode("PHP", 0x8, 1, (3))
def PHPFunc(cpu, args):
    status = cpu.flags.getStatus()
    cpu.pushStack(status)
    return 0
PHP.function = PHPFunc

ORAImmediate = Opcode("ORA #d8", 0x9, 2, (2))
def ORAIMFunc(cpu, args):
    result = args[0] | cpu.a
    cpu.flags.checkNegative(result)
    cpu.flags.checkZero(result)
    cpu.a = clampResult(result)
    return 0
ORAImmediate.function = ORAIMFunc

ASLA = Opcode("ASL A", 0xA, 1, (2))
def ASLAFunc(cpu, args):
    topBit  = 1 if (0b10000000 & cpu.a) != 0 else 0
    cpu.a = clampResult(cpu.a << 1)
    cpu.flags.checkNegative(cpu.a)
    cpu.flags.checkZero(cpu.a)
    cpu.flags.setCarry(topBit)
    return 0
ASLA.function = ASLAFunc

ORAAbsolute = Opcode("ORA a16", 0xD, 3, (4))
def ORAAbsoluteFunc(cpu, args):
    address = (args[1] << 8) + args[0]
    value = clampResult(cpu.readByte(address) | cpu.a)
    cpu.flags.checkNegative(value)
    cpu.flags.checkZero(value)
    cpu.a = value
    return 0
ORAAbsolute.function = ORAAbsoluteFunc

ASLAbsolute = Opcode("ASL a16", 0xE, 3, (6))
def ASLAbsoluteFunc(cpu, args):
    address = (args[1] << 8) + args[0]
    value = cpu.readByte(address)
    topBit  = 1 if (0b10000000 & value) != 0 else 0
    value = clampResult(value << 1)
    cpu.flags.checkNegative(value)
    cpu.flags.checkZero(value)
    cpu.flags.setCarry(topBit)
    cpu.a = value
    return 0
ASLAbsolute.function = ASLAbsoluteFunc

