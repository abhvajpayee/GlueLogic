from myhdl import block, Signal, intbv, modbv, delay, instance, instances, always_comb, always_seq, always, ConcatSignal
from gluelogic.grayCode import bin2gray, gray2bin
from random import randrange
import numpy as np
import math
from gluelogic import fifo, mux 
import inspect
from utils import functionStat
#Collection of variables in class
class bus:
    def __init__(self, DATA=8, WORDS=4, ADDR=8, UPPER=2**8-4, LOWER=4, OFFSET=8):
        self.busS   = fifo.bus(DATA=DATA, ADDR=ADDR, UPPER=UPPER, LOWER=LOWER, OFFSET=OFFSET)
        self.busL   = fifo.bus(DATA=DATA*WORDS, ADDR=ADDR, UPPER=UPPER, LOWER=LOWER, OFFSET=OFFSET)
        self.DATA   = DATA
        self.WORDS  = WORDS
        self.ADDR   = ADDR
        self.UPPER  = UPPER
        self.LOWER  = LOWER
        self.OFFSET = OFFSET

    
    @block
    def one2many(self, clkS, clkL, rst):
        functionStat(inspect.currentframe().f_code.co_name, __name__)
        count = Signal(modbv(0)[math.ceil(math.log(self.WORDS,2)):])
        inbusy_t  = [Signal(bool(0)) for i in range(self.WORDS)]
        we_t      = [Signal(bool(0)) for i in range(self.WORDS)]
        din_t     = [Signal(modbv(0)[self.DATA:]) for i in range(self.WORDS)]
        outbusy_t = [Signal(bool(0)) for i in range(self.WORDS)]
        rd_t      = [Signal(bool(0)) for i in range(self.WORDS)]
        dout_t    = [Signal(modbv(0)[self.DATA:]) for i in range(self.WORDS)]
        rdout_t   = [Signal(bool(0)) for i in range(self.WORDS)]
        hfull_t   = [Signal(bool(0)) for i in range(self.WORDS)]
        
        fifo_inst = [None for i in range(self.WORDS)]
        toBus_inst = [None for i in range(self.WORDS)]
        busC   = [fifo.bus(DATA=self.DATA, ADDR=self.ADDR, UPPER=self.UPPER,
                           LOWER=self.LOWER, OFFSET=self.OFFSET) for i in range(self.WORDS)]
        
        demux_t = mux.demux(self.busS.we, we_t, count, BITS = self.WORDS)
        
        for i in range(self.WORDS):
            fifo_inst[i] = busC[i].fifo(clkS, clkL, rst)
            toBus_inst[i] = busC[i].toBus(inbusy_t[i], we_t[i], din_t[i],
                                                 outbusy_t[i], rd_t[i], dout_t[i], rdout_t[i], hfull_t[i])
            
        p = [dout_t[i](j) for i in reversed(range(self.WORDS)) for j in reversed(range(self.DATA))]
        q = ConcatSignal(*p)
        print(type(busC[0].inbusy))
        @always_comb
        def logic():
            self.busS.inbusy.next = inbusy_t[0]
            self.busL.outbusy.next = outbusy_t[self.WORDS-1]
            self.busL.hfull.next = hfull_t[self.WORDS-1]
            self.busL.rdout.next = rdout_t[0]
            for i in range(self.WORDS):
                rd_t[i].next  = self.busL.rd
                din_t[i].next = self.busS.din
            self.busL.dout.next = q

        @always_seq(clkS.posedge, reset=rst)
        def write_logic():
            if self.busS.we:
                if count == self.WORDS-1:
                    count.next = 0
                else:
                    count.next = count + 1
        return instances()

    @block
    def many2one(self, clkS, clkL, rst):
        functionStat(inspect.currentframe().f_code.co_name, __name__)
        busC   = [fifo.bus(DATA=self.DATA, ADDR=self.ADDR, UPPER=self.UPPER,
                           LOWER=self.LOWER, OFFSET=self.OFFSET) for i in range(self.WORDS)]
        
        count_rd         = Signal(modbv(0)[math.ceil(math.log(self.WORDS,2)):])
        count_rdout      = Signal(modbv(0)[math.ceil(math.log(self.WORDS,2)):])
        count_rd_next    = Signal(modbv(0)[math.ceil(math.log(self.WORDS,2)):])
        count_rdout_next = Signal(modbv(0)[math.ceil(math.log(self.WORDS,2)):])
        
        
        inbusy_t  = [Signal(bool(0)) for i in range(self.WORDS)]
        we_t      = [Signal(bool(0)) for i in range(self.WORDS)]
        din_t     = [Signal(modbv(0)[self.DATA:]) for i in range(self.WORDS)]
        outbusy_t = [Signal(bool(0)) for i in range(self.WORDS)]
        rd_t      = [Signal(bool(0)) for i in range(self.WORDS)]
        dout_t    = [Signal(modbv(0)[self.DATA:]) for i in range(self.WORDS)]
        rdout_t   = [Signal(bool(0)) for i in range(self.WORDS)]
        hfull_t   = [Signal(bool(0)) for i in range(self.WORDS)]
        outbusy_f = Signal(bool(0))
        demux_t     = mux.demux(self.busS.rd, rd_t, count_rd_next,  BITS = self.WORDS)
        mux2_t      = mux.mux(outbusy_f, outbusy_t, count_rd_next)
        rdout_mux_t = mux.mux(self.busS.rdout, rdout_t, count_rdout_next)
        dout_mux_t  = mux.mux(self.busS.dout, dout_t, count_rdout_next)    
        fifo_inst   = [None for i in range(self.WORDS)]
        toBus_inst  = [None for i in range(self.WORDS)]
        
        for i in range(self.WORDS):
            fifo_inst[i]  = busC[i].fifo(clkL, clkS, rst)
            toBus_inst[i] = busC[i].toBus(inbusy_t[i], we_t[i], din_t[i],
                                          outbusy_t[i], rd_t[i], dout_t[i], rdout_t[i], hfull_t[i])
        
        @always_comb
        def countlogic():
            count_rd.next = count_rd_next
            if self.busS.rd and not outbusy_f: #outbusy_t[self.WORDS-1]:
                count_rd.next = count_rd_next + 1
                if count_rd_next == self.WORDS:
                    count_rd.next = 0
                    
            count_rdout.next = count_rdout_next    
            if self.busS.rdout: # and not outbusy_t[self.WORDS-1]:
                count_rdout.next = count_rdout_next + 1
                if count_rdout_next == self.WORDS:
                    count_rdout.next = 0
                    
        @always_comb
        def logic():
            self.busL.inbusy.next = inbusy_t[0]
            self.busS.outbusy.next = outbusy_f #outbusy_t[self.WORDS-1]
            self.busS.hfull.next = hfull_t[self.WORDS-1]
            for i in range(self.WORDS):
                we_t[i].next  = self.busL.we
                din_t[i].next = self.busL.din[self.DATA*(i+1): self.DATA*i]
                
        @always_seq(clkS.posedge, reset=rst)
        def read_logic():
            count_rdout_next.next = count_rdout
            count_rd_next.next = count_rd

        return instances()
