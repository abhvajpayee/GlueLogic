from myhdl import block, Signal, intbv, modbv, delay, instance, instances, always_comb, always_seq, always
from gluelogic.grayCode import bin2gray, gray2bin
from random import randrange
import numpy as np
import inspect
from utils import functionStat

#Collection of variables in class
class bus:
    def __init__(self, DATA=8, ADDR=8, UPPER=2**8-4, LOWER=4, OFFSET=8):
        self.inbusy  = Signal(bool(0))
        self.we      = Signal(bool(0))
        self.din     = Signal(modbv(0)[DATA:])
        self.outbusy = Signal(bool(0))
        self.rd      = Signal(bool(0))
        self.dout    = Signal(modbv(0)[DATA:])
        self.rdout   = Signal(bool(0))
        self.hfull   = Signal(bool(0))
        self.length  = Signal(modbv(0)[ADDR+1:])
        self.DATA    = DATA
        self.ADDR    = ADDR
        self.UPPER   = UPPER
        self.LOWER   = LOWER
        self.OFFSET  = OFFSET

    '''@block
    def toBus(self, inbusy, we, din, outbusy, rd, dout, rdout, hfull):        
        functionStat(inspect.currentframe().f_code.co_name, __name__)
        @always_comb
        def logic():
            inbusy.next = self.inbusy
            self.we.next = we
            self.din.next = din
            outbusy.next = self.outbusy
            self.rd.next = rd
            dout.next = self.dout
            rdout.next = self.rdout
            hfull.next = self.hfull
        return instances()'''
    
    @block
    def toBus(self, fifoBus):        
        functionStat(inspect.currentframe().f_code.co_name, __name__)
        @always_comb
        def logic():
            fifoBus.inbusy.next = self.inbusy
            self.we.next = fifoBus.we
            self.din.next = fifoBus.din
            fifoBus.outbusy.next = self.outbusy
            self.rd.next = fifoBus.rd
            fifoBus.dout.next = self.dout
            fifoBus.rdout.next = self.rdout
            fifoBus.hfull.next = self.hfull
        return instances()
    
    
    @block
    def fifo(self, inclk, outclk, rst):
        functionStat(inspect.currentframe().f_code.co_name, __name__)
    
        mem             = [Signal(modbv(0)[self.DATA:]) for i in range(2**self.ADDR)]
        in_addr         = Signal(modbv(0)[self.ADDR+1:])
        out_addr        = Signal(modbv(0)[self.ADDR+1:])
        in_addr_1       = Signal(modbv(0)[self.ADDR+1:])
        out_addr_1      = Signal(modbv(0)[self.ADDR+1:])
        in_addr_gray    = Signal(modbv(0)[self.ADDR+1:])
        out_addr_gray   = Signal(modbv(0)[self.ADDR+1:])
        in_addr_gray_1  = Signal(modbv(0)[self.ADDR+1:])
        out_addr_gray_1 = Signal(modbv(0)[self.ADDR+1:])
        in_addr_gray_2  = Signal(modbv(0)[self.ADDR+1:])
        out_addr_gray_2 = Signal(modbv(0)[self.ADDR+1:])
        next_in_addr    = Signal(modbv(0)[self.ADDR+1:])
        next_out_addr   = Signal(modbv(0)[self.ADDR+1:])
        in_length       = Signal(modbv(0)[self.ADDR:])
        out_length      = Signal(modbv(0)[self.ADDR:])
        canread         = Signal(bool(0))
        inMsbflag       = Signal(bool(0))
        outMsbflag      = Signal(bool(0))

        bin2gray0_inst  = bin2gray(in_addr,         in_addr_gray,  DATA = self.ADDR+1)
        bin2gray1_inst  = bin2gray(out_addr,        out_addr_gray, DATA = self.ADDR+1)
        gray2bin0_inst  = gray2bin(in_addr_gray_2,  in_addr_1,     DATA = self.ADDR+1)
        gray2bin1_inst  = gray2bin(out_addr_gray_2, out_addr_1,    DATA = self.ADDR+1)

        @always_seq(inclk.posedge, reset = rst)
        def in_addr_two_ff_sync():
            out_addr_gray_1.next = out_addr_gray
            out_addr_gray_2.next = out_addr_gray_1

        @always_seq(outclk.posedge, reset = rst)
        def out_addr_two_ff_sync():
            self.length.next = out_length
            in_addr_gray_1.next = in_addr_gray
            in_addr_gray_2.next = in_addr_gray_1

        @always_comb
        def diffLogic():
            in_length.next = in_addr - out_addr_1
            out_length.next = in_addr_1 - out_addr

        @always_comb
        def writeLogic():
            self.inbusy.next = in_length >= self.UPPER-1
            next_in_addr.next = in_addr
            if self.we:
                next_in_addr.next = in_addr + 1

        @always_comb
        def readLogic2():
            canread.next = (out_length > 0) and self.rd and not self.outbusy

        @always_comb
        def readLogic():
            next_out_addr.next = out_addr
            self.hfull.next = out_length >= self.OFFSET
            if out_length >= self.LOWER:
                self.outbusy.next = 0
            elif out_length < 1:
                self.outbusy.next = 1
            if canread:
                next_out_addr.next = out_addr + 1

        @always(inclk.posedge)
        def writemem():
            if self.we:
                mem[in_addr[self.ADDR:0]].next = self.din

        @always(outclk.posedge)
        def readmem():
            self.dout.next  = 0
            self.rdout.next = 0
            if canread:
                self.dout.next = mem[out_addr[self.ADDR:0]]
                self.rdout.next = 1

        @always_seq(inclk.posedge, reset = rst)
        def write():
            in_addr.next = next_in_addr
            outMsbflag.next = outMsbflag
            if not in_addr[self.ADDR] and not out_addr_1[self.ADDR]:
                outMsbflag.next = 0
            if out_addr_1[self.ADDR]:
                outMsbflag.next = 1
            if in_addr[self.ADDR] and outMsbflag:
                in_addr.next = next_in_addr[self.ADDR:]
                outMsbflag.next = 0

        @always_seq(outclk.posedge, reset = rst)
        def read():
            out_addr.next = next_out_addr
            inMsbflag.next = inMsbflag
            if not in_addr_1[self.ADDR] and not out_addr[self.ADDR]:
                inMsbflag.next = 0
            if in_addr_1[self.ADDR]:
                inMsbflag.next = 1
            if out_addr[self.ADDR] and inMsbflag:
                out_addr.next = next_out_addr[self.ADDR:]            
                inMsbflag.next = 0

        return instances()
    
    def createbuff(self):
        return [Signal(modbv(randrange(2**self.DATA))) for i in range(400)]
        
    
    @block
    def busConnect(self, inBus, outBus):
        functionStat(inspect.currentframe().f_code.co_name, __name__)

        @always_comb
        def connectorLogic():
            inBus.inbusy.next   = self.inbusy
            self.din.next       = inBus.din
            self.we.next        = inBus.we
            outBus.outbusy.next = self.outbusy
            self.rd.next        = outBus.rd
            outBus.dout.next    = self.dout
            outBus.rdout.next   = self.rdout
            outBus.hfull.next   = self.hfull
            outBus.length.next  = self.length
            
        return instances()
    
    @block
    def connector(self, clk, rst):
        functionStat(inspect.currentframe().f_code.co_name, __name__)

        readFlag = Signal(bool(0))
        @always_comb
        def connectorLogic():
            self.din.next = self.dout
            self.we.next = self.rdout
            self.rd.next = not self.outbusy and not self.inbusy and readFlag

        @always_seq(clk.posedge, reset = rst)
        def Logic():
            if self.hfull:
                readFlag.next = 1
            if self.outbusy:
                readFlag.next = 0
        return instances()
    
    @block
    def tester(self, inclk, outclk, rst, PRINTLOG=False, SYNCWRITE=False,
               SYNCREAD=False, inbuff =[], outbuff=[], SLOWFACTOR=2):
        functionStat(inspect.currentframe().f_code.co_name, __name__)
        
        if len(inbuff):
            fifobuff = inbuff
        else:
            fifobuff =self.createbuff()
            
        if len(outbuff):
            respbuff = outbuff
        else:
            respbuff = fifobuff
        
        #Write driver for fifo    
        @instance
        def write():
            self.we.next = 0
            yield delay(50)
            i = 0
            while 1:
                yield inclk.posedge
                if not self.inbusy and ( SYNCWRITE or np.random.choice(SLOWFACTOR) == 0):
                    self.we.next = 1
                    self.din.next = fifobuff[i]
                    i += 1
                else:
                    self.we.next = 0
                    self.din.next = 0
                if i == len(fifobuff):
                    break
            yield inclk.posedge
            self.we.next = 0

        #Read driver for fifo
        @instance
        def read():
            self.rd.next = 0
            yield outclk.posedge
            while(self.hfull == 0):
                yield outclk.posedge
                pass
            yield outclk.posedge      #Extra delay is introduced to check hfull,else hfull is always one,length never dec. below '8'
            i = 0
            while(1):
                yield outclk.posedge
                if not self.outbusy and (SYNCREAD or np.random.choice(2)):
                    self.rd.next = 1
                else:
                    self.rd.next = 0                   
                if self.rdout:
                    if PRINTLOG:
                        print(hex(self.dout), hex(respbuff[i]))
                    else:
                        #print(dout, modbv(respbuff[i]), i)
                        assert hex(self.dout) == hex(respbuff[i])
                    i += 1;
                if i == len(respbuff):
                    break

            yield outclk.posedge
            self.rd.next = 0
        
        @always_comb
        def printlogic():
            if PRINTLOG:
                if self.inbusy:
                    print('Overflow')
                if self.outbusy:
                    print('Underflow')

        return instances()
