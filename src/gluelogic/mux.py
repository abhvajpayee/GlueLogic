from myhdl import *
import random
from random import randrange
import math
import inspect
from utils import functionStat

@block
def mux(out, inp, sel):
    functionStat(inspect.currentframe().f_code.co_name, __name__)
    @always_comb
    def logic():
        out.next = inp[sel]
    return logic

@block
def select(insig, sel, outsig, ID=1):
    functionStat(inspect.currentframe().f_code.co_name, __name__)
    @always_comb
    def logic():
        if ID == sel:
            outsig.next = insig
        else:
            outsig.next = 0
    return instances()

@block
def demux(insig, outsig, sel, BITS=4):
    functionStat(inspect.currentframe().f_code.co_name, __name__)
    @always_comb
    def logic():
        for i in range(BITS):
            if modbv(i) == sel:
                outsig[i].next = insig
            else:
                outsig[i].next = 0  
    return instances()