import os
import sys
from myhdl import block, Signal, intbv, delay, instance, always_comb, instances, ResetSignal, StopSimulation, always, now
from random import randrange
#from pyhdl import gluelogic
from gluelogic.grayCode import bin2gray, gray2bin, signalSync, bin2grayCoSim
from gluelogic.clock import clockDriver
import tempfile
import logging
from utils import logtb
from hypothesis import given, settings
from hypothesis.strategies import text, integers, composite, lists
from hypothesis.extra import numpy as hnp
import numpy as np
DATA = 8

@block
def bin2grayBench(bin2gray = bin2gray, DATA = DATA, indata = tuple([i for i in range(2**DATA)])):

    B = Signal(intbv(0)[DATA:])
    G = Signal(intbv(0)[DATA:])
    B2 = Signal(intbv(0)[DATA:])

    bin2gray_inst = bin2gray(B, G, DATA)
    gray2bin_inst = gray2bin(G, B2, DATA)

    @instance
    def stimulus():
        for i in range(len(indata)):
            B.next = indata[i]
            yield delay(10)
            print("%d" % now(), "%d" % B, "%d" % G, "%d" % B2)
            assert B == B2, "Error occured !!"

    return instances()

@block
def signalSyncBench(DATA = DATA, indata = tuple([i for i in range(2**DATA)])):

    #n = 2**DATA
    
    dIn, dOut     = [Signal(intbv(0)[DATA:]) for i in range(2)]
    clkIn, clkOut = [Signal(bool(0))         for i in range(2)]
    rst = ResetSignal(0, active=1, isasync=False)
    
    clockDriver0_inst = clockDriver(clkIn , DELAY = 5)
    clockDriver1_inst = clockDriver(clkOut, DELAY = 7)
    signalSync_inst   = signalSync(clkOut, rst, dIn, dOut, DATA = DATA)
    
    @instance
    def ResetStimulus():
        yield delay(15)
        rst.next = rst.active
        yield delay(10)
        rst.next = not rst.active
        
        for i in indata:
            dIn.next = i
            yield clkIn.posedge
            print("%d" % dIn, "%d" % dOut)
            #assert B == B2, "Error occured !!"
        #assert False, "Error occured !!"
        raise StopSimulation()

    return instances()

@composite
def randomDataWithBusSize(draw):
    dataWidth   = draw(integers(min_value=4, max_value=32))
    values = draw(lists(integers(min_value=0, max_value=2**dataWidth-1), min_size=16, max_size=256))
    return {'dataWidth': dataWidth, 'values': values}

@given(randomDataWithBusSize())
@settings(deadline=None)
def test0(testData):
    assert bin2grayBench(bin2gray = bin2gray, 
                         DATA = testData['dataWidth'], 
                         indata=tuple(testData['values'])).verify_convert() == 0
    
def test1():
    testData = {'dataWidth': 9, 'values': [randrange(0, 2**9) for i in range(256)]}
    tb1 = bin2grayBench(bin2gray = bin2gray, DATA = testData['dataWidth'], indata=tuple(testData['values']))
    tb1.config_sim(trace= True)
    tb1.run_sim(duration=1000)
    tb1.quit_sim()


def test2():
    testData = {'dataWidth': 9, 'values': [randrange(0, 2**9) for i in range(256)]}
    tb1 = signalSyncBench(DATA = testData['dataWidth'], indata=tuple(testData['values']))
    tb1.config_sim(trace= True)
    tb1.run_sim(duration=1000)
    tb1.quit_sim()
    
#def test_Bin2Gray0(tmpdir):
#    cwd = os.getcwd()
#    os.chdir(tmpdir)
#    tb1 = bin2grayBench(bin2gray = bin2gray, DATA = 8)
#    tb2 = bin2grayBench(bin2gray = bin2grayCoSim, DATA = 8)
#    logtb(tmpdir, tb1, tb2, 4000)
#    os.chdir(cwd)   
    
#def test_Bin2Gray(tmpdir):
#    cwd = os.getcwd()
#    os.chdir(tmpdir)
#    tb = bin2grayBench(bin2gray = bin2grayCoSim, DATA = 8)
#    tb.run_sim(duration=4000)
#    os.chdir(cwd)
    
#if __name__ == '__main__':
#    test_binary()
