from myhdl import *
from gluelogic import fifo
from gluelogic.clock import clockDriver
from gluelogic import hdlcfg

ADDR  = 5
DATA  = 8
LOWER = 2               #lower limit for FIFO read
UPPER = (2**ADDR)-4     #upper limit for FIFO write
OFFSET = 8
DELAY  = 5
SIMULATION=True

@block
def fifoBench(SYNCWRITE=False, SYNCREAD=False):
    fifoBus = fifo.bus(DATA=DATA, ADDR=ADDR, UPPER=UPPER, LOWER=LOWER, OFFSET=OFFSET)
    inclk = Signal(bool(0))
    outclk = Signal(bool(0))
    rst   = ResetSignal(0, active=1, isasync=False)
    
    
    inclkInst  = clockDriver(inclk, DELAY = 5)
    outclkInst = clockDriver(outclk, DELAY = 8)
    fifoInst   = fifoBus.fifo(inclk, outclk, rst)
    fifoTesterInst   = fifoBus.tester(inclk, outclk, rst, 
                                      PRINTLOG=False, SYNCWRITE=SYNCWRITE,
                                      SYNCREAD=SYNCREAD, inbuff =[], outbuff=[],
                                      SLOWFACTOR=2)
    
    @instance
    def stimulus():
        yield delay(10)
        yield outclk.posedge
        rst.next = rst.active
        yield outclk.posedge
        rst.next = not rst.active
    
    return instances()

def test0():
    tb1 = fifoBench()
    tb1.config_sim(trace= True)
    tb1.run_sim(duration=10000)
    tb1.quit_sim()


#def test1():
#    assert fifoBench().verify_convert() == 0
    
if __name__ == '__main__':
    test0()
    #test1()
