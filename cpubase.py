from opcode import AddressMode, OpcodeFamily
from addressutils import *

class CPUBase:
    def __init__(self):
        self.RAM = [0] * 2048
        self.flags = None
        self.mapper = None
        self.pc = 0
        self.sp = 0x1FF
        self.a = 0
        self.x = 0
        self.y = 0

    def pushStack(self, value):
        self.RAM[self.sp] = value
        self.sp -= 1

    def popStack(self):
        self.sp += 1
        value = self.RAM[self.sp]
        self.RAM[self.sp] = 0
        return value

    def writeByte(self, location, value):
        pass

    def readByte(self, location):
        pass

    def readWord(self, location):
        pass

    def execute(self):
        pass

    def _clampResult(self, value):
    return value & 0xFF

    def OR(self, value):
        result = self.a | value
        self.flags.checkNegative(result)
        self.flags.checkZero(result)
        self.a = self._clampResult(result)

    def AND(self, value):
        result = self._clampResult(value & self.a)
        self.flags.checkNegative(result)
        self.flags.checkZero(result)
        self.a = value

    def ASL(self, value):
        topBit  = 1 if (0b10000000 & value) != 0 else 0
        value = self._clampResult(value << 1)
        self.flags.checkNegative(value)
        self.flags.checkZero(value)
        self.flags.setCarry(topBit)
        self.a = value

    def ROR(self, value):
        newCarry = value & 0x1
        oldCarry = self.flags.getCarry()
        value = value >> 1
        self.flags.setCarry(newCarry)
        if oldCarry == 0:
            value = value & 0b01111111
        else:
            value = (value | 0b10000000) & 0xFF
        self.flags.checkNegative(value)
        self.flags.checkZero(value)
        self.a = value

    def ROL(self, value):
        newCarry = 1 if (value & 0b10000000 > 0) else 0
        oldCarry = self.flags.getCarry()
        value = value << 1
        self.flags.setCarry(newCarry)
        if oldCarry == 0:
            value = value & 0b10000000
        else:
            value = (value | 0x1) if (value & 0x1 == 0) else value
        self.flags.checkNegative(value)
        self.flags.checkZero(value)
        self.a = value

    def EOR(self, value):
        self.a ^= value
        self.flags.checkNegative(self.a)
        self.flags.checkZero(self.a)

    def ADC(self, value):
        unsigned_total = self.a + value + self.flags.getCarry()

        signed_a = (self.a - 256) if a > 127 else self.a
        signed_val = (value - 256) if value > 127 else value

        signed_total = signed_a + signed_val + self.flags.getCarry()

        if unsigned_total > 255:
            self.flags.setCarry(1)
        else:
            self.flags.setCarry(0)

        if signed_total >= -128 and signed_total <= 127:
            self.setOverflow(0)
        else:
            self.setOverflow(1)

        self.a = unsigned_total & 0xFF
        self.flags.checkZero(self.a)
        self.flags.checkNegative(self.a)

    def SBC(self, value):
        self.ADC(~value)

    def INX(self):
        self.x = (self.x + 1) & 0xFF
        self.flags.checkZero(self.x)
        self.flags.checkNegative(self.x)

    def DEX(self):
        self.x = (self.x - 1) & 0xFF
        self.flags.checkZero(self.x)
        self.flags.checkNegative(self.x)

    def INY(self):
        self.y = (self.y + 1) & 0xFF
        self.flags.checkZero(self.y)
        self.flags.checkNegative(self.y)

    def DEY(self):
        self.y = (self.y + 1) & 0xFF
        self.flags.checkZero(self.y)
        self.flags.checkNegative(self.y)

    def INC(self, value):
        self.x = (self.x + value) & 0xFF
        self.flags.checkZero(self.x)
        self.flags.checkNegative(self.x)

    def DEC(self, value):
        self.a = (self.a - value) & 0xFF
        self.flags.checkZero(self.a)
        self.flags.checkNegative(self.a)

    def TAX(self):
        self.x = self.a
        self.flags.checkNegative(self.x)
        self.flags.checkZero(self.x)
        pass

    def TXA(self):
        self.a = self.x
        self.flags.checkNegative(self.a)
        self.flags.checkZero(self.a)
        pass

    def TAY(self):
        self.y = self.a
        self.flags.checkNegative(self.y)
        self.flags.checkZero(self.y)
        pass

    def TYA(self):
        self.a = self.y
        self.flags.checkNegative(self.a)
        self.flags.checkZero(self.a)
        pass

    def TSX(self):
        self.x = self.sp
        self.flags.checkNegative(self.x)
        self.flags.checkZero(self.x)

    def TXS(self):
        self.sp = self.x
        self.flags.checkNegative(self.sp)
        self.flags.checkZero(self.sp)

    def STore(self, location, value):
        self.writeByte(location, value)

    def LDA(self, value):
        self.a = value
        self.flags.checkNegative(self.a)
        self.flags.checkZero(self.a)

    def LDX(self, value):
        self.x = value
        self.flags.checkNegative(self.x)
        self.flags.checkZero(self.x)

    def LDY(self, value):
        self.y = value
        self.flags.checkNegative(self.y)
        self.flags.checkZero(self.y)

    def CoMPare(self, regval, value):
        result = regval - value
        if regval > value:
            self.flags.setCarry(1)
        else:
            self.flags.setCarry(0)
        self.flags.checkZero(result)
        self.flags.checkNegative(result)

    def _fetchAppropriateOpcodeData(self, address_mode):
        #This returns a tuple with the data requested
        #and if a page boundary was crossed
        value = 0
        page_crossed = False
        if address_mode == AddressMode.ACCUMULATOR:
            value = self.a
            page_crossed = False
        elif address_mode == AddressMode.ABSOLUTE:
            args = [self.readByte(self.pc + 1), self.readByte(self.pc + 2)]
            address = readAbsoluteAddress(self, args)
            value = self.readByte(address)
            page_crossed = False
        elif  address_mode == AddressMode.ABSOLUTE_INDEXED_X:
            args = [self.readByte(self.pc + 1), self.readByte(self.pc + 2)]
            address, page_crossed = readIAbsoluteIndexedAddressX(self, args)
            value = self.readByte(address)
        elif  address_mode == AddressMode.ABSOLUTE_INDEXED_Y:
            args = [self.readByte(self.pc + 1), self.readByte(self.pc + 2)]
            address, page_crossed = readIAbsoluteIndexedAddressY(self, args)
            value = self.readByte(address)
        elif address_mode == AddressMode.IMMEDIATE:
            value, page_crossed = self.readByte(self.pc + 1), False
        elif address_mode == AddressMode.RELATIVE:
            value, page_crossed = self.readByte(self.pc + 1), False
        elif address_mode == AddressMode.IMPLIED:
            value, page_crossed = 0, False
        elif address_mode == AddressMode.ZEROPAGE:
            address, page_crossed = self.readByte(self.pc + 1), False
            value = self.readByte(address)
        elif address_mode == AddressMode.ZEROPAGE_INDEXED:
            args = [self.readByte(self.pc + 1)]
            address, page_crossed = readZeroPageXAddress(self, args)
        elif address_mode == AddressMode.INDIRECT:
            #Only the JMP instruction uses this
            value, page_crossed = self.readWord(self.readWord(self.pc + 1)), False
        elif address_mode == AddressMode.INDEXED_INDIRECT:
            args = [self.readByte(self.pc + 1)]
            value, page_crossed = self.readByte(readIndexedIndirectAddress(self, args))
        elif address_mode == AddressMode.INDIRECT_INDEXED:
            args = [self.readByte(self.pc + 1)]
            value, page_crossed = self.readByte(readIndirectIndexedAddress(self, args))
        else:
            raise Exception("The specified address mode is not known or defined")

        return value, page_crossed

    def _executeOpcode(self, oc):
        #This function returns how much to advance the program counter by
        #And how long this operation took
        value, page_crossed = self._fetchAppropriateOpcodeData(oc.address_mode)
        counter_advance, duration = oc.length, oc.duration[0]
        if oc.family == OpcodeFamily.ADC:
            self.ADC(value)
        elif oc.family == OpcodeFamily.AND:
            self.AND(value)
        elif oc.family == OpcodeFamily.ASL:
            self.ASL(value)
        elif oc.family == OpcodeFamily.BCC:
            pass
        elif oc.family == OpcodeFamily.BCS:
            pass
        elif oc.family == OpcodeFamily.BEQ:
            pass
        elif oc.family == OpcodeFamily.BIT:
            pass
        elif oc.family == OpcodeFamily.BMI:
            pass
        elif oc.family == OpcodeFamily.BNE:
            pass
        elif oc.family == OpcodeFamily.BPL:
            pass
        elif oc.family == OpcodeFamily.BRK:
            pass
        elif oc.family == OpcodeFamily.BVC:
            pass
        elif oc.family == OpcodeFamily.BVS:
            pass
        elif oc.family == OpcodeFamily.CLC:
            self.flags.setCarry(0)
        elif oc.family == OpcodeFamily.CLD:
            #Doesn't do anything on the NES
            pass
        elif oc.family == OpcodeFamily.CLI:
            self.flags.setInterruptDisable(0)
        elif oc.family == OpcodeFamily.CLV:
            self.flags.setOverflow(0)
        elif oc.family == OpcodeFamily.CMP:
            self.CoMPare(self.a, value)
        elif oc.family == OpcodeFamily.CPX:
            self.CoMPare(self.x, value)
        elif oc.family == OpcodeFamily.CPY:
            self.CoMPare(self.y, value)
        elif oc.family == OpcodeFamily.DEC:
            self.DEC(value)
        elif oc.family == OpcodeFamily.DEX:
            self.DEX()
        elif oc.family == OpcodeFamily.DEY:
            self.DEY()
        elif oc.family == OpcodeFamily.EOR:
            self.EOR(value)
        elif oc.family == OpcodeFamily.INC:
            self.INC(value)
        elif oc.family == OpcodeFamily.INX:
            self.INX()
        elif oc.family == OpcodeFamily.INY:
            self.INY()
        elif oc.family == OpcodeFamily.JMP:
            pass
        elif oc.family == OpcodeFamily.JSR:
            pass
        elif oc.family == OpcodeFamily.LDA:
            self.LDA(value)
        elif oc.family == OpcodeFamily.LDX:
            self.LDX(value)
        elif oc.family == OpcodeFamily.LDY:
            self.LDY(value)
        elif oc.family == OpcodeFamily.LSR:
            pass
        elif oc.family == OpcodeFamily.NOP:
            pass
        elif oc.family == OpcodeFamily.ORA:
            self.OR(value)
        elif oc.family == OpcodeFamily.PHA:
            self.pushStack(self.a)
        elif oc.family == OpcodeFamily.PHP:
            self.pushStack(self.flags.getStatus())
        elif oc.family == OpcodeFamily.PLA:
            self.a = self.popStack()
            self.flags.checkNegative(self.a)
            self.flags.checkZero(self.a)
        elif oc.family == OpcodeFamily.PLP:
            temp = self.popStack()
            self.flags.setStatus(temp)
        elif oc.family == OpcodeFamily.ROL:
            self.ROL(value)
        elif oc.family == OpcodeFamily.ROR:
            self.ROR(value)
        elif oc.family == OpcodeFamily.RTI:
            pass
        elif oc.family == OpcodeFamily.RTS:
            pass
        elif oc.family == OpcodeFamily.SBC:
            self.SBC(value)
        elif oc.family == OpcodeFamily.SEC:
            self.flags.setCarry(1)
        elif oc.family == OpcodeFamily.SED:
            #Doesn't do anything on the NES
            pass
        elif oc.family == OpcodeFamily.SEI:
            self.flags.setInterruptDisable(1)
        elif oc.family == OpcodeFamily.STA:
            page_crossed = False #save us a lot of problems related to duration issues
            location = value
            self.STore(location, self.a)
        elif oc.family == OpcodeFamily.STX:
            page_crossed = False #save us a lot of problems related to duration issues
            location = value
            self.STore(location, self.x)
        elif oc.family == OpcodeFamily.STY:
            page_crossed = False #save us a lot of problems
            location = value
            self.STore(location, self.y)
        elif oc.family == OpcodeFamily.TAX
            self.TAX()
        elif oc.family == OpcodeFamily.TAY
            self.TAY()
        elif oc.family == OpcodeFamily.TSX
            self.TSX()
        elif oc.family == OpcodeFamily.TXA
            self.TXA()
        elif oc.family == OpcodeFamily.TXS
            self.TXS()
        elif oc.family == OpcodeFamily.TYA
            self.TYA()
        else:
            raise Exception("Unrecognized opcode, what are you doing?")

        if page_crossed == True:
            duration += 1
        
        return counter_advance, duration


#The NES memory map is as follows:
#0x0000 - 0x7FF - 2kb internal ram
#0x7FF to 0x1FFF - mirror of the 2kb
#0x2000 to 0x2007 - NES PPU registers
#0x2008 to 0x3FFF - Mirrors of the PPU register
#0x4000 to 0x4017 - Input and APU
#0x4018 to 0x401F - CPU Test
#0x4020 to 0xFFFF - cartridge space and mapper registers
#The written byte needs to be checked and hijacked appropriately