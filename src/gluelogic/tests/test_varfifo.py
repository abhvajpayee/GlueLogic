from myhdl import *
from gluelogic import varfifo
from gluelogic.clock import clockDriver
from gluelogic import hdlcfg
from random import randrange

ADDR  = 5
DATA  = 8
WORDS = 2
LOWER = 2               #lower limit for FIFO read
UPPER = (2**ADDR)-4     #upper limit for FIFO write
OFFSET = 8
DELAY  = 5
SIMULATION=True

@block
def varfifoBench(SYNCWRITE=False, SYNCREAD=False):
    varfifoBus = varfifo.bus(DATA=DATA, WORDS=WORDS, ADDR=ADDR, UPPER=UPPER, LOWER=LOWER, OFFSET=OFFSET)
    
    clkS = Signal(bool(0))
    clkL = Signal(bool(0))
    rst   = ResetSignal(0, active=1, isasync=False)
    
    
    clkSInst   = clockDriver(clkS, DELAY = 5)
    clkLInst   = clockDriver(clkL, DELAY = 8)
    varfifo0Inst   = varfifoBus.one2many(clkS, clkL, rst)
    varfifo1Inst   = varfifoBus.many2one(clkS, clkL, rst)
    
    #varfifo0Inst.convert(hdl='Verilog', header=hdlcfg.header, directory=hdlcfg.hdl_path)
    #varfifo1Inst.convert(hdl='Verilog', header=hdlcfg.header, directory=hdlcfg.hdl_path)
    
    fifoTesterInst   = varfifoBus.busS.tester(clkS, clkS, rst,
                                              PRINTLOG=False,
                                              SYNCWRITE=SYNCWRITE,
                                              SYNCREAD=SYNCREAD, 
                                              inbuff =[Signal(modbv(randrange(2**DATA))) for i in range(1024)],
                                              outbuff=[], SLOWFACTOR=2)
    LanePlugInst = varfifoBus.busL.connector(clkL, rst)
    
    @instance
    def stimulus():
        yield delay(10)
        yield clkL.posedge
        rst.next = rst.active
        yield clkL.posedge
        rst.next = not rst.active
    
    return instances()

def test0():
    tb1 = varfifoBench()
    tb1.config_sim(trace= True)
    tb1.run_sim(duration=100000)
    tb1.quit_sim()


#def test1():
#    assert fifoBench().verify_convert() == 0
    
if __name__ == '__main__':
    test0()
    #test1()
