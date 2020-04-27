from opcode import *

from testcpu import *
import re

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
    0x10 : Opcode("BPL r8", 0x10, OpcodeFamily.BPL, 2, AddressMode.RELATIVE, [2,3,4], jump = True),
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
    0x30: Opcode("BMI r8", 0x30, OpcodeFamily.BMI, 2, AddressMode.RELATIVE,[2, 3, 4], jump = True),
    0x31 : Opcode("AND (a8), Y", 0x31, OpcodeFamily.AND, 2, AddressMode.INDIRECT_INDEXED, [5, 6]),
    0x35: Opcode("AND a8, X", 0x35, OpcodeFamily.AND, 2, AddressMode.ZEROPAGE_INDEXED, [4]),
    0x36: Opcode("ROL a8, X", 0x36, OpcodeFamily.ROL, 2, AddressMode.ZEROPAGE_INDEXED, [6]),
    0x38: Opcode("SEC", 0x38, OpcodeFamily.SEC, 1, AddressMode.IMPLIED, [2]),
    0x39: Opcode("AND a16, Y", 0x39, OpcodeFamily.AND, 3, AddressMode.ABSOLUTE_INDEXED_Y, [4,5]),
    0x3D: Opcode("AND a16, X", 0x3D, OpcodeFamily.AND, 3, AddressMode.ABSOLUTE_INDEXED_X, [4,5]),
    0x3E: Opcode("ROL a16, X", 0x3E, OpcodeFamily.ROL, 3, AddressMode.ABSOLUTE_INDEXED_X, [7, 7]), 
}

if __name__ == '__main__':
    mycpu = TestCPU()
    quit = False
    print("Welcome to the NES 6502 Emulator Core Tester.")
    print("This allows you to evaluate commands as you write the code for them, ensuring that their behaviour is as expected.")
    print("Please pick an option to continue. Press H at any time for help.")
    while quit == False:
        choice = input("> ")
        try:
            if choice.lower() == 'h':
                print("The following commands are supported.")
                print("R - displays the current status of the 6502 registers")
                print("F - displays the current status of the 6502 flags")
                print("S - displays the values currently stored in the stack")
                print("M [start]:[end] - displays the slice of memory between start and end")
                print("L - allows you to load a file containing 6502 code")
                print("A - step through the code of a loaded file")
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
                with open(choice2, "rb") as myrom:
                    abyte = myrom.read(1)
                    while abyte:
                        temp = int.from_bytes(abyte, byteorder='little')
                        mycpu.RAM[0x100 + val] = temp
                        val += 1
                        abyte = myrom.read(1)
                mycpu.pc = 0x100
            elif choice.lower() == "a":
                currentOp = code_dict[mycpu.RAM[mycpu.pc]]
                advance, duration = mycpu._executeOpcode(currentOp)
                mycpu.pc += advance
                if currentOp.jump == False:
                    print(f"The last command was {advance} bytes long and took {duration} cycles.")
                else:
                    print(f"The last command was a jump that took the program counter to {mycpu.pc} and took {duration} cycles.")
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

