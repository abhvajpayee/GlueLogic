from myhdl import * 
from gluelogic import axi4Stream, varlane
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
def axi4StreamBench(packet, SYNCWRITE=False, SYNCREAD=False):
    clk = Signal(bool(0))
    rst   = ResetSignal(0, active=1, isasync=False)
    
    clkInst   = clockDriver(clk, DELAY = 5)
    axi4StreamBus0 = axi4Stream.axi4Stream(DATA=DATA, WORDS=WORDS,
                                    ADDR=ADDR, UPPER=UPPER,
                                    LOWER=LOWER, OFFSET=OFFSET,
                                    U_SIZE=U_SIZE)
    axi4StreamBus1 = axi4Stream.axi4Stream(DATA=DATA, WORDS=WORDS,
                                    ADDR=ADDR, UPPER=UPPER,
                                    LOWER=LOWER, OFFSET=OFFSET,
                                    U_SIZE=U_SIZE)
    
    axi2lane0 = axi4Stream.axi2lane(clk, rst, axi4StreamBus0)
    axi2lane1 = axi4Stream.axi2lane(clk, rst, axi4StreamBus1)
    
    
    fifoTesterInst   = axi4StreamBus0.laneBus.busB.tester(clk, clk, rst,
                                               PRINTLOG=False, SYNCWRITE=SYNCWRITE,
                                               SYNCREAD=SYNCREAD, inbuff =packet, outbuff=[],
                                               SLOWFACTOR=2)
    axiConnectorInst = axi4StreamBus0.connector(axi4StreamBus1)
    LanePlugInst = axi4StreamBus1.laneBus.busB.connector(clk, rst)
    
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
    #src = 0xEE
    #dest = 0xFF
    #algo = 0xAB
    #mode = 0xDE
    #pktid = randrange(0, 2**16)
    #packet = axi4Stream.packetize(randomData, src, dest, algo, mode, pktid, DATA = 512)
    packet = axi4Stream.toModbv(randomData, DATA = 512)
    for i in packet:
        print(i)
    tb1 = axi4StreamBench(packet)
    tb1.config_sim(trace= True)
    tb1.run_sim(duration=10000)
    tb1.quit_sim()


#def test1():
#    assert fifoBench().verify_convert() == 0
    
if __name__ == '__main__':
    test0()
    #test1()
