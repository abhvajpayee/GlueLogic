from myhdl import block, Signal, intbv, modbv, delay, instance, instances, always_comb, always_seq, always
from gluelogic import axi4Stream, lane
from random import randrange
import inspect
from utils import functionStat
import numpy as np
np.set_printoptions(formatter={'int':hex})

SYNC           = 0xAFAF

PKTSYNCPTR     = 0
SOURCEPTR      = 16
DESTENPTR      = 24
LENPTR         = 32
ALGOPTR        = 48
MODEPTR        = 56
PKTIDPTR       = 64

PKTSYNCSIZE    = SOURCEPTR - PKTSYNCPTR
SOURCESIZE     = DESTENPTR - SOURCEPTR
DESTENSIZE     = LENPTR    - DESTENPTR
LENSIZE        = ALGOPTR   - LENPTR
ALGOSIZE       = MODEPTR   - ALGOPTR
MODESIZE       = PKTIDPTR  - MODEPTR
PKTIDSIZE      = 80        - PKTIDPTR

@block
def node(clk, rst, axi4StreamBus, fifoBus):
    functionStat(inspect.currentframe().f_code.co_name, __name__)
    axi2lane0   = axi4Stream.axi2lane(clk, rst, axi4StreamBus)
    fifoBusInst = axi4StreamBus.laneBus.busB.toBus(fifoBus)
    return instances()

@block
def switchSelFromUpBus(clk, rst, axiSBusUp, sel, ADDRESS=0, PRIORITY=1):
    functionStat(inspect.currentframe().f_code.co_name, __name__)
    
    ctr = Signal(modbv(-1)[16:])
    selreg = Signal(bool(0))
    length, sync, sLength, sSync = [Signal(modbv(0)[16:]) for i in range(4)]
    src, dst, sSrc, sDst = [Signal(modbv(0)[8:]) for i in range(4)]
    
    @always_comb
    def headerLogic():
        sync.next   = axiSBusUp.tdata[PKTSYNCPTR + PKTSYNCSIZE: PKTSYNCPTR]
        length.next = axiSBusUp.tdata[LENPTR     + LENSIZE    : LENPTR    ]
        src.next    = axiSBusUp.tdata[SOURCEPTR  + SOURCESIZE : SOURCEPTR ]
        dst.next    = axiSBusUp.tdata[DESTENPTR  + DESTENSIZE : DESTENPTR ]
        
    @always_comb
    def combLogic():
        if axiSBusUp.tvalid:
            if sync == SYNC and dst == ADDRESS:
                sel.next = 1
            else:
                sel.next = selreg
        else:
            sel.next = 0
        
    @always_seq(clk.posedge, reset = rst)
    def SeqLogic():
        if sync == SYNC and dst == ADDRESS:
            sSync.next   = sync
            sLength.next = length
            sSrc.next    = src
            sDst.next    = dst
            selreg.next  = 1
        if sel:
            ctr.next = ctr + 1
            if ctr == sLength - 1 and ctr != 0:
                ctr.next    = 0
                selreg.next = 0
    
    return instances()
    
@block
def tNode(clk, rst, axi4StreamBusUp, axi4StreamBusDown, fifoBus, ADDRESS=0, PRIORITY=1):
    en, selS = [Signal(bool(0)) for i in range(2)]
    
    axi4StreamBus  = axi4StreamBusUp.clone()
    connectorTInst = axi4StreamBusUp.connectorT(clk, rst, axi4StreamBus, axi4StreamBusDown, en, selS)
    axi2lane0      = axi4StreamBus.axi2lane(clk, rst)
    fifoBusInst    = axi4StreamBus.laneBus.busB.toBus(fifoBus)
    switchInst     = switchSelFromUpBus(clk, rst, axi4StreamBusUp.axiSBus, selS, ADDRESS=ADDRESS, PRIORITY=PRIORITY)
    
    return instances()

def includeElement(header, data, pos):
    '''Add header elements at given bit positions in the packet'''
    header[int(pos/64)  ] = int(header[int(pos/64)  ]) ^ (data << int(     pos%64)) & 0xFFFFFFFFFFFFFFFF
    header[int(pos/64)+1] = int(header[int(pos/64)+1]) ^ (data >> int(64 - pos%64)) & 0xFFFFFFFFFFFFFFFF
    return header

def packetize(data, src, dest, algo, mode, pktid, DATA = 512):
    header = np.zeros(int(DATA/64), dtype=np.uint64  )
    header = includeElement(header, SYNC , PKTSYNCPTR)
    header = includeElement(header, src  , SOURCEPTR )
    header = includeElement(header, dest , DESTENPTR )
    header = includeElement(header, int(len(data)*64//DATA), LENPTR)
    header = includeElement(header, algo , ALGOPTR   )
    header = includeElement(header, mode , MODEPTR   )
    header = includeElement(header, pktid, PKTIDPTR  )
    pkt = np.append(header, data)
    return pkt