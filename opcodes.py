from opcodes0 import *
from opcodes1 import *
from opcodes2 import *
from opcodes3 import *

from testcpu import *
import re

code_dict = { 
        BRK.code : BRK, 
        ORAIndirectX.code : ORAIndirectX, 
        ORAZeroPage.code : ORAZeroPage,
        ASLZP.code : ASLZP, 
        PHP.code : PHP, 
        ORAImmediate.code : ORAImmediate, 
        ASLA.code : ASLA, 
        ORAAbsolute.code : ORAAbsolute,
        ASLAbsolute.code : ASLAbsolute,
        BPL.code : BPL,
        ORAIndY.code : ORAIndY, 
        ORAZPX.code : ORAZPX, 
        ASLZPX.code : ASLZPX, 
        CLC.code : CLC, 
        ORAAbsoluteY.code : ORAAbsoluteY, 
        ORAAbsoluteX.code : ORAAbsoluteX,
        ASLAbsoluteX.code : ASLAbsoluteX,
        JSRAbsolute.code : JSRAbsolute,
        ANDIndX.code : ANDIndX,
        BITZP.code : BITZP,
        ANDZP.code : ANDZP,
        ROLZP.code : ROLZP,
        PLP.code : PLP,
        ANDImmediate.code : ANDImmediate,
        ROLA.code : ROLA,
        BITAbsolute.code : BITAbsolute,
        ANDAbsolute.code : ANDAbsolute,
        ROLAbsolute.code : ROLAbsolute,
        BMIR8.code : BMIR8,
        ANDIndY.code : ANDIndY,
        ANDZPX.code : ANDZPX,
        ROLZPX.code : ROLZPX,
        SEC.code : SEC,
        ANDAbsoluteY.code : ANDAbsoluteY,
        ANDAbsoluteX.code : ANDAbsoluteX,
        ROLAbsoluteX.code : ROLAbsoluteX
}

if __name__ == '__main__':
    mycpu = TestCPU()
    quit = False
    print("Welcome to the NES 6502 Emulator Core Tester.")
    print("This allows you to evaluate commands as you write the code for them, ensuring that their behaviour is as expected.")
    print("A single prompt '>' means that the tester is taking user interface commands, but a double prompt '>>' means that the tester is taking CPU commands. Remember that all inputs are in hex, but all output values are in decimal.")
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
                print("E - switches this console to execution mode, allowing you to run a command")
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
            elif choice.lower() == "e":
                print("Enter the command you want to execute below. Enter the bytes in hex, and separate every byte with a single space character")
                command = input(">> ")
                values = re.findall("([0-9A-Fa-f]{2})+", command)
                opcode = int(values[0], 16)
                print(code_dict[opcode].name, " ", end="")
                params = []
                try:
                    for i in values[1:]:
                        print(i, " ", end="")
                        params.append(int(i, 16))
                    print("")
                    code_dict[opcode].function(mycpu, params)
                except IndexError:
                    print("The instruction does not have the correct number of parameters. Nothing was done.")

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

