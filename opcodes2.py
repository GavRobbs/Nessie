from opcode import *

JSRAbsolute = Opcode("JSR a16", 0x20, 3, (6), jump = True)
def JSRFunc(cpu, args):
    pcLowByte = cpu.pc & 0x00FF
    pcHighByte = (cpu.pc & 0xFF00) >> 8
    cpu.pushStack(pcLowByte)
    cpu.pushStack(pcHighByte)
    address = (args[1] << 8) + args[0]
    cpu.pc = address
    return 0 
JSRAbsolute.function = JSRFunc

ANDIndX = Opcode("AND (a8, X)", 0x21, 2, (6))
def ANDIndXFunc(cpu, args):
    address = cpu.readWord((args[0] + cpu.x) & 0b11111111)
    value = clampResult(cpu.readByte(address) & cpu.a)
    cpu.flags.checkNegative(value)
    cpu.flags.checkZero(value)
    cpu.a = value
    return 0
ANDIndX.function = ANDIndXFunc

BITZP = Opcode("BIT a8", 0x24, 2, (3))
def BITZPFunc(cpu, args):
    value = cpu.readByte(args(0)) & cpu.a
    cpu.flags.checkZero(value)
    cpu.flags.setNegative(1 if value & 0b10000000 != 0 else 0)
    cpu.flags.setOverflow(1 if value & 0b01000000 != 0 else 0)
    return 0
BITZP.function = BITZPFunc

ANDZP = Opcode("AND a8", 0x25, 2, (3))
def ANDZPFunc(cpu, args):
    value = clampResult(cpu.readByte(args[0]) & cpu.a)
    cpu.flags.checkNegative(value)
    cpu.flags.checkZero(value)
    cpu.a = value
    return 0
ANDZP.function = ANDZPFunc

ROLZP = Opcode("ROL a8", 0x26, 2, (5))
def ROLZPFunc(cpu, args):
    value = cpu.readByte(args[0])
    oldcarry = cpu.flags.getCarry()
    newcarry = (0b10000000 & value) >> 7
    cpu.a = value << 1
    cpu.flags.setCarry(newcarry)
    if cpu.a << 7 == 0 and oldcarry == 1:
        cpu.a |= 0b1
    elif cpu.a << 7 != 0 and oldcarry == 0:
        cpu.a &= 0b11111110
    else:
        #The only two cases that matter were covered above
        pass
    cpu.flags.checkNegative(cpu.a)
    cpu.flags.checkZero(cpu.a)
    return 0
ROLZP.function = ROLZPFunc

PLP = Opcode("PLP", 0x28, 1, (4))
def PLPFunc(cpu, args):
    value = cpu.popStack()
    cpu.flags.setStatus(value)
    return 0
PLP.function = PLPFunc

ANDImmediate = Opcode("AND #d8", 0x29, 2, (2))
def ANDImmediateFunc(cpu, args):
    value = clampResult(args[0] & cpu.a)
    cpu.flags.checkNegative(value)
    cpu.flags.checkZero(value)
    cpu.a = value
    return 0
ANDImmediate.function = ANDImmediateFunc

ROLA = Opcode("ROL A", 0x2A, 1, (2))
def ROLAFunc(cpu, args):
    value = cpu.a
    oldcarry = cpu.flags.getCarry()
    newcarry = (0b10000000 & value) >> 7
    cpu.a = value << 1
    cpu.flags.setCarry(newcarry)
    if cpu.a << 7 == 0 and oldcarry == 1:
        cpu.a |= 0b1
    elif cpu.a << 7 != 0 and oldcarry == 0:
        cpu.a &= 0b11111110
    else:
        #The only two cases that matter were covered above
        pass
    cpu.flags.checkNegative(cpu.a)
    cpu.flags.checkZero(cpu.a)
    return 0
ROLA.function = ROLAFunc

BITAbsolute = Opcode("BIT a16", 0x2C, 3, (4))
def BITAbsoluteFunc(cpu, args):
    address = (args[1] << 8) + args[0]
    value = cpu.readByte(address) & cpu.a
    cpu.flags.checkZero(value)
    cpu.flags.setNegative(1 if value & 0b10000000 != 0 else 0)
    cpu.flags.setOverflow(1 if value & 0b01000000 != 0 else 0)
    return 0
BITAbsolute.function = BITAbsoluteFunc

ANDAbsolute = Opcode("AND a16", 0x2D, 3, (4))
def ANDAbsoluteFunc(cpu, args):
    address = (args[1] << 8) + args[0] 
    value = clampResult(cpu.readByte(address) & cpu.a)
    cpu.flags.checkNegative(value)
    cpu.flags.checkZero(value)
    cpu.a = value
    return 0
ANDAbsolute.function = ANDAbsoluteFunc

ROLAbsolute = Opcode("ROL a16", 0x2E, 3, (6))
def ROLAbsoluteFunc(cpu, args):
    address = (args[1] << 8) + args[0] 
    value = cpu.readByte(address)
    oldcarry = cpu.flags.getCarry()
    newcarry = (0b10000000 & value) >> 7
    cpu.a = value << 1
    cpu.flags.setCarry(newcarry)
    if cpu.a << 7 == 0 and oldcarry == 1:
        cpu.a |= 0b1
    elif cpu.a << 7 != 0 and oldcarry == 0:
        cpu.a &= 0b11111110
    else:
        #The only two cases that matter were covered above
        pass
    cpu.flags.checkNegative(cpu.a)
    cpu.flags.checkZero(cpu.a)
    return 0
ROLAbsolute.function = ROLAbsoluteFunc




