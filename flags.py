import enum

class BreakHandler(enum.Enum):
    NONE = 0
    PHPBRK = 1
    IRQNMI = 2

class Flags:
    #need to implement the psuedo B flag
    def __init__(self):
        self.zero = 0
        self.carry = 0
        self.negative = 0
        self.overflow = 0
        self.interruptDisable = 0
        self.b0 = 0
        self.b1 = 1

    def setZero(self, value):
        self.zero = value

    def getZero(self):
        return self.zero

    def getOverflow(self):
        return self.overflow

    def setOverflow(self, value):
        self.overflow = value

    def setCarry(self, value):
        self.carry = value

    def getCarry(self):
        return self.carry

    def setNegative(self, value):
        self.negative = value

    def getNegative(self):
        return self.negative

    def getStatus(self, break_handler=BreakHandler.NONE):
        temp = (self.negative << 7) | (self.overflow << 6) | (self.interruptDisable << 2) | (self.zero << 1) | (self.carry)
        if break_handler == BreakHandler.NONE:
            pass
        elif break_handler == BreakHandler.PHPBRK:
            temp |= (1 << 5) | (1 << 4)
        else:
            temp |= (1 << 5)
        return temp

    def setStatus(self, value):
        self.setNegative(1 if value & 0b10000000 else 0)
        self.setOverflow(1 if value & 0b01000000 else 0)
        self.setInterruptDisable(1 if value & 0b00000100 else 0)
        self.setZero(1 if value & 0b00000010 else 0)
        self.setCarry(1 if value & 0b00000001 else 0)

    def setInterruptDisable(self, status):
        self.interruptDisable = status

    def getInterruptDisable(self):
        return self.interruptDisable

    def checkNegative(self, value):
        if value & 0b10000000 > 0:
            self.setNegative(1)
        else:
            self.setNegative(0)
        pass

    def checkZero(self, value):
        if value == 0:
            self.setZero(1)
        else:
            self.setZero(0)

    def checkCarry(self, value):
        pass