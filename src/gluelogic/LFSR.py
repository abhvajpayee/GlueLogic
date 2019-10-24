from myhdl import *
import inspect
from utils import functionStat

@block
def LFSR(dout, din, run, ready, clk, rst, SIZE, TRINOMIAL, IV):
    functionStat(inspect.currentframe().f_code.co_name, __name__)
    
    shiftReg = Signal(modbv(0)[SIZE:])
    feedback = Signal(bool(0))
    counter = Signal(modbv(0)[8:])
    
    @always_seq(clk.posedge, reset = rst)
    def shift():
        if run:       
            if counter < 2*SIZE:
                counter.next = counter + 1
            if counter == 0:
                shiftReg.next = IV
                ready.next = 0
            else:
                shiftReg.next = concat(shiftReg[SIZE-1:0], feedback) 
                dout.next = shiftReg[SIZE-1]
                if counter >= 2*SIZE:
                    ready.next = 1
        else:
            ready.next = 0

    @always_comb
    def taplogic():
        feedback.next = shiftReg[SIZE-1] ^ shiftReg[TRINOMIAL] ^ din
        
    return instances()


@block
def ser2par(din, we, dout, rd, clk, rst, SIZE=8):
    functionStat(inspect.currentframe().f_code.co_name, __name__)
    shiftReg = Signal(modbv(0)[SIZE:])
    counter = Signal(modbv(0)[8:])
    
    @always_seq(clk.posedge, reset = rst)
    def shift():
        if we:
            shiftReg.next = concat(shiftReg[SIZE-1:0], din)
            if counter == SIZE - 1:
                dout.next = shiftReg
                rd.next = 1
                counter.next = 0
            else:
                counter.next = counter + 1
                rd.next = 0
        
    return instances()

def LFSR_convert():
    dout  = Signal(bool(0))
    din   = Signal(bool(0))
    run   = Signal(bool(0))
    #load  = Signal(bool(0))
    ready = Signal(bool(0))
    clk   = Signal(bool(0))
    rst   = ResetSignal(0, active=1, isasync=False)
    SIZE  = 65
    TRINOMIAL = 18
    IV    = 0x00000000000001111
    
    lfsr_inst = LFSR(dout, din, run, ready, clk, rst, SIZE, TRINOMIAL, IV)
    lfsr_inst.convert(hdl='Verilog', header=hdlcfg.header, directory=hdlcfg.hdl_path)

if __name__ == '__main__':
    LFSR_convert()   
