from myhdl import block, Signal, intbv, modbv, delay, instance, instances, always_comb, always_seq, always
from gluelogic import varfifo
from random import randrange
import numpy as np
import inspect
from utils import functionStat

#Collection of variables in class
class bus:
    def __init__(self, DATA=8, WORDS=4, ADDR=8, UPPER=2**8-4, LOWER=4, OFFSET=8):
        self.bus   = varfifo.bus(DATA=DATA, WORDS=WORDS, ADDR=ADDR, UPPER=UPPER, LOWER=LOWER, OFFSET=OFFSET)
        self.DATA   = DATA
        self.WORDS  = WORDS
        self.ADDR   = ADDR
        self.UPPER  = UPPER
        self.LOWER  = LOWER
        self.OFFSET = OFFSET
        
    @block
    def varlane(self, clkS, clkL, rst):
        functionStat(inspect.currentframe().f_code.co_name, __name__)
        varfifo0Inst   = self.bus.one2many(clkS, clkL, rst)
        varfifo1Inst   = self.bus.many2one(clkS, clkL, rst)
    
        return instances()

@block    
def varlane(clkS, clkL, rst, laneBus):
    functionStat(inspect.currentframe().f_code.co_name, __name__)
    laneInst = laneBus.varlane(clkS, clkL, rst)
    return instances()

        
    