from myhdl import block, delay, instance
import inspect
from utils import functionStat

@block
def resetDriver(rst, DELAY = 5):
    functionStat(inspect.currentframe().f_code.co_name, __name__)
    """ Reset driver

    rst -- output signal, 50% duty cycle drived clock
    DELAY -- nano second delay for derived clock
    """
    @instance
    def clkgen():
        yield delay(DELAY)   
        clk.next = not clk
        yield delay(DELAY)   
        clk.next = not clk
    return clkgen