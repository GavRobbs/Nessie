from opcode import *

STAA8X = Opcode("STA (a8, X)", 0x81, 2, (6))
def STAA8XFunc(cpu, args):
    address = (args[0] + cpu.x) & 0b11111111
    cpu.writeByte(address, cpu.a)
    return 0
STAA8X.function = STAA8XFunc

STYA8 = Opcode("STY a8", 0x84, 2, (3))
def STYA8Func(cpu, args):
    address = args[0]
    cpu.writeByte(address, cpu.y)
    return 0
STYA8.function = STYA8Func

STAA8 = Opcode("STA a8", 0x85, 2, (3))
def STAA8Func(cpu, args):
    address = args[0]
    cpu.writeByte(address, cpu.a)
    return 0
STAA8.function = STAA8Func

STXA8 = Opcode("STX a8", 0x86, 2, (3))
def STXA8Func(cpu, args):
    address = args[0]
    cpu.writeByte(address, cpu.x)
    return 0
STXA8.function = STXA8Func

DEY = Opcode("DEY", 0x88, 1, (2))
def DEYFunc(cpu, args):
    cpu.y = (cpu.y - 1) & 0b11111111
    cpu.flags.checkZero(cpu.y)
    cpu.flags.checkNegative(cpu.y)
    return 0
DEY.function = DEYFunc

TXA = Opcode("TXA", 0x8A, 1, (2))
def TXAFunc(cpu, args):
    cpu.a = cpu.x
    cpu.flags.checkZero(cpu.a)
    cpu.flags.checkNegative(cpu.a)
    return 0
TXA.function = TXAFunc

STYA16 = Opcode("STY a16", 0x8C, 3, (4))
def STYA16Func(cpu, args):
    address = (args[1] << 8) + args[0]
    cpu.writeByte(address, cpu.y)
    return 0
STYA16.function = STYA16Func

STAA16 = Opcode("STA a16", 0x8D, 3, (4))
def STAA16Func(cpu, args):
    address = (args[1] << 8) + args[0]
    cpu.writeByte(address, cpu.a)
    return 0
STAA16.function = STAA16Func

STXA16 = Opcode("STX a16", 0x8E, 3, (4))
def STXA16Func(cpu, args):
    address = (args[1] << 8) + args[0]
    cpu.writeByte(address, cpu.x)
    return 0
STXA16.function = STXA16Func