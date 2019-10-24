from myhdl import * 
from gluelogic import axi4Stream, axi4Node, lane, fifo
from gluelogic.clock import clockDriver
from gluelogic import hdlcfg
from random import randrange
import numpy as np
np.set_printoptions(formatter={'int':hex})


ADDR   = 5
WORDS  = 64
DATA   = 8
LOWER  = 2               #lower limit for FIFO read
UPPER  = (2**ADDR)-4     #upper limit for FIFO write
OFFSET = 8
DELAY  = 5
U_SIZE = 1
SIMULATION=True


@block
def axi4NodeBench(packet, SYNCWRITE=False, SYNCREAD=False):
    clk = Signal(bool(0))
    rst   = ResetSignal(0, active=1, isasync=False)
    
    clkInst   = clockDriver(clk, DELAY = 5)
    axi4StreamBus0 = axi4Stream.axi4Stream(DATA=DATA, WORDS=WORDS,
                                           ADDR=ADDR, UPPER=UPPER,
                                           LOWER=LOWER, OFFSET=OFFSET,
                                           U_SIZE=U_SIZE)
    axi4StreamBus1 = axi4StreamBus0.clone()
    axi4StreamBus2 = axi4StreamBus0.clone()
    
    
    fifoBus0 = fifo.bus(DATA=DATA*WORDS, ADDR=ADDR, UPPER=UPPER, LOWER=LOWER, OFFSET=OFFSET)
    fifoBus1 = fifo.bus(DATA=DATA*WORDS, ADDR=ADDR, UPPER=UPPER, LOWER=LOWER, OFFSET=OFFSET)
    fifoBus2 = fifo.bus(DATA=DATA*WORDS, ADDR=ADDR, UPPER=UPPER, LOWER=LOWER, OFFSET=OFFSET)
    
    axi4Node0 = axi4Node.node(clk, rst, axi4StreamBus0, fifoBus0)
    axi4Node1 = axi4Node.tNode(clk, rst, axi4StreamBus1, axi4StreamBus2, fifoBus1, ADDRESS=0xFF, PRIORITY=1)
    axi4Node2 = axi4Node.node(clk, rst, axi4StreamBus2, fifoBus2)    
    
    fifoTesterInst   = fifoBus0.tester(clk, clk, rst,
                                       PRINTLOG=False, SYNCWRITE=SYNCWRITE,
                                       SYNCREAD=SYNCREAD, inbuff =packet, outbuff=[],
                                       SLOWFACTOR=2)
    axiConnectorInst = axi4StreamBus0.connector(axi4StreamBus1)
    fifoPlugInst0 = fifoBus1.connector(clk, rst)
    fifoPlugInst1 = fifoBus2.connector(clk, rst)
    
    @instance
    def stimulus():
        yield delay(10)
        yield clk.posedge
        rst.next = rst.active
        yield clk.posedge
        rst.next = not rst.active
    
    return instances()

def test0():
    randomData = np.array([randrange(0, 2**64) for i in range(512)], dtype=np.uint64)
    src = 0xEE
    dest = 0xFF
    algo = 0xAB
    mode = 0xDE
    pktid = randrange(0, 2**16)
    packet = axi4Node.packetize(randomData, src, dest, algo, mode, pktid, DATA = 512)
    packet = axi4Stream.toModbv(packet, DATA = 512)
    for i in packet:
        print(i)
    tb1 = axi4NodeBench(packet)
    tb1.config_sim(trace= True)
    tb1.run_sim(duration=10000)
    tb1.quit_sim()


#def test1():
#    assert fifoBench().verify_convert() == 0
    
if __name__ == '__main__':
    test0()
    #test1()
