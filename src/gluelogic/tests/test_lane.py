from myhdl import *
from gluelogic import fifo, lane
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
def laneBench(SYNCWRITE=False, SYNCREAD=False):
    laneBus = lane.bus(DATA=DATA, ADDR=ADDR, UPPER=UPPER, LOWER=LOWER, OFFSET=OFFSET)
    clkA = Signal(bool(0))
    clkB = Signal(bool(0))
    rst   = ResetSignal(0, active=1, isasync=False)
    
    
    clkAInst   = clockDriver(clkA, DELAY = 5)
    clkBInst   = clockDriver(clkB, DELAY = 8)
    laneInst   = lane.lane(clkA, clkB, rst, laneBus)
    laneInst.convert(hdl='Verilog', header=hdlcfg.header, directory=hdlcfg.hdl_path, name='lane')
    
    fifoTesterInst   = laneBus.busA.tester(clkA, clkA, rst,
                                           PRINTLOG=False, SYNCWRITE=SYNCWRITE,
                                           SYNCREAD=SYNCREAD, inbuff =[], outbuff=[],
                                           SLOWFACTOR=2)
    LanePlugInst = laneBus.busB.connector(clkB, rst)
    
    @instance
    def stimulus():
        yield delay(10)
        yield clkB.posedge
        rst.next = rst.active
        yield clkB.posedge
        rst.next = not rst.active
    
    return instances()

def test0():
    tb1 = laneBench()
    tb1.config_sim(trace= True)
    tb1.run_sim(duration=10000)
    tb1.quit_sim()


#def test1():
#    assert fifoBench().verify_convert() == 0
    
if __name__ == '__main__':
    test0()
    #test1()
