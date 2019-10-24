from myhdl import block, Signal, intbv, modbv, delay, instance, instances, always_comb, always_seq, always
from gluelogic import fifo
from random import randrange
import numpy as np
import inspect
from utils import functionStat

#Collection of variables in class
class bus:
    def __init__(self, DATA=8, ADDR=8, UPPER=2**8-4, LOWER=4, OFFSET=8):
        self.busA   = fifo.bus(DATA=DATA, ADDR=ADDR, UPPER=UPPER, LOWER=LOWER, OFFSET=OFFSET)
        self.busB   = fifo.bus(DATA=DATA, ADDR=ADDR, UPPER=UPPER, LOWER=LOWER, OFFSET=OFFSET)
        self.DATA   = DATA
        self.ADDR   = ADDR
        self.UPPER  = UPPER
        self.LOWER  = LOWER
        self.OFFSET = OFFSET
        
    @block
    def lane(self, clkA, clkB, rst):
        functionStat(inspect.currentframe().f_code.co_name, __name__)
    
        busC   = fifo.bus(DATA=self.DATA, ADDR=self.ADDR, UPPER=self.UPPER, LOWER=self.LOWER, OFFSET=self.OFFSET)
        busD   = fifo.bus(DATA=self.DATA, ADDR=self.ADDR, UPPER=self.UPPER, LOWER=self.LOWER, OFFSET=self.OFFSET)
        fifoCInst   = busC.fifo(clkA, clkB, rst)
        fifoDInst   = busD.fifo(clkB, clkA, rst)
        connCInst   = busC.busConnect(self.busA, self.busB)
        connDInst   = busD.busConnect(self.busB, self.busA)
        
        return instances()

@block    
def lane(clkA, clkB, rst, laneBus):
    functionStat(inspect.currentframe().f_code.co_name, __name__)
    laneInst = laneBus.lane(clkA, clkB, rst)
    return instances()

        
    