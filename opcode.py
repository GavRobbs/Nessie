class Opcode:
    def __init__(self, name, code, length, duration, jump = False):
        self.name = name
        self.code = code
        self.duration = duration
        self.length = length
        self.function = None
        self.jump = jump
        #Jump says that the CPU doesn't need to increment the program counter
        #after the function returns, because the function will directly modify it

def clampResult(value):
    return value & 0b11111111

#Length is constant, but duration changes depending on if it is a condition that is taken
#or if a 256 byte page boundary is crossed. Because of this, duration is passed as a tuple.
#The function variable returns the index of the item in the tuple that represents how much time #the function took