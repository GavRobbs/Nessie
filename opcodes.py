from opcode import *

from testcpu import *
import re
import os

code_dict = {
    0x0 : Opcode("BRK", 0x0, OpcodeFamily.BRK, 2, AddressMode.IMPLIED, [7], jump = True),
    0x1 : Opcode("ORA (a8, X)", 0x1, OpcodeFamily.ORA, 2, AddressMode.INDEXED_INDIRECT, [6]),
    0x5 : Opcode("ORA a8", 0x5, OpcodeFamily.ORA, 2, AddressMode.ZEROPAGE, [3]),
    0x6 : Opcode("ASL a8", 0x6, OpcodeFamily.ASL, 2, AddressMode.ZEROPAGE, [5]),
    0x8 : Opcode("PHP", 0x8, OpcodeFamily.PHP, 1, AddressMode.IMPLIED, [3]),
    0x9 : Opcode("ORA #d8", 0x9, OpcodeFamily.ORA, 2, AddressMode.IMMEDIATE, [2]),
    0xA : Opcode("ASL A", 0xA, OpcodeFamily.ASL, 1, AddressMode.ACCUMULATOR, [2]),
    0xD : Opcode("ORA a16", 0xD, OpcodeFamily.ORA, 3, AddressMode.ABSOLUTE, [4]),
    0xE : Opcode("ASL a16", 0xE, OpcodeFamily.ASL, 3, AddressMode.ABSOLUTE, [6]),
    0x10 : Opcode("BPL r8", 0x10, OpcodeFamily.BPL, 2, AddressMode.RELATIVE, [2,3,4]),
    0x11 : Opcode("ORA (a8), Y", 0x11, OpcodeFamily.ORA, 2, AddressMode.INDIRECT_INDEXED, [5, 6]),
    0x15: Opcode("ORA a8, X", 0x15, OpcodeFamily.ORA, 2, AddressMode.ZEROPAGE_INDEXED, [4]),
    0x16: Opcode("ASL a8, X", 0x16, OpcodeFamily.ASL, 2, AddressMode.ZEROPAGE_INDEXED, [6]),
    0x18: Opcode("CLC", 0x18, OpcodeFamily.CLC, 1, AddressMode.IMPLIED, [2]),
    0x19: Opcode("ORA a16, Y", 0x19, OpcodeFamily.ORA, 3, AddressMode.ABSOLUTE_INDEXED_Y, [4,5]),
    0x1D: Opcode("ORA a16, X", 0x1D, OpcodeFamily.ORA, 3, AddressMode.ABSOLUTE_INDEXED_X, [4,5]),
    0x1E: Opcode("ASL a16, X", 0x1E, OpcodeFamily.ASL, 3, AddressMode.ABSOLUTE_INDEXED_X, [7, 7]),
    0x20: Opcode("JSR a16", 0x20, OpcodeFamily.JSR, 3, AddressMode.ABSOLUTE, [6]),
    0x21: Opcode("AND (a8, X)", 0x21, OpcodeFamily.AND, 2, AddressMode.INDEXED_INDIRECT, [6]),
    0x24: Opcode("BIT a8", 0x24, OpcodeFamily.BIT, 2, AddressMode.ZEROPAGE, [3]),
    0x25: Opcode("AND a8", 0x25, OpcodeFamily.AND, 2, AddressMode.ZEROPAGE, [3]),
    0x26: Opcode("ROL a8", 0x26, OpcodeFamily.ROL, 2, AddressMode.ZEROPAGE, [5]),
    0x28: Opcode("PLP", 0x28, OpcodeFamily.PLP, 1, AddressMode.IMPLIED, [4]),
    0x29: Opcode("AND #d8", 0x29, OpcodeFamily.AND, 2, AddressMode.IMMEDIATE, [2]),
    0x2A: Opcode("ROL A", 0x2A, OpcodeFamily.ROL, 1, AddressMode.ACCUMULATOR, [2]),
    0x2C: Opcode("BIT a16", 0x2C, OpcodeFamily.BIT, 3, AddressMode.ABSOLUTE, [4]),
    0x2D: Opcode("AND a16", 0x2D, OpcodeFamily.BIT, 3, AddressMode.ABSOLUTE, [4]),
    0x2E: Opcode("ROL a16", 0x2E, OpcodeFamily.BIT, 3, AddressMode.ABSOLUTE, [6]),
    0x30: Opcode("BMI r8", 0x30, OpcodeFamily.BMI, 2, AddressMode.RELATIVE,[2, 3, 4]),
    0x31 : Opcode("AND (a8), Y", 0x31, OpcodeFamily.AND, 2, AddressMode.INDIRECT_INDEXED, [5, 6]),
    0x35: Opcode("AND a8, X", 0x35, OpcodeFamily.AND, 2, AddressMode.ZEROPAGE_INDEXED, [4]),
    0x36: Opcode("ROL a8, X", 0x36, OpcodeFamily.ROL, 2, AddressMode.ZEROPAGE_INDEXED, [6]),
    0x38: Opcode("SEC", 0x38, OpcodeFamily.SEC, 1, AddressMode.IMPLIED, [2]),
    0x39: Opcode("AND a16, Y", 0x39, OpcodeFamily.AND, 3, AddressMode.ABSOLUTE_INDEXED_Y, [4,5]),
    0x3D: Opcode("AND a16, X", 0x3D, OpcodeFamily.AND, 3, AddressMode.ABSOLUTE_INDEXED_X, [4,5]),
    0x3E: Opcode("ROL a16, X", 0x3E, OpcodeFamily.ROL, 3, AddressMode.ABSOLUTE_INDEXED_X, [7, 7]),
    0x40: Opcode("RTI", 0x40, OpcodeFamily.RTI, 1, AddressMode.IMPLIED_JUMP, [6]),
    0x41: Opcode("EOR (a8, X)", 0x41, OpcodeFamily.EOR, 2, AddressMode.INDEXED_INDIRECT, [6]),
    0x45: Opcode("EOR a8",0x45, OpcodeFamily.EOR, 2, AddressMode.ZEROPAGE, [3]),
    0x46: Opcode("LSR a8", 0x46, OpcodeFamily.LSR, 2, AddressMode.ZEROPAGE, [5]),
    0x48: Opcode("PHA", 0x48, OpcodeFamily.PHA, 1, AddressMode.IMPLIED, [3]),
    0x49: Opcode("EOR #d8", 0x49, OpcodeFamily.EOR, 2, AddressMode.IMMEDIATE, [2]),
    0x4A: Opcode("LSR A", 0x4A, OpcodeFamily.LSR, 1, AddressMode.ACCUMULATOR, [2]),
    0x4C: Opcode("JMP a16", 0x4C, OpcodeFamily.JMP, 3, AddressMode.ABSOLUTE_JUMP, [3], jump=True),
    0x4D: Opcode("EOR a16", 0x4D, OpcodeFamily.EOR, 3, AddressMode.ABSOLUTE, [4]),
    0x4E: Opcode("LSR a16", 0x4E, OpcodeFamily.LSR, 3, AddressMode.ABSOLUTE, [6]),
    0x50: Opcode("BVC r8", 0x50, OpcodeFamily.BVC, 2, AddressMode.RELATIVE, [2, 3, 4]),
    0x51: Opcode("EOR (a8), Y", 0x51, OpcodeFamily.EOR, 2, AddressMode.INDIRECT_INDEXED, [5,6]),
    0x55: Opcode("EOR a8, X", 0x55, OpcodeFamily.EOR, 2, AddressMode.ZEROPAGE_INDEXED, [4]),
    0x56: Opcode("LSR a8, X", 0x56, OpcodeFamily.LSR, 2, AddressMode.ZEROPAGE_INDEXED, [6]),
    0x58: Opcode("CLI", 0x58, OpcodeFamily.CLI, 1, AddressMode.IMPLIED, [2]),
    0x59: Opcode("EOR a16, Y", 0x59,OpcodeFamily.EOR,3,AddressMode.ABSOLUTE_INDEXED_Y,[4, 5]),
    0x5D: Opcode("EOR a16, X", 0x5D, OpcodeFamily.EOR,3,AddressMode.ABSOLUTE_INDEXED_X,[5, 6]),
    0x5E: Opcode("LSR a16, X", 0x5E, OpcodeFamily.LSR,3,AddressMode.ABSOLUTE_INDEXED_X,[7, 7]),
    0x60: Opcode("RTS", 0x60, OpcodeFamily.RTS, 1, AddressMode.IMPLIED_JUMP, [6]),
    0x61: Opcode("ADC (a8, X)", 0x61, OpcodeFamily.ADC, 2, AddressMode.INDEXED_INDIRECT, [6]),
    0x65: Opcode("ADC a8", 0x65, OpcodeFamily.ADC, 2, AddressMode.ZEROPAGE, [3]),
    0x66: Opcode("ROR a8", 0x66, OpcodeFamily.ROR, 2, AddressMode.ZEROPAGE, [5]),
    0x68: Opcode("PLA", 0x68, OpcodeFamily.PLA, 1, AddressMode.IMPLIED, [4]),
    0x69: Opcode("ADC #d8", 0x69, OpcodeFamily.ADC, 2, AddressMode.IMMEDIATE, [2]),
    0x6A: Opcode("ROR A", 0x6A, OpcodeFamily.ROR, 1, AddressMode.ACCUMULATOR, [2]),
    0x6C: Opcode("JMP (a16)", 0x6C, OpcodeFamily.JMP, 3, AddressMode.INDIRECT, [5]),
    0x6D: Opcode("ADC a16", 0x6D, OpcodeFamily.ADC, 3, AddressMode.IMMEDIATE, [4]),
    0x6E: Opcode("ROR a16", 0x6E, OpcodeFamily.ROR, 3, AddressMode.IMMEDIATE, [6]),
    0x70: Opcode("BVS r8", 0x70, OpcodeFamily.BVS, 2, AddressMode.RELATIVE, [2, 3, 4]),
    0x71: Opcode("ADC (a8), Y", 0x71, OpcodeFamily.ADC, 2, AddressMode.INDIRECT_INDEXED, [5, 6]),
    0x75: Opcode("ADC a8, X", 0x75, OpcodeFamily.ADC, 2, AddressMode.INDEXED_INDIRECT, [4]),
    0x76: Opcode("ROR a8, X", 0x76, OpcodeFamily.ROR, 2, AddressMode.INDEXED_INDIRECT, [6]),
    0x78: Opcode("SEI", 0x78, OpcodeFamily.SEI, 1, AddressMode.IMPLIED, [2]),
    0x79: Opcode("ADC a16, Y", 0x79, OpcodeFamily.ADC, 3, AddressMode.ABSOLUTE_INDEXED_Y, [4, 5]),
    0x7D: Opcode("ADC a16, X", 0x7D, OpcodeFamily.ADC, 3, AddressMode.ABSOLUTE_INDEXED_X, [4, 5]),
    0x7E: Opcode("ROR a16, X", 0x7E, OpcodeFamily.ADC, 3, AddressMode.ABSOLUTE_INDEXED_X, [7, 7]),
    0x81: Opcode("STA (a8, X)", 0x81, OpcodeFamily.STA, 2, AddressMode.INDEXED_INDIRECT, [6], isStorage=True),
    0x84: Opcode("STY a8", 0x84, OpcodeFamily.STY, 2, AddressMode.ZEROPAGE, [3], isStorage=True),
    0x85: Opcode("STA a8", 0x85, OpcodeFamily.STA, 2, AddressMode.ZEROPAGE, [3], isStorage=True),
    0x86: Opcode("STX a8", 0x86, OpcodeFamily.STX, 2, AddressMode.ZEROPAGE, [3], isStorage=True),
    0x88: Opcode("DEY", 0x88, OpcodeFamily.DEY, 1, AddressMode.IMPLIED, [2]),
    0x8A: Opcode("TXA", 0x8A, OpcodeFamily.TXA, 1, AddressMode.IMPLIED, [2]),
    0x8C: Opcode("STY a16", 0x8C, OpcodeFamily.STY, 3, AddressMode.ABSOLUTE, [4], isStorage=True),
    0x8D: Opcode("STA a16", 0x8D, OpcodeFamily.STA, 3, AddressMode.ABSOLUTE, [4], isStorage=True),
    0x8E: Opcode("STX a16", 0x8E, OpcodeFamily.STX, 3, AddressMode.ABSOLUTE, [4], isStorage=True),
    0x90: Opcode("BCC r8", 0x90, OpcodeFamily.BCC, 2, AddressMode.RELATIVE, [2, 3, 4]),
    0x91: Opcode("STA (a8), Y", 0x91, OpcodeFamily.STA, 2, AddressMode.INDIRECT_INDEXED, [6, 6], isStorage=True),
    0x94: Opcode("STY a8, X", 0x94, OpcodeFamily.STY, 2, AddressMode.ZEROPAGE_INDEXED, [4], isStorage=True),
    0x95: Opcode("STA a8, X", 0x95, OpcodeFamily.STA, 2, AddressMode.ZEROPAGE_INDEXED, [4], isStorage=True),
    0x96: Opcode("STX a8, Y", 0x96, OpcodeFamily.STX, 2, AddressMode.ZEROPAGE_INDEXED_Y, [4], isStorage=True),
    0x98: Opcode("TYA", 0x98, OpcodeFamily.TYA, 1, AddressMode.IMPLIED, [2]),
    0x99: Opcode("STA a16, Y", 0x99, OpcodeFamily.STA, 3, AddressMode.ABSOLUTE_INDEXED_Y, [5,5], isStorage=True),
    0x9A: Opcode("TXS", 0x9A, OpcodeFamily.TXS,1, AddressMode.IMPLIED, [2]),
    0x9D: Opcode("STA a16, X", 0x9D, OpcodeFamily.STA, 3, AddressMode.ABSOLUTE_INDEXED_X, [5,5]),
    0xA0: Opcode("LDY #d8", 0xA0, OpcodeFamily.LDY, 2, AddressMode.IMMEDIATE, [2]),
    0xA1: Opcode("LDA (a8, X)", 0xA1, OpcodeFamily.LDA, 2, AddressMode.INDEXED_INDIRECT, [6]),
    0xA2: Opcode("LDX #d8", 0xA2, OpcodeFamily.LDX, 2, AddressMode.IMMEDIATE, [2]),
    0xA4: Opcode("LDY a8", 0xA4, OpcodeFamily.LDY, 2, AddressMode.ZEROPAGE, [3]),
    0xA5: Opcode("LDA a8", 0xA5, OpcodeFamily.LDA, 2, AddressMode.ZEROPAGE, [3]),
    0xA6: Opcode("LDX a8", 0xA6, OpcodeFamily.LDX, 2, AddressMode.ZEROPAGE, [3]),
    0xA8: Opcode("TAY", 0xA8, OpcodeFamily.TAY, 1, AddressMode.IMPLIED, [2]),
    0xA9: Opcode("LDA #d8", 0xA9, OpcodeFamily.LDA, 2, AddressMode.IMMEDIATE, [2]),
    0xAA: Opcode("TAX", 0xAA, OpcodeFamily.TAX, 1, AddressMode.IMPLIED, [2]),
    0xAC: Opcode("LDY a16", 0xAC, OpcodeFamily.LDY, 3, AddressMode.ABSOLUTE, [4]),
    0xAD: Opcode("LDA a16", 0xAD, OpcodeFamily.LDA, 3, AddressMode.ABSOLUTE, [4]),
    0xAE: Opcode("LDX a16", 0xAE, OpcodeFamily.LDX, 3, AddressMode.ABSOLUTE, [4]),
    0xB0: Opcode("BCS r8", 0xB0, OpcodeFamily.BCS, 2, AddressMode.RELATIVE, [2,3,4]),
    0xB1: Opcode("LDA (a8), Y", 0xB1, OpcodeFamily.LDA, 2, AddressMode.INDIRECT_INDEXED, [5, 6]),
    0xB4: Opcode("LDY a8, X", 0xB4, OpcodeFamily.LDY, 2, AddressMode.ZEROPAGE_INDEXED, [4]),
    0xB5: Opcode("LDA a8, X", 0xB5, OpcodeFamily.LDA, 2, AddressMode.ZEROPAGE_INDEXED, [4]),
    0xB6: Opcode("LDX a8, Y", 0xB6, OpcodeFamily.LDX, 2, AddressMode.ZEROPAGE_INDEXED_Y, [4]),
    0xB8: Opcode("CLV", 0xB8, OpcodeFamily.CLV, 1, AddressMode.IMPLIED, [2]),
    0xB9: Opcode("LDA a16, Y", 0xB9, OpcodeFamily.LDA, 3, AddressMode.ABSOLUTE_INDEXED_Y, [4,5]),
    0xBA: Opcode("TSX", 0xBA, OpcodeFamily.TSX, 1, AddressMode.IMPLIED, [2]),
    0xBC: Opcode("LDY a16, X", 0xBC, OpcodeFamily.LDY, 3, AddressMode.ABSOLUTE_INDEXED_X, [4, 5]),
    0xBD: Opcode("LDA a16, X", 0xBD, OpcodeFamily.LDA, 3, AddressMode.ABSOLUTE_INDEXED_X, [4, 5]),
    0xBE: Opcode("LDX a16, Y", 0xBE, OpcodeFamily.LDX, 3, AddressMode.ABSOLUTE_INDEXED_Y, [4, 5]),
    0xC0: Opcode("CPY #d8", 0xC0, OpcodeFamily.CPY, 2, AddressMode.IMMEDIATE, [2]),
    0xC1: Opcode("CMP (a8, X)", 0xC1, OpcodeFamily.CMP, 2, AddressMode.INDEXED_INDIRECT, [6]),
    0xC4: Opcode("CPY a8", 0xC4, OpcodeFamily.CPY, 2, AddressMode.ZEROPAGE, [3]),
    0xC5: Opcode("CMP a8", 0xC5, OpcodeFamily.CMP, 2, AddressMode.ZEROPAGE, [3]),
    0xC6: Opcode("DEC a8", 0xC6, OpcodeFamily.DEC, 2, AddressMode.ZEROPAGE, [5]),
    0xC8: Opcode("INY", 0xC8, OpcodeFamily.INY, 1, AddressMode.IMPLIED, [2]),
    0xC9: Opcode("CMP #d8", 0xC9, OpcodeFamily.CMP, 2, AddressMode.IMMEDIATE, [2]),
    0xCA: Opcode("DEX", 0xCA, OpcodeFamily.DEX, 1, AddressMode.IMPLIED, [2]),
    0xCC: Opcode("CPY a16", 0xCC, OpcodeFamily.CPY, 3, AddressMode.ABSOLUTE, [4]),
    0xCD: Opcode("CMP a16", 0xCD, OpcodeFamily.CMP, 3, AddressMode.ABSOLUTE, [4]),
    0xCE: Opcode("DEC a16", 0xCE, OpcodeFamily.DEC, 3, AddressMode.ABSOLUTE, [4])
}

if __name__ == '__main__':
    mycpu = TestCPU()
    quit = False
    print("Welcome to the NES 6502 Emulator Core Tester.")
    print("This allows you to evaluate commands as you write the code for them, ensuring that their behaviour is as expected.")
    print("Please pick an option to continue. Press H at any time for help.")

    fname = ""
    fsize = 0

    while quit == False:
        choice = input(f"{fname}#{mycpu.pc}> ")
        try:
            if choice.lower() == 'h':
                print("The following commands are supported.")
                print("R - displays the current status of the 6502 registers")
                print("F - displays the current status of the 6502 flags")
                print("S - displays the values currently stored in the stack")
                print("M [start]:[end] - displays the slice of memory between start and end")
                print("L - allows you to load a file containing 6502 code")
                print("A - step through the code of a loaded file")
                print("P - runs a file from beginning to end")
                print("H - displays this help menu")
                print("Q - quit")
            elif choice.lower() == "r":
                mycpu.printRegisters()
            elif choice.lower() == "f":
                mycpu.printFlags()
            elif choice.lower() == "s":
                mycpu.printStack()
            elif choice.lower() == "q":
                quit = True
            elif choice.lower() == "l":
                choice2 = input("Please enter the name of the file you want to load: ")
                val = 0
                fname = choice2.strip()
                mycpu.RAM = [0] * 2048 #Empty the list out
                with open(choice2, "rb") as myrom:
                    myrom.seek(0, os.SEEK_END)
                    fsize = myrom.tell()
                    myrom.seek(0, 0)
                    abyte = myrom.read(1)
                    while abyte:
                        temp = int.from_bytes(abyte, byteorder='little')
                        mycpu.RAM[val] = temp
                        val += 1
                        abyte = myrom.read(1)
                mycpu.pc = 0
            elif choice.lower() == "a":
                currentOp = code_dict[mycpu.RAM[mycpu.pc]]
                advance, duration = mycpu._executeOpcode(currentOp)
                mycpu.pc += advance
                print(currentOp.name)
                if currentOp.jump == False:
                    print(f"The command was {advance} bytes long and took {duration} cycles.")
                else:
                    print(f"The command was a jump that took the program counter to {mycpu.pc} and took {duration} cycles.")
            elif choice.lower() == "p":
                while mycpu.pc < fsize:
                    currentOp = code_dict[mycpu.RAM[mycpu.pc]]
                    advance, duration = mycpu._executeOpcode(currentOp)
                    mycpu.pc += advance
                    print(currentOp.name)
            elif choice[0].lower() == "m":
                m = re.findall("[m|M]{1}\s+(\d+)[\:](\d+)",choice)
                start = int(m[0][0], 16)
                end = int(m[0][1], 16)

                if end < start:
                    print("The start index cannot be greater than the start index!")
                elif end >= 2048 or start >= 2048:
                    raise LocationNotAvailableError
                else:
                    mycpu.printMemorySlice(start, end)
            else:
                print("Unrecognized command")
        except LocationNotAvailableError:
            print("This emulator only allows you to access the work RAM, in memory locations 0 to 2047. Any other location, which would be memory mapped in a real NES, is not available.")
        except KeyError:
            print("There is no instruction with that hex code available.")

