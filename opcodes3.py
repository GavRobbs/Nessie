from opcode import *

BMIR8 = Opcode("BMI r8", 0x30, 2, (3, 2, 4), jump = True)
def BMIR8Func(cpu, args):
    if cpu.flags.getNegative():
        relative = args[0]
        newAddr = cpu.pc + relative
        if (cpu.pc // 256) != (newAddr // 256):
            cpu.pc = newAddr
            return 2
        else:
            cpu.pc = newAddr
            return 0
    else:
        cpu.pc += 2
        return 1
    pass
BMIR8.function = BMIR8Func

ANDIndY = Opcode("AND (a8), Y", 0x31, 2, (5, 6))
def ANDIndYFunc(cpu, args):
    initial_address = cpu.readWord(args[0])
    y_offset = cpu.y
    final_address = initial_address + y_offset
    fetched_value = cpu.readByte(final_address)
    value = clampResult(fetched_value & cpu.a)
    cpu.flags.checkNegative(value)
    cpu.flags.checkZero(value)
    cpu.a = value
    if (initial_address // 256) != (final_address // 256):
        return 1
    else:
        return 0
ANDIndY.function = ANDIndYFunc

ANDZPX = Opcode("AND a8, X", 0x35, 2, (4))
def ANDZPXFunc(cpu, args):
    address = (args[0] + cpu.x) & 0b11111111
    value = clampResult(cpu.readByte(address) & cpu.a)
    cpu.flags.checkNegative(value)
    cpu.flags.checkZero(value)
    cpu.a = value
    return 0
ANDZPX.function = ANDZPXFunc

ROLZPX = Opcode("ROL a8, X", 0x36, 2, (6))
def ROLZPXFunc(cpu, args):
    address = (args[0] + cpu.x) & 0b11111111
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
ROLZPX.function = ROLZPXFunc

SEC = Opcode("SEC", 0x38, 1, (2))
def SECFunc(cpu, args):
    cpu.flags.setCarry(1)
    return 0
SEC.function = SECFunc

ANDAbsoluteY = Opcode("AND a16, Y", 0x39, 3, (4,5))
def ANDAbsoluteYFunc(cpu, args):
    initial_address = (args[1] << 8) + args[0]
    final_address = initial_address + cpu.y
    value = clampResult(cpu.readByte(final_address) & cpu.a)
    cpu.a = value
    cpu.flags.checkNegative(value)
    cpu.flags.checkZero(value)
    if (initial_address // 256) != (final_address // 256):
        return 1
    else:
        return 0
ANDAbsoluteY.function = ANDAbsoluteYFunc

ANDAbsoluteX = Opcode("AND a16, X", 0x3D, 3, (4,5))
def ANDAbsoluteXFunc(cpu, args):
    initial_address = (args[1] << 8) + args[0]
    final_address = initial_address + cpu.x
    value = clampResult(cpu.readByte(final_address) & cpu.a)
    cpu.a = value
    cpu.flags.checkNegative(value)
    cpu.flags.checkZero(value)
    if (initial_address // 256) != (final_address // 256):
        return 1
    else:
        return 0
ANDAbsoluteX.function = ANDAbsoluteXFunc

ROLAbsoluteX = Opcode("ROL a16, X", 0x3E, 2, (6))
def ROLAbsoluteXFunc(cpu, args):
    initial_address = (args[1] << 8) + args[0]
    final_address = initial_address + cpu.x    
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
ROLAbsoluteX.function = ROLAbsoluteXFunc