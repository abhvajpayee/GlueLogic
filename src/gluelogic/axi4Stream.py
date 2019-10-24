from myhdl import block, Signal, intbv, modbv, delay, instance, instances, always_comb, always_seq, always
from gluelogic import lane
from random import randrange
import inspect
from utils import functionStat
import numpy as np
np.set_printoptions(formatter={'int':hex})

class bus:
    def __init__(self, DATA=8, WORDS=4, ADDR=8, UPPER=2**8-4, LOWER=4, OFFSET=8, U_SIZE=1):
        self.tvalid  = Signal(bool(0))
        self.tready  = Signal(bool(0))
        self.tdata   = Signal(modbv(0)[DATA*WORDS:])
        self.tkeep   = Signal(modbv(0)[WORDS:])
        self.tlast   = Signal(bool(0))
        self.tuser   = Signal(modbv(0)[U_SIZE:])
        self.DATA    = DATA
        self.WORDS   = WORDS
        self.ADDR    = ADDR
        self.UPPER   = UPPER
        self.LOWER   = LOWER
        self.OFFSET  = OFFSET
        self.U_SIZE  = U_SIZE
        
    @block
    def sConnector(self, axiBus):
        functionStat(inspect.currentframe().f_code.co_name, __name__)
        @always_comb
        def logic():
            self.tvalid.next   = axiBus.tvalid
            axiBus.tready.next = self.tready
            self.tdata.next    = axiBus.tdata
            self.tkeep.next    = axiBus.tkeep
            self.tlast.next    = axiBus.tlast
            self.tuser.next    = axiBus.tuser
        return instances()
    
    @block  
    def muxT(self, clk, rst, axiBusA, axiBusB, en, sel):

        @always_seq(clk.posedge, reset = rst)
        def muxlogic():
            if en:
                if sel:
                    axiBusA.tready.next = self.tready  
                    axiBusB.tready.next = 0
                    self.tvalid.next    = axiBusA.tvalid
                    self.tdata.next     = axiBusA.tdata
                    self.tlast.next     = axiBusA.tlast
                    self.tkeep.next     = axiBusA.tkeep
                    self.tuser.next     = axiBusA.tuser  
                else:
                    axiBusA.tready.next = 0 
                    axiBusB.tready.next = self.tready 
                    self.tvalid.next    = axiBusB.tvalid
                    self.tdata.next     = axiBusB.tdata
                    self.tlast.next     = axiBusB.tlast
                    self.tkeep.next     = axiBusB.tkeep
                    self.tuser.next     = axiBusB.tuser  
            else:
                axiBusA.tready.next = 0 
                axiBusB.tready.next = 0 
                self.tvalid.next    = 0
                self.tdata.next     = 0
                self.tlast.next     = 0
                self.tkeep.next     = 0
                if sel:
                    self.tuser.next  = axiBusA.tuser  
                else:
                    self.tuser.next  = axiBusB.tuser  
        return instances()

    @block  
    def demuxT(self, clk, rst, axiBusA, axiBusB, sel):
                
        @always_seq(clk.posedge, reset = rst)
        def demuxlogic():
            if sel:
                self.tready.next    = axiBusA.tready
                axiBusA.tvalid.next = self.tvalid
                axiBusA.tdata.next  = self.tdata
                axiBusA.tlast.next  = self.tlast
                axiBusA.tkeep.next  = self.tkeep
                axiBusA.tuser.next  = self.tuser  
                axiBusB.tvalid.next = 0
                axiBusB.tdata.next  = 0
                axiBusB.tlast.next  = 0
                axiBusB.tkeep.next  = 0
                axiBusB.tuser.next  = 0
            else:
                self.tready.next    = axiBusB.tready
                axiBusB.tvalid.next = self.tvalid
                axiBusB.tdata.next  = self.tdata
                axiBusB.tlast.next  = self.tlast
                axiBusB.tkeep.next  = self.tkeep
                axiBusB.tuser.next  = self.tuser
                axiBusA.tvalid.next = 0
                axiBusA.tdata.next  = 0
                axiBusA.tlast.next  = 0
                axiBusA.tkeep.next  = 0
                axiBusA.tuser.next  = 0
            
        return instances()

    @block
    def axi2fifo(self, clk, rst, fifoBus):
        functionStat(inspect.currentframe().f_code.co_name, __name__)
        @always_comb
        def writeLogic():
            self.tready.next = not fifoBus.inbusy
            if self.tvalid:
                fifoBus.din.next = self.tdata
                fifoBus.we.next  = 1
            else:
                fifoBus.din.next = 0
                fifoBus.we.next  = 0
        return instances()
    
    @block
    def fifo2axi(self, clk, rst, fifoBus):
        functionStat(inspect.currentframe().f_code.co_name, __name__)
        readFlag = Signal(bool(0))
        
        @always_comb
        def readLogic():
            fifoBus.rd.next = self.tready and readFlag
            self.tvalid.next = fifoBus.rdout
            if fifoBus.rdout:
                self.tdata.next = fifoBus.dout
                self.tkeep.next = 0xFFFFFFFFFFFFFFFF
                self.tlast.next = fifoBus.outbusy
            else:
                self.tdata.next = 0x0
                self.tkeep.next = 0x0
                self.tlast.next = 0x0
                
        @always_seq(clk.posedge, reset = rst)
        def readSeqLogic():
            if fifoBus.hfull:
                readFlag.next = 1
            if fifoBus.outbusy:
                readFlag.next = 0
        return instances()

@block    
def axi2fifo(clk, rst, axiBus, fifoBus):
    functionStat(inspect.currentframe().f_code.co_name, __name__)
    axi2fifoInst = axiBus.axi2fifo(clk, rst, fifoBus)
    return instances()

@block    
def fifo2axi(clk, rst, axiBus, fifoBus):
    functionStat(inspect.currentframe().f_code.co_name, __name__)
    fifo2axiInst = axiBus.fifo2axi(clk, rst, fifoBus)
    return instances()

class axi4Stream:
    def __init__(self, DATA=8, WORDS=4, ADDR=8, UPPER=2**8-4, LOWER=4, OFFSET=8, U_SIZE=1):
        self.axiMBus = bus(DATA=DATA, WORDS=WORDS, ADDR=ADDR, UPPER=UPPER, LOWER=LOWER, OFFSET=OFFSET, U_SIZE=U_SIZE)
        self.axiSBus = bus(DATA=DATA, WORDS=WORDS, ADDR=ADDR, UPPER=UPPER, LOWER=LOWER, OFFSET=OFFSET, U_SIZE=U_SIZE)
        self.laneBus = lane.bus(DATA=DATA*WORDS, ADDR=ADDR, UPPER=UPPER, LOWER=LOWER, OFFSET=OFFSET)
        
        self.DATA    = DATA
        self.WORDS   = WORDS
        self.ADDR    = ADDR
        self.UPPER   = UPPER
        self.LOWER   = LOWER
        self.OFFSET  = OFFSET
        self.U_SIZE  = U_SIZE

    def clone(self):
        return axi4Stream(DATA=self.DATA, WORDS=self.WORDS,
                          ADDR=self.ADDR, UPPER=self.UPPER,
                          LOWER=self.LOWER, OFFSET=self.OFFSET,
                          U_SIZE=self.U_SIZE)
        
    @block
    def connector(self, axi4StreamBus):
        functionStat(inspect.currentframe().f_code.co_name, __name__)
        sConnectorInst = self.axiSBus.sConnector(axi4StreamBus.axiMBus)
        mConnectorInst = axi4StreamBus.axiSBus.sConnector(self.axiMBus)
        return instances()
    
    @block
    def connectorT(self, clk, rst, axi4StreamBus, axi4StreamBusDown, en, sel):
        functionStat(inspect.currentframe().f_code.co_name, __name__)
        muxTInst   = self.axiSBus.demuxT  (clk, rst, axi4StreamBus.axiSBus, axi4StreamBusDown.axiSBus, sel)
        demuxTInst = self.axiMBus.muxT    (clk, rst, axi4StreamBus.axiMBus, axi4StreamBusDown.axiMBus, en, sel)
        return instances()
    
    @block
    def axi2lane(self, clk, rst):
        functionStat(inspect.currentframe().f_code.co_name, __name__)
        axi2fifoInst = self.axiSBus.axi2fifo(clk, rst, self.laneBus.busA)
        fifo2axiInst = self.axiMBus.fifo2axi(clk, rst, self.laneBus.busA)
        laneInst     = lane.lane(clk, clk, rst, self.laneBus)
        return instances()
        
@block    
def axi2lane(clk, rst, axi4StreamBus):
    functionStat(inspect.currentframe().f_code.co_name, __name__)
    axi2laneInst = axi4StreamBus.axi2lane(clk, rst)
    return instances()

def toModbv(data, DATA = 512):
    i = 0
    vector = 0
    vectors = []
    for d in data:
        vector ^= int(d) << (i * 64)
        i += 1
        if i == int(DATA/64):
            i = 0
            vectors.append(modbv(vector)[DATA:])
            vector = 0
    return vectors    

