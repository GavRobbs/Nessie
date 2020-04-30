import enum

class OpcodeFamily(enum.Enum):
    ADC = 0
    AND = 1
    ASL = 2
    BCC = 3
    BCS = 4
    BEQ = 5
    BIT = 6
    BMI = 7
    BNE = 8
    BPL = 9
    BRK = 10
    BVC = 11
    BVS = 12
    CLC = 13
    CLD = 14
    CLI = 15
    CLV = 16
    CMP = 17
    CPX = 18
    CPY = 19
    DEC = 20
    DEX = 21
    DEY = 22
    EOR = 23
    INC = 24
    INX = 25
    INY = 26
    JMP = 27
    JSR = 28
    LDA = 29
    LDX = 30
    LDY = 31
    LSR = 32
    NOP = 33
    ORA = 34
    PHA = 35
    PHP = 36
    PLA = 37
    PLP = 38
    ROL = 39
    ROR = 40
    RTI = 41
    RTS = 42
    SBC = 43
    SEC = 44
    SED = 45
    SEI = 46
    STA = 47
    STX = 48
    STY = 49
    TAX = 50
    TAY = 51
    TSX = 52
    TXA = 53
    TXS = 54
    TYA = 55

class AddressMode(enum.Enum):
    ACCUMULATOR = 0
    IMMEDIATE = 1
    IMPLIED = 2
    RELATIVE = 3
    ABSOLUTE = 4
    ZEROPAGE = 5
    INDIRECT = 6
    ABSOLUTE_INDEXED_X = 7
    ABSOLUTE_INDEXED_Y = 8
    ZEROPAGE_INDEXED = 9
    INDEXED_INDIRECT = 10
    INDIRECT_INDEXED = 11
    ABSOLUTE_JUMP = 12
    IMPLIED_JUMP = 13 #For RTI and RTS
    ZEROPAGE_INDEXED_Y = 14

class Opcode:
    def __init__(self, name, code, family, length, address_mode, duration, isStorage = False, jump = False):
        self.name = name
        self.code = code
        self.family = family
        self.length = length
        self.address_mode = address_mode
        self.duration = duration
        self.function = None
        self.jump = jump
        self.isStorage = isStorage
        #Jump says that the CPU doesn't need to increment the program counter
        #after the function returns, because the function will directly modify it