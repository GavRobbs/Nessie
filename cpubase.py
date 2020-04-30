from opcode import AddressMode, OpcodeFamily
import flags
from addressutils import *

class CPUBase:
    def __init__(self):
        self.RAM = [0] * 2048
        self.flags = None
        self.LIDC = 0 #Last instruction duration in cycles
        self.pc = 0
        self.sp = 0x1FF
        self.a = 0
        self.x = 0
        self.y = 0
        self.pendingRST = False
        self.pendingNMI = False
        self.pendingIRQ = False
        self.pendingBRK = False

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

    def execute(self, delta):
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
        self.y = (self.y - 1) & 0xFF
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

    def LSR(self, value):
        self.flags.setCarry(value & 0x1)
        self.a = value >> 1
        self.flags.checkNegative(self.a)
        self.flags.checkCarry(self.a)
        self.flags.checkZero(self.a)

    def BPL(self, value):
        #Branch if N = 0
        #The program counter is incremented by 2 during instruction execution
        if self.flags.getNegative() == 0:
            self.pc += value
            return True
        else:
            return False

    def BMI(self, value):
        if self.flags.getNegative() == 1:
            self.pc += value
            return True
        else:
            return False

    def BCC(self, value):
        if self.flags.getCarry() == 0:
            self.pc += value
            return True
        else:
            return False

    def BCS(self, value):
        if self.flags.getCarry() == 1:
            self.pc += value
            return True
        else:
            return False

    def BVC(self, value):
        if self.flags.getOverflow() == 0:
            self.pc += value
            return True
        else:
            return False

    def BVS(self, value):
        if self.flags.getOverflow() == 1:
            self.pc += value
            return True
        else:
            return False

    def BNE(self, value):
        if self.flags.getZero() == 0:
            self.pc += value
            return True
        else:
            return False

    def BEQ(self, value):
        if self.flags.getZero() == 1:
            self.pc += value
            return True
        else:
            return False

    def BIT(self, value):
        self.flags.checkZero(value & self.a)
        self.flags.setNegative((value & 0b10000000) >> 7)
        self.flags.setOverflow((value & 0b01000000) >> 6)

    def JMP(self, value):
        self.pc = value

    def JSR(self, value):
        nextOpvalue = self.pc + 2 #Next operation, which is pc+3 minus 1 = pc+2
        self.pushStack(nextOpvalue & 0xFF00) #push the high byte first
        self.pushStack(nextOpvalue & 0x00FF) #push the low byte next
        self.pc = value

    def RTS(self):
        lowByte = self.popStack()
        highByte = self.popStack()
        totalWord = ((highByte << 8) | lowByte) + 1
        self.pc  = totalWord

    def RTI(self):
        status = self.popStack()
        self.flags.setStatus(status)
        lowByte = self.popStack()
        highByte = self.popStack()
        totalWord = ((highByte << 8) | lowByte)
        self.pc = totalWord

    def BRK(self):
        self.pendingBRK = False
        self.pc += 2 #So that the return address from RTI is the next instruction
        self.pushStack(self.pc & 0xFF00)
        self.pushStack(self.pc & 0x00FF)
        status = self.flags.getStatus(flags.BreakHandler.PHPBRK)
        self.pc = self.readWord(0xFFFE)

    def RESET(self):
        #The whole system has been reset, so all interrupts can be cancelled
        self.pendingRST = False
        self.pendingIRQ = False
        self.pendingBRK = False
        self.pendingNMI = False
        self.sp = 0
        self.flags.setInterruptDisable(1)
        self.pc = self.readWord(0xFFFC)

    def NMI(self):
        self.pendingNMI = False
        self.pushStack(self.pc & 0xFF00)
        self.pushStack(self.pc & 0x00FF)
        status = self.flags.getStatus(flags.BreakHandler.IRQNMI)
        self.pc = self.readWord(0xFFFA)
        self.flags.setInterruptDisable(1)

    def IRQ(self):
        self.pendingIRQ = False
        self.pushStack(self.pc & 0xFF00)
        self.pushStack(self.pc & 0x00FF)
        status = self.flags.getStatus(flags.BreakHandler.IRQNMI)
        self.pc = self.readWord(0xFFFE)
        self.flags.setInterruptDisable(1)

    def _fetchAppropriateOpcodeData(self, address_mode, isStorage=False):
        #This returns a tuple with the data requested
        #and if a page boundary was crossed
        value = 0
        page_crossed = False
        address = 0

        #isStorage is for the LDx and STx function which actually want an
        #address, and not the value at the address

        if address_mode == AddressMode.ACCUMULATOR:
            value = self.a
            page_crossed = False
        elif address_mode == AddressMode.ABSOLUTE:
            args = [self.readByte(self.pc + 1), self.readByte(self.pc + 2)]
            address = readAbsoluteAddress(self, args)
            value = self.readByte(address)
            page_crossed = False
        elif address_mode == AddressMode.ABSOLUTE_JUMP:
            args = [self.readByte(self.pc + 1), self.readByte(self.pc + 2)]
            value = readAbsoluteAddress(self, args)
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
            address = value #A bit of a hack 
        elif address_mode == AddressMode.RELATIVE:
            args = [self.readByte(self.pc + 1)]
            address, page_crossed = readRelativeAddress(self, args), False
            #The relative jump address is read
            if address & 0b10000000 > 0:
                #This is a negative number
                value_oc = (address & 0xFF) - 1
                inverse_oc = ~value_oc & 0xFF
                value = -inverse_oc
            else:
                #It is a positive number
                value = address

            if (self.pc & 0xFF00) != ((self.pc + value) & 0xFF00):
                page_crossed = True
            else:
                page_crossed = False
        elif address_mode == AddressMode.IMPLIED:
            value, page_crossed = 0, False
        elif address_mode == AddressMode.ZEROPAGE:
            address, page_crossed = self.readByte(self.pc + 1), False
            value = self.readByte(address)
        elif address_mode == AddressMode.ZEROPAGE_INDEXED:
            args = [self.readByte(self.pc + 1)]
            address, page_crossed = readIZeroPageIndexedAddressX(self, args), False
            value = self.readByte(address)
        elif address_mode == AddressMode.ZEROPAGE_INDEXED_Y:
            args = [self.readByte(self.pc + 1)]
            address, page_crossed = readIZeroPageIndexedAddressY(self, args), False
            value = self.readByte(address)
        elif address_mode == AddressMode.INDIRECT:
            #Only the JMP instruction uses this
            value, page_crossed = self.readWord(self.readWord(self.pc + 1)), False
        elif address_mode == AddressMode.INDEXED_INDIRECT:
            args = [self.readByte(self.pc + 1)]
            address = readIndexedIndirectAddress(self, args)
            value, page_crossed = self.readByte(address)
        elif address_mode == AddressMode.INDIRECT_INDEXED:
            args = [self.readByte(self.pc + 1)]
            address = readIndirectIndexedAddress(self, args)
            value, page_crossed = self.readByte(address)
        elif address_mode == AddressMode.IMPLIED_JUMP:
            value, page_crossed = 0, False
            #For RTI and RTS
        else:
            raise Exception("The specified address mode is not known or defined")

        if isStorage:
            #Storage instructions want the address itself, not the value at the address
            value = address

        return value, page_crossed

    def _executeOpcode(self, oc):
        #This function returns how much to advance the program counter by
        #And how long this operation took
        value, page_crossed = self._fetchAppropriateOpcodeData(oc.address_mode, oc.isStorage)
        counter_advance =  oc.length
        duration = oc.duration[0]
        if oc.family == OpcodeFamily.ADC:
            self.ADC(value)
        elif oc.family == OpcodeFamily.AND:
            self.AND(value)
        elif oc.family == OpcodeFamily.ASL:
            self.ASL(value)
        elif oc.family == OpcodeFamily.BCC:
            result = self.BCC(value)
            if result == True & page_crossed == False:
                duration = oc.duration[1]
            elif result == True & page_crossed == True:
                duration = oc.duration[2]
            else:
                duration = oc.duration[0]
        elif oc.family == OpcodeFamily.BCS:
            result = self.BCS(value)
            if result == True & page_crossed == False:
                duration = oc.duration[1]
            elif result == True & page_crossed == True:
                duration = oc.duration[2]
            else:
                duration = oc.duration[0]
        elif oc.family == OpcodeFamily.BEQ:
            result = self.BEQ(value)
            if result == True & page_crossed == False:
                duration = oc.duration[1]
            elif result == True & page_crossed == True:
                duration = oc.duration[2]
            else:
                duration = oc.duration[0]
        elif oc.family == OpcodeFamily.BIT:
            self.BIT(value)
        elif oc.family == OpcodeFamily.BMI:
            result = self.BMI(value)
            if result == True & page_crossed == False:
                duration = oc.duration[1]
            elif result == True & page_crossed == True:
                duration = oc.duration[2]
            else:
                duration = oc.duration[0]
        elif oc.family == OpcodeFamily.BNE:
            result = self.BNE(value)
            if result == True & page_crossed == False:
                duration = oc.duration[1]
            elif result == True & page_crossed == True:
                duration = oc.duration[2]
            else:
                duration = oc.duration[0]
        elif oc.family == OpcodeFamily.BPL:
            result = self.BPL(value)
            if result == True & page_crossed == False:
                duration = oc.duration[1]
            elif result == True & page_crossed == True:
                duration = oc.duration[2]
            else:
                duration = oc.duration[0]
        elif oc.family == OpcodeFamily.BRK:
            self.BRK()
        elif oc.family == OpcodeFamily.BVC:
            result = self.BVC(value)
            if result == True & page_crossed == False:
                duration = oc.duration[1]
            elif result == True & page_crossed == True:
                duration = oc.duration[2]
            else:
                duration = oc.duration[0]
        elif oc.family == OpcodeFamily.BVS:
            result = self.BVS(value)
            if result == True & page_crossed == False:
                duration = oc.duration[1]
            elif result == True & page_crossed == True:
                duration = oc.duration[2]
            else:
                duration = oc.duration[0]
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
            self.JMP(value)
            counter_advance = 0
        elif oc.family == OpcodeFamily.JSR:
            self.JSR(value)
        elif oc.family == OpcodeFamily.LDA:
            self.LDA(value)
        elif oc.family == OpcodeFamily.LDX:
            self.LDX(value)
        elif oc.family == OpcodeFamily.LDY:
            self.LDY(value)
        elif oc.family == OpcodeFamily.LSR:
            self.LSR(value)
        elif oc.family == OpcodeFamily.NOP:
            pass
        elif oc.family == OpcodeFamily.ORA:
            self.OR(value)
        elif oc.family == OpcodeFamily.PHA:
            self.pushStack(self.a)
        elif oc.family == OpcodeFamily.PHP:
            self.pushStack(self.flags.getStatus(flags.BreakHandler.PHPBRK))
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
            self.RTI()
        elif oc.family == OpcodeFamily.RTS:
            self.RTS()
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
        elif oc.family == OpcodeFamily.TAX:
            self.TAX()
        elif oc.family == OpcodeFamily.TAY:
            self.TAY()
        elif oc.family == OpcodeFamily.TSX:
            self.TSX()
        elif oc.family == OpcodeFamily.TXA:
            self.TXA()
        elif oc.family == OpcodeFamily.TXS:
            self.TXS()
        elif oc.family == OpcodeFamily.TYA:
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