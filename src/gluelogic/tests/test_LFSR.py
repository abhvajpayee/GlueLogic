import os
from myhdl import block, Signal, intbv, delay, instance, always_comb, instances, ResetSignal, StopSimulation, always, now
from random import randrange
#from pyhdl import gluelogic
from gluelogic.LFSR import LFSR
from gluelogic.clock import clockDriver


@block
def LFSRBench(LFSR = LFSR):
    dout  = Signal(bool(0))
    din   = Signal(bool(0))
    run   = Signal(bool(0))
    ready = Signal(bool(0))
    clk   = Signal(bool(0))
    rst   = ResetSignal(0, active=1, isasync=False)
    SIZE  = 65
    TRINOMIAL = 18
    IV    = 0x00000000000001111
    clkInst = clockDriver(clk, DELAY = 5)
    lfsrInst = LFSR(dout, din, run, ready, clk, rst, SIZE, TRINOMIAL, IV)

    @instance
    def stimulus():
        yield delay(10)
        yield clk.posedge
        rst.next = rst.active
        yield clk.posedge
        rst.next = not rst.active
        
        din.next = 0
        for i in range(10):
            yield clk.posedge
            print("%d" % now()) #, "%d" % dout) #, "%d" % ready)
            pass
        
        raise StopSimulation()
        #    run.next = 1
        #    #print "B: " + bin(B, width) + "| G_v: " + bin(G_v, width)
        #    #print bin(G, width)
        #    #print bin(G_v, width)
        #    #print("%d" % G)
        #    print("%d" % dout, "%d" % ready)
        #    #assert B == B2, "Error occured !!"
        

    return instances()


def test0():
    tb = LFSRBench(LFSR = LFSR)
    tb.config_sim(trace= True)
    tb.run_sim(duration=1000)
    tb.quit_sim()
    
#def test1():
#    assert LFSRBench(LFSR = LFSR).verify_convert() == 0
