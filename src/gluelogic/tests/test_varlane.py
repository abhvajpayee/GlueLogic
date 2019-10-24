from myhdl import *
from gluelogic import fifo, varlane
from gluelogic.clock import clockDriver
from gluelogic import hdlcfg

ADDR  = 5
WORDS = 4
DATA  = 8
LOWER = 2               #lower limit for FIFO read
UPPER = (2**ADDR)-4     #upper limit for FIFO write
OFFSET = 8
DELAY  = 5
SIMULATION=True

@block
def varlaneBench(SYNCWRITE=False, SYNCREAD=False):
    laneBus = varlane.bus(DATA=DATA, ADDR=ADDR, UPPER=UPPER, LOWER=LOWER, OFFSET=OFFSET)
    clkS = Signal(bool(0))
    clkL = Signal(bool(0))
    rst   = ResetSignal(0, active=1, isasync=False)
    
    
    clkSInst   = clockDriver(clkS, DELAY = 5)
    clkLInst   = clockDriver(clkL, DELAY = 8)
    laneInst   = varlane.varlane(clkS, clkL, rst, laneBus)
    laneInst.convert(hdl='Verilog', header=hdlcfg.header, directory=hdlcfg.hdl_path)
    
    fifoTesterInst   = laneBus.bus.busS.tester(clkS, clkS, rst,
                                               PRINTLOG=False, SYNCWRITE=SYNCWRITE,
                                               SYNCREAD=SYNCREAD, inbuff =[], outbuff=[],
                                               SLOWFACTOR=2)
    LanePlugInst = laneBus.bus.busL.connector(clkL, rst)
    
    @instance
    def stimulus():
        yield delay(10)
        yield clkS.posedge
        rst.next = rst.active
        yield clkS.posedge
        rst.next = not rst.active
    
    return instances()

def test0():
    tb1 = varlaneBench()
    tb1.config_sim(trace= True)
    tb1.run_sim(duration=10000)
    tb1.quit_sim()


#def test1():
#    assert fifoBench().verify_convert() == 0
    
if __name__ == '__main__':
    test0()
    #test1()
